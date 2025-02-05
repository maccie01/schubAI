# Perplexica Technical Specifications

## Executive Summary
This document provides comprehensive technical specifications for the Perplexica Docker implementation, optimized for Apple M2 Pro hardware. The system utilizes a microservices architecture with containerized components, focusing on performance, security, and maintainability.

## Table of Contents
1. Docker Infrastructure
2. Build System
3. Resource Management
4. Monitoring & Logging
5. Security Implementation
6. Performance Optimization
7. Configuration Management
8. Maintenance Procedures
9. Development Guidelines
10. Deployment Process

## 1. Docker Infrastructure

### 1.1 Base Architecture
The system is built on a microservices architecture with Docker containers, optimized for Apple M2 Pro hardware:

#### Core Components
1. **Backend Service**
   - Runtime: Node.js 20 on Bullseye Slim
   - Memory: 8GB limit
   - Ports: 3001 (HTTP/WebSocket)
   - Key Features:
     * WebSocket server for real-time communication
     * SQLite database with Drizzle ORM
     * Health monitoring endpoints
     * Resource usage tracking

2. **Vector Store (Qdrant)**
   - Version: 1.8.0-arm64
   - Memory: 4GB limit
   - Ports: 6333
   - Storage: Persistent volume mount
   - Features:
     * Vector similarity search
     * Collection management
     * Health monitoring
     * Backup/restore capability

3. **OCR Service**
   - Base: PaddleOCR with FastAPI
   - Memory: 2GB limit
   - Ports: 8080
   - Features:
     * Document text extraction
     * Image preprocessing
     * Batch processing capability
     * Health monitoring

4. **Local Training Service**
   - Memory: 8GB limit
   - GPU: MLX/Metal integration
   - Features:
     * Model fine-tuning
     * Training metrics collection
     * Resource monitoring
     * Checkpoint management

### 1.2 Container Networking
```yaml
Networks:
  perplexica-network:
    driver: bridge
    internal: false
    dns_resolution: enabled
    subnet: 172.20.0.0/16
```

### 1.3 Volume Management
```yaml
Volumes:
  data:
    - /app/data         # Database storage
    - /app/uploads      # User uploads
    - /app/models       # Model files
    - /app/logs         # Service logs
  temp:
    - /app/temp         # Processing workspace
    - /tmp/perplexica   # Host temp directory
```

## 2. Build System

### 2.1 Multi-stage Build Process
```dockerfile
# Build Stage
FROM node:20-bullseye AS builder
- Typescript compilation
- Dependency installation
- Resource optimization

# Runtime Stage
FROM node:20-bullseye-slim
- Minimal runtime dependencies
- Security hardening
- Configuration injection
```

### 2.2 BuildKit Optimization
1. **Cache Management**
   ```yaml
   cache:
     type: buildkit
     mode: max
     sharing: shared
     compression: true
   ```

2. **Layer Strategy**
   - Base image selection
   - Dependency installation
   - Source code copying
   - Configuration
   - Runtime setup

### 2.3 ARM64 Optimization
1. **Base Images**
   - Native ARM64 support
   - Minimal runtime footprint
   - Security hardening

2. **Rosetta 2 Integration**
   - x86 compatibility layer
   - Performance optimization
   - Resource monitoring

## 3. Resource Management

### 3.1 Memory Allocation
```yaml
limits:
  backend:
    memory: 8GB
    node_heap: 8GB
  rag:
    memory: 12GB
  training:
    memory: 8GB
  ocr:
    memory: 2GB
  vector_store:
    memory: 4GB
```

### 3.2 CPU Management
```yaml
cpu:
  backend:
    cores: 4
    threads: 8
  ocr:
    cores: 2
  training:
    cores: 6
```

### 3.3 GPU Configuration
```yaml
gpu:
  type: mps
  device: /dev/mlx0
  env:
    MLX_ENABLE_METAL: 1
    MLX_USE_METAL_GPU: 1
    METAL_DEVICE_WRAPPER_TYPE: 1
```

## 4. Monitoring & Logging

### 4.1 Health Checks
```yaml
health_check:
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 5s
  endpoints:
    - /health
    - /metrics
```

### 4.2 Metrics Collection
1. **System Metrics**
   - CPU usage
   - Memory utilization
   - Network I/O
   - Disk usage

2. **Application Metrics**
   - Request latency
   - Error rates
   - Queue lengths
   - Processing times

### 4.3 Logging Infrastructure
```yaml
logging:
  driver: json-file
  options:
    max-size: 10m
    max-file: 3
  format: json
  fields:
    - timestamp
    - level
    - message
    - service
    - container_id
```

