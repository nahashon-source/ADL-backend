"""
Prometheus Metrics Router

Provides /metrics endpoint for Prometheus scraping.
"""
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from backend.app.core.config import settings

router = APIRouter()

# ============= PROMETHEUS METRICS =============

# Application Info
app_info = Info('adl_application', 'Application information', registry=REGISTRY)
app_info.info({
    'version': settings.version,
    'environment': settings.environment,
    'name': settings.project_name
})

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Application Metrics
active_users_gauge = Gauge(
    'active_users_total',
    'Total number of active users',
    registry=REGISTRY
)

registered_users_gauge = Gauge(
    'registered_users_total',
    'Total number of registered users',
    registry=REGISTRY
)

# Error Metrics
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type'],
    registry=REGISTRY
)

# ============================================


@router.get("/metrics", include_in_schema=False)
async def metrics():
    """
    Prometheus metrics endpoint.
    
    This endpoint exposes application metrics in Prometheus format.
    It's excluded from the API documentation and should be scraped by Prometheus.
    
    Metrics include:
    - HTTP request count, duration, and errors
    - Active users count
    - Registered users count
    - In-progress requests
    
    Returns:
        Response: Prometheus-formatted metrics
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )
