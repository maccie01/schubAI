# schubAI Development Roadmap

## Current Phase: Alpha (1.0.0-alpha)

### Immediate Focus (Q1 2024)

#### 1. Training Service Implementation
- [ ] Complete Local Training Service
  - [ ] Memory limit: 8GB
  - [ ] GPU access configuration
  - [ ] Model registry integration
  - [ ] Training metrics exposure
- [ ] MLX Integration
  - [ ] GPU passthrough setup
  - [ ] Performance optimization
  - [ ] Resource monitoring

#### 2. Monitoring Enhancements
- [ ] Set up Grafana dashboards for Loki metrics
- [ ] Configure alerting for resource usage
- [ ] Implement log rotation policies
- [ ] Add storage usage monitoring

#### 3. Security Improvements
- [ ] Review container permissions
- [ ] Implement proper secrets management
- [ ] Configure network policies
- [ ] Add log encryption at rest

### Short-term Goals (Q2 2024)

#### 1. Performance Optimization
- [ ] Monitor memory usage patterns
- [ ] Optimize container startup sequence
- [ ] Fine-tune log ingestion rates
- [ ] Implement log compression

#### 2. OCR Service Enhancements
- [ ] Improve model download time
- [ ] Enhance ARM64 optimization
- [ ] Implement batch processing
- [ ] Add support for more document types

#### 3. Documentation
- [ ] Complete API documentation
- [ ] Add development guides
- [ ] Create troubleshooting guides
- [ ] Improve configuration documentation

### Mid-term Goals (Q3-Q4 2024)

#### 1. Advanced Features
- [ ] Distributed training support
- [ ] Advanced model registry
- [ ] Custom model training
- [ ] Enhanced search capabilities

#### 2. Infrastructure
- [ ] High availability setup
- [ ] Backup and recovery
- [ ] Auto-scaling
- [ ] Cross-platform support

#### 3. Integration
- [ ] External API integrations
- [ ] Plugin system
- [ ] Export/Import functionality
- [ ] Third-party authentication

### Long-term Vision

1. **Scalability**
   - Distributed processing
   - Cloud deployment options
   - Multi-region support

2. **AI Capabilities**
   - Advanced document understanding
   - Automated workflow processing
   - Real-time analysis

3. **Community**
   - Open-source ecosystem
   - Plugin marketplace
   - Developer tools

## Completed Milestones

### Base Infrastructure (✓)
- [x] Create base Docker network
- [x] Set up shared volumes
- [x] Configure BuildKit with ARM64 optimizations
- [x] Implement Rosetta 2 emulation layer

### Core Services (Partial ✓)
- [x] Qdrant Vector Store
- [x] OCR Service
- [x] RAG Processor
- [ ] Local Training Service

### Monitoring Stack (✓)
- [x] Prometheus integration
- [x] Grafana dashboards
- [x] Loki log aggregation
- [x] Health monitoring system

## Contributing

We welcome contributions! See our [Contributing Guide](./Contributing) for details on how to get involved. 