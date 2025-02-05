from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from prometheus_client import Counter, Histogram, generate_latest
import structlog
import time
import os
from typing import Dict, List

# Initialize logging
logger = structlog.get_logger()

# Initialize metrics
OCR_REQUESTS = Counter('ocr_requests_total', 'Total OCR requests')
OCR_ERRORS = Counter('ocr_errors_total', 'Total OCR errors')
OCR_PROCESSING_TIME = Histogram('ocr_processing_seconds', 'Time spent processing OCR requests')

# Initialize FastAPI app
app = FastAPI(title="Perplexica OCR Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PaddleOCR with optimized settings for ARM64
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    use_gpu=False,
    cpu_threads=4,  # Optimize for M2 Pro
    enable_mkldnn=False,  # Disable MKL-DNN due to ARM64 compatibility
    total_process_num=1  # Single process for better resource control
)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.post("/ocr")
async def process_image(file: UploadFile = File(...)) -> Dict[str, List[str]]:
    """Process an image and extract text using OCR."""
    OCR_REQUESTS.inc()
    start_time = time.time()
    
    try:
        # Save uploaded file temporarily
        temp_path = f"/app/temp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with PaddleOCR
        result = ocr.ocr(temp_path, cls=True)
        
        # Extract text from results
        texts = []
        for line in result:
            for word_info in line:
                text = word_info[1][0]  # Extract text from OCR result
                texts.append(text)
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Record processing time
        processing_time = time.time() - start_time
        OCR_PROCESSING_TIME.observe(processing_time)
        
        logger.info("OCR processing successful",
                   file_name=file.filename,
                   processing_time=processing_time,
                   text_blocks=len(texts))
        
        return {"texts": texts}
    
    except Exception as e:
        OCR_ERRORS.inc()
        logger.error("OCR processing failed",
                    file_name=file.filename,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 