## 5. Security Implementation

### 5.1 Container Security
```yaml
security:
  user: non-root
  capabilities:
    drop: [ALL]
  read_only: true
  no_new_privileges: true
```

### 5.2 Network Security
1. **Service Isolation**
   - Internal network segmentation
   - Minimal port exposure
   - TLS termination

2. **Access Control**
   - Service authentication
   - Rate limiting
   - IP filtering

## 6. Performance Optimization

### 6.1 Build Performance
- Current backend build time: 39.2s
- Cache hit rate: ~85%
- Layer optimization
- Dependency caching

### 6.2 Runtime Performance
- Container startup: ~3s
- Database migration: 0.4s
- Health check latency: <100ms
- Memory footprint: 71MB RSS

## 7. Configuration Management

### 7.1 Environment Variables
```toml
[GENERAL]
PORT = 3001
HOST = "0.0.0.0"
KEEP_ALIVE = "5m"

[API_ENDPOINTS]
SEARXNG = "http://searxng:8080"
OLLAMA = "http://host.docker.internal:11434"
QDRANT = "http://qdrant:6333"
OCR = "http://ocr-service:8080"

[STORAGE]
DATABASE_URL = "sqlite:///app/data/perplexica.db"
UPLOAD_DIR = "/app/uploads"
MODEL_DIR = "/app/models"

[LOGGING]
LOG_LEVEL = "info"
LOG_FORMAT = "json"
```

### 7.2 Secrets Management
1. **API Keys**
   - OpenAI
   - Groq
   - Anthropic
   - Gemini

2. **Service Credentials**
   - Database
   - Vector store
   - External services

## 8. Maintenance Procedures

### 8.1 Regular Maintenance
1. **Daily Tasks**
   - Log rotation
   - Health check verification
   - Resource monitoring
   - Backup verification

2. **Weekly Tasks**
   - Security updates
   - Performance analysis
   - Resource optimization
   - Configuration review

### 8.2 Troubleshooting Guide
1. **Container Issues**
   ```bash
   # Check container status
   docker ps -a
   
   # View logs
   docker logs <container>
   
   # Check resource usage
   docker stats
   
   # Inspect configuration
   docker inspect <container>
   ```

2. **Network Issues**
   ```bash
   # Check network connectivity
   docker network inspect perplexica-network
   
   # Test service discovery
   docker exec <container> ping <service>
   
   # Verify port mappings
   docker port <container>
   ```

## 9. Development Guidelines

### 9.1 Local Development
1. **Setup Requirements**
   - Docker Desktop for Mac
   - Node.js 20.x
   - Python 3.11+
   - Xcode Command Line Tools

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository>
   
   # Install dependencies
   yarn install
   
   # Start development environment
   docker compose up -d
   ```

### 9.2 Testing Procedures
1. **Unit Tests**
   - Service-level testing
   - API endpoint validation
   - Error handling verification

2. **Integration Tests**
   - Cross-service communication
   - Data flow validation
   - Resource management

3. **Performance Tests**
   - Load testing
   - Resource utilization
   - Scalability verification

## 10. Deployment Process

### 10.1 Production Deployment
1. **Pre-deployment Checks**
   - Configuration validation
   - Resource availability
   - Security verification
   - Backup confirmation

2. **Deployment Steps**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Build containers
   docker compose build
   
   # Deploy services
   docker compose up -d
   
   # Verify deployment
   docker compose ps
   ```

### 10.2 Rollback Procedures
1. **Quick Rollback**
   ```bash
   # Revert to previous version
   docker compose down
   git checkout <previous-tag>
   docker compose up -d
   ```

2. **Data Recovery**
   - Database restore
   - Configuration rollback
   - Service state recovery

## Appendix A: Service Dependencies
- Node.js 20.x
- Python 3.11+
- Docker Engine 24.x
- MLX Framework
- PaddleOCR
- Qdrant Vector Store
- SQLite3

## Appendix B: Resource Requirements
- Minimum RAM: 32GB
- Storage: 100GB SSD
- CPU: 8 cores
- GPU: Apple M2 Pro

## Appendix C: Network Ports
- Backend: 3001
- Vector Store: 6333
- OCR Service: 8080
- Monitoring: 9090
- Grafana: 3000

## Appendix D: Backup Strategy
1. **Database Backups**
   - Daily incremental
   - Weekly full backup
   - 30-day retention

2. **Configuration Backups**
   - Version controlled
   - Environment-specific
   - Encrypted secrets

3. **Model Checkpoints**
   - After each training
   - Version tagged
   - Performance metrics included 