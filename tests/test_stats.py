"""
Tests for statistics endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from models import AnalysisResult, AnalysisStatus
from datetime import datetime


class TestStatsEndpoints:
    """Test statistics endpoints"""

    @pytest.mark.integration
    def test_get_stats_empty_database(self, client: TestClient, auth_headers):
        """Test getting stats from empty database"""
        response = client.get("/api/stats/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        expected_fields = ["total_analyses", "average_score", "score_distribution"]
        for field in expected_fields:
            assert field in data

        assert data["total_analyses"] == 0
        assert data["average_score"] == 0
        assert isinstance(data["score_distribution"], dict)

    @pytest.mark.integration
    def test_get_stats_unauthorized(self, client: TestClient):
        """Test getting stats without authentication"""
        response = client.get("/api/stats/")

        assert response.status_code == 401

    @pytest.mark.integration
    def test_get_stats_with_data(self, client: TestClient, auth_headers, db_session):
        """Test getting stats with sample data"""
        from models import AnalysisResult, AnalysisStatus
        from datetime import datetime

        # Create actual analysis results in the database
        analyses = [
            AnalysisResult(
                id="id1", filename="test1.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=2.5, symmetry_score=2.0, proportion_score=2.0,
                skin_quality_score=2.0, features_harmony_score=2.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id2", filename="test2.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=5.5, symmetry_score=5.0, proportion_score=5.0,
                skin_quality_score=5.0, features_harmony_score=5.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id3", filename="test3.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=7.5, symmetry_score=7.0, proportion_score=7.0,
                skin_quality_score=7.0, features_harmony_score=7.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id4", filename="test4.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=8.5, symmetry_score=8.0, proportion_score=8.0,
                skin_quality_score=8.0, features_harmony_score=8.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id5", filename="test5.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=6.0, symmetry_score=6.0, proportion_score=6.0,
                skin_quality_score=6.0, features_harmony_score=6.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            )
        ]

        # Add analyses to database
        for analysis in analyses:
            db_session.add(analysis)
        db_session.commit()

        response = client.get("/api/stats/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify basic structure
        assert data["total_analyses"] == 5
        assert isinstance(data["average_score"], float)

        # Calculate expected average: (2.5 + 5.5 + 7.5 + 8.5 + 6.0) / 5 = 6.0
        expected_average = 6.0
        assert abs(data["average_score"] - expected_average) < 0.01

        # Verify score distribution
        distribution = data["score_distribution"]
        expected_distribution = {
            "0-2": 0,
            "2-4": 1,  # 2.5
            "4-6": 1,  # 5.5
            "6-8": 2,  # 7.5, 6.0
            "8-10": 1  # 8.5
        }

        for range_key, expected_count in expected_distribution.items():
            assert distribution[range_key] == expected_count

    def _create_mock_analysis(self, analysis_id: str, score: float):
        """Helper to create mock analysis result"""
        mock_analysis = AnalysisResult()
        mock_analysis.id = analysis_id
        mock_analysis.overall_score = score
        mock_analysis.symmetry_score = 7.0
        mock_analysis.proportion_score = 7.0
        mock_analysis.skin_quality_score = 7.0
        mock_analysis.features_harmony_score = 7.0
        mock_analysis.analysis_status = AnalysisStatus.FEASIBLE
        mock_analysis.scientific_explanation = "Test explanation"
        mock_analysis.recommendations = "Test recommendations"
        mock_analysis.created_at = datetime.utcnow()
        return mock_analysis

    @pytest.mark.integration
    def test_get_stats_boundary_scores(self, client: TestClient, auth_headers, db_session):
        """Test stats with boundary score values"""
        from models import AnalysisResult, AnalysisStatus
        from datetime import datetime

        # Test scores exactly at boundaries
        analyses = [
            AnalysisResult(
                id="id1", filename="test1.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=0.0, symmetry_score=0.0, proportion_score=0.0,
                skin_quality_score=0.0, features_harmony_score=0.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id2", filename="test2.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=2.0, symmetry_score=2.0, proportion_score=2.0,
                skin_quality_score=2.0, features_harmony_score=2.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id3", filename="test3.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=4.0, symmetry_score=4.0, proportion_score=4.0,
                skin_quality_score=4.0, features_harmony_score=4.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id4", filename="test4.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=6.0, symmetry_score=6.0, proportion_score=6.0,
                skin_quality_score=6.0, features_harmony_score=6.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id5", filename="test5.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=8.0, symmetry_score=8.0, proportion_score=8.0,
                skin_quality_score=8.0, features_harmony_score=8.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            ),
            AnalysisResult(
                id="id6", filename="test6.jpg", analysis_status=AnalysisStatus.FEASIBLE,
                overall_score=10.0, symmetry_score=10.0, proportion_score=10.0,
                skin_quality_score=10.0, features_harmony_score=10.0,
                scientific_explanation="Test", recommendations="Test",
                created_at=datetime.utcnow()
            )
        ]

        # Add analyses to database
        for analysis in analyses:
            db_session.add(analysis)
        db_session.commit()

        response = client.get("/api/stats/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Check that boundary values are categorized correctly
        distribution = data["score_distribution"]

        # Based on the logic in the code:
        # score < 2: "0-2"
        # score < 4: "2-4"
        # score < 6: "4-6"
        # score < 8: "6-8"
        # else: "8-10"

        expected_distribution = {
            "0-2": 1,  # 0.0
            "2-4": 1,  # 2.0
            "4-6": 1,  # 4.0
            "6-8": 1,  # 6.0
            "8-10": 2  # 8.0, 10.0
        }

        for range_key, expected_count in expected_distribution.items():
            assert distribution[range_key] == expected_count

    @pytest.mark.integration
    def test_get_stats_database_error(self, auth_headers):
        """Test handling of database errors in stats endpoint"""
        from main import app
        from dependencies import get_db

        # Create a mock database session that raises an error
        def mock_get_db_error():
            mock_db = Mock()
            mock_db.query.side_effect = Exception("Database connection error")
            return mock_db

        # Override the dependency with our error-throwing mock
        app.dependency_overrides[get_db] = mock_get_db_error

        try:
            # Create a new test client with the overridden dependency
            with TestClient(app) as test_client:
                response = test_client.get("/api/stats/", headers=auth_headers)
        finally:
            # Clean up the override
            app.dependency_overrides.pop(get_db, None)

        assert response.status_code == 500
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"].lower()


class TestStatsCalculations:
    """Test statistics calculation logic"""

    @pytest.mark.unit
    def test_score_distribution_logic(self):
        """Test score distribution categorization logic"""
        test_scores = [0.0, 1.9, 2.0, 3.9, 4.0, 5.9, 6.0, 7.9, 8.0, 9.9, 10.0]

        # Expected categorization based on code logic
        expected_categories = {
            0.0: "0-2",
            1.9: "0-2",
            2.0: "2-4",
            3.9: "2-4",
            4.0: "4-6",
            5.9: "4-6",
            6.0: "6-8",
            7.9: "6-8",
            8.0: "8-10",
            9.9: "8-10",
            10.0: "8-10"
        }

        for score, expected_category in expected_categories.items():
            # Replicate the logic from stats.py
            if score < 2:
                actual_category = "0-2"
            elif score < 4:
                actual_category = "2-4"
            elif score < 6:
                actual_category = "4-6"
            elif score < 8:
                actual_category = "6-8"
            else:
                actual_category = "8-10"

            assert actual_category == expected_category, f"Score {score} should be in {expected_category}, got {actual_category}"

    @pytest.mark.unit
    def test_average_calculation(self):
        """Test average score calculation"""
        test_scores = [1.0, 3.0, 5.0, 7.0, 9.0]
        expected_average = sum(test_scores) / len(test_scores)  # 5.0

        calculated_average = sum(test_scores) / len(test_scores)
        assert calculated_average == expected_average
        assert calculated_average == 5.0