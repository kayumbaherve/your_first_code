"""
Configuration settings for the AI Interior Design Assistant
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Interior Design Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://interior_user:interior_pass@localhost:5432/interior_design_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
    ALLOWED_3D_EXTENSIONS: List[str] = [".obj", ".fbx", ".gltf", ".glb", ".dae"]
    
    # AI Models
    MODEL_DIR: str = "models"
    ROOM_ANALYSIS_MODEL: str = "room_analysis_v1.pkl"
    STYLE_CLASSIFICATION_MODEL: str = "style_classifier_v1.pkl"
    FURNITURE_RECOMMENDATION_MODEL: str = "furniture_recommender_v1.pkl"
    
    # Computer Vision
    CV_CONFIDENCE_THRESHOLD: float = 0.5
    CV_NMS_THRESHOLD: float = 0.4
    
    # 3D Visualization
    DEFAULT_ROOM_HEIGHT: float = 2.7  # meters
    MAX_ROOM_SIZE: float = 50.0  # meters
    
    # Virtual Staging
    STAGING_QUALITY: str = "high"  # low, medium, high
    MAX_STAGING_OBJECTS: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # External APIs
    FURNITURE_API_KEY: str = ""
    TEXTURE_API_KEY: str = ""
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

