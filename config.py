from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


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
    APP_PORT: int = int(os.environ.get("PORT", 8000))
    DEBUG: bool = True
    
    # Video Sources
    WEBCAM_INDEX: int = 0
    VIDEO_UPLOAD_DIR: str = "./uploads/videos"
    
    # Feature Flags
    DISABLE_CV: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        # If DATABASE_URL env var is set (e.g. on Render), use it
        import os
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
            
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Global settings instance
settings = Settings()
