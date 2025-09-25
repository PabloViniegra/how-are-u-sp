"""
Shared test fixtures and configuration
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import io
from PIL import Image

from main import app
from database import Base, get_db
from dependencies import get_db as get_db_dependency
from config import settings, Settings


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependencies
app.dependency_overrides[get_db_dependency] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def valid_api_key():
    """Provide a valid API key for testing from environment"""
    api_keys = os.environ.get("VALID_API_KEYS", "")
    if api_keys:
        return api_keys.split(",")[0].strip()
    pytest.skip("No VALID_API_KEYS environment variable set")


@pytest.fixture
def invalid_api_key():
    """Provide an invalid API key for testing"""
    return "invalid_key_123"


@pytest.fixture
def auth_headers(valid_api_key):
    """Provide authentication headers"""
    return {"X-API-Key": valid_api_key}


@pytest.fixture
def bearer_auth_headers(valid_api_key):
    """Provide Bearer token authentication headers"""
    return {"Authorization": f"Bearer {valid_api_key}"}


@pytest.fixture
def test_image():
    """Create a test image file"""
    # Create a simple RGB image with valid size for analysis (minimum 200x200)
    img = Image.new('RGB', (400, 400), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def test_image_file(test_image):
    """Create a test image file for upload"""
    return ("test.jpg", test_image, "image/jpeg")


@pytest.fixture
def invalid_file():
    """Create an invalid file (not an image)"""
    content = b"This is not an image"
    return ("test.txt", io.BytesIO(content), "text/plain")


@pytest.fixture
def mock_analysis_result():
    """Mock analysis result from AI service"""
    return {
        "status": "feasible",
        "overall_score": 7.5,
        "symmetry_score": 8.0,
        "proportion_score": 7.2,
        "skin_quality_score": 7.8,
        "features_harmony_score": 7.0,
        "eye_appeal_score": 8.2,
        "nose_harmony_score": 7.5,
        "lip_aesthetics_score": 7.1,
        "jawline_definition_score": 6.8,
        "cheekbone_prominence_score": 7.3,
        "facial_composition_score": 7.6,
        "scientific_explanation": "Test explanation of facial analysis results.",
        "recommendations": "Test recommendations for improvement."
    }


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for database tests"""
    return {
        "id": "test-analysis-id-123",
        "filename": "test.jpg",
        "overall_score": 7.5,
        "symmetry_score": 8.0,
        "proportion_score": 7.2,
        "skin_quality_score": 7.8,
        "features_harmony_score": 7.0,
        "scientific_explanation": "Test explanation",
        "recommendations": "Test recommendations"
    }


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    original_env = os.environ.copy()
    original_valid_api_keys = settings.VALID_API_KEYS

    # Set test environment variables (use environment or default test keys)
    if "VALID_API_KEYS" not in os.environ:
        os.environ["VALID_API_KEYS"] = "test_key_123,test_key_456"
    os.environ["DEBUG"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    # Update settings with test values
    settings.VALID_API_KEYS = os.environ.get("VALID_API_KEYS", "test_key_123,test_key_456")

    yield

    # Restore original environment and settings
    os.environ.clear()
    os.environ.update(original_env)
    settings.VALID_API_KEYS = original_valid_api_keys