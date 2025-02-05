# Build stage
FROM --platform=linux/arm64/v8 python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM --platform=linux/arm64/v8 python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set MLX environment variables
ENV MLX_ENABLE_METAL=1
ENV MLX_USE_METAL_GPU=1
ENV METAL_DEVICE_WRAPPER_TYPE=1

# Create non-root user
RUN useradd -m -u 1000 trainer
USER trainer

# Set up working directory
WORKDIR /app

# Copy application code
COPY --chown=trainer:trainer ./src/training ./app/training
COPY --chown=trainer:trainer ./config.toml ./app/config.toml

# Create necessary directories
RUN mkdir -p /app/models /app/data /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose metrics port
EXPOSE 8080

# Set resource constraints
ENV MEMORY_LIMIT=8G
ENV CPU_LIMIT=4

# Start training service
CMD ["python", "-m", "training.main"] 