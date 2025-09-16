# Docker Deployment Guide

Complete guide for deploying the All-in-One Crypto Trading MCP Server using Docker containers with production-ready configurations.

## 🐳 Docker Overview

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Application Stack"
            APP[MCP Server Container]
            BOT[Telegram Bot Container]
            WEB[Web Interface Container]
        end
        
        subgraph "Data Stack"
            DB[PostgreSQL Container]
            REDIS[Redis Container]
            BACKUP[Backup Container]
        end
        
        subgraph "Infrastructure Stack"
            NGINX[Nginx Reverse Proxy]
            MONITOR[Monitoring Stack]
        end
    end
    
    APP --> DB
    APP --> REDIS
    BOT --> DB
    BOT --> REDIS
    WEB --> APP
    NGINX --> APP
    NGINX --> WEB
    MONITOR --> APP
    BACKUP --> DB
```

## 🏗️ Basic Docker Setup

### Single Container Deployment

#### Quick Start with Docker Run
```bash
# Pull the latest image
docker pull cryptomcp/allinone-crypto-mcp:latest

# Run with basic configuration
docker run -d \
  --name allinone-crypto-mcp \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  --restart unless-stopped \
  cryptomcp/allinone-crypto-mcp:latest

# Check container status
docker logs allinone-crypto-mcp -f
```

#### Environment Variables for Docker
```bash
# Create environment file for Docker
cat > .env.docker << EOF
# Container Configuration
ENVIRONMENT=docker
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Database (using SQLite for simplicity)
DATABASE_URL=sqlite:///app/data/trading.db
DATABASE_ECHO=false

# Redis (optional - will use memory cache if not available)
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_docker_secret_key_here
ENCRYPTION_KEY=your_docker_encryption_key

# Trading (start safely)
LIVE=false
AM_I_SURE=false
DRY_RUN_DEFAULT=true

# API Keys (add your actual keys)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=true
EOF
```

### Custom Dockerfile

#### Development Dockerfile
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional development tools
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    pytest \
    pytest-asyncio \
    black \
    flake8

# Copy application code
COPY . .

# Install application in development mode
RUN pip install -e .

# Create data directories
RUN mkdir -p /app/data /app/logs

# Expose ports
EXPOSE 8000 8888

# Development entrypoint
CMD ["python", "-m", "allinone_crypto_mcp.main", "--debug"]
```

#### Production Dockerfile
```dockerfile
# Dockerfile.prod
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY --chown=appuser:appuser . .

# Install application
RUN pip install --no-cache-dir -e .

# Create directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production entrypoint
ENTRYPOINT ["python", "-m", "allinone_crypto_mcp.main"]
CMD ["--production"]
```

## 🐙 Docker Compose Deployments

### Development Stack

#### docker-compose.dev.yml
```yaml
version: '3.8'

services:
  # Main application
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: allinone-crypto-mcp-dev
    ports:
      - "8000:8000"
      - "8888:8888"  # Jupyter notebook
    volumes:
      - .:/app
      - app-data:/app/data
      - app-logs:/app/logs
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://postgres:development@postgres:5432/trading_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    restart: unless-stopped

  # Development database
  postgres:
    image: postgres:15-alpine
    container_name: postgres-dev
    environment:
      - POSTGRES_DB=trading_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=development
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init-dev.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - app-network

  # Development Redis
  redis:
    image: redis:7-alpine
    container_name: redis-dev
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - app-network

  # Database admin interface
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin-dev
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@cryptomcp.dev
      - PGADMIN_DEFAULT_PASSWORD=development
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    ports:
      - "5050:80"
    depends_on:
      - postgres
    networks:
      - app-network

  # Redis admin interface
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: redis-commander-dev
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    networks:
      - app-network

volumes:
  app-data:
  app-logs:
  postgres-data:
  redis-data:
  pgadmin-data:

networks:
  app-network:
    driver: bridge
```

