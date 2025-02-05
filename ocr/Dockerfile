# Build stage
FROM --platform=linux/arm64/v8 python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libopenblas-dev \
    cmake \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install OCR dependencies optimized for ARM64
RUN pip install --no-cache-dir \
    paddlepaddle==2.6.0 \
    "paddleocr>=2.7.0.3" \
    transformers==4.36.2 \
    transformers_stream_generator==0.0.4 \
    einops==0.7.0 \
    safetensors==0.4.1 \
    torch==2.1.2 \
    numpy==1.26.3 \
    Pillow==10.2.0 \
    opencv-python-headless==4.9.0.80 \
    fastapi==0.109.0 \
    uvicorn==0.27.0.post1 \
    python-multipart==0.0.6 \
    prometheus-client==0.19.0 \
    python-json-logger==2.0.7 \
    albumentations==1.3.1 \
    structlog==23.1.0 \
    paddle2onnx==1.3.1 \
    cachetools==5.3.2 \
    aiofiles==23.2.1

# Create cache directories
RUN mkdir -p /root/.paddleocr/whl \
    /root/.cache/huggingface \
    /root/.cache/paddle \
    /root/.cache/torch

# Runtime stage
FROM --platform=linux/arm64/v8 python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libopenblas0 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 ocr

# Set up working directory and create necessary directories
WORKDIR /app
RUN mkdir -p \
    /app/temp \
    /app/logs \
    /app/models \
    /app/models/cache \
    /app/models/offload \
    /home/ocr/.paddleocr/whl \
    /home/ocr/.cache/huggingface && \
    chown -R ocr:ocr \
    /app \
    /home/ocr/.paddleocr \
    /home/ocr/.cache

# Set environment variables for model caching
ENV PADDLE_OCR_CACHE_DIR=/home/ocr/.paddleocr/whl \
    TRANSFORMERS_CACHE=/home/ocr/.cache/huggingface \
    HF_HOME=/home/ocr/.cache/huggingface \
    QWEN_OFFLOAD_DIR=/app/models/offload

# Copy application code
COPY --chown=ocr:ocr ./src /app/ocr

# Set environment variables for M2 Pro optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PADDLE_INFERENCE_CPU_MATH_LIBRARY_NUM_THREADS=8
ENV OCR_WORKER_THREADS=4
ENV OCR_QUEUE_SIZE=10
ENV PADDLE_INFERENCE_USE_MLX=1
ENV PADDLE_INFERENCE_MLX_THREADS=4
ENV PADDLE_INFERENCE_MLX_CACHE_CAPACITY=2048
ENV PADDLE_INFERENCE_MLX_WORKSPACE_SIZE=4096
ENV TORCH_HOME=/home/ocr/.cache/torch
ENV PADDLE_HOME=/home/ocr/.cache/paddle

# Switch to non-root user
USER ocr

# Health check with proper port
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD wget -q --spider http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Start OCR service with optimized workers
CMD ["python", "-m", "uvicorn", "ocr.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--limit-concurrency", "20"] 