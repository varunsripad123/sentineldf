"""OpenTelemetry distributed tracing setup.

This module provides optional tracing capabilities that are only activated
when OTEL_EXPORTER_OTLP_ENDPOINT environment variable is set. This ensures
no behavior change unless explicitly enabled.
"""

from __future__ import annotations

import os
from typing import Optional


def setup_tracing(app_name: str = "sentineldf-api") -> Optional[object]:
    """Setup OpenTelemetry tracing if OTLP endpoint is configured.

    Tracing is only enabled when OTEL_EXPORTER_OTLP_ENDPOINT environment
    variable is set. This allows zero-config local development while
    enabling distributed tracing in production.

    Args:
        app_name: Service name for tracing (default: "sentineldf-api").

    Returns:
        TracerProvider instance if tracing is enabled, None otherwise.

    Example:
        >>> # Without OTEL_EXPORTER_OTLP_ENDPOINT set
        >>> provider = setup_tracing()
        >>> provider is None
        True

        >>> # With OTEL_EXPORTER_OTLP_ENDPOINT="http://collector:4318"
        >>> provider = setup_tracing()
        >>> provider is not None
        True
    """
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return None

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
        OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource(attributes={SERVICE_NAME: app_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider
