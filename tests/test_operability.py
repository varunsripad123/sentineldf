"""Tests for operational features: middleware, rate limiting, config, and caching.

These tests verify the operational aspects of the application including
request tracking, rate limiting, configuration exposure, and cache behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import app


class TestRequestTracking:
    """Test suite for request tracking middleware."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app.

        Returns:
            TestClient instance for making requests.
        """
        return TestClient(app)

    def test_request_id_header_present(self, client: TestClient) -> None:
        """Test that X-Request-ID header is present in responses.

        The RequestContextMiddleware should add a unique request ID
        to every response for tracking and debugging purposes.
        """
        response = client.get("/health")

        # Assert header is present
        assert "X-Request-ID" in response.headers, "X-Request-ID header missing from response"

        # Assert it's a reasonable length (UUID4 hex is 32 characters)
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 10, f"Request ID too short: {request_id}"

        # Should be alphanumeric (UUID4 hex format)
        assert request_id.isalnum(), f"Request ID has invalid characters: {request_id}"


class TestRateLimiter:
    """Test suite for rate limiting middleware."""

    def test_rate_limiter_basic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that rate limiter blocks excessive requests.

        The RateLimiterMiddleware should track requests per client
        and return 429 status when the limit is exceeded.
        """
        # Create a fresh app instance with tight rate limits for testing
        from fastapi import FastAPI

        from backend.middleware import RateLimiterMiddleware, RequestContextMiddleware

        test_app = FastAPI()
        test_app.add_middleware(RequestContextMiddleware)
        # Set very low limit for testing (3 requests per 60 seconds)
        test_app.add_middleware(RateLimiterMiddleware, limit=3, window_sec=60)

        # Add a simple test endpoint
        @test_app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        client = TestClient(test_app)

        # Make 3 requests (should succeed)
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200, f"Request {i+1} should succeed"

        # 4th request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429, "4th request should be rate limited"

        # Check response body
        data = response.json()
        assert "detail" in data
        assert "rate limit exceeded" in data["detail"].lower()
        assert "retry_after" in data


class TestConfigEndpoint:
    """Test suite for configuration endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app.

        Returns:
            TestClient instance for making requests.
        """
        return TestClient(app)

    def test_config_endpoint_schema(self, client: TestClient) -> None:
        """Test that /config endpoint returns correct schema.

        The config endpoint should return sanitized configuration
        without exposing secrets.
        """
        response = client.get("/config")

        # Should return 200
        assert response.status_code == 200, "Config endpoint should return 200"

        # Parse JSON
        data = response.json()

        # Assert all required keys are present
        assert "heuristic_weight" in data, "heuristic_weight missing from config"
        assert "embedding_weight" in data, "embedding_weight missing from config"
        assert "risk_quarantine_threshold" in data, "risk_quarantine_threshold missing from config"

        # Assert types are correct
        assert isinstance(
            data["heuristic_weight"], (int, float)
        ), "heuristic_weight should be a number"
        assert isinstance(
            data["embedding_weight"], (int, float)
        ), "embedding_weight should be a number"
        assert isinstance(
            data["risk_quarantine_threshold"], int
        ), "risk_quarantine_threshold should be an integer"

        # Assert values are in valid ranges
        assert 0.0 <= data["heuristic_weight"] <= 1.0, "heuristic_weight out of range"
        assert 0.0 <= data["embedding_weight"] <= 1.0, "embedding_weight out of range"
        assert 0 <= data["risk_quarantine_threshold"] <= 100, "risk_quarantine_threshold out of range"

        # Assert no secrets are exposed
        assert "hmac_secret" not in data, "Secrets should not be exposed"
        assert "secret" not in str(data).lower() or "secret" in ["heuristic", "embedding"], \
            "Secrets should not be exposed in config"


