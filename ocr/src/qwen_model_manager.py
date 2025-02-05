import os
import numpy as np
import cv2
import structlog
from typing import List, Optional, Dict
from prometheus_client import Counter, Histogram
import time
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
import re
from PIL import Image
import io

# Initialize metrics
QWEN_MODEL_LOAD_TIME = Histogram('qwen_ocr_model_load_seconds', 'Time spent loading Qwen models')
QWEN_MODEL_CACHE_HITS = Counter('qwen_ocr_cache_hits', 'Number of Qwen model cache hits')
QWEN_MODEL_CACHE_MISSES = Counter('qwen_ocr_cache_misses', 'Number of Qwen model cache misses')
QWEN_PROCESSING_TIME = Histogram('qwen_ocr_processing_seconds', 'Time spent processing with Qwen OCR')

logger = structlog.get_logger()

class QwenOCRModelManager:
    """Manages Qwen OCR models and processing"""
    
    def __init__(self, cache_dir: str = "/app/models_cache/qwen"):
        self.cache_dir = cache_dir
        self.model = None
        self.processor = None
        self.initialized = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize OCR
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize Qwen OCR with optimized settings for ARM64"""
        try:
            with QWEN_MODEL_LOAD_TIME.time():
                # Load model with optimizations
                offload_dir = os.getenv("QWEN_OFFLOAD_DIR", "/app/models/offload")
                os.makedirs(offload_dir, exist_ok=True)
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    "Qwen/Qwen-VL-Chat",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto",
                    cache_dir=self.cache_dir,
                    offload_folder=offload_dir,
                    trust_remote_code=True
                )
                
                # Load processor
                self.processor = AutoProcessor.from_pretrained(
                    "Qwen/Qwen-VL-Chat",
                    cache_dir=self.cache_dir,
                    trust_remote_code=True
                )
                
                # Run a test inference to ensure everything is working
                test_img = np.zeros((100, 100, 3), dtype=np.uint8)
                test_img_bytes = cv2.imencode('.png', test_img)[1].tobytes()
                _ = self.process_image(test_img_bytes)
                
                self.initialized = True
                logger.info("Qwen OCR engine initialized successfully",
                          device=self.device,
                          model_path=os.path.join(self.cache_dir, "Qwen-VL-Chat"))
                
        except Exception as e:
            logger.error("Failed to initialize Qwen OCR engine", error=str(e))
            raise
    
    def process_image(self, image_data: bytes) -> List[str]:
        """Process image using Qwen OCR"""
        if not self.initialized:
            raise RuntimeError("Qwen OCR engine not initialized")
        
        try:
            with QWEN_PROCESSING_TIME.time():
                logger.info("Starting Qwen OCR processing", data_size=len(image_data))
                
                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(image_data))
                logger.debug("Image loaded successfully", size=image.size)
                
                # Prepare messages for the model
                messages = [{
                    "role": "user",
                    "content": [{
                        "type": "image",
                        "image": image
                    }, {
                        "type": "text",
                        "text": "Extract all text from this image with bounding boxes and confidence scores. Format each text element as: 'text (confidence: score)'"
                    }]
                }]
                
                # Process input
                inputs = self.processor(
                    text=self.processor.apply_chat_template(messages, tokenize=False),
                    images=[image],
                    return_tensors="pt"
                ).to(self.device)
                
                # Generate OCR results
                with torch.inference_mode():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_new_tokens=512,
                        do_sample=False
                    )
                
                # Decode results
                raw_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                
                # Extract text elements and confidence scores
                texts = self._parse_ocr_output(raw_text)
                
                logger.info("Qwen OCR processing completed", 
                           num_texts=len(texts), 
                           texts=texts)
                return texts
                
        except Exception as e:
            logger.error("Qwen OCR processing failed", error=str(e))
            raise
    
    def _parse_ocr_output(self, raw_text: str) -> List[str]:
        """Parse the raw OCR output to extract text elements"""
        # Split into lines and clean up
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # Extract text elements (assuming format: "text (confidence: score)")
        texts = []
        for line in lines:
            # Skip non-text lines
            if not line or line.startswith(('I found', 'Here are', 'The text', 'Bounding box')):
                continue
                
            # Extract text and confidence if available
            match = re.match(r'"([^"]+)"(?:\s*\(confidence:\s*([\d.]+)\))?', line)
            if match:
                text = match.group(1)
                texts.append(text)
            else:
                # If no match, just add the line as is
                texts.append(line)
        
        return texts
    
    def get_engine_info(self) -> Dict[str, any]:
        """Get information about the OCR engine"""
        return {
            "name": "Qwen OCR",
            "version": "2.0.0",
            "models": {
                "base": "Qwen-VL-Chat"
            },
            "initialized": self.initialized,
            "cache_dir": self.cache_dir,
            "device": self.device,
            "capabilities": {
                "languages": ["en"],
                "optimizations": ["arm64", "mlx", "cuda" if self.device == "cuda" else "cpu"],
                "features": [
                    "text_detection",
                    "text_recognition",
                    "layout_analysis",
                    "confidence_scores"
                ]
            }
        } 