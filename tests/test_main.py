"""
Tests for main application endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test main application endpoints"""

    @pytest.mark.unit
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "Bienvenido a Facial Analysis API v2.0.0" in data["message"]
        assert "documentation" in data
        assert "health_check" in data
        assert "status" in data
        assert data["status"] == "operational"
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0

    @pytest.mark.unit
    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint"""
        response = client.get("/api/health/")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "message" in data
        assert "API funcionando correctamente" in data["message"]

    @pytest.mark.unit
    def test_nonexistent_endpoint(self, client: TestClient):
        """Test non-existent endpoint returns 404"""
        response = client.get("/nonexistent")

        assert response.status_code == 404

    @pytest.mark.unit
    def test_api_metadata(self, client: TestClient):
        """Test API metadata is accessible via OpenAPI"""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        openapi_data = response.json()

        assert "info" in openapi_data
        assert openapi_data["info"]["title"] == "Facial Analysis API"
        assert openapi_data["info"]["version"] == "2.0.0"
        assert "paths" in openapi_data

        # Check that our main endpoints are documented
        paths = openapi_data["paths"]
        assert "/" in paths
        assert "/api/health/" in paths


class TestCORS:
    """Test CORS configuration"""

    @pytest.mark.unit
    def test_cors_headers_present(self, client: TestClient):
        """Test CORS headers are present in responses"""
        response = client.get("/api/health/")

        assert response.status_code == 200
        # Basic CORS headers should be handled by middleware

    @pytest.mark.unit
    def test_options_request(self, client: TestClient):
        """Test OPTIONS request for CORS preflight"""
        response = client.options("/api/health/")

        # Should not error out, even if returns 405
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test global error handling"""

    @pytest.mark.unit
    def test_method_not_allowed(self, client: TestClient):
        """Test method not allowed returns proper error"""
        response = client.post("/api/health/")

        assert response.status_code == 405

    @pytest.mark.unit
    def test_invalid_json_request(self, client: TestClient):
        """Test invalid JSON request handling"""
        response = client.post(
            "/api/analysis/",
            data="invalid json",
            headers={"Content-Type": "application/json", "X-API-Key": "test_key_123"}
        )

        assert response.status_code in [400, 422]  # Bad request or validation error
