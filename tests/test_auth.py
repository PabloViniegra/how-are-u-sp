"""
Tests for API key authentication
"""

import pytest
import os
from fastapi.testclient import TestClient
from middleware.api_key_auth import APIKeyAuth


class TestAPIKeyAuth:
    """Test API key authentication functionality"""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_api_key_valid(self):
        """Test validation of valid API key"""
        # Test with known valid key from test environment
        api_keys = os.environ.get("VALID_API_KEYS", "")
        if api_keys:
            valid_key = api_keys.split(",")[0].strip()
            assert APIKeyAuth.validate_api_key(valid_key) is True
        else:
            pytest.skip("No VALID_API_KEYS environment variable set")

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_api_key_invalid(self):
        """Test validation of invalid API key"""
        invalid_key = "invalid_key_123456"
        assert APIKeyAuth.validate_api_key(invalid_key) is False

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_api_key_empty(self):
        """Test validation of empty API key"""
        assert APIKeyAuth.validate_api_key("") is False
        assert APIKeyAuth.validate_api_key(None) is False


class TestEndpointAuthentication:
    """Test endpoint authentication requirements"""

    @pytest.mark.auth
    def test_protected_endpoint_without_auth(self, client: TestClient):
        """Test protected endpoint without authentication"""
        response = client.get("/api/analysis/")

        assert response.status_code == 401
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "Authentication required"
        assert "code" in data["detail"]
        assert data["detail"]["code"] == "NO_AUTHENTICATION"

    @pytest.mark.auth
    def test_protected_endpoint_with_valid_x_api_key(self, client: TestClient, auth_headers):
        """Test protected endpoint with valid X-API-Key header"""
        response = client.get("/api/analysis/", headers=auth_headers)

        assert response.status_code == 200

    @pytest.mark.auth
    def test_protected_endpoint_with_valid_bearer_token(self, client: TestClient, bearer_auth_headers):
        """Test protected endpoint with valid Bearer token"""
        response = client.get("/api/analysis/", headers=bearer_auth_headers)

        assert response.status_code == 200

    @pytest.mark.auth
    def test_protected_endpoint_with_invalid_x_api_key(self, client: TestClient, invalid_api_key):
        """Test protected endpoint with invalid X-API-Key header"""
        headers = {"X-API-Key": invalid_api_key}
        response = client.get("/api/analysis/", headers=headers)

        assert response.status_code == 401
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "Invalid API key"
        assert data["detail"]["code"] == "INVALID_X_API_KEY"

    @pytest.mark.auth
    def test_protected_endpoint_with_invalid_bearer_token(self, client: TestClient, invalid_api_key):
        """Test protected endpoint with invalid Bearer token"""
        headers = {"Authorization": f"Bearer {invalid_api_key}"}
        response = client.get("/api/analysis/", headers=headers)

        assert response.status_code == 401
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "Invalid API key"
        assert data["detail"]["code"] == "INVALID_BEARER_TOKEN"

    @pytest.mark.auth
    def test_health_endpoint_no_auth_required(self, client: TestClient):
        """Test that health endpoint doesn't require authentication"""
        response = client.get("/api/health/")

        assert response.status_code == 200

    @pytest.mark.auth
    def test_root_endpoint_no_auth_required(self, client: TestClient):
        """Test that root endpoint doesn't require authentication"""
        response = client.get("/")

        assert response.status_code == 200

    @pytest.mark.auth
    def test_stats_endpoint_requires_auth(self, client: TestClient):
        """Test that stats endpoint requires authentication"""
        response = client.get("/api/stats/")

        assert response.status_code == 401

    @pytest.mark.auth
    def test_stats_endpoint_with_auth(self, client: TestClient, auth_headers):
        """Test stats endpoint with valid authentication"""
        response = client.get("/api/stats/", headers=auth_headers)

        assert response.status_code == 200


class TestAuthErrorMessages:
    """Test authentication error message details"""

    @pytest.mark.auth
    def test_no_auth_error_includes_examples(self, client: TestClient):
        """Test that no authentication error includes usage examples"""
        response = client.get("/api/analysis/")

        assert response.status_code == 401
        data = response.json()

        assert "examples" in data["detail"]
        examples = data["detail"]["examples"]
        assert "header" in examples
        assert "bearer" in examples
        assert "X-API-Key:" in examples["header"]
        assert "Authorization: Bearer" in examples["bearer"]

    @pytest.mark.auth
    def test_invalid_key_error_structure(self, client: TestClient):
        """Test invalid API key error structure"""
        headers = {"X-API-Key": "invalid_key"}
        response = client.get("/api/analysis/", headers=headers)

        assert response.status_code == 401
        data = response.json()

        required_fields = ["error", "message", "code"]
        for field in required_fields:
            assert field in data["detail"]

        assert data["detail"]["error"] == "Invalid API key"
        assert data["detail"]["code"] == "INVALID_X_API_KEY"