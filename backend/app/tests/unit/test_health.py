"""
Unit tests for health check and root endpoints.
Tests basic functionality without database dependencies.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for health check and system endpoints."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test that health endpoint returns 200 status."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_json(self, client: TestClient):
        """Test that health endpoint returns JSON."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_check_has_required_fields(self, client: TestClient):
        """Test that health endpoint returns required fields."""
        response = client.get("/health")
        data = response.json()
        
        # Check for actual fields returned by your API
        assert "status" in data
        assert "project" in data
        assert "version" in data
        assert "environment" in data
        assert data["status"] == "healthy"

    # Root endpoint tests
    def test_root_endpoint_returns_200(self, client: TestClient):
        """Test that root endpoint returns 200 status."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_returns_json(self, client: TestClient):
        """Test that root endpoint returns JSON."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"

    def test_root_endpoint_has_welcome_message(self, client: TestClient):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")
        data = response.json()
        
        # Check for actual fields returned by your API
        assert "message" in data
        assert "version" in data
        assert "docs" in data  # Changed from "links" to match actual response
        assert "health" in data
        assert "Welcome" in data["message"]

    # Documentation endpoints
    def test_api_docs_endpoint(self, client: TestClient):
        """Test that /docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        # Swagger UI returns HTML
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client: TestClient):
        """Test that /redoc endpoint is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
        # ReDoc returns HTML
        assert "text/html" in response.headers["content-type"]

    # Error handling tests
    def test_nonexistent_endpoint_returns_404(self, client: TestClient):
        """Test that nonexistent endpoint returns 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Check error response format
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "status_code" in data
        assert data["status_code"] == 404

    # Request ID tracking test
    def test_response_includes_request_id(self, client: TestClient):
        """Test that error responses include request_id for tracking."""
        response = client.get("/health")
        
        # For successful requests, check headers (if you add it there)
        # For now, just verify the endpoint works
        assert response.status_code == 200
        
        # Test with an error endpoint to verify request_id in error response
        error_response = client.get("/nonexistent")
        error_data = error_response.json()
        
        # Request ID should be in error responses
        assert "request_id" in error_data
        assert len(error_data["request_id"]) == 36  # UUID format
        assert error_data["request_id"].count("-") == 4  # UUID has 4 hyphens
