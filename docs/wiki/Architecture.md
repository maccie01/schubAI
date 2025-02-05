# schubAI Architecture

## System Overview

schubAI is built on a microservices architecture optimized for Apple Silicon (M2 Pro) with a focus on containerization and resource efficiency.

```
Docker Services:
├── Core Services
│   ├── Frontend (Next.js)
│   ├── Backend (Node.js)
│   └── OCR Service (FastAPI)
├── Storage & Search
│   ├── Qdrant Vector Store
│   └── SearXNG Search
└── Monitoring Stack
    ├── Prometheus
    ├── Grafana
    ├── Loki
    └── Promtail
```

## Component Details

### 1. Core Services

#### Frontend Service (Port 3000)
- **Technology**: Next.js 14
- **Resources**: 4GB RAM
- **Features**:
  - Modern React components
  - Server-side rendering
  - Real-time updates
  - Responsive design

#### Backend Service (Port 3001)
- **Technology**: Node.js
- **Resources**: 12GB RAM
- **Features**:
  - REST API endpoints
  - WebSocket support
  - Document processing
  - Search orchestration

#### OCR Service (Port 8082)
- **Technology**: FastAPI/Python
- **Resources**: 2GB RAM
- **Features**:
  - Hybrid OCR engine (PaddleOCR + Qwen-VL)
  - MLX optimization
  - Batch processing
  - Language detection

### 2. Storage & Search

#### Qdrant Vector Store (Port 6333)
- **Technology**: Qdrant
- **Resources**: 4GB RAM
- **Features**:
  - Vector similarity search
  - ARM64 optimization
  - Persistent storage
  - High performance

#### SearXNG Search (Port 4000)
- **Technology**: SearXNG
- **Resources**: 2GB RAM
- **Features**:
  - Meta search capabilities
  - Privacy focus
  - Rate limiting
  - Custom engines

### 3. Monitoring Stack

#### Prometheus (Port 9090)
- Metrics collection
- Resource monitoring
- Alert management
- Query interface

#### Grafana (Port 3002)
- Visualization
- Dashboards
- Alert configuration
- Data analysis

#### Loki & Promtail
- Log aggregation
- Search capabilities
- Real-time monitoring
- Retention management

## Resource Management

### Memory Allocation
```yaml
Resources:
  Backend: 
    limit: 12GB
    reserved: 8GB
  Frontend:
    limit: 4GB
    reserved: 2GB
  OCR:
    limit: 2GB
    reserved: 1GB
  Qdrant:
    limit: 4GB
    reserved: 2GB
  SearXNG:
    limit: 2GB
    reserved: 1GB
  Monitoring:
    limit: 4GB
    reserved: 2GB
```

### Storage Configuration
```yaml
Volumes:
  - backend-dbstore:/app/data
  - uploads:/app/uploads
  - qdrant-storage:/qdrant/storage
  - prometheus-data:/prometheus
  - grafana-data:/var/lib/grafana
  - loki-data:/loki
```

## Network Architecture

### Internal Network
- Network: perplexica-network
- Driver: bridge
- Internal: false

### Port Mapping
```yaml
Ports:
  Frontend: 3000:3000
  Backend: 3001:3001
  Grafana: 3002:3000
  SearXNG: 4000:8080
  Qdrant: 6333:6333
  OCR: 8082:8000
  Prometheus: 9090:9090
```

## Security Considerations

### Container Security
- Non-root users
- Limited capabilities
- Resource constraints
- Volume permissions

### Network Security
- Internal network isolation
- Exposed ports minimization
- Health check security
- Rate limiting

## Development Guidelines

### Docker Best Practices
1. Use multi-stage builds
2. Implement proper caching
3. Optimize layer ordering
4. Minimize image size

### Resource Optimization
1. Monitor memory usage
2. Implement proper cleanup
3. Use efficient algorithms
4. Cache when appropriate

### Error Handling
1. Implement health checks
2. Add proper logging
3. Use graceful degradation
4. Monitor error rates

## Future Architecture

### Planned Enhancements
1. Distributed training support
2. Advanced caching layer
3. Auto-scaling capabilities
4. High availability setup

### Scalability Considerations
1. Service replication
2. Load balancing
3. Database sharding
4. Cache distribution 