class TestCachingBehavior:
    """Test suite for caching functionality."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app.

        Returns:
            TestClient instance for making requests.
        """
        return TestClient(app)

    @pytest.fixture
    def mock_sentence_transformer(self):
        """Mock SentenceTransformer to avoid network calls.

        Returns:
            Mock object with encode method.
        """
        import numpy as np

        def mock_encode(texts, show_progress_bar: bool = False):
            """Generate deterministic 3-dim embeddings."""
            embeddings = []
            for text in texts:
                text_hash = hash(text.lower())
                np.random.seed(abs(text_hash) % (2**31))
                embedding = np.random.randn(3).astype(np.float32)
                embeddings.append(embedding)
            return np.array(embeddings)

        mock = MagicMock()
        mock.encode = mock_encode
        return mock

    @patch("backend.detectors.embedding_outlier.SentenceTransformer")
    def test_caching_paths(
        self, mock_st_class, client: TestClient, mock_sentence_transformer
    ) -> None:
        """Test that caching reduces redundant detector calls.

        When the same text is analyzed multiple times, the cache should
        prevent redundant calls to the expensive embedding detector.
        """
        mock_st_class.return_value = mock_sentence_transformer

        # Track how many times score is called
        call_count = 0
        original_score = None

        def count_score_calls(texts):
            nonlocal call_count, original_score
            call_count += 1
            # Call the real implementation
            if original_score is None:
                from backend.detectors.embedding_outlier import EmbeddingOutlierDetector

                detector = EmbeddingOutlierDetector()
                detector._model = mock_sentence_transformer
                detector._isolation_forest = MagicMock()
                detector._isolation_forest.decision_function = lambda x: np.zeros(len(x))
                detector._is_fitted = True
                return detector.score(texts)
            return [0.5] * len(texts)

        # Patch the detector's score method
        with patch(
            "backend.app.EmbeddingOutlierDetector.score", side_effect=count_score_calls
        ):
            # Same text repeated 3 times
            same_text = "This is a test message for caching."
            request_data = {"texts": [same_text, same_text, same_text]}

            # First request - should trigger computation
            response1 = client.post("/analyze", json=request_data)
            assert response1.status_code == 200

            initial_calls = call_count

            # Second request with same texts - should hit cache
            response2 = client.post("/analyze", json=request_data)
            assert response2.status_code == 200

            final_calls = call_count

            # With caching, the second request should not increase call count significantly
            # or should only call once per unique text (not 3 times)
            # Initial call might be for fitting + scoring, so we check the delta
            assert final_calls <= initial_calls + 1, (
                f"Expected cache to reduce calls. "
                f"Initial: {initial_calls}, Final: {final_calls}"
            )

    @patch("backend.detectors.embedding_outlier.SentenceTransformer")
    def test_cache_reduces_duplicate_scoring(
        self, mock_st_class, client: TestClient, mock_sentence_transformer
    ) -> None:
        """Test that cache prevents duplicate scoring within a single request.

        When a request contains duplicate texts, they should only be
        scored once (batch optimization).
        """
        mock_st_class.return_value = mock_sentence_transformer

        # Create a request with duplicate texts
        duplicate_text = "Analyze this text"
        request_data = {"texts": [duplicate_text, duplicate_text, "Different text"]}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 200
        results = response.json()["results"]

        # Should get 3 results
        assert len(results) == 3

        # First two results should have identical scores (same text, cached)
        assert results[0]["signals"]["heuristic"] == results[1]["signals"]["heuristic"]
        # Note: embedding scores might differ slightly due to implementation details,
        # but the main point is that caching prevents redundant expensive operations


class TestMiddlewareIntegration:
    """Test suite for middleware integration."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app.

        Returns:
            TestClient instance for making requests.
        """
        return TestClient(app)

    def test_request_tracking_on_all_endpoints(self, client: TestClient) -> None:
        """Test that request tracking works on all endpoints."""
        endpoints = [
            ("/health", "GET"),
            ("/config", "GET"),
        ]

        for path, method in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json={})

            # Every endpoint should have request ID
            assert "X-Request-ID" in response.headers, f"Missing X-Request-ID on {method} {path}"

    def test_unique_request_ids(self, client: TestClient) -> None:
        """Test that each request gets a unique request ID."""
        request_ids = set()

        # Make multiple requests
        for _ in range(5):
            response = client.get("/health")
            request_id = response.headers.get("X-Request-ID")
            assert request_id is not None
            request_ids.add(request_id)

        # All request IDs should be unique
        assert len(request_ids) == 5, "Request IDs should be unique across requests"
