"""Middleware components for request tracking and rate limiting.

This module provides ASGI-compatible middleware for:
- Request ID generation and tracking
- Request/response logging with latency measurement
- In-memory rate limiting with sliding window algorithm
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .utils.logging import get_logger

logger = get_logger(__name__)


def generate_request_id() -> str:
    """Generate a unique request identifier.

    Returns:
        UUID4 as hexadecimal string.

    Example:
        >>> request_id = generate_request_id()
        >>> len(request_id)
        32
    """
    return uuid.uuid4().hex


def get_client_key(request: Request) -> str:
    """Extract client identifier from request.

    Uses client IP address if available, otherwise returns 'test'.

    Args:
        request: Starlette Request object.

    Returns:
        Client identifier string (IP address or 'test').

    Example:
        >>> # In production: returns IP like "192.168.1.1"
        >>> # In tests: returns "test"
    """
    if request.client and request.client.host:
        return request.client.host
    return "test"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and logging.

    Adds X-Request-ID header to all responses and logs request details
    including path, status code, and handler latency in milliseconds.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> app.add_middleware(RequestContextMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add tracking information.

        Args:
            request: Incoming HTTP request.
            call_next: Next handler in the chain.

        Returns:
            HTTP response with X-Request-ID header.
        """
        # Generate request ID
        request_id = generate_request_id()

        # Record start time
        start_time = time.perf_counter()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[{request_id}] {duration_ms:.2f}ms - Error: {e}"
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add request ID header
        response.headers["X-Request-ID"] = request_id

        # Log request
        logger.info(
            f"{request.method} {request.url.path} "
            f"[{request_id}] {response.status_code} {duration_ms:.2f}ms"
        )

        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter using sliding window algorithm.

    Tracks request timestamps per client and enforces rate limits.
    Returns 429 Too Many Requests when limit is exceeded.

    Attributes:
        limit: Maximum number of requests allowed per window.
        window_sec: Time window in seconds for rate limiting.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> # Allow 60 requests per 60 seconds per client
        >>> app.add_middleware(RateLimiterMiddleware, limit=60, window_sec=60)
    """

    def __init__(
        self,
        app,
        limit: int = 60,
        window_sec: int = 60,
    ) -> None:
        """Initialize rate limiter middleware.

        Args:
            app: ASGI application.
            limit: Maximum requests per window (default: 60).
            window_sec: Time window in seconds (default: 60).
        """
        super().__init__(app)
        self.limit = limit
        self.window_sec = window_sec

        # Storage: client_key -> deque of timestamps
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

    def _cleanup_old_requests(self, client_key: str, current_time: float) -> None:
        """Remove timestamps outside the current window.

        Args:
            client_key: Client identifier.
            current_time: Current timestamp.
        """
        cutoff_time = current_time - self.window_sec
        request_times = self._requests[client_key]

        # Remove old timestamps from the left (oldest)
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()

    def _check_rate_limit(self, client_key: str, current_time: float) -> Tuple[bool, int]:
        """Check if client has exceeded rate limit.

        Args:
            client_key: Client identifier.
            current_time: Current timestamp.

        Returns:
            Tuple of (is_allowed, retry_after_seconds).
        """
        # Clean up old requests
        self._cleanup_old_requests(client_key, current_time)

        request_times = self._requests[client_key]
        request_count = len(request_times)

        if request_count >= self.limit:
            # Calculate retry_after based on oldest request in window
            if request_times:
                oldest_request = request_times[0]
                retry_after = int(self.window_sec - (current_time - oldest_request)) + 1
            else:
                retry_after = self.window_sec
            return False, retry_after

        return True, 0

    def _record_request(self, client_key: str, current_time: float) -> None:
        """Record a new request timestamp.

        Args:
            client_key: Client identifier.
            current_time: Current timestamp.
        """
        self._requests[client_key].append(current_time)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce rate limits.

        Args:
            request: Incoming HTTP request.
            call_next: Next handler in the chain.

        Returns:
            HTTP response or 429 error if rate limit exceeded.
        """
        # Get client identifier
        client_key = get_client_key(request)
        current_time = time.time()

        # Check rate limit
        is_allowed, retry_after = self._check_rate_limit(client_key, current_time)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_key}: "
                f"{request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Record request
        self._record_request(client_key, current_time)

        # Process request
        response = await call_next(request)
        return response
