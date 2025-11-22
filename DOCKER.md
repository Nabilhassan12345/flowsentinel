# 🐳 FlowSentinel - Docker Quick Start Guide

Complete guide for running FlowSentinel using Docker and Docker Compose.

---

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

Check your installation:
```bash
docker --version
docker-compose --version
```

---

## 🚀 Quick Start with Docker Compose

### 1. Build and Run

```bash
# Build and start the service
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the API

- **API Server:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 3. Stop the Service

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🔧 Docker Commands

### Build Commands

```bash
# Build from scratch (no cache)
docker-compose build --no-cache

# Build specific service
docker-compose build flowsentinel-backend

# Pull latest base images
docker pull python:3.11-slim
```

### Run Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Restart services
docker-compose restart

# View running containers
docker-compose ps
```

### Debug Commands

```bash
# View logs
docker-compose logs -f flowsentinel-backend

# Execute commands in container
docker-compose exec flowsentinel-backend python demo.py

# Access container shell
docker-compose exec flowsentinel-backend /bin/bash

# Check health status
docker-compose exec flowsentinel-backend curl http://localhost:8000/health
```

### Cleanup Commands

```bash
# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required for production:**
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id
ORCHESTRATE_API_KEY=your_api_key_here
```

---

## 🛠️ Development Mode

The docker-compose.yml includes volume mounts for hot reload:

```yaml
volumes:
  - ./main.py:/app/main.py
  - ./demo.py:/app/demo.py
```

**Benefits:**
- ✅ Code changes reflect immediately
- ✅ No need to rebuild image
- ✅ Faster development cycle

**To disable hot reload (production):**
Comment out the `volumes` section in `docker-compose.yml`

---

## 🏭 Production Deployment

### Option 1: Docker Compose (Simple)

```bash
# Remove development volumes from docker-compose.yml
# Set restart: always
# Then deploy:
docker-compose up -d
```

### Option 2: Standalone Docker

```bash
# Build image
docker build -t flowsentinel-backend:latest .

# Run container
docker run -d \
  --name flowsentinel \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  flowsentinel-backend:latest
```

### Option 3: Docker Hub

```bash
# Tag image
docker tag flowsentinel-backend:latest yourusername/flowsentinel:latest

# Push to Docker Hub
docker push yourusername/flowsentinel:latest

# Pull and run on production server
docker pull yourusername/flowsentinel:latest
docker run -d -p 8000:8000 --env-file .env yourusername/flowsentinel:latest
```

---

## 🏥 Health Checks

The container includes automatic health checks:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=3)"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
```

**Check health status:**
```bash
docker inspect --format='{{json .State.Health}}' flowsentinel-api
```

---

## 📊 Resource Limits

Configure resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Maximum 1 CPU core
      memory: 512M     # Maximum 512MB RAM
    reservations:
      cpus: '0.5'      # Reserve 0.5 CPU core
      memory: 256M     # Reserve 256MB RAM
```

---

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs flowsentinel-backend

# Check container status
docker-compose ps

# Restart container
docker-compose restart flowsentinel-backend
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Build Fails

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Cannot Access API

```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs -f

# Test from inside container
docker-compose exec flowsentinel-backend curl http://localhost:8000/health
```

---

## 📦 Multi-Stage Build Benefits

The Dockerfile uses multi-stage builds:

**Stage 1 (Builder):**
- Installs build dependencies (gcc)
- Compiles Python packages
- Creates optimized wheels

**Stage 2 (Runtime):**
- Uses minimal base image
- Copies only compiled packages
- No build tools in final image

**Results:**
- 🎯 Smaller image size (~200MB vs 500MB+)
- 🔒 Better security (fewer attack vectors)
- ⚡ Faster deployment

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose run flowsentinel-backend python test_api.py
      
      - name: Push to registry
        run: |
          docker tag flowsentinel-backend:latest ${{ secrets.DOCKER_REGISTRY }}/flowsentinel:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/flowsentinel:latest
```

---

## 🌐 Networking

The compose file creates a dedicated network:

```yaml
networks:
  flowsentinel-network:
    driver: bridge
```

**Benefits:**
- Isolated from other containers
- Easy to add database/cache services
- Better security

**Add services (example):**
```yaml
services:
  flowsentinel-backend:
    # ... existing config
    
  postgres:
    image: postgres:15
    networks:
      - flowsentinel-network
    environment:
      POSTGRES_DB: flowsentinel
```

---

## 📝 Docker Tips

### Reduce Image Size
```dockerfile
# Use slim base images
FROM python:3.11-slim

# Remove apt cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Use --no-cache-dir for pip
RUN pip install --no-cache-dir -r requirements.txt
```

### Security Best Practices
```dockerfile
# Run as non-root user
USER flowsentinel

# Set read-only filesystem (if possible)
# docker run --read-only ...

# Drop capabilities
# docker run --cap-drop=ALL ...
```

### Optimize Build Time
```dockerfile
# Copy requirements first (leverage cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes frequently)
COPY main.py .
```

---

## 🎯 Summary

**To run FlowSentinel with Docker:**

1. Ensure Docker and Docker Compose are installed
2. Copy `.env.example` to `.env` (optional for demo)
3. Run: `docker-compose up --build`
4. Access: http://localhost:8000/docs

**That's it! 🚀**

---

**Need help? Check the main README.md or open an issue on GitHub.**
