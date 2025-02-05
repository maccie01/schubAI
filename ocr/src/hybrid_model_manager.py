import os
import structlog
from typing import List, Dict, Optional
from prometheus_client import Counter, Histogram
import time
from ocr.model_manager import OCRModelManager as PaddleOCRModelManager
from ocr.qwen_model_manager import QwenOCRModelManager
import langdetect

# Initialize metrics
MODEL_SWITCH_TIME = Histogram('ocr_model_switch_seconds', 'Time spent switching between OCR models')
MODEL_SELECTION_COUNT = Counter('ocr_model_selection_total', 'Number of times each model was selected',
                              labelnames=['model'])

logger = structlog.get_logger()

class HybridOCRManager:
    """Manages multiple OCR engines and selects the best one for each task"""
    
    def __init__(self, 
                 paddle_cache_dir: str = "/app/models_cache/paddle",
                 qwen_cache_dir: str = "/app/models_cache/qwen",
                 preferred_engine: Optional[str] = None):
        """Initialize OCR engines"""
        self.paddle_manager = PaddleOCRModelManager(cache_dir=paddle_cache_dir)
        self.qwen_manager = QwenOCRModelManager(cache_dir=qwen_cache_dir)
        self.preferred_engine = preferred_engine
        
        # Get engine capabilities
        self.paddle_info = self.paddle_manager.get_engine_info()
        self.qwen_info = self.qwen_manager.get_engine_info()
        
        logger.info("Hybrid OCR manager initialized",
                   paddle_info=self.paddle_info,
                   qwen_info=self.qwen_info,
                   preferred_engine=preferred_engine)
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of a text sample"""
        try:
            return langdetect.detect(text)
        except:
            return "en"  # Default to English if detection fails
    
    def _select_engine(self, sample_text: Optional[str] = None) -> str:
        """Select the best OCR engine based on content and capabilities"""
        with MODEL_SWITCH_TIME.time():
            # If preferred engine is set, use it
            if self.preferred_engine:
                MODEL_SELECTION_COUNT.labels(model=self.preferred_engine).inc()
                logger.info(f"Using preferred engine: {self.preferred_engine}")
                return self.preferred_engine
            
            # Detect language if sample text is available
            if sample_text:
                lang = self._detect_language(sample_text)
                logger.debug("Language detected", language=lang)
            else:
                lang = "en"  # Default to English
            
            # Use Qwen for English content (now that it's fully implemented)
            if lang == "en":
                MODEL_SELECTION_COUNT.labels(model="qwen").inc()
                logger.info("Selected Qwen OCR for English content")
                return "qwen"
            
            # Use PaddleOCR for non-English content
            MODEL_SELECTION_COUNT.labels(model="paddle").inc()
            logger.info("Selected PaddleOCR for non-English content", language=lang)
            return "paddle"
    
    def process_image(self, image_data: bytes, sample_text: Optional[str] = None) -> List[str]:
        """Process image using the best available OCR engine"""
        engine = self._select_engine(sample_text)
        
        try:
            if engine == "qwen":
                logger.info("Processing with Qwen OCR")
                return self.qwen_manager.process_image(image_data)
            else:
                logger.info("Processing with PaddleOCR")
                return self.paddle_manager.process_image(image_data)
                
        except Exception as e:
            logger.error(f"Error processing with {engine}", error=str(e))
            # Fallback to PaddleOCR if Qwen fails
            if engine == "qwen":
                logger.info("Falling back to PaddleOCR")
                return self.paddle_manager.process_image(image_data)
            raise
    
    def get_status(self) -> Dict[str, any]:
        """Get status of all OCR engines"""
        return {
            "paddle": self.paddle_info,
            "qwen": self.qwen_info,
            "preferred_engine": self.preferred_engine
        } 