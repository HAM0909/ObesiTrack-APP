# ObesiTrack - Deployment Guide

## 📚 Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Traditional Server Deployment](#traditional-server-deployment)
5. [Cloud Platform Deployments](#cloud-platform-deployments)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Performance Optimization](#performance-optimization)
10. [Security Hardening](#security-hardening)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)

---

## 🌍 Deployment Overview

### Deployment Options

ObesiTrack can be deployed in several ways depending on your requirements:

| Option | Best For | Complexity | Scalability | Cost |
|--------|----------|------------|-------------|------|
| **Docker Compose** | Development, Small Teams | Low | Limited | Low |
| **Traditional Server** | Full Control, Custom Setup | Medium | Medium | Medium |
| **Heroku** | Quick Deployment, Startups | Low | High | Medium-High |
| **AWS/GCP/Azure** | Enterprise, High Availability | High | Very High | Variable |
| **DigitalOcean** | Balance of Features/Cost | Medium | High | Medium |

### Prerequisites

- **Server Requirements**: 2+ CPU cores, 4GB+ RAM, 20GB+ storage
- **Python**: 3.11 or higher
- **PostgreSQL**: 13 or higher
- **Node.js**: 18+ (for Playwright tests)
- **Docker**: Latest version (for containerized deployment)
- **SSL Certificate**: For production HTTPS

---

## 🔧 Environment Setup

### 1. Production Environment Variables

Create a `.env.production` file with the following configuration:

```bash
# Application Configuration
APP_NAME=ObesiTrack
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://username:password@hostname:5432/obesittrack

# JWT Configuration
SECRET_KEY=your-super-secure-random-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# PostgreSQL Configuration
POSTGRES_DB=obesittrack
POSTGRES_USER=obesittrack_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Security Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO

# Redis Configuration (optional, for caching)
REDIS_URL=redis://redis:6379/0
```

### 2. Security Best Practices

```bash
# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate secure database password
openssl rand -base64 32

# Set proper file permissions
chmod 600 .env.production
chown app:app .env.production
```

---

## 🐳 Docker Deployment

### 1. Docker Compose (Recommended for Most Cases)

#### Production Docker Compose Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    image: obesitrack:latest
    container_name: obesitrack-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    networks:
      - obesitrack-network
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  db:
    image: postgres:15-alpine
    container_name: obesitrack-db
    restart: unless-stopped
    env_file:
      - .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - obesitrack-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: obesitrack-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - obesitrack-network

  nginx:
    image: nginx:alpine
    container_name: obesitrack-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
    networks:
      - obesitrack-network

volumes:
  postgres_data:
  redis_data:

networks:
  obesitrack-network:
    driver: bridge
```

#### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Create logs directory
RUN mkdir -p /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream obesitrack {
        server api:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;

        client_max_body_size 10M;

        location / {
            proxy_pass http://obesitrack;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            
            # Add security headers
            add_header X-Frame-Options DENY;
            add_header X-Content-Type-Options nosniff;
            add_header X-XSS-Protection "1; mode=block";
            add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        }

        location /static/ {
            alias /app/app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /health {
            proxy_pass http://obesitrack/health;
            access_log off;
        }
    }
}
```

#### Deployment Commands

```bash
# 1. Clone repository
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# 2. Set up environment
cp .env.example .env.production
# Edit .env.production with production values

# 3. Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

# 4. Initialize database
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py

# 5. Create admin user
docker-compose -f docker-compose.prod.yml exec api python create_demo_users.py

# 6. Verify deployment
curl -k https://yourdomain.com/health
```

### 2. Single Container Deployment

```bash
# Build production image
docker build -f Dockerfile.prod -t obesitrack:latest .

# Run with external database
docker run -d \
  --name obesitrack \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  obesitrack:latest

# With health check monitoring
docker run -d \
  --name obesitrack \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-retries=3 \
  --health-start-period=60s \
  obesitrack:latest
```

---

## 🖥️ Traditional Server Deployment

### 1. Ubuntu/Debian Server Setup

#### System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    git \
    curl \
    htop \
    ufw

# Install Node.js (for testing)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### User Setup

```bash
# Create application user
sudo adduser --system --group --home /opt/obesitrack obesitrack

# Add user to sudo group (optional)
sudo usermod -aG sudo obesitrack

# Switch to application user
sudo su - obesitrack
```

#### Application Setup

```bash
# Clone repository
cd /opt/obesitrack
git clone https://github.com/HAM0909/ObesiTrack-APP.git app
cd app/ObesiTrack

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies (for testing)
npm install

# Set up environment
cp .env.example .env
# Edit .env with production values

# Create directories
mkdir -p logs backups uploads
chmod 755 logs backups uploads
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb obesittrack
createuser -P obesittrack_user
# Enter password when prompted

# Grant privileges
psql obesittrack
GRANT ALL PRIVILEGES ON DATABASE obesittrack TO obesittrack_user;
ALTER USER obesittrack_user CREATEDB;
\q

# Exit postgres user
exit

# Initialize application database
cd /opt/obesitrack/app/ObesiTrack
source venv/bin/activate
python scripts/init_db.py
```

### 3. Supervisor Configuration

Create `/etc/supervisor/conf.d/obesitrack.conf`:

```ini
[program:obesitrack]
command=/opt/obesitrack/app/ObesiTrack/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/opt/obesitrack/app/ObesiTrack
user=obesitrack
group=obesitrack
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/obesitrack/app/ObesiTrack/logs/supervisor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="/opt/obesitrack/app/ObesiTrack/venv/bin"
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start obesitrack

# Check status
sudo supervisorctl status obesitrack
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/obesitrack`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/obesitrack.pem;
    ssl_certificate_key /etc/ssl/private/obesitrack.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /opt/obesitrack/app/ObesiTrack/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/obesitrack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Firewall Setup

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

---

## ☁️ Cloud Platform Deployments

### 1. Heroku Deployment

#### Heroku Configuration Files

Create `Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
release: python scripts/init_db.py
```

Create `runtime.txt`:

```
python-3.12.1
```

Create `heroku.yml` (for container deployment):

```yaml
build:
  docker:
    web: Dockerfile.heroku
run:
  web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
```

#### Deployment Steps

```bash
# Install Heroku CLI and login
heroku login

# Create application
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon (optional)
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set ENVIRONMENT=production

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run database migrations
heroku run python scripts/init_db.py

# Open application
heroku open
```

### 2. DigitalOcean App Platform

Create `.do/app.yaml`:

```yaml
name: obesitrack
services:
- name: api
  source_dir: /
  github:
    repo: your-username/ObesiTrack-APP
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key"
    type: SECRET
  - key: DATABASE_URL
    value: "${db.DATABASE_URL}"
  http_port: 8080
  health_check:
    http_path: /health
  
databases:
- name: db
  engine: PG
  num_nodes: 1
  size: db-s-dev-database
  version: "13"
```

### 3. AWS ECS Deployment

#### ECS Task Definition

```json
{
  "family": "obesitrack",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "obesitrack-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/obesitrack:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:ssm:region:account:parameter/obesitrack/secret-key"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:ssm:region:account:parameter/obesitrack/database-url"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/obesitrack",
          "awslogs-region": "your-region",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## 🗄️ Database Setup

### 1. PostgreSQL Production Configuration

#### Configuration File (`postgresql.conf`)

```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connection settings
max_connections = 100
listen_addresses = '*'

# Logging
log_destination = 'stderr'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'mod'
log_min_duration_statement = 1000
```

#### Host-Based Authentication (`pg_hba.conf`)

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   obesittrack     obesittrack_user                        md5
host    obesittrack     obesittrack_user    127.0.0.1/32        md5
host    obesittrack     obesittrack_user    ::1/128             md5
```

### 2. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_predictions_user_id_created_at 
ON predictions (user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_users_email 
ON users (email);

CREATE INDEX CONCURRENTLY idx_predictions_created_at 
ON predictions (created_at);

-- Analyze tables
ANALYZE users;
ANALYZE predictions;

-- Set up automatic vacuuming
ALTER TABLE users SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE predictions SET (autovacuum_vacuum_scale_factor = 0.1);
```

### 3. Database Backup Strategy

Create backup script `/opt/obesitrack/scripts/backup_db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/obesitrack/app/ObesiTrack/backups"
DB_NAME="obesittrack"
DB_USER="obesittrack_user"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"

# Create backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME -f $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

```bash
# Make script executable
chmod +x /opt/obesitrack/scripts/backup_db.sh

# Add to crontab for daily backups
crontab -e
# Add line: 0 2 * * * /opt/obesitrack/scripts/backup_db.sh
```

---

## 🔒 SSL/TLS Configuration

### 1. Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Set up automatic renewal
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Manual SSL Certificate

```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/certs /etc/ssl/private

# Copy your certificate files
sudo cp your_certificate.pem /etc/ssl/certs/obesitrack.pem
sudo cp your_private_key.key /etc/ssl/private/obesitrack.key

# Set proper permissions
sudo chmod 644 /etc/ssl/certs/obesitrack.pem
sudo chmod 600 /etc/ssl/private/obesitrack.key
sudo chown root:root /etc/ssl/certs/obesitrack.pem
sudo chown root:root /etc/ssl/private/obesitrack.key
```

### 3. SSL Security Configuration

Add to Nginx configuration:

```nginx
# SSL Security
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/ssl/certs/obesitrack.pem;

# Security Headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring

#### Health Check Monitoring Script

Create `/opt/obesitrack/scripts/health_monitor.sh`:

```bash
#!/bin/bash

HEALTH_URL="http://localhost:8000/health"
LOG_FILE="/opt/obesitrack/app/ObesiTrack/logs/health_monitor.log"
ALERT_EMAIL="admin@yourdomain.com"

# Check health endpoint
if ! curl -f -s $HEALTH_URL > /dev/null; then
    echo "$(date): Health check failed" >> $LOG_FILE
    echo "ObesiTrack health check failed at $(date)" | mail -s "ObesiTrack Alert" $ALERT_EMAIL
    
    # Restart service
    sudo supervisorctl restart obesitrack
else
    echo "$(date): Health check passed" >> $LOG_FILE
fi
```

```bash
# Make executable
chmod +x /opt/obesitrack/scripts/health_monitor.sh

# Add to crontab (every 5 minutes)
crontab -e
# Add line: */5 * * * * /opt/obesitrack/scripts/health_monitor.sh
```

### 2. Log Management

#### Logrotate Configuration

Create `/etc/logrotate.d/obesitrack`:

```
/opt/obesitrack/app/ObesiTrack/logs/*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    create 644 obesitrack obesitrack
    postrotate
        sudo supervisorctl restart obesitrack
    endscript
}
```

### 3. Performance Monitoring

#### System Monitoring Script

Create `/opt/obesitrack/scripts/system_monitor.py`:

```python
#!/usr/bin/env python3

import psutil
import json
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/opt/obesitrack/app/ObesiTrack/logs/system_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def collect_metrics():
    """Collect system metrics"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
        'network': psutil.net_io_counters()._asdict(),
        'processes': len(psutil.pids())
    }

def check_thresholds(metrics):
    """Check if metrics exceed thresholds"""
    alerts = []
    
    if metrics['cpu_percent'] > 80:
        alerts.append(f"High CPU usage: {metrics['cpu_percent']}%")
    
    if metrics['memory']['percent'] > 85:
        alerts.append(f"High memory usage: {metrics['memory']['percent']}%")
    
    if metrics['disk']['percent'] > 90:
        alerts.append(f"High disk usage: {metrics['disk']['percent']}%")
    
    return alerts

def main():
    try:
        metrics = collect_metrics()
        alerts = check_thresholds(metrics)
        
        # Log metrics
        logging.info(f"System metrics: {json.dumps(metrics, indent=2)}")
        
        # Send alerts if any
        if alerts:
            for alert in alerts:
                logging.warning(alert)
                # Send email alert (implement as needed)
        
    except Exception as e:
        logging.error(f"Error collecting metrics: {e}")

if __name__ == "__main__":
    main()
```

```bash
# Make executable
chmod +x /opt/obesitrack/scripts/system_monitor.py

# Add to crontab (every 15 minutes)
crontab -e
# Add line: */15 * * * * /opt/obesitrack/app/ObesiTrack/venv/bin/python /opt/obesitrack/scripts/system_monitor.py
```

---

## ⚡ Performance Optimization

### 1. Application Performance

#### Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4  # 2 * CPU cores
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

Update supervisor configuration:

```ini
[program:obesitrack]
command=/opt/obesitrack/app/ObesiTrack/venv/bin/gunicorn main:app -c gunicorn.conf.py
...
```

### 2. Database Performance

#### Connection Pooling Configuration

Add to application configuration:

```python
# app/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 3. Caching Strategy

#### Redis Implementation

```python
# app/cache.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def cache_result(timeout=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage in prediction service
@cache_result(timeout=1800)  # 30 minutes
def get_prediction_history(user_id, limit=10):
    # Implementation here
    pass
```

---

## 🛡️ Security Hardening

### 1. System Security

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Configure fail2ban for nginx
sudo tee /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 3600
EOF

sudo systemctl restart fail2ban
```

### 2. Application Security

#### Environment Variable Encryption

```bash
# Use environment variable encryption service
# Example with AWS Systems Manager Parameter Store

# Store secrets
aws ssm put-parameter \
    --name "/obesitrack/secret-key" \
    --value "your-secret-key" \
    --type "SecureString"

# Retrieve in application
SECRET_KEY=$(aws ssm get-parameter \
    --name "/obesitrack/secret-key" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)
```

#### Input Validation Middleware

```python
# app/middleware/security.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import re

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_request_size = max_request_size
        self.blocked_ips = set()
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(413, "Request too large")
        
        # Check for suspicious patterns
        user_agent = request.headers.get('user-agent', '')
        if self.is_suspicious_user_agent(user_agent):
            raise HTTPException(403, "Forbidden")
        
        # Process request
        response = await call_next(request)
        return response
    
    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        suspicious_patterns = [
            r'sqlmap',
            r'nikto',
            r'nessus',
            r'<script',
            r'union.*select'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False

# Add to main.py
app.add_middleware(SecurityMiddleware)
```

---

## 💾 Backup & Recovery

### 1. Automated Backup Strategy

#### Complete Backup Script

Create `/opt/obesitrack/scripts/full_backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/obesitrack/backups"
APP_DIR="/opt/obesitrack/app"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="obesitrack_full_backup_${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Database backup
pg_dump -h localhost -U obesittrack_user obesittrack > "$BACKUP_DIR/$BACKUP_NAME/database.sql"

# Application files backup
tar -czf "$BACKUP_DIR/$BACKUP_NAME/application.tar.gz" -C "$APP_DIR" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='logs/*.log' \
    .

# Configuration backup
cp /etc/nginx/sites-available/obesitrack "$BACKUP_DIR/$BACKUP_NAME/nginx.conf"
cp /etc/supervisor/conf.d/obesitrack.conf "$BACKUP_DIR/$BACKUP_NAME/supervisor.conf"

# Create archive
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Upload to cloud storage (optional)
# aws s3 cp "${BACKUP_NAME}.tar.gz" s3://your-backup-bucket/

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "obesitrack_full_backup_*.tar.gz" -mtime +30 -delete

echo "Full backup completed: ${BACKUP_NAME}.tar.gz"
```

### 2. Disaster Recovery Plan

#### Recovery Script

Create `/opt/obesitrack/scripts/restore_backup.sh`:

```bash
#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/obesitrack_restore"
APP_DIR="/opt/obesitrack/app"

# Extract backup
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

BACKUP_NAME=$(basename "$BACKUP_FILE" .tar.gz)

# Stop services
sudo supervisorctl stop obesitrack
sudo systemctl stop nginx

# Restore database
sudo -u postgres dropdb obesittrack
sudo -u postgres createdb obesittrack
sudo -u postgres psql obesittrack < "$RESTORE_DIR/$BACKUP_NAME/database.sql"

# Restore application
rm -rf "$APP_DIR.backup"
mv "$APP_DIR" "$APP_DIR.backup"
tar -xzf "$RESTORE_DIR/$BACKUP_NAME/application.tar.gz" -C "/opt/obesitrack/"

# Restore configurations
sudo cp "$RESTORE_DIR/$BACKUP_NAME/nginx.conf" /etc/nginx/sites-available/obesitrack
sudo cp "$RESTORE_DIR/$BACKUP_NAME/supervisor.conf" /etc/supervisor/conf.d/obesitrack.conf

# Restart services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start obesitrack
sudo systemctl start nginx

echo "Restore completed from: $BACKUP_FILE"
```

---

## 🔧 Troubleshooting

### 1. Common Issues

#### Service Won't Start

```bash
# Check logs
sudo supervisorctl tail -f obesitrack stderr

# Check process
ps aux | grep uvicorn

# Check ports
netstat -tlnp | grep 8000

# Check configuration
sudo supervisorctl reread
sudo supervisorctl update
```

#### Database Connection Issues

```bash
# Test database connection
psql -h localhost -U obesittrack_user -d obesittrack -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection limits
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

#### High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
sudo apt install valgrind
valgrind --tool=memcheck --leak-check=full python app.py
```

### 2. Performance Issues

#### Slow Database Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

#### Application Response Times

```bash
# Monitor with htop
htop

# Check application logs
tail -f /opt/obesitrack/app/ObesiTrack/logs/app.log

# Profile with py-spy
pip install py-spy
py-spy record -o profile.svg --pid $(pgrep -f uvicorn)
```

### 3. Emergency Procedures

#### Service Recovery

```bash
#!/bin/bash
# emergency_restart.sh

echo "Emergency service restart initiated..."

# Stop all services
sudo supervisorctl stop obesitrack
sudo systemctl stop nginx

# Kill any remaining processes
pkill -f uvicorn
pkill -f gunicorn

# Start services
sudo systemctl start nginx
sudo supervisorctl start obesitrack

# Wait and check health
sleep 10
curl -f http://localhost/health

echo "Emergency restart completed"
```

#### Database Recovery

```bash
#!/bin/bash
# emergency_db_recovery.sh

echo "Emergency database recovery initiated..."

# Stop application
sudo supervisorctl stop obesitrack

# Backup current state
pg_dump obesittrack > /tmp/emergency_backup.sql

# Restore from latest backup
LATEST_BACKUP=$(ls -t /opt/obesitrack/backups/backup_*.sql.gz | head -n1)
gunzip -c "$LATEST_BACKUP" | psql obesittrack

# Start application
sudo supervisorctl start obesitrack

echo "Database recovery completed"
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Server provisioned and configured
- [ ] SSL certificates obtained and installed
- [ ] Environment variables configured
- [ ] Database set up and optimized
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Security hardening applied
- [ ] Load testing completed
- [ ] Documentation updated

### Deployment

- [ ] Application code deployed
- [ ] Database migrations applied
- [ ] Static files served correctly
- [ ] Health checks passing
- [ ] SSL/HTTPS working
- [ ] All services running
- [ ] Logs being generated
- [ ] Metrics being collected

### Post-Deployment

- [ ] Smoke tests passed
- [ ] Performance baseline established
- [ ] Monitoring alerts configured
- [ ] Backup schedule verified
- [ ] Team notified of deployment
- [ ] Rollback plan confirmed
- [ ] Documentation updated
- [ ] Success metrics tracked

---

**Last Updated**: January 2025
**Version**: 1.0.0

For additional deployment support, refer to the [DOCUMENTATION.md](./DOCUMENTATION.md) and [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md) files.