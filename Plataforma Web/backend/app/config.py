"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/bim_fm_platform"
    
    # File uploads
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AI Model
    AI_MODEL_PATH: str = "../PonteInspecao.lib/best_deeplab_lr0.0001_bs4_fold2.pth"
    AI_IMAGE_SIZE: int = 512
    AI_THRESHOLD: float = 0.30
    
    # IFC Processing
    IFC_CACHE_DIR: Path = Path("cache/ifc")
    
    # JWT (if needed)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

