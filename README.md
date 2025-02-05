# 🚀 schubAI - Advanced AI-Powered Document Processing and Search Platform

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Docker Installation](#docker-installation)
  - [Configuration](#configuration)
- [Components](#components)
  - [OCR Service](#ocr-service)
  - [Vector Store](#vector-store)
  - [Search Service](#search-service)
  - [Training Service](#training-service)
- [Monitoring & Logging](#monitoring--logging)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

schubAI is a comprehensive AI-powered platform designed for advanced document processing, search, and analysis. Built with a focus on performance and scalability, it leverages cutting-edge technologies like MLX for Apple Silicon optimization and provides a robust architecture for handling complex document processing workflows.

## Features

### Core Capabilities
- **Hybrid OCR Engine**
  - PaddleOCR for multi-language support
  - Qwen-VL for enhanced English text recognition
  - Automatic engine selection based on content
  - M2 Pro optimization with MLX support

### Document Processing
- Advanced text extraction with confidence scoring
- Layout analysis and structure recognition
- Multi-language support
- Batch processing capabilities

### Search & Analysis
- Vector-based similarity search using Qdrant
- Meta-search capabilities via SearXNG
- Real-time document indexing
- Semantic search functionality

### Infrastructure
- **Containerized Architecture**
  - ARM64 optimization for M2 Pro
  - Multi-stage builds for efficiency
  - Resource-aware orchestration
  - Cross-container communication

- **Monitoring Stack**
  - Prometheus metrics collection
  - Grafana dashboards
  - Loki log aggregation
  - Health monitoring system

## Architecture

The platform consists of several microservices:

- **Frontend**: Next.js 14 application (Port 3000)
- **Backend**: Node.js API service (Port 3001)
- **OCR Service**: FastAPI service with hybrid OCR engines (Port 8082)
- **Vector Store**: Qdrant for similarity search (Port 6333)
- **Search Service**: SearXNG for meta-search capabilities (Port 4000)
- **Monitoring**: 
  - Grafana (Port 3002)
  - Prometheus (Port 9090)
  - Loki (Port 3100)

## Installation

### Prerequisites
- Docker and Docker Compose
- Git
- Apple Silicon Mac (M1/M2/M3) for MLX optimization
- At least 16GB RAM recommended

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/maccie01/schubAI.git
   cd schubAI
   ```

2. Create configuration files:
   ```bash
   cp config.example.toml config.toml
   ```

3. Start the services:
   ```bash
   docker compose up -d
   ```

### Configuration

Key configuration files:
- `config.toml`: Main configuration file
- `docker-compose.yml`: Service orchestration
- `.env`: Environment variables

## Components

### OCR Service

The OCR service implements a hybrid approach using both PaddleOCR and Qwen-VL:

- **PaddleOCR Features**:
  - Multi-language support
  - Fast processing speed
  - Optimized for various document types

- **Qwen-VL Features**:
  - Enhanced English text recognition
  - Better handling of complex layouts
  - Improved accuracy for English content

- **Resource Management**:
  - Memory limit: 2GB
  - CPU allocation: 2 cores
  - Efficient model caching
  - MLX optimization for Apple Silicon

### Vector Store

Qdrant vector database configuration:

- Memory allocation: 4GB
- Optimized for ARM64
- Persistent storage
- High-performance similarity search

### Search Service

SearXNG integration:

- Custom configuration for meta-search
- Rate limiting support
- Privacy-focused setup
- Multiple search engine aggregation

### Training Service

Local training capabilities:

- MLX GPU passthrough
- 8GB memory allocation
- Model fine-tuning support
- Resource monitoring

## Monitoring & Logging

Comprehensive monitoring stack:

- **Prometheus**:
  - Custom metrics
  - Resource utilization
  - Performance monitoring
  - Alert configuration

- **Grafana**:
  - Pre-configured dashboards
  - Real-time monitoring
  - Performance visualization
  - Resource tracking

- **Loki & Promtail**:
  - Centralized logging
  - Log aggregation
  - Search capabilities
  - Retention policies

## API Documentation

The platform exposes several REST APIs:

- OCR API (Port 8082):
  - POST /ocr: Submit documents for processing
  - GET /ocr/{task_id}: Retrieve results
  - GET /health: Service health check
  - GET /metrics: Prometheus metrics

- Backend API (Port 3001):
  - Document management endpoints
  - Search functionality
  - System configuration
  - Status monitoring

## Development

For development:

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development servers:
   ```bash
   npm run dev
   ```

3. Run tests:
   ```bash
   npm test
   ```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 schubAI
