from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    """

    GOOGLE_AI_API_KEY: str = ''

    DATABASE_URL: str = 'sqlite:///./facial_analysis.db'

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://how-are-u.netlify.app"
    ]

    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    ]

    AI_MODEL_NAME: str = "gemini-1.5-flash"
    AI_MAX_TOKENS: int = 2048
    AI_TEMPERATURE: float = 0.1

    DEBUG: bool = True

    # API Keys válidas (string separado por comas)
    VALID_API_KEYS: str = ""

    def get_api_keys_list(self) -> List[str]:
        """Convierte el string de API keys a lista"""
        if not self.VALID_API_KEYS:
            return []
        return [key.strip() for key in self.VALID_API_KEYS.split(',') if key.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