### Production Stack

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  # Load balancer
  nginx:
    image: nginx:alpine
    container_name: nginx-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
      - ./certs:/etc/nginx/certs:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - app-network
    restart: unless-stopped

  # Main application (scaled)
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/trading
      - REDIS_URL=redis://redis:6379/0
      - PROMETHEUS_METRICS=true
    volumes:
      - app-data:/app/data
      - app-logs:/app/logs
      - ./.env.prod:/app/.env:ro
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Telegram bot service
  telegram-bot:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: telegram-bot-prod
    command: ["python", "-m", "allinone_crypto_mcp.telegram.bot"]
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/trading
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./.env.prod:/app/.env:ro
      - app-logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    restart: unless-stopped

  # Production database
  postgres:
    image: postgres:15
    container_name: postgres-prod
    environment:
      - POSTGRES_DB=trading
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - postgres-backups:/backups
      - ./database/init-prod.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network
    restart: unless-stopped
    command: postgres -c max_connections=200 -c shared_buffers=256MB -c effective_cache_size=1GB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Production Redis
  redis:
    image: redis:7-alpine
    container_name: redis-prod
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backup service
  backup:
    build:
      context: ./backup
      dockerfile: Dockerfile
    container_name: backup-service
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/trading
      - S3_BUCKET=${BACKUP_S3_BUCKET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - postgres-backups:/backups
      - ./backup/scripts:/scripts:ro
    depends_on:
      - postgres
    networks:
      - app-network
    restart: unless-stopped
    # Run backup every 6 hours
    command: crond -f

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus-prod
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - app-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana-prod
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - app-network
    restart: unless-stopped

volumes:
  app-data:
  app-logs:
  postgres-data:
  postgres-backups:
  redis-data:
  nginx-logs:
  prometheus-data:
  grafana-data:

networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Monitoring Stack

#### docker-compose.monitoring.yml
```yaml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus:/etc/prometheus:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - monitoring
    restart: unless-stopped

  # AlertManager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager:ro
      - alertmanager-data:/alertmanager
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:${DB_PASSWORD}@postgres:5432/trading?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - monitoring
      - app-network
    restart: unless-stopped

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    environment:
      - REDIS_ADDR=redis://redis:6379
    ports:
      - "9121:9121"
    networks:
      - monitoring
      - app-network
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:

networks:
  monitoring:
    driver: bridge
  app-network:
    external: true
```

## ⚙️ Docker Configuration Files

### Nginx Configuration

#### nginx/nginx.conf
```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # Upstream servers
    upstream app_servers {
        least_conn;
        server app:8000 max_fails=3 fail_timeout=30s;
    }

    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
```

#### nginx/sites-enabled/default
```nginx
server {
    listen 80;
    server_name _;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    # Rate limiting
    limit_req zone=api burst=20 nodelay;

    # Main application
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://app_servers/health;
        access_log off;
    }

    # Metrics endpoint (restrict access)
    location /metrics {
        allow 172.20.0.0/16;  # Docker network
        deny all;
        proxy_pass http://app_servers/metrics;
    }
}
```

### Database Initialization

#### database/init-prod.sql
```sql
-- Production database initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application user
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Create databases
CREATE DATABASE trading OWNER app_user;
CREATE DATABASE trading_test OWNER app_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE trading TO app_user;
GRANT ALL PRIVILEGES ON DATABASE trading_test TO app_user;

-- Performance settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### Backup Configuration

#### backup/Dockerfile
```dockerfile
FROM alpine:latest

RUN apk add --no-cache \
    postgresql-client \
    aws-cli \
    curl \
    dcron \
    bash

COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

# Create cron job
RUN echo "0 */6 * * * /scripts/backup.sh" > /etc/crontabs/root

CMD ["crond", "-f"]
```

#### backup/scripts/backup.sh
```bash
#!/bin/bash

set -euo pipefail

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"

echo "Starting backup at $(date)"

# Database backup
echo "Backing up database..."
pg_dump $DATABASE_URL | gzip > "$DB_BACKUP_FILE"

# Upload to S3 if configured
if [ -n "${S3_BUCKET:-}" ]; then
    echo "Uploading to S3..."
    aws s3 cp "$DB_BACKUP_FILE" "s3://$S3_BUCKET/backups/"
fi

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed at $(date)"
```

## 🚀 Deployment Commands

### Development Deployment
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Run migrations
docker-compose -f docker-compose.dev.yml exec app allinone-crypto-mcp migrate

# Run tests
docker-compose -f docker-compose.dev.yml exec app pytest

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

### Production Deployment
```bash
# Set environment variables
export DB_PASSWORD="secure_database_password"
export GRAFANA_PASSWORD="secure_grafana_password"
export BACKUP_S3_BUCKET="your-backup-bucket"

# Build and start production environment
docker-compose -f docker-compose.prod.yml up -d --build

# Scale application instances
docker-compose -f docker-compose.prod.yml up -d --scale app=5

# View application logs
docker-compose -f docker-compose.prod.yml logs -f app

# Check health status
curl -f http://localhost/health

# Stop production environment
docker-compose -f docker-compose.prod.yml down
```

### Monitoring Deployment
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3000

# Access Prometheus
open http://localhost:9090

# View metrics
curl http://localhost:9090/metrics
```

## 🔧 Docker Management

### Container Management
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Check container resource usage
docker stats

# Execute commands in container
docker exec -it allinone-crypto-mcp bash

# View container logs
docker logs allinone-crypto-mcp -f --tail 100

# Restart container
docker restart allinone-crypto-mcp

# Remove container
docker rm -f allinone-crypto-mcp
```

### Volume Management
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect app-data

# Backup volume
docker run --rm -v app-data:/data -v $(pwd):/backup alpine tar czf /backup/app-data.tar.gz -C /data .

# Restore volume
docker run --rm -v app-data:/data -v $(pwd):/backup alpine tar xzf /backup/app-data.tar.gz -C /data

# Remove volume
docker volume rm app-data
```

### Image Management
```bash
# List images
docker images

# Build image
docker build -t allinone-crypto-mcp:latest .

# Tag image
docker tag allinone-crypto-mcp:latest cryptomcp/allinone-crypto-mcp:v2.1.0

# Push image
docker push cryptomcp/allinone-crypto-mcp:v2.1.0

# Remove image
docker rmi allinone-crypto-mcp:latest

# Clean up unused images
docker image prune -a
```

## 🔍 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker logs allinone-crypto-mcp

# Check container configuration
docker inspect allinone-crypto-mcp

# Check resource usage
docker stats

# Check port conflicts
netstat -tulpn | grep :8000
```

#### Database Connection Issues
```bash
# Test database connectivity
docker exec -it postgres-prod psql -U postgres -d trading -c "SELECT 1;"

# Check database logs
docker logs postgres-prod

# Verify database configuration
docker exec -it postgres-prod cat /var/lib/postgresql/data/postgresql.conf
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats --no-stream

# Check application logs for errors
docker logs allinone-crypto-mcp | grep ERROR

# Monitor database performance
docker exec -it postgres-prod psql -U postgres -d trading -c "SELECT * FROM pg_stat_activity;"
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
docker exec postgres-prod pg_isready -U postgres

# Redis health
docker exec redis-prod redis-cli ping

# Container health status
docker inspect --format='{{.State.Health.Status}}' allinone-crypto-mcp
```

## 📞 Support

For Docker deployment support:
- **Docker Support**: docker@cryptomcp.dev
- **Container Issues**: containers@cryptomcp.dev
- **Technical Support**: support@cryptomcp.dev
- **Infrastructure**: infrastructure@cryptomcp.dev

---

**🐳 Docker Best Practices:**
- Use multi-stage builds for smaller images
- Run containers as non-root users
- Use health checks for all services
- Implement proper logging and monitoring
- Regular security updates for base images
- Use secrets management for sensitive data
- Implement backup and disaster recovery