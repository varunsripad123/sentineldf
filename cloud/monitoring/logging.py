"""
Structured logging for SentinelDF Cloud.

Features:
- JSON formatted logs
- Trace ID propagation
- Performance tracking
- Error context capture
"""
import logging
import json
import sys
import time
import uuid
from datetime import datetime
from contextvars import ContextVar
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger

# Context variables for request tracing
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
org_id_var: ContextVar[Optional[str]] = ContextVar('org_id', default=None)

# ============================================================================
# CUSTOM JSON FORMATTER
# ============================================================================

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with trace context."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add trace context
        trace_id = trace_id_var.get()
        if trace_id:
            log_record['trace_id'] = trace_id
        
        span_id = span_id_var.get()
        if span_id:
            log_record['span_id'] = span_id
        
        user_id = user_id_var.get()
        if user_id:
            log_record['user_id'] = user_id
        
        org_id = org_id_var.get()
        if org_id:
            log_record['org_id'] = org_id
        
        # Add service name
        log_record['service'] = 'sentineldf-cloud'
        
        # Add level as string
        log_record['level'] = record.levelname
        
        # Add source location
        log_record['source'] = {
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName
        }

# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logging(level: str = "INFO", service_name: str = "sentineldf-cloud"):
    """
    Configure structured JSON logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        service_name: Service name for logs
    """
    log_level = getattr(logging, level.upper())
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Set JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(handler)
    
    # Silence noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    
    return root_logger

# ============================================================================
# TRACE CONTEXT MANAGEMENT
# ============================================================================

def start_trace() -> str:
    """Start a new trace with unique ID."""
    trace_id = uuid.uuid4().hex
    trace_id_var.set(trace_id)
    return trace_id

def start_span(parent_trace_id: Optional[str] = None) -> str:
    """Start a new span within a trace."""
    if parent_trace_id:
        trace_id_var.set(parent_trace_id)
    
    span_id = uuid.uuid4().hex[:16]
    span_id_var.set(span_id)
    return span_id

def set_user_context(user_id: str, org_id: str):
    """Set user context for logging."""
    user_id_var.set(user_id)
    org_id_var.set(org_id)

def clear_context():
    """Clear all context variables."""
    trace_id_var.set(None)
    span_id_var.set(None)
    user_id_var.set(None)
    org_id_var.set(None)

def get_trace_id() -> Optional[str]:
    """Get current trace ID."""
    return trace_id_var.get()

# ============================================================================
# LOGGING HELPERS
# ============================================================================

class StructuredLogger:
    """Logger wrapper with structured logging helpers."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info with structured data."""
        self.logger.info(message, extra={'data': kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning with structured data."""
        self.logger.warning(message, extra={'data': kwargs})
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error with exception context."""
        extra = {'data': kwargs}
        if error:
            extra['error'] = {
                'type': type(error).__name__,
                'message': str(error)
            }
        self.logger.error(message, extra=extra, exc_info=error is not None)
    
    def debug(self, message: str, **kwargs):
        """Log debug with structured data."""
        self.logger.debug(message, extra={'data': kwargs})
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        latency_ms: float,
        **kwargs
    ):
        """Log HTTP request."""
        self.info(
            f"{method} {endpoint}",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            latency_ms=latency_ms,
            **kwargs
        )
    
    def log_job(
        self,
        job_id: str,
        status: str,
        duration_seconds: Optional[float] = None,
        **kwargs
    ):
        """Log job processing."""
        self.info(
            f"Job {status}",
            job_id=job_id,
            status=status,
            duration_seconds=duration_seconds,
            **kwargs
        )
    
    def log_cache(
        self,
        operation: str,
        cache_type: str,
        hit: bool,
        **kwargs
    ):
        """Log cache operation."""
        self.debug(
            f"Cache {operation}",
            operation=operation,
            cache_type=cache_type,
            hit=hit,
            **kwargs
        )
    
    def log_database(
        self,
        query_type: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
        **kwargs
    ):
        """Log database operation."""
        self.debug(
            f"Database {query_type}",
            query_type=query_type,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            **kwargs
        )

# ============================================================================
# PERFORMANCE TRACKING
# ============================================================================

class PerformanceTimer:
    """Context manager for performance tracking."""
    
    def __init__(self, logger: StructuredLogger, operation: str, **kwargs):
        self.logger = logger
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"{self.operation} completed",
                operation=self.operation,
                duration_seconds=duration,
                **self.kwargs
            )
        else:
            self.logger.error(
                f"{self.operation} failed",
                error=exc_val,
                operation=self.operation,
                duration_seconds=duration,
                **self.kwargs
            )

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Example of structured logging usage."""
    # Setup logging
    setup_logging(level="INFO")
    
    # Create logger
    logger = StructuredLogger("sentineldf.api")
    
    # Start trace
    trace_id = start_trace()
    set_user_context(user_id="user_123", org_id="org_456")
    
    # Log request
    logger.log_request(
        method="POST",
        endpoint="/v1/scan/async",
        status_code=200,
        latency_ms=45.2,
        files_count=100
    )
    
    # Log with performance tracking
    with PerformanceTimer(logger, "process_batch", batch_size=100):
        time.sleep(0.1)  # Simulate work
    
    # Log error
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.error("Processing failed", error=e, context="example")
    
    # Clear context
    clear_context()

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    example_usage()
