"""
Tests for configuration and dependencies
"""

import pytest
import os
from config import Settings
from dependencies import get_db


class TestSettings:
    """Test application settings and configuration"""

    @pytest.mark.unit
    def test_settings_default_values(self):
        """Test default configuration values"""
        settings = Settings()

        # Test default values
        assert settings.AI_MODEL_NAME == "gemini-1.5-flash"
        assert settings.AI_MAX_TOKENS == 2048
        assert settings.AI_TEMPERATURE == 0.1
        assert settings.DEBUG is True
        assert settings.MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB

    @pytest.mark.unit
    def test_settings_allowed_image_types(self):
        """Test allowed image types configuration"""
        settings = Settings()

        expected_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        assert settings.ALLOWED_IMAGE_TYPES == expected_types

    @pytest.mark.unit
    def test_settings_allowed_origins(self):
        """Test CORS allowed origins configuration"""
        settings = Settings()

        expected_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
        assert settings.ALLOWED_ORIGINS == expected_origins

    @pytest.mark.unit
    def test_get_api_keys_list_empty(self):
        """Test API keys parsing when empty"""
        settings = Settings(VALID_API_KEYS="")

        api_keys = settings.get_api_keys_list()
        assert api_keys == []

    @pytest.mark.unit
    def test_get_api_keys_list_single(self):
        """Test API keys parsing with single key"""
        settings = Settings(VALID_API_KEYS="single_key_123")

        api_keys = settings.get_api_keys_list()
        assert api_keys == ["single_key_123"]

    @pytest.mark.unit
    def test_get_api_keys_list_multiple(self):
        """Test API keys parsing with multiple keys"""
        settings = Settings(VALID_API_KEYS="key1,key2,key3")

        api_keys = settings.get_api_keys_list()
        expected_keys = ["key1", "key2", "key3"]
        assert api_keys == expected_keys

    @pytest.mark.unit
    def test_get_api_keys_list_with_spaces(self):
        """Test API keys parsing with spaces around commas"""
        settings = Settings(VALID_API_KEYS="key1, key2 , key3  ,  key4")

        api_keys = settings.get_api_keys_list()
        expected_keys = ["key1", "key2", "key3", "key4"]
        assert api_keys == expected_keys

    @pytest.mark.unit
    def test_get_api_keys_list_with_empty_values(self):
        """Test API keys parsing with empty values between commas"""
        settings = Settings(VALID_API_KEYS="key1,,key2,,,key3")

        api_keys = settings.get_api_keys_list()
        expected_keys = ["key1", "key2", "key3"]
        assert api_keys == expected_keys

    @pytest.mark.unit
    def test_settings_database_url(self):
        """Test database URL configuration"""
        settings = Settings()

        # In test environment, DATABASE_URL is set to in-memory
        assert settings.DATABASE_URL == 'sqlite:///:memory:'

    @pytest.mark.unit
    def test_settings_database_url_default(self):
        """Test default database URL when not set in environment"""
        import os
        # Temporarily remove DATABASE_URL to test default
        original_url = os.environ.get('DATABASE_URL')
        if 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']

        try:
            settings = Settings()
            assert settings.DATABASE_URL == 'sqlite:///./facial_analysis.db'
        finally:
            # Restore original value
            if original_url:
                os.environ['DATABASE_URL'] = original_url

    @pytest.mark.unit
    def test_settings_environment_override(self):
        """Test that environment variables override defaults"""
        # This test relies on the test environment setup in conftest.py
        settings = Settings()

        # Check that test environment API keys are loaded
        api_keys = settings.get_api_keys_list()
        assert "test_key_123" in api_keys
        assert len(api_keys) >= 1


class TestDependencies:
    """Test application dependencies"""

    @pytest.mark.unit
    def test_get_db_dependency(self):
        """Test database dependency function"""
        # Test that get_db is a generator function
        db_generator = get_db()

        # Should be a generator
        assert hasattr(db_generator, '__next__')
        assert hasattr(db_generator, '__iter__')

        # Should be able to get a database session
        try:
            db_session = next(db_generator)
            assert db_session is not None

            # Should be able to close the generator
            db_generator.close()

        except StopIteration:
            # This is also acceptable for a generator
            pass

    @pytest.mark.unit
    def test_get_db_context_manager(self):
        """Test database dependency as context manager"""
        # Test the dependency in a way similar to how FastAPI uses it
        db_gen = get_db()

        try:
            db = next(db_gen)
            assert db is not None
            # Simulate some database operation
            # (In real tests, we would use the test database)

        except Exception as e:
            pytest.fail(f"Database dependency failed: {e}")

        finally:
            try:
                next(db_gen)
            except StopIteration:
                # Expected behavior when generator is exhausted
                pass


class TestEnvironmentHandling:
    """Test environment variable handling"""

    @pytest.mark.unit
    def test_missing_google_api_key(self):
        """Test behavior when Google AI API key is missing"""
        # Create settings without Google API key
        settings = Settings(GOOGLE_AI_API_KEY="")

        # Should not raise an error, but key should be empty
        assert settings.GOOGLE_AI_API_KEY == ""

    @pytest.mark.unit
    def test_env_file_configuration(self):
        """Test that settings can load from .env file"""
        settings = Settings()

        # Settings class should have env_file configuration
        assert hasattr(settings.Config, 'env_file')
        assert settings.Config.env_file == ".env"
        assert settings.Config.case_sensitive is True

    @pytest.mark.unit
    def test_settings_validation_types(self):
        """Test that settings have correct types"""
        settings = Settings()

        # Test integer types
        assert isinstance(settings.AI_MAX_TOKENS, int)
        assert isinstance(settings.MAX_FILE_SIZE, int)

        # Test float types
        assert isinstance(settings.AI_TEMPERATURE, float)

        # Test boolean types
        assert isinstance(settings.DEBUG, bool)

        # Test string types
        assert isinstance(settings.AI_MODEL_NAME, str)
        assert isinstance(settings.DATABASE_URL, str)

        # Test list types
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert isinstance(settings.ALLOWED_IMAGE_TYPES, list)


class TestConfigurationValidation:
    """Test configuration validation and constraints"""

    @pytest.mark.unit
    def test_ai_temperature_range(self):
        """Test AI temperature is within valid range"""
        settings = Settings()

        # Temperature should be between 0 and 1 for most AI models
        assert 0.0 <= settings.AI_TEMPERATURE <= 1.0

    @pytest.mark.unit
    def test_max_tokens_positive(self):
        """Test max tokens is positive"""
        settings = Settings()

        assert settings.AI_MAX_TOKENS > 0

    @pytest.mark.unit
    def test_max_file_size_reasonable(self):
        """Test max file size is reasonable"""
        settings = Settings()

        # Should be positive and not too large (less than 100MB)
        assert settings.MAX_FILE_SIZE > 0
        assert settings.MAX_FILE_SIZE <= 100 * 1024 * 1024

    @pytest.mark.unit
    def test_allowed_origins_format(self):
        """Test allowed origins have correct URL format"""
        settings = Settings()

        for origin in settings.ALLOWED_ORIGINS:
            assert isinstance(origin, str)
            assert origin.startswith("http://") or origin.startswith("https://")

    @pytest.mark.unit
    def test_allowed_image_types_format(self):
        """Test allowed image types have correct MIME format"""
        settings = Settings()

        for mime_type in settings.ALLOWED_IMAGE_TYPES:
            assert isinstance(mime_type, str)
            assert mime_type.startswith("image/")
            assert "/" in mime_type