## Port Configuration and Service Mapping

### Current Port Assignments
```yaml
Frontend Service:
  - External Port: 3000
  - Internal Port: 3000
  - Purpose: Next.js web interface
  - Status: Port conflict with Grafana

Grafana:
  - External Port: 3002 (Changed from 3000)
  - Internal Port: 3000
  - Purpose: Monitoring dashboard
  - Status: Moved to avoid conflict with frontend

Backend Service:
  - External Port: 3001
  - Internal Port: 3001
  - Purpose: API and WebSocket server
  - Status: No conflicts

Qdrant Vector Store:
  - External Port: 6333
  - Internal Port: 6333
  - Purpose: Vector database
  - Additional Port: 6334 (gRPC)
  - Status: No conflicts

SearXNG:
  - External Port: 8080
  - Internal Port: 8080
  - Purpose: Meta search engine
  - Status: No conflicts

OCR Service:
  - External Port: 8082
  - Internal Port: 8000
  - Purpose: Document processing
  - Status: No conflicts

Prometheus:
  - External Port: 9090
  - Internal Port: 9090
  - Purpose: Metrics collection
  - Status: No conflicts

Node Exporter:
  - External Port: 9100
  - Internal Port: 9100
  - Purpose: System metrics
  - Status: No conflicts

Loki:
  - External Port: 3100
  - Internal Port: 3100
  - Purpose: Log aggregation
  - Status: No conflicts
```

### Port Conflict Resolution
1. **Identified Issue**: 
   - Grafana and Frontend were both attempting to use port 3000
   - This caused the frontend to be inaccessible as Grafana took precedence

2. **Resolution**:
   - Moved Grafana to port 3002
   - Kept Frontend on original port 3000
   - All other services remain on their designated ports

3. **Verification Process**:
   - Bring down all containers
   - Update port mappings in docker-compose.yml
   - Restart all services
   - Verify each service is accessible on its designated port

### Service Access URLs
```yaml
Frontend: http://localhost:3000
Backend API: http://localhost:3001
Grafana Dashboard: http://localhost:3002
Qdrant UI: http://localhost:6333
SearXNG: http://localhost:8080
OCR Service: http://localhost:8082
Prometheus: http://localhost:9090
Node Exporter: http://localhost:9100
Loki: http://localhost:3100
``` 