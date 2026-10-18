"""Application configuration and environment settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """LinguaType application settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "LinguaType Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*",
    ]

    # LLM Provider: 'mock' for tests/offline development, 'gemini' for live production
    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # Auth: 'mock' for offline sandbox/tests, 'firebase' for real JWT verification
    AUTH_MODE: str = "mock"
    FIREBASE_PROJECT_ID: str = "linguatype-dev"

    # Latency SLAs (in milliseconds)
    SLA_TTFT_MS: float = 800.0
    SLA_INFERENCE_MS: float = 2500.0
    SLA_PIPELINE_MS: float = 3000.0

    # Operational limits
    MAX_TEXT_LENGTH: int = 1000
    SESSION_EXPIRY_HOURS: int = 24


settings = Settings()
