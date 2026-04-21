"""
Configuration management for AfriConnect backend.
Uses Pydantic Settings to load environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name: Application name
        debug: Debug mode flag
        api_v1_str: API v1 prefix
        secret_key: Secret key for JWT encoding/decoding
        algorithm: JWT algorithm
        access_token_expire_minutes: JWT token expiration time
        database_url: Database connection string
    """
    
    # App Configuration
    app_name: str = "AfriConnect"
    debug: bool = False
    api_v1_str: str = "/api/v1"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database Configuration
    database_url: str = "sqlite:///./africonnect.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Caching prevents reloading environment variables.
    """
    return Settings()

# Create a global settings instance for easy import
settings = get_settings()
