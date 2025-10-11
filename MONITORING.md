# Monitoring & Observability Setup

Complete guide for setting up monitoring, logging, and alerting for ADL Backend.

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Setup (5 minutes)](#-quick-setup-5-minutes)
- [Prometheus Metrics](#-prometheus-metrics)
- [Grafana Dashboards](#-grafana-dashboards)
- [Alerting Rules](#-alerting-rules)
- [Log Management](#-log-management)
- [Application Performance Monitoring](#-application-performance-monitoring)
- [Uptime Monitoring](#-uptime-monitoring)
- [Cost-Effective Alternatives](#-cost-effective-alternatives)

---

## 🎯 Overview

### What We'll Monitor

1. **Application Metrics**
   - Request rate, latency, errors
   - Active users, registrations
   - Token generation/validation
   - Email delivery success rate

2. **System Metrics**
   - CPU, Memory, Disk usage
   - Container health
   - Database connections
   - Network I/O

3. **Business Metrics**
   - User registrations per day
   - Login success/failure rates
   - Password reset requests
   - API endpoint usage

### Architecture

```
┌─────────────┐
│   FastAPI   │──┐
│  (Backend)  │  │
└─────────────┘  │
                 │ Metrics
┌─────────────┐  │
│ PostgreSQL  │──┼──→ ┌────────────┐      ┌──────────┐
└─────────────┘  │    │ Prometheus │─────→│ Grafana  │
                 │    └────────────┘      └──────────┘
┌─────────────┐  │           │
│    Nginx    │──┘           │
└─────────────┘              ↓
                      ┌─────────────┐
                      │ Alertmanager│
                      └─────────────┘
                             │
                             ↓
                      Email/Slack/PagerDuty
```

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Add Monitoring Services to Docker Compose

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  # Existing services from your docker-compose.yml
  # ...

  prometheus:
    image: prom/prometheus:latest
    container_name: adl_prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - adl_network
    depends_on:
      - backend

  grafana:
    image: grafana/grafana:latest
    container_name: adl_grafana
    restart: unless-stopped
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=https://yourdomain.com/grafana
    ports:
      - "3001:3000"
    networks:
      - adl_network
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    container_name: adl_alertmanager
    restart: unless-stopped
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - adl_network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: adl_node_exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - adl_network

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: adl_postgres_exporter
    restart: unless-stopped
    environment:
      DATA_SOURCE_NAME: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}?sslmode=disable"
    ports:
      - "9187:9187"
    networks:
      - adl_network
    depends_on:
      - postgres

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  adl_network:
    external: true
```

### Step 2: Create Directory Structure

```bash
mkdir -p monitoring/{prometheus/{rules,},grafana/{provisioning/{datasources,dashboards},dashboards},alertmanager}
```

### Step 3: Configure Prometheus

Create `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'adl-backend'
    environment: 'production'

# Load alerting rules
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Scrape configurations
scrape_configs:
  # Backend application metrics
  - job_name: 'fastapi-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  # PostgreSQL metrics
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Node/System metrics
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Nginx metrics (if nginx-exporter is added)
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:8080']
```

### Step 4: Add Prometheus to FastAPI

Update `backend/app/main.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_users = Gauge('active_users_total', 'Total active users')
registered_users = Gauge('registered_users_total', 'Total registered users')
failed_logins = Counter('failed_login_attempts_total', 'Total failed login attempts')
successful_logins = Counter('successful_login_attempts_total', 'Total successful login attempts')
email_sent = Counter('emails_sent_total', 'Total emails sent', ['status'])

# Middleware for metrics
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Update user count on startup
@app.on_event("startup")
async def update_metrics():
    """Update metrics on startup"""
    async with get_db_session() as db:
        # Count total users
        result = await db.execute(select(func.count(User.id)))
        total_users = result.scalar_one()
        registered_users.set(total_users)
        
        # Count active users
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_count = result.scalar_one()
        active_users.set(active_count)
```

Update `requirements.txt`:

```txt
prometheus-client==0.19.0
```

### Step 5: Configure Grafana Data Source

Create `monitoring/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
```

### Step 6: Create Grafana Dashboard Provisioning

Create `monitoring/grafana/provisioning/dashboards/dashboard.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'ADL Backend Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### Step 7: Start Monitoring Stack

```bash
# Rebuild backend with metrics
docker compose build backend

# Start all services including monitoring
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Check services
docker compose ps

# View logs
docker compose logs -f prometheus grafana
```

### Step 8: Access Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123` (change in .env)
- **Alertmanager**: http://localhost:9093

---

## 📈 Prometheus Metrics

### Custom Application Metrics

Add to `backend/app/services/metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, Info

# Application Info
app_info = Info('adl_application', 'Application information')
app_info.info({
    'version': '1.0.0',
    'environment': 'production',
    'name': 'ADL Backend'
})

# User Metrics
user_registrations = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['status']  # success, failed
)

user_logins = Counter(
    'user_logins_total',
    'Total login attempts',
    ['status', 'method']  # success/failed, username/email
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

# Database Metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation']  # select, insert, update, delete
)

db_connection_pool = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    ['state']  # available, in_use
)

# Email Metrics
email_delivery = Counter(
    'email_delivery_total',
    'Email delivery attempts',
    ['type', 'status']  # password_reset/welcome, success/failed
)

email_queue_size = Gauge(
    'email_queue_size',
    'Number of emails in queue'
)

# API Metrics
api_response_time = Histogram(
    'api_response_time_seconds',
    'API response time',
    ['endpoint', 'method'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

api_errors = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

# Token Metrics
tokens_generated = Counter(
    'jwt_tokens_generated_total',
    'JWT tokens generated',
    ['type']  # access, refresh
)

tokens_validated = Counter(
    'jwt_tokens_validated_total',
    'JWT tokens validated',
    ['status']  # valid, expired, invalid
)

# Rate Limiting Metrics
rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Rate limit exceeded events',
    ['endpoint']
)
```

### Using Metrics in Code

```python
# In user registration endpoint
from backend.app.services.metrics import user_registrations

@router.post("/register")
async def register_user(user_data: UserCreate, db: AsyncSession):
    try:
        # ... registration logic
        user_registrations.labels(status='success').inc()
        return user
    except Exception as e:
        user_registrations.labels(status='failed').inc()
        raise

# In login endpoint
from backend.app.services.metrics import user_logins

@router.post("/login")
async def login(credentials: LoginRequest, db: AsyncSession):
    try:
        # ... authentication logic
        user_logins.labels(status='success', method='username').inc()
        return tokens
    except:
        user_logins.labels(status='failed', method='username').inc()
        raise
```

---

## 📊 Grafana Dashboards

### ADL Backend Dashboard (JSON)

Create `monitoring/grafana/dashboards/adl-backend.json`:

```json
{
  "dashboard": {
    "title": "ADL Backend Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "active_users_total"
          }
        ]
      },
      {
        "title": "Login Success vs Failed",
        "targets": [
          {
            "expr": "rate(user_logins_total{status=\"success\"}[5m])"
          },
          {
            "expr": "rate(user_logins_total{status=\"failed\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

### Import Pre-built Dashboards

1. **Node Exporter Dashboard** (ID: 1860)
2. **PostgreSQL Dashboard** (ID: 9628)
3. **FastAPI Dashboard** (Custom - see above)

**To import:**
1. Go to Grafana → Dashboards → Import
2. Enter dashboard ID
3. Select Prometheus data source
4. Click Import

---

## 🚨 Alerting Rules

### Create Alert Rules

Create `monitoring/prometheus/rules/alerts.yml`:

```yaml
groups:
  - name: ADL Backend Alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          component: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # Slow Response Time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        labels:
          severity: warning
          component: backend
        annotations:
          summary: "Slow API response time"
          description: "95th percentile response time is {{ $value }}s"

      # High Failed Login Rate
      - alert: HighFailedLoginRate
        expr: |
          rate(user_logins_total{status="failed"}[5m]) > 5
        for: 2m
        labels:
          severity: warning
          component: security
        annotations:
          summary: "High rate of failed login attempts"
          description: "{{ $value }} failed logins per second"

      # Backend Down
      - alert: BackendDown
        expr: up{job="fastapi-backend"} == 0
        for: 1m
        labels:
          severity: critical
          component: backend
        annotations:
          summary: "Backend service is down"
          description: "FastAPI backend has been down for 1 minute"

      # Database Connection Issues
      - alert: DatabaseConnectionIssues
        expr: |
          rate(db_connection_errors_total[5m]) > 0
        for: 2m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Database connection errors"
          description: "Database connection errors detected"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "Low memory available"
          description: "Available memory is {{ $value | humanizePercentage }}"

      # Disk Space Low
      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} / 
           node_filesystem_size_bytes{mountpoint="/"}) < 0.15
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "Low disk space"
          description: "Disk space available is {{ $value | humanizePercentage }}"

      # Email Delivery Failing
      - alert: EmailDeliveryFailing
        expr: |
          rate(email_delivery_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          component: email
        annotations:
          summary: "Email delivery failing"
          description: "Email delivery failure rate is high"

      # Too Many Rate Limit Hits
      - alert: HighRateLimitHits
        expr: |
          rate(rate_limit_exceeded_total[5m]) > 10
        for: 5m
        labels:
          severity: info
          component: security
        annotations:
          summary: "High rate of rate limit violations"
          description: "Rate limit exceeded {{ $value }} times per second"
```

### Configure Alertmanager

Create `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
  smtp_require_tls: true

# Alert routing
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  
  routes:
    # Critical alerts go to PagerDuty and Email
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true
    
    # Warning alerts go to Slack
    - match:
        severity: warning
      receiver: 'slack-warnings'

# Alert receivers
receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@yourdomain.com'
        headers:
          Subject: '[{{ .Status }}] {{ .CommonLabels.alertname }}'

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@yourdomain.com'
        send_resolved: true
    pagerduty_configs:
      - service_key: '<your-pagerduty-key>'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: '<your-slack-webhook-url>'
        channel: '#alerts'
        title: 'Alert: {{ .CommonLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

# Inhibition rules (suppress alerts)
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

---

## 📝 Log Management

### Centralized Logging with Loki

Add to `docker-compose.monitoring.yml`:

```yaml
  loki:
    image: grafana/loki:latest
    container_name: adl_loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/loki-config.yml
    networks:
      - adl_network

  promtail:
    image: grafana/promtail:latest
    container_name: adl_promtail
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./monitoring/promtail:/etc/promtail
    command: -config.file=/etc/promtail/promtail-config.yml
    networks:
      - adl_network
    depends_on:
      - loki

volumes:
  loki_data:
```

Create `monitoring/loki/loki-config.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 168h
```

---

## 🔍 Application Performance Monitoring

### Add OpenTelemetry (Optional)

```bash
# Add to requirements.txt
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-instrumentation-fastapi==0.41b0
opentelemetry-exporter-prometheus==1.20.0
```

```python
# backend/app/main.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

---

## 📡 Uptime Monitoring

### Simple Health Check Script

Create `monitoring/uptime-check.sh`:

```bash
#!/bin/bash

URLS=(
    "https://yourdomain.com/health"
    "https://yourdomain.com/docs"
)

SLACK_WEBHOOK="<your-webhook-url>"

for URL in "${URLS[@]}"; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "$URL")
    
    if [ $HTTP_CODE -ne 200 ]; then
        # Send alert
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"🔴 Alert: $URL is DOWN (HTTP $HTTP_CODE)\",
                \"username\": \"Uptime Monitor\"
            }"
        
        echo "$(date): $URL - DOWN (HTTP $HTTP_CODE)" >> /var/log/uptime.log
    else
        echo "$(date): $URL - UP" >> /var/log/uptime.log
    fi
done
```

```bash
# Make executable
chmod +x monitoring/uptime-check.sh

# Add to crontab (every 5 minutes)
*/5 * * * * /opt/adl-backend/monitoring/uptime-check.sh
```

### Third-Party Uptime Services (Free Tiers)

1. **UptimeRobot** (Free)
   - 50 monitors
   - 5-minute intervals
   - https://uptimerobot.com

2. **Pingdom** (Free trial)
   - Advanced monitoring
   - https://www.pingdom.com

3. **StatusCake** (Free tier)
   - Unlimited tests
   - https://www.statuscake.com

4. **Better Uptime** (Free tier)
   - Incident management
   - https://betteruptime.com

---

## 💰 Cost-Effective Alternatives

### Self-Hosted Free Stack
- **Prometheus** ✅ (Already included)
- **Grafana** ✅ (Already included)
- **Alertmanager** ✅ (Already included)
- **Cost**: $0 (uses existing server resources)

### Cloud-Based Free Tiers
1. **Grafana Cloud**
   - Free tier: 10K series, 50GB logs
   - https://grafana.com/products/cloud/

2. **Datadog**
   - Free tier: 5 hosts
   - https://www.datadoghq.com

3. **New Relic**
   - Free tier: 100GB/month
   - https://newrelic.com

### Lightweight Alternative

If resources are limited, use this minimal setup:

```yaml
# docker-compose.lite-monitoring.yml
version: '3.8'

services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: adl_cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - adl_network
```

Access at: http://localhost:8080

---

## 🧪 Testing Alerts

```bash
# Trigger high error rate
for i in {1..100}; do
    curl -k https://localhost/api/invalid-endpoint
done

# Check Prometheus alerts
curl http://localhost:9090/api/v1/alerts

# Check Alertmanager
curl http://localhost:9093/api/v1/alerts
```

---

## 📚 Monitoring Checklist

### Daily Tasks
- [ ] Check Grafana dashboards
- [ ] Review critical alerts
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review resource usage trends
- [ ] Check disk space
- [ ] Review slow queries
- [ ] Update alert thresholds if needed

### Monthly Tasks
- [ ] Review and optimize dashboards
- [ ] Clean up old metrics
- [ ] Test alert delivery
- [ ] Review monitoring costs

---

## 🆘 Troubleshooting

### Prometheus Not Scraping Metrics

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check backend metrics endpoint
curl -k https://localhost:8000/metrics

# Restart Prometheus
docker compose restart prometheus
```

### Grafana Can't Connect to Prometheus

```bash
# Check network connectivity
docker exec adl_grafana ping prometheus

# Verify Prometheus URL in datasource
# Should be: http://prometheus:9090
```

### Alerts Not Firing

```bash
# Check alert rules syntax
docker exec adl_prometheus promtool check rules /etc/prometheus/rules/alerts.yml

# View active alerts
curl http://localhost:9090/api/v1/alerts

# Check Alertmanager config
docker exec adl_alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

---

## 📊 Dashboard Examples

Access pre-configured dashboards at:
- **Overview**: http://localhost:3001/d/adl-overview
- **Performance**: http://localhost:3001/d/adl-performance
- **Security**: http://localhost:3001/d/adl-security
- **Business**: http://localhost:3001/d/adl-business

---

## 📖 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Observability](https://fastapi.tiangolo.com/advanced/metrics/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

---

**Last Updated:** October 11, 2025
**Version:** 1.0.0
