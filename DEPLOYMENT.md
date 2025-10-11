# Production Deployment Guide

Complete guide for deploying the ADL Backend to production environments.

## 📋 Table of Contents

- [Pre-Deployment Checklist](#-pre-deployment-checklist)
- [Deployment Options](#-deployment-options)
- [Option 1: Docker Compose (VPS)](#option-1-docker-compose-vps)
- [Option 2: Cloud Platforms](#option-2-cloud-platforms)
- [Option 3: Kubernetes](#option-3-kubernetes)
- [SSL Certificate Setup](#-ssl-certificate-setup)
- [Database Backup & Recovery](#-database-backup--recovery)
- [Monitoring & Logging](#-monitoring--logging)
- [Scaling Strategies](#-scaling-strategies)
- [Rollback Procedures](#-rollback-procedures)
- [Security Hardening](#-security-hardening)

---

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **SECRET_KEY**: Generate new production secret key
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

- [ ] **Database Password**: Strong, random password (min 32 characters)
  ```bash
  openssl rand -base64 32
  ```

- [ ] **CORS Origins**: Update with production frontend URL
  ```bash
  ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
  ```

- [ ] **Debug Mode**: Ensure disabled
  ```bash
  DEBUG=false
  ```

- [ ] **Email Configuration**: Production SMTP credentials configured

### 2. Security Review

- [ ] All passwords changed from defaults
- [ ] SSL certificates installed (not self-signed)
- [ ] Firewall rules configured
- [ ] Rate limiting tested
- [ ] CORS properly restricted
- [ ] Security headers verified

### 3. Database

- [ ] Backup strategy implemented
- [ ] Connection pooling configured
- [ ] Indexes verified
- [ ] Migration scripts tested

### 4. Testing

- [ ] All 54 tests passing
- [ ] Load testing completed
- [ ] Security scanning performed
- [ ] API endpoints tested in production-like environment

### 5. Documentation

- [ ] API documentation accessible
- [ ] Environment variables documented
- [ ] Runbook created for common issues
- [ ] Contact information updated

---

## 🚀 Deployment Options

### Option 1: Docker Compose (VPS)

**Best for:** Small to medium applications, cost-effective

**Requirements:**
- VPS with Ubuntu 22.04+ (2GB RAM minimum, 4GB recommended)
- Docker & Docker Compose installed
- Domain name pointed to server IP

#### Step-by-Step Deployment

##### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install certbot for SSL
sudo apt install certbot -y
```

##### 2. Clone Repository

```bash
# Clone your repository
git clone <your-repository-url> /opt/adl-backend
cd /opt/adl-backend

# Set proper permissions
sudo chown -R $USER:$USER /opt/adl-backend
```

##### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Production .env example:**
```bash
# Database
POSTGRES_USER=adl_user
POSTGRES_PASSWORD=<generate-secure-password>
POSTGRES_DB=adl_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://adl_user:<password>@postgres:5432/adl_db

# Application
APP_NAME="ADL Production"
APP_VERSION="1.0.0"
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=<generate-64-char-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - UPDATE WITH YOUR DOMAIN
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<app-password>
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="ADL Application"

# Rate Limiting
RATE_LIMIT=200/hour
```

##### 4. SSL Certificate Setup

```bash
# Stop nginx if running
docker compose stop nginx

# Get Let's Encrypt certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project
sudo mkdir -p nginx/certs
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/certs/key.pem
sudo chown $USER:$USER nginx/certs/*
```

##### 5. Update Nginx Configuration

Edit `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of configuration
}
```

##### 6. Deploy Application

```bash
# Build images
docker compose build --no-cache

# Start services
docker compose up -d

# Check logs
docker compose logs -f

# Verify health
sleep 30
curl https://yourdomain.com/health
```

##### 7. Setup Auto-Start on Boot

```bash
# Create systemd service
sudo nano /etc/systemd/system/adl-backend.service
```

**Service file content:**
```ini
[Unit]
Description=ADL Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/adl-backend
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable adl-backend
sudo systemctl start adl-backend
sudo systemctl status adl-backend
```

##### 8. Setup Automatic SSL Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Create renewal hook
sudo nano /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh
```

**Hook script:**
```bash
#!/bin/bash
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/adl-backend/nginx/certs/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/adl-backend/nginx/certs/key.pem
chown $USER:$USER /opt/adl-backend/nginx/certs/*
cd /opt/adl-backend && docker compose restart nginx
```

```bash
# Make executable
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh
```

##### 9. Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (IMPORTANT - Don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose
```

##### 10. Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/adl-backend
```

```
/opt/adl-backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    sharedscripts
    postrotate
        docker compose -f /opt/adl-backend/docker-compose.yml restart backend
    endscript
}
```

---

### Option 2: Cloud Platforms

#### AWS Deployment (ECS + RDS)

**Architecture:**
- Application: ECS Fargate
- Database: RDS PostgreSQL
- Load Balancer: Application Load Balancer
- SSL: AWS Certificate Manager

**Cost Estimate:** $50-150/month

##### Quick Setup

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure

# Create ECR repository
aws ecr create-repository --repository-name adl-backend

# Build and push image
docker build -t adl-backend .
docker tag adl-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/adl-backend:latest
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/adl-backend:latest

# Deploy using ECS (use AWS Console or Terraform)
```

#### DigitalOcean App Platform

**Architecture:**
- Application: App Platform
- Database: Managed PostgreSQL
- SSL: Automatic

**Cost Estimate:** $20-60/month

##### Setup

1. **Push code to GitHub**
2. **Create DigitalOcean account**
3. **Create new App**:
   - Connect GitHub repository
   - Select branch
   - Detect Dockerfile automatically
4. **Add Database**:
   - Create managed PostgreSQL cluster
   - Link to app
5. **Configure Environment Variables**:
   - Add all .env variables in App settings
6. **Deploy**:
   - Click deploy
   - SSL configured automatically

#### Heroku

**Quick deployment:**

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create adl-backend-prod

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set SECRET_KEY=<your-secret>
heroku config:set ENVIRONMENT=production
# ... add all other variables

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2

# View logs
heroku logs --tail
```

---

### Option 3: Kubernetes

**Best for:** Large-scale applications, high availability requirements

#### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or self-hosted)
- kubectl configured
- Helm installed

#### Kubernetes Manifests

##### 1. Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: adl-backend
```

##### 2. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: adl-config
  namespace: adl-backend
data:
  APP_NAME: "ADL Production"
  ENVIRONMENT: "production"
  POSTGRES_HOST: "postgres-service"
  POSTGRES_PORT: "5432"
```

##### 3. Secrets

```bash
# Create secrets
kubectl create secret generic adl-secrets \
  --from-literal=POSTGRES_PASSWORD=<password> \
  --from-literal=SECRET_KEY=<secret> \
  --from-literal=SMTP_PASSWORD=<password> \
  -n adl-backend
```

##### 4. PostgreSQL Deployment

```yaml
# k8s/postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: adl-backend
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: adl-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: adl-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_USER
          value: adl_user
        - name: POSTGRES_DB
          value: adl_db
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: adl-backend
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

##### 5. Backend Deployment

```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adl-backend
  namespace: adl-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adl-backend
  template:
    metadata:
      labels:
        app: adl-backend
    spec:
      containers:
      - name: backend
        image: <your-registry>/adl-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: adl-secrets
              key: SECRET_KEY
        envFrom:
        - configMapRef:
            name: adl-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: adl-backend
spec:
  selector:
    app: adl-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

##### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml

# Check status
kubectl get pods -n adl-backend
kubectl get services -n adl-backend

# View logs
kubectl logs -f deployment/adl-backend -n adl-backend
```

---

## 🔒 SSL Certificate Setup

### Let's Encrypt (Free)

#### Automatic Renewal with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run

# Auto-renewal is setup via cron
sudo systemctl status certbot.timer
```

### Cloudflare (Recommended for DDoS Protection)

1. **Add domain to Cloudflare**
2. **Enable SSL/TLS** → Full (strict)
3. **Generate Origin Certificate**:
   - SSL/TLS → Origin Server → Create Certificate
   - Copy certificate and key
   - Save to `nginx/certs/`
4. **Update Nginx** to use certificates
5. **Enable Always Use HTTPS**

---

## 💾 Database Backup & Recovery

### Automated Backups

#### Daily Backup Script

```bash
# Create backup script
nano /opt/adl-backend/scripts/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/adl-backend/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/adl_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec adl_postgres pg_dump -U adl_user adl_db > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
# Make executable
chmod +x /opt/adl-backend/scripts/backup.sh

# Test backup
/opt/adl-backend/scripts/backup.sh
```

#### Setup Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/adl-backend/scripts/backup.sh >> /var/log/adl-backup.log 2>&1
```

### Restore from Backup

```bash
# Stop application
docker compose down

# Restore database
gunzip -c /opt/adl-backend/backups/adl_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i adl_postgres psql -U adl_user -d adl_db

# Start application
docker compose up -d
```

### Offsite Backup (S3)

```bash
# Install AWS CLI
pip install awscli

# Configure AWS
aws configure

# Add to backup script
aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/adl-backups/
```

---

## 📊 Monitoring & Logging

### Health Check Monitoring

#### Setup Monitoring Script

```bash
# Create health check script
nano /opt/adl-backend/scripts/health-check.sh
```

```bash
#!/bin/bash
HEALTH_URL="https://yourdomain.com/health"
SLACK_WEBHOOK="<your-slack-webhook-url>"

# Check health
HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $HTTP_CODE -ne 200 ]; then
    # Send alert to Slack
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"⚠️ ADL Backend is DOWN! HTTP Code: $HTTP_CODE\"}" \
        $SLACK_WEBHOOK
    
    echo "$(date): Health check failed - HTTP $HTTP_CODE" >> /var/log/adl-health.log
else
    echo "$(date): Health check passed" >> /var/log/adl-health.log
fi
```

```bash
# Make executable
chmod +x /opt/adl-backend/scripts/health-check.sh

# Add to cron (every 5 minutes)
crontab -e
*/5 * * * * /opt/adl-backend/scripts/health-check.sh
```

### Application Logs

```bash
# View real-time logs
docker compose logs -f backend

# Save logs to file
docker compose logs backend > /var/log/adl-backend-$(date +%Y%m%d).log

# Search logs
docker compose logs backend | grep ERROR
```

### Prometheus + Grafana (Optional)

Add to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## �� Scaling Strategies

### Horizontal Scaling (Multiple Containers)

Update `docker-compose.yml`:

```yaml
services:
  backend:
    # ... existing config
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Load Balancer Setup

Use Nginx as load balancer:

```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://backend_servers;
    }
}
```

### Database Connection Pooling

In production, adjust pool size:

```python
# backend/app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,          # Increase for production
    max_overflow=10,
    pool_pre_ping=True
)
```

---

## ⏮️ Rollback Procedures

### Quick Rollback

```bash
# Stop current version
docker compose down

# Checkout previous version
git checkout <previous-commit-hash>

# Deploy previous version
docker compose up -d --build

# Verify
curl https://yourdomain.com/health
```

### Database Rollback

```bash
# View migration history
docker exec -it adl_backend alembic history

# Rollback to specific version
docker exec -it adl_backend alembic downgrade <revision>
```

### Backup Before Deployment

```bash
# Always backup before deployment
/opt/adl-backend/scripts/backup.sh

# Tag current version
git tag -a v1.0.0 -m "Production release 1.0.0"
git push origin v1.0.0
```

---

## 🛡️ Security Hardening

### 1. Disable Root Login (SSH)

```bash
sudo nano /etc/ssh/sshd_config
```

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
sudo systemctl restart sshd
```

### 2. Setup Fail2Ban

```bash
sudo apt install fail2ban -y

sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Security Updates

```bash
# Setup automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 4. Container Security Scanning

```bash
# Install Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install trivy

# Scan image
trivy image adl-backend:latest
```

---

## 📱 Post-Deployment Verification

### Deployment Checklist

```bash
# 1. Health check
curl https://yourdomain.com/health

# 2. API documentation accessible
curl https://yourdomain.com/docs

# 3. User registration
curl https://yourdomain.com/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123"}'

# 4. User login
curl https://yourdomain.com/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123"}'

# 5. Check logs for errors
docker compose logs backend | grep ERROR

# 6. Monitor resource usage
docker stats

# 7. Test email functionality
curl https://yourdomain.com/api/password/test-email \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com"}'
```

---

## 🆘 Emergency Contacts

**Production Issues:**
- Primary: [Your Contact]
- Secondary: [Backup Contact]
- Database Admin: [DBA Contact]

**Escalation Path:**
1. Check logs: `docker compose logs -f`
2. Check health: `curl https://yourdomain.com/health`
3. Rollback if critical: Follow rollback procedures
4. Contact team lead

---

## 📚 Additional Resources

- [FastAPI Deployment Docs](https://fastapi.tiangolo.com/deployment/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

---

**Last Updated:** October 11, 2025
**Version:** 1.0.0
