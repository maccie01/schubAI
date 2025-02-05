# Build stage
FROM --platform=linux/arm64/v8 python:3.11-slim as builder

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
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install OCR dependencies with specific versions for ARM64
RUN pip install --no-cache-dir \
    paddlepaddle==2.6.0 \
    "paddleocr>=2.7.0" \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    python-multipart==0.0.6 \
    prometheus-client==0.19.0 \
    python-json-logger==2.0.7 \
    numpy==1.24.3 \
    opencv-python-headless==4.8.1.78 \
    albumentations==1.3.1 \
    structlog==23.1.0

# Runtime stage
FROM --platform=linux/arm64/v8 python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libopenblas0 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 ocr
USER ocr

# Set up working directory
WORKDIR /app

# Copy application code
COPY --chown=ocr:ocr ./src/ocr ./ocr

# Set Python path
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/temp /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose API port
EXPOSE 8080

# Start OCR service
CMD ["python", "-m", "uvicorn", "ocr.main:app", "--host", "0.0.0.0", "--port", "8080"] 