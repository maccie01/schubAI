import os
import paddle
import numpy as np
from paddleocr import PaddleOCR
from typing import Dict, Optional
import structlog
from prometheus_client import Counter, Histogram
import time
import cv2

# Initialize metrics
MODEL_LOAD_TIME = Histogram('ocr_model_load_seconds', 'Time spent loading models')
MODEL_CACHE_HITS = Counter('ocr_model_cache_hits', 'Number of model cache hits')
MODEL_CACHE_MISSES = Counter('ocr_model_cache_misses', 'Number of model cache misses')
MODEL_QUANTIZATION_ERRORS = Counter('ocr_model_quantization_errors', 'Number of model quantization errors')

logger = structlog.get_logger()

class OCRModelManager:
    def __init__(self, cache_dir: str = "/app/models_cache"):
        self.cache_dir = cache_dir
        self.model_cache: Dict[str, paddle.jit.TranslatedLayer] = {}
        self.ocr_engine: Optional[PaddleOCR] = None
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize OCR with optimized settings
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize PaddleOCR with optimized settings for ARM64"""
        try:
            # Configure Paddle to use CPU only
            paddle.device.set_device('cpu')
            
            with MODEL_LOAD_TIME.time():
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    use_gpu=False,
                    cpu_threads=4,  # Optimized for M2 Pro
                    enable_mkldnn=False,  # Disabled for ARM64 compatibility
                    total_process_num=1,  # Single process for better control
                    show_log=True  # Enable logging for debugging
                )
            
            logger.info("OCR engine initialized successfully")
            
            # Ensure models are downloaded by running a test inference
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            _ = self.ocr_engine.ocr(test_img, cls=True)
            
            # Now that models are initialized, we can load or create quantized versions
            self._load_quantized_models()
            
        except Exception as e:
            logger.error("Failed to initialize OCR engine", error=str(e))
            raise
    
    def _load_quantized_models(self):
        """Load or create quantized models"""
        try:
            # Access the models using correct PaddleOCR attribute names
            models = {
                'det': getattr(self.ocr_engine, 'text_detector', None),
                'rec': getattr(self.ocr_engine, 'text_recognizer', None),
                'cls': getattr(self.ocr_engine, 'text_classifier', None)
            }
            
            for model_type, model in models.items():
                if model is None:
                    logger.warning(f"Model not available", model_type=model_type)
                    continue
                
                cache_path = os.path.join(self.cache_dir, f"{model_type}_model_quant")
                
                try:
                    if os.path.exists(cache_path):
                        MODEL_CACHE_HITS.inc()
                        self.model_cache[model_type] = self._load_cached_model(cache_path)
                        logger.info(f"Loaded cached model", model_type=model_type)
                    else:
                        MODEL_CACHE_MISSES.inc()
                        logger.info(f"Using original model", model_type=model_type)
                        # Use original model directly
                        self.model_cache[model_type] = model
                
                except Exception as e:
                    MODEL_QUANTIZATION_ERRORS.inc()
                    logger.error(f"Failed to load model", 
                               model_type=model_type, 
                               error=str(e))
                    # Use original model as fallback
                    self.model_cache[model_type] = model
        
        except Exception as e:
            logger.error("Failed to load models", error=str(e))
            raise
    
    def _save_model(self, model: paddle.jit.TranslatedLayer, path: str):
        """Save quantized model to disk"""
        try:
            paddle.jit.save(model, path)
            logger.info("Saved quantized model", path=path)
        except Exception as e:
            logger.error("Failed to save model", path=path, error=str(e))
            raise
    
    def _load_cached_model(self, path: str) -> paddle.jit.TranslatedLayer:
        """Load quantized model from disk"""
        try:
            model = paddle.jit.load(path)
            logger.info("Loaded cached model", path=path)
            return model
        except Exception as e:
            logger.error("Failed to load cached model", path=path, error=str(e))
            raise
    
    def process_image(self, image_data: bytes) -> list:
        """Process image using optimized models"""
        if not self.ocr_engine:
            raise RuntimeError("OCR engine not initialized")
        
        try:
            logger.info("Starting image processing", data_size=len(image_data))
            
            # Convert bytes to numpy array and decode as image
            np_arr = np.frombuffer(image_data, np.uint8)
            logger.debug("Converted bytes to numpy array", array_shape=np_arr.shape)
            
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                logger.error("Image decoding failed", array_size=len(np_arr))
                raise ValueError("Failed to decode image")
            
            logger.debug("Image decoded successfully", image_shape=image.shape)
            
            # Check if image is grayscale (2D array) and convert to RGB if needed
            if len(image.shape) == 2:
                logger.debug("Converting grayscale to RGB")
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                # Convert BGR to RGB (OpenCV loads as BGR, but PaddleOCR expects RGB)
                logger.debug("Converting BGR to RGB")
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                logger.error("Invalid image format", shape=image.shape)
                raise ValueError(f"Unexpected image format with shape {image.shape}")
            
            logger.debug("Image prepared for OCR", final_shape=image.shape)
            
            # Process with OCR engine
            result = self.ocr_engine.ocr(image, cls=True)
            logger.debug("OCR result", result=result)
            
            # Extract text from result
            texts = []
            if result and isinstance(result, list):
                for line in result:
                    if isinstance(line, list):
                        for item in line:
                            if isinstance(item, list) and len(item) == 2:
                                # item[1] is (text, confidence)
                                text, confidence = item[1]
                                texts.append(text)
            
            logger.info("OCR processing completed", 
                       num_texts=len(texts), 
                       texts=texts)
            return texts
            
        except Exception as e:
            logger.error("Image processing failed", error=str(e))
            raise 