from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
import structlog
import time
import os
from typing import Dict, List, Optional
import aiofiles
from ocr.pipeline_manager import OCRPipeline
from ocr.hybrid_model_manager import HybridOCRManager

# Initialize logging
logger = structlog.get_logger()

# Initialize metrics
OCR_REQUESTS = Counter('ocr_requests_total', 'Total OCR requests')
OCR_ERRORS = Counter('ocr_errors_total', 'Total OCR errors')
OCR_PROCESSING_TIME = Histogram('ocr_processing_seconds', 'Time spent processing OCR requests')

# Initialize test metrics
TEST_OCR_REQUESTS = Counter('test_ocr_requests_total', 'Total test OCR requests')
TEST_OCR_ERRORS = Counter('test_ocr_errors_total', 'Total test OCR errors')
TEST_OCR_PROCESSING_TIME = Histogram('test_ocr_processing_seconds', 'Time spent processing test OCR requests')

# Initialize FastAPI app
app = FastAPI(
    title="Perplexica OCR Service",
    root_path="/",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model_manager = None
pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global model_manager, pipeline
    try:
        # Initialize hybrid model manager
        model_manager = HybridOCRManager(
            paddle_cache_dir=os.path.join(os.getenv("PADDLE_OCR_CACHE_DIR", "/app/models_cache"), "paddle"),
            qwen_cache_dir=os.path.join(os.getenv("PADDLE_OCR_CACHE_DIR", "/app/models_cache"), "qwen")
        )
        logger.info("Model manager initialized successfully")
        
        # Initialize pipeline with hybrid manager
        pipeline = OCRPipeline(
            model_manager=model_manager,
            max_workers=int(os.getenv("OCR_WORKER_THREADS", "4")),
            queue_size=int(os.getenv("OCR_QUEUE_SIZE", "10"))
        )
        logger.info("Pipeline initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global pipeline
    if pipeline:
        await pipeline.shutdown()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not model_manager or not pipeline:
        return {
            "status": "unhealthy",
            "details": {
                "ready": False,
                "models_loaded": False,
                "pipeline_active": False
            }
        }
    
    status = model_manager.get_status()
    return {
        "status": "healthy",
        "details": {
            "ready": True,
            "models_loaded": True,
            "pipeline_active": pipeline.processing,
            "engines": status
        }
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.post("/ocr")
async def process_image(
    file: UploadFile = File(...),
    engine: Optional[str] = Query(None, enum=["paddle", "qwen"]),
    language: str = Query("en", description="Language code for OCR")
):
    """Process image with OCR"""
    OCR_REQUESTS.inc()
    
    try:
        logger.info("Received file upload request", 
                   filename=file.filename, 
                   content_type=file.content_type,
                   size=file.size if hasattr(file, 'size') else 'unknown',
                   engine=engine,
                   language=language)
        
        # Read file content
        contents = await file.read()
        
        logger.info("File read complete", 
                   total_size=len(contents))
        
        # Process image with specified engine preference
        task_id = await pipeline.process_image(contents, engine, language)
        logger.info("Image queued for processing", task_id=task_id)
        
        return {"task_id": task_id, "status": "processing"}
        
    except Exception as e:
        OCR_ERRORS.inc()
        logger.error("Failed to process image", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ocr/{task_id}")
async def get_result(task_id: str):
    """Get OCR result for task ID"""
    result = pipeline.get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@app.get("/test/health")
async def test_health_check():
    """Test health check endpoint"""
    if not model_manager or not pipeline:
        return {
            "status": "unhealthy",
            "details": {
                "ready": False,
                "models_loaded": False,
                "pipeline_active": False,
                "test": True
            }
        }
    
    status = model_manager.test_get_status()
    return {
        "status": "healthy",
        "details": {
            "ready": True,
            "models_loaded": True,
            "pipeline_active": pipeline.processing,
            "engines": status,
            "test": True
        }
    }

@app.post("/test/ocr")
async def test_process_image(
    file: UploadFile = File(...),
    engine: Optional[str] = Query(None, enum=["paddle", "qwen"]),
    language: str = Query("en", description="Language code for OCR")
):
    """Process image with OCR in test mode"""
    TEST_OCR_REQUESTS.inc()
    
    try:
        logger.info("Test: Received file upload request", 
                   filename=file.filename, 
                   content_type=file.content_type,
                   size=file.size if hasattr(file, 'size') else 'unknown',
                   engine=engine,
                   language=language)
        
        # Read file content
        contents = await file.read()
        
        logger.info("Test: File read complete", 
                   total_size=len(contents))
        
        # Process image with specified engine preference in test mode
        task_id = await pipeline.test_process_image(contents, engine, language)
        logger.info("Test: Image queued for processing", task_id=task_id)
        
        return {"task_id": task_id, "status": "processing", "test": True}
        
    except Exception as e:
        TEST_OCR_ERRORS.inc()
        logger.error("Test: Failed to process image", error=str(e))
        raise HTTPException(status_code=500, detail=f"Test: {str(e)}")

@app.get("/test/ocr/{task_id}")
async def test_get_result(task_id: str):
    """Get OCR result for task ID in test mode"""
    result = pipeline.test_get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Test: Task not found")
    return {**result, "test": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips="*",
        root_path="/"
    ) 