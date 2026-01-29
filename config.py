from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_NAME: str = "supabase11"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "0155"
    DB_PORT: int = 5432
    
    # Groq API Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Application Configuration
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # Video Sources
    WEBCAM_INDEX: int = 0
    VIDEO_UPLOAD_DIR: str = "./uploads/videos"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Global settings instance
settings = Settings()
