from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog
import psutil
import time
from typing import Dict, List

# Initialize logging
logger = structlog.get_logger()

# Initialize metrics
TRAINING_REQUESTS = Counter('training_requests_total', 'Total training requests')
TRAINING_ERRORS = Counter('training_errors_total', 'Total training errors')
TRAINING_TIME = Histogram('training_seconds', 'Time spent on training')
GPU_MEMORY = Gauge('gpu_memory_usage_bytes', 'GPU memory usage in bytes')

# Initialize FastAPI app
app = FastAPI(title="Perplexica Training Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint with GPU status."""
    try:
        # Test PyTorch device availability
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        x = torch.tensor([1, 2, 3], device=device)
        y = torch.tensor([4, 5, 6], device=device)
        z = x + y
        
        gpu_status = "available" if torch.backends.mps.is_available() else "cpu_only"
        
        return {
            "status": "healthy",
            "gpu": gpu_status,
            "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f}MB"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.post("/train/status")
async def training_status() -> Dict[str, Dict]:
    """Get current training status and resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            "resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "gpu_status": "active" if torch.backends.mps.is_available() else "inactive"
            }
        }
    except Exception as e:
        logger.error("Status check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 