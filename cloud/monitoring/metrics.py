"""
Prometheus metrics for SentinelDF Cloud.

Tracks:
- API request latency
- Job queue depth
- Worker utilization
- Cache hit rates
- Error rates
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from functools import wraps
import time
from typing import Callable
from datetime import datetime

# ============================================================================
# METRICS DEFINITIONS
# ============================================================================

# API Metrics
api_requests_total = Counter(
    'sentineldf_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'sentineldf_api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

api_active_requests = Gauge(
    'sentineldf_api_active_requests',
    'Number of active API requests'
)

# Job Queue Metrics
job_queue_depth = Gauge(
    'sentineldf_job_queue_depth',
    'Number of jobs in queue',
    ['priority']
)

job_processing_duration = Histogram(
    'sentineldf_job_processing_duration_seconds',
    'Job processing time',
    ['priority'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
)

jobs_completed_total = Counter(
    'sentineldf_jobs_completed_total',
    'Total completed jobs',
    ['status']  # completed, failed
)

# Worker Metrics
worker_active_tasks = Gauge(
    'sentineldf_worker_active_tasks',
    'Number of active worker tasks',
    ['worker_id']
)

worker_task_duration = Histogram(
    'sentineldf_worker_task_duration_seconds',
    'Worker task processing time',
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
)

# Cache Metrics
cache_hits_total = Counter(
    'sentineldf_cache_hits_total',
    'Cache hits',
    ['cache_type']  # embedding, apikey, session
)

cache_misses_total = Counter(
    'sentineldf_cache_misses_total',
    'Cache misses',
    ['cache_type']
)

cache_size = Gauge(
    'sentineldf_cache_size_bytes',
    'Cache size in bytes',
    ['cache_type']
)

# Database Metrics
db_query_duration = Histogram(
    'sentineldf_db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

db_connections = Gauge(
    'sentineldf_db_connections',
    'Active database connections'
)

# ML Inference Metrics
inference_duration = Histogram(
    'sentineldf_inference_duration_seconds',
    'ML inference time',
    ['model'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

documents_scanned_total = Counter(
    'sentineldf_documents_scanned_total',
    'Total documents scanned',
    ['org_id']
)

quarantine_rate = Gauge(
    'sentineldf_quarantine_rate',
    'Percentage of documents quarantined',
    ['org_id']
)

# Error Metrics
errors_total = Counter(
    'sentineldf_errors_total',
    'Total errors',
    ['error_type', 'component']
)

# Rate Limiting Metrics
rate_limit_hits_total = Counter(
    'sentineldf_rate_limit_hits_total',
    'Requests blocked by rate limiting',
    ['org_id']
)

# System Info
system_info = Info(
    'sentineldf_system',
    'System information'
)

# ============================================================================
# DECORATORS
# ============================================================================

def track_api_request(endpoint: str):
    """Decorator to track API request metrics."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            api_active_requests.inc()
            start_time = time.time()
            status = "200"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "500"
                errors_total.labels(
                    error_type=type(e).__name__,
                    component='api'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                api_request_duration.labels(
                    method='POST',
                    endpoint=endpoint
                ).observe(duration)
                api_requests_total.labels(
                    method='POST',
                    endpoint=endpoint,
                    status=status
                ).inc()
                api_active_requests.dec()
        
        return wrapper
    return decorator

def track_cache_access(cache_type: str):
    """Decorator to track cache hits/misses."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if result is not None:
                cache_hits_total.labels(cache_type=cache_type).inc()
            else:
                cache_misses_total.labels(cache_type=cache_type).inc()
            
            return result
        return wrapper
    return decorator

def track_job_processing(priority: str):
    """Decorator to track job processing."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "completed"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failed"
                errors_total.labels(
                    error_type=type(e).__name__,
                    component='worker'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                job_processing_duration.labels(priority=priority).observe(duration)
                jobs_completed_total.labels(status=status).inc()
        
        return wrapper
    return decorator

# ============================================================================
# METRIC HELPERS
# ============================================================================

def update_queue_depth(priority: str, depth: int):
    """Update job queue depth metric."""
    job_queue_depth.labels(priority=priority).set(depth)

def track_scan_result(org_id: str, quarantined: bool):
    """Track scan result for an organization."""
    documents_scanned_total.labels(org_id=org_id).inc()
    
    # Update quarantine rate (simplified - in production, use sliding window)
    # This would typically be calculated from recent scans

def track_rate_limit_hit(org_id: str):
    """Track rate limit hit."""
    rate_limit_hits_total.labels(org_id=org_id).inc()

def set_system_info(version: str, environment: str):
    """Set system information."""
    system_info.info({
        'version': version,
        'environment': environment,
        'started_at': datetime.utcnow().isoformat()
    })

# ============================================================================
# METRICS ENDPOINT
# ============================================================================

def get_metrics() -> bytes:
    """Get Prometheus metrics in text format."""
    return generate_latest()

# ============================================================================
# INITIALIZATION
# ============================================================================

# Set initial system info
set_system_info(version='3.0.0', environment='production')

if __name__ == "__main__":
    # Test metrics
    print("📊 SentinelDF Metrics initialized")
    print(get_metrics().decode('utf-8'))
