# Production Deployment Guide

Complete guide for deploying the All-in-One Crypto Trading MCP Server in production environments with high availability, security, and scalability.

## 🏗️ Production Architecture

### Recommended Architecture

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>nginx/HAProxy]
    end
    
    subgraph "Application Layer"
        APP1[MCP Server 1]
        APP2[MCP Server 2]
        APP3[MCP Server 3]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Primary)]
        DB_REPLICA[(PostgreSQL<br/>Replica)]
        REDIS[(Redis Cluster)]
    end
    
    subgraph "External Services"
        EXCHANGES[Exchanges<br/>APIs]
        BLOCKCHAIN[Blockchain<br/>RPCs]
        NEWS[News APIs]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    
    APP1 --> DB_REPLICA
    APP2 --> DB_REPLICA
    APP3 --> DB_REPLICA
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> EXCHANGES
    APP2 --> BLOCKCHAIN
    APP3 --> NEWS
```

## 🐳 Docker Production Deployment

### Production Docker Setup

#### Dockerfile.prod
```dockerfile
# Production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY allinone_crypto_mcp/ ./allinone_crypto_mcp/
COPY setup.py .
COPY README.md .

# Install application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["allinone-crypto-mcp", "--production"]
```

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  # Application Services
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/trading
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./.env:/app/.env:ro
    depends_on:
      - db
      - redis
    networks:
      - app-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.app.tls=true"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"

  # Telegram Bot Service
  telegram-bot:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    command: ["python", "-m", "allinone_crypto_mcp.telegram.bot"]
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/trading
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./.env:/app/.env:ro
    depends_on:
      - db
      - redis
    networks:
      - app-network

  # Load Balancer
  traefik:
    image: traefik:v3.0
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--providers.docker=true"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-acme:/acme.json
    networks:
      - app-network

  # Database
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=trading
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
      - ./database/backups:/backups
    networks:
      - app-network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  # Database Replica
  db-replica:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=trading
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - PGUSER=postgres
    volumes:
      - postgres-replica-data:/var/lib/postgresql/data
    networks:
      - app-network
    depends_on:
      - db

  # Redis Cluster
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --replica-read-only no
    volumes:
      - redis-data:/data
    networks:
      - app-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - app-network

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - app-network
    depends_on:
      - prometheus

volumes:
  postgres-data:
  postgres-replica-data:
  redis-data:
  prometheus-data:
  grafana-data:
  traefik-acme:

networks:
  app-network:
    driver: bridge
```

### Environment Variables for Production

#### .env.production
```env
# Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_production_secret_key_32_chars_min
ENCRYPTION_KEY=your_production_encryption_key_32_chars
ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com

# Database
DATABASE_URL=postgresql://postgres:secure_password@db:5432/trading
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_SSL_MODE=require

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=secure_redis_password
REDIS_SSL=false

# SSL/TLS
SSL_CERT_PATH=/app/certs/cert.pem
SSL_KEY_PATH=/app/certs/key.pem
FORCE_HTTPS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_BURST_SIZE=100

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=your-backup-bucket
```

## ☁️ Cloud Platform Deployment

### AWS Deployment

#### Using AWS ECS with Fargate
```yaml
# ecs-task-definition.json
{
  "family": "allinone-crypto-mcp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "allinone-crypto-mcp",
      "image": "your-account.dkr.ecr.region.amazonaws.com/allinone-crypto-mcp:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/trading"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:prod/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/allinone-crypto-mcp",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### Terraform Configuration
```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "allinone-crypto-mcp-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  
  tags = {
    Environment = "production"
    Project     = "allinone-crypto-mcp"
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "allinone-crypto-mcp-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.large"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "trading"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "allinone-crypto-mcp-final-snapshot"
  
  tags = {
    Environment = "production"
    Project     = "allinone-crypto-mcp"
  }
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "allinone-crypto-mcp-redis"
  description                = "Redis cluster for caching"
  
  node_type                  = "cache.r6g.large"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 3
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Environment = "production"
    Project     = "allinone-crypto-mcp"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "allinone-crypto-mcp"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Environment = "production"
    Project     = "allinone-crypto-mcp"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "allinone-crypto-mcp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets
  
  enable_deletion_protection = true
  
  tags = {
    Environment = "production"
    Project     = "allinone-crypto-mcp"
  }
}
```

### Google Cloud Platform Deployment

#### GKE Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: allinone-crypto-mcp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: allinone-crypto-mcp
  template:
    metadata:
      labels:
        app: allinone-crypto-mcp
    spec:
      containers:
      - name: app
        image: gcr.io/your-project/allinone-crypto-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: allinone-crypto-mcp-service
  namespace: production
spec:
  selector:
    app: allinone-crypto-mcp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Azure Deployment

#### Azure Container Instances
```yaml
# azure-container-group.yaml
apiVersion: 2019-12-01
location: eastus
name: allinone-crypto-mcp
properties:
  containers:
  - name: app
    properties:
      image: youracr.azurecr.io/allinone-crypto-mcp:latest
      resources:
        requests:
          cpu: 2
          memoryInGB: 4
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: ENVIRONMENT
        value: production
      - name: DATABASE_URL
        secureValue: postgresql://user:pass@server.postgres.database.azure.com:5432/trading
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 80
    dnsNameLabel: allinone-crypto-mcp
