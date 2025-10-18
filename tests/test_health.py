"""Tests for FastAPI health endpoint.

These tests verify the /health endpoint using TestClient.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import app


class TestHealthEndpoint:
    """Test suite for /health endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app.

        Returns:
            TestClient instance for making requests.
        """
        return TestClient(app)

    def test_health_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that /health endpoint returns 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_response_structure(self, client: TestClient) -> None:
        """Test that /health response has correct structure."""
        response = client.get("/health")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "uptime_seconds" in data
        assert "python_version" in data
        assert "installed" in data

    def test_health_endpoint_status_ok(self, client: TestClient) -> None:
        """Test that /health returns status 'ok'."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "ok"

    def test_health_endpoint_uptime_positive(self, client: TestClient) -> None:
        """Test that uptime_seconds is a positive number."""
        response = client.get("/health")
        data = response.json()

        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_health_endpoint_python_version_format(self, client: TestClient) -> None:
        """Test that python_version has correct format."""
        response = client.get("/health")
        data = response.json()

        python_version = data["python_version"]
        assert isinstance(python_version, str)

        # Should be in format like "3.10.8"
        parts = python_version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_health_endpoint_installed_packages(self, client: TestClient) -> None:
        """Test that installed packages list is present."""
        response = client.get("/health")
        data = response.json()

        installed = data["installed"]
        assert isinstance(installed, list)
        assert len(installed) > 0

        # Check for expected packages
        expected_packages = [
            "fastapi",
            "uvicorn",
            "sentence-transformers",
            "scikit-learn",
            "streamlit",
        ]

        for package in expected_packages:
            assert package in installed

    def test_health_endpoint_multiple_calls(self, client: TestClient) -> None:
        """Test that multiple calls to /health work correctly."""
        response1 = client.get("/health")
        response2 = client.get("/health")

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Uptime should increase between calls
        uptime1 = response1.json()["uptime_seconds"]
        uptime2 = response2.json()["uptime_seconds"]
        assert uptime2 >= uptime1

    def test_health_endpoint_response_schema(self, client: TestClient) -> None:
        """Test that response matches the HealthResponse schema."""
        response = client.get("/health")
        data = response.json()

        # Validate types
        assert isinstance(data["status"], str)
        assert isinstance(data["uptime_seconds"], (int, float))
        assert isinstance(data["python_version"], str)
        assert isinstance(data["installed"], list)

        # Validate list contents
        for package in data["installed"]:
            assert isinstance(package, str)
