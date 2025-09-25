"""
Tests for analysis endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json


class TestAnalysisEndpoints:
    """Test analysis CRUD endpoints"""

    @pytest.mark.integration
    def test_get_empty_analysis_list(self, client: TestClient, auth_headers):
        """Test getting empty analysis list"""
        response = client.get("/api/analysis/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.integration
    def test_get_analysis_list_unauthorized(self, client: TestClient):
        """Test getting analysis list without authentication"""
        response = client.get("/api/analysis/")

        assert response.status_code == 401

    @pytest.mark.integration
    def test_get_nonexistent_analysis(self, client: TestClient, auth_headers):
        """Test getting non-existent analysis by ID"""
        fake_id = "nonexistent-analysis-id"
        response = client.get(f"/api/analysis/{fake_id}", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()

        assert "detail" in data
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.integration
    def test_delete_nonexistent_analysis(self, client: TestClient, auth_headers):
        """Test deleting non-existent analysis"""
        fake_id = "nonexistent-analysis-id"
        response = client.delete(f"/api/analysis/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.integration
    def test_delete_analysis_unauthorized(self, client: TestClient):
        """Test deleting analysis without authentication"""
        fake_id = "some-analysis-id"
        response = client.delete(f"/api/analysis/{fake_id}")

        assert response.status_code == 401


class TestAnalysisUpload:
    """Test image upload and analysis"""

    @pytest.mark.integration
    def test_upload_without_auth(self, client: TestClient, test_image_file):
        """Test uploading image without authentication"""
        response = client.post(
            "/api/analysis/",
            files={"file": test_image_file}
        )

        assert response.status_code == 401

    @pytest.mark.integration
    def test_upload_invalid_file_type(self, client: TestClient, auth_headers, invalid_file):
        """Test uploading non-image file"""
        response = client.post(
            "/api/analysis/",
            headers=auth_headers,
            files={"file": invalid_file}
        )

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        assert "imagen" in data["detail"].lower()

    @pytest.mark.integration
    def test_upload_missing_file(self, client: TestClient, auth_headers):
        """Test uploading without file"""
        response = client.post(
            "/api/analysis/",
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @patch('services.ai_service.FacialAnalysisService.analyze_facial_attractiveness')
    @patch('services.image_service.ImageProcessingService.process_image')
    def test_upload_valid_image_mock(
        self,
        mock_process_image,
        mock_analyze,
        client: TestClient,
        auth_headers,
        test_image_file,
        mock_analysis_result
    ):
        """Test uploading valid image with mocked services"""
        # Setup mocks
        mock_process_image.return_value = b"processed_image_data"
        mock_analyze.return_value = mock_analysis_result

        response = client.post(
            "/api/analysis/",
            headers=auth_headers,
            files={"file": test_image_file}
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        required_fields = [
            "id", "status", "overall_score", "detailed_scores",
            "scientific_explanation", "recommendations", "analysis_date"
        ]

        for field in required_fields:
            assert field in data

        # Check detailed scores structure
        detailed_scores = data["detailed_scores"]
        expected_detailed_keys = ["symmetry", "proportions", "skin_quality", "features_harmony"]

        for key in expected_detailed_keys:
            assert key in detailed_scores
            assert isinstance(detailed_scores[key], (int, float))

        # Check additional scores if present
        if "additional_scores" in data and data["additional_scores"]:
            additional_scores = data["additional_scores"]
            assert isinstance(additional_scores, dict)

        # Verify mocks were called
        mock_process_image.assert_called_once()
        mock_analyze.assert_called_once()

    @pytest.mark.integration
    @patch('services.ai_service.FacialAnalysisService.analyze_facial_attractiveness')
    def test_upload_ai_service_error(
        self,
        mock_analyze,
        client: TestClient,
        auth_headers,
        test_image_file
    ):
        """Test handling of AI service error"""
        # Make AI service raise an exception
        mock_analyze.side_effect = Exception("AI service error")

        response = client.post(
            "/api/analysis/",
            headers=auth_headers,
            files={"file": test_image_file}
        )

        assert response.status_code == 500
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"].lower()


class TestAnalysisWorkflow:
    """Test complete analysis workflow"""

    @pytest.mark.integration
    @patch('services.ai_service.FacialAnalysisService.analyze_facial_attractiveness')
    @patch('services.image_service.ImageProcessingService.process_image')
    def test_complete_analysis_workflow(
        self,
        mock_process_image,
        mock_analyze,
        client: TestClient,
        auth_headers,
        test_image_file,
        mock_analysis_result
    ):
        """Test complete workflow: upload, list, get, delete"""
        # Setup mocks
        mock_process_image.return_value = b"processed_image_data"
        mock_analyze.return_value = mock_analysis_result

        # 1. Upload analysis
        upload_response = client.post(
            "/api/analysis/",
            headers=auth_headers,
            files={"file": test_image_file}
        )

        assert upload_response.status_code == 200
        analysis_data = upload_response.json()
        analysis_id = analysis_data["id"]

        # 2. List analyses - should contain our analysis
        list_response = client.get("/api/analysis/", headers=auth_headers)

        assert list_response.status_code == 200
        analyses_list = list_response.json()

        assert len(analyses_list) == 1
        assert analyses_list[0]["id"] == analysis_id

        # 3. Get specific analysis
        get_response = client.get(f"/api/analysis/{analysis_id}", headers=auth_headers)

        assert get_response.status_code == 200
        retrieved_analysis = get_response.json()

        assert retrieved_analysis["id"] == analysis_id
        assert retrieved_analysis["overall_score"] == mock_analysis_result["overall_score"]

        # 4. Delete analysis
        delete_response = client.delete(f"/api/analysis/{analysis_id}", headers=auth_headers)

        assert delete_response.status_code == 200
        delete_data = delete_response.json()

        assert "message" in delete_data
        assert delete_data["id"] == analysis_id

        # 5. Verify analysis is deleted
        get_deleted_response = client.get(f"/api/analysis/{analysis_id}", headers=auth_headers)
        assert get_deleted_response.status_code == 404

        # 6. List should be empty again
        final_list_response = client.get("/api/analysis/", headers=auth_headers)
        assert final_list_response.status_code == 200
        final_list = final_list_response.json()
        assert len(final_list) == 0


class TestAnalysisValidation:
    """Test analysis data validation"""

    @pytest.mark.unit
    def test_analysis_response_structure(self, mock_analysis_result):
        """Test that mock analysis result has correct structure"""
        required_fields = [
            "status", "overall_score", "symmetry_score", "proportion_score",
            "skin_quality_score", "features_harmony_score",
            "scientific_explanation", "recommendations"
        ]

        for field in required_fields:
            assert field in mock_analysis_result

        # Test score ranges
        score_fields = [
            "overall_score", "symmetry_score", "proportion_score",
            "skin_quality_score", "features_harmony_score"
        ]

        for field in score_fields:
            score = mock_analysis_result[field]
            assert isinstance(score, (int, float))
            assert 0 <= score <= 10

        # Test status value
        valid_statuses = ["denied", "improvable", "feasible"]
        assert mock_analysis_result["status"] in valid_statuses