```

## 🔒 Security Hardening

### SSL/TLS Configuration

#### Nginx SSL Configuration
```nginx
# /etc/nginx/sites-available/allinone-crypto-mcp
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

### Firewall Configuration

#### UFW Rules
```bash
#!/bin/bash
# firewall-setup.sh

# Reset UFW
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH access
ufw allow 22/tcp

# HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Application port (only from load balancer)
ufw allow from 10.0.0.0/16 to any port 8000

# Database port (only from app servers)
ufw allow from 10.0.1.0/24 to any port 5432

# Redis port (only from app servers)
ufw allow from 10.0.1.0/24 to any port 6379

# Monitoring
ufw allow from 10.0.0.0/16 to any port 9090  # Prometheus
ufw allow from 10.0.0.0/16 to any port 3000  # Grafana

# Enable firewall
ufw --force enable

# Show status
ufw status verbose
```

## 📊 Monitoring and Observability

### Prometheus Configuration

#### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'allinone-crypto-mcp'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### Alert Rules
```yaml
# alert_rules.yml
groups:
  - name: allinone-crypto-mcp
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: "95th percentile latency is {{ $value }}s"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Database is down
          description: "PostgreSQL database is not responding"

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Redis is down
          description: "Redis cache is not responding"
```

### Logging Configuration

#### Structured Logging
```python
# logging_config.py
import structlog
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "plain": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "/app/logs/app.log",
            "maxBytes": 100000000,  # 100MB
            "backupCount": 10,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "/app/logs/error.log",
            "maxBytes": 100000000,
            "backupCount": 10,
            "level": "ERROR",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "allinone_crypto_mcp": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        }
    }
}

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🔄 Backup and Disaster Recovery

### Automated Backup Script

#### backup.sh
```bash
#!/bin/bash
# Production backup script

set -euo pipefail

# Configuration
BACKUP_DIR="/app/backups"
S3_BUCKET="your-backup-bucket"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
echo "Starting database backup..."
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Redis backup
echo "Starting Redis backup..."
redis-cli --rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Application data backup
echo "Starting application data backup..."
tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" /app/data

# Upload to S3
echo "Uploading to S3..."
aws s3 cp "$BACKUP_DIR/" "s3://$S3_BUCKET/backups/" --recursive --exclude "*" --include "*$DATE*"

# Cleanup old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
echo "Verifying backup integrity..."
gzip -t "$BACKUP_DIR/db_backup_$DATE.sql.gz"
tar -tzf "$BACKUP_DIR/app_data_$DATE.tar.gz" > /dev/null

echo "Backup completed successfully: $DATE"
```

### Disaster Recovery Plan

#### Recovery Procedures
```bash
#!/bin/bash
# disaster_recovery.sh

set -euo pipefail

BACKUP_DATE=${1:-"latest"}
S3_BUCKET="your-backup-bucket"
RECOVERY_DIR="/tmp/recovery"

echo "Starting disaster recovery for backup: $BACKUP_DATE"

# Create recovery directory
mkdir -p "$RECOVERY_DIR"

# Download backups from S3
echo "Downloading backups from S3..."
if [ "$BACKUP_DATE" = "latest" ]; then
    aws s3 sync "s3://$S3_BUCKET/backups/" "$RECOVERY_DIR/" --exclude "*" --include "*$(date +%Y%m%d)*"
else
    aws s3 sync "s3://$S3_BUCKET/backups/" "$RECOVERY_DIR/" --exclude "*" --include "*$BACKUP_DATE*"
fi

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
echo "Restoring database..."
gunzip < "$RECOVERY_DIR"/db_backup_*.sql.gz | psql $DATABASE_URL

# Restore Redis
echo "Restoring Redis..."
cp "$RECOVERY_DIR"/redis_backup_*.rdb /var/lib/redis/dump.rdb

# Restore application data
echo "Restoring application data..."
tar -xzf "$RECOVERY_DIR"/app_data_*.tar.gz -C /

# Start services
echo "Starting services..."
docker-compose up -d

# Verify recovery
echo "Verifying recovery..."
sleep 30
curl -f http://localhost:8000/health || (echo "Health check failed" && exit 1)

echo "Disaster recovery completed successfully"
```

## 📞 Support

For production deployment support:
- **Deployment Support**: deployment@cryptomcp.dev
- **Infrastructure**: infrastructure@cryptomcp.dev
- **Security**: security@cryptomcp.dev
- **24/7 Emergency**: emergency@cryptomcp.dev

---

**⚠️ Production Checklist:**
- [ ] All security configurations applied
- [ ] SSL/TLS certificates installed
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested
- [ ] Load balancing configured
- [ ] Database optimized for production
- [ ] Rate limiting enabled
- [ ] Log aggregation configured