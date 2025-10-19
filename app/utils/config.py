"""
GTMForge Configuration Management
Loads and validates environment variables and configuration settings.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class GeminiConfig(BaseModel):
    """Gemini API configuration"""
    api_key: str = Field(..., description="Gemini API key")
    pro_key: Optional[str] = Field(None, description="Gemini Pro API key")
    flash_key: Optional[str] = Field(None, description="Gemini Flash API key")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or v.startswith("your-") or v.startswith("YOUR_"):
            raise ValueError("Gemini API key not configured. Check your .env file.")
        return v


class VertexAIConfig(BaseModel):
    """Vertex AI configuration"""
    project_id: str = Field(..., description="GCP project ID")
    location: str = Field(default="us-central1", description="Vertex AI location")
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if not v or v.startswith("your-"):
            raise ValueError("GCP project ID not configured. Check your .env file.")
        return v


class ImagenConfig(BaseModel):
    """Imagen configuration"""
    model: str = Field(default="imagegeneration@006", description="Imagen model version")
    project_id: str = Field(..., description="GCP project ID for Imagen")


class VeoConfig(BaseModel):
    """Veo configuration"""
    model: str = Field(default="veo-3.1", description="Veo model version")
    project_id: str = Field(..., description="GCP project ID for Veo")


class StorageConfig(BaseModel):
    """Google Cloud Storage configuration"""
    bucket_name: str = Field(..., description="GCS bucket name")
    bucket_region: str = Field(default="us-central1", description="GCS bucket region")
    credentials_path: Optional[str] = Field(None, description="Path to service account credentials")


class CanvaConfig(BaseModel):
    """Canva API configuration (Phase 2+)"""
    client_id: Optional[str] = Field(None, description="Canva client ID")
    client_secret: Optional[str] = Field(None, description="Canva client secret")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class ADKConfig(BaseModel):
    """Agent Development Kit configuration"""
    log_level: str = Field(default="INFO", description="ADK log level")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    timeout_seconds: int = Field(default=60, description="Request timeout in seconds")


class AppConfig(BaseModel):
    """Application-wide configuration"""
    env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode enabled")
    log_level: str = Field(default="INFO", description="Application log level")


class GTMForgeConfig(BaseModel):
    """
    Complete GTMForge configuration.
    Loads all settings from environment variables.
    """
    gemini: GeminiConfig
    vertex_ai: VertexAIConfig
    imagen: ImagenConfig
    veo: VeoConfig
    storage: StorageConfig
    canva: CanvaConfig
    adk: ADKConfig
    app: AppConfig
    
    @classmethod
    def load_from_env(cls) -> "GTMForgeConfig":
        """
        Load configuration from environment variables.
        
        Returns:
            Validated GTMForgeConfig instance
            
        Raises:
            ValidationError: If required configuration is missing or invalid
        """
        try:
            config = cls(
                gemini=GeminiConfig(
                    api_key=os.getenv("GEMINI_API_KEY", ""),
                    pro_key=os.getenv("GEMINI_PRO_KEY"),
                    flash_key=os.getenv("GEMINI_FLASH_KEY"),
                ),
                vertex_ai=VertexAIConfig(
                    project_id=os.getenv("GCP_PROJECT_ID", ""),
                    location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
                ),
                imagen=ImagenConfig(
                    model=os.getenv("IMAGEN_MODEL", "imagegeneration@006"),
                    project_id=os.getenv("IMAGEN_PROJECT_ID", os.getenv("GCP_PROJECT_ID", "")),
                ),
                veo=VeoConfig(
                    model=os.getenv("VEO_MODEL", "veo-3.1"),
                    project_id=os.getenv("VEO_PROJECT_ID", os.getenv("GCP_PROJECT_ID", "")),
                ),
                storage=StorageConfig(
                    bucket_name=os.getenv("GCS_BUCKET_NAME", "gtmforge-assets"),
                    bucket_region=os.getenv("GCS_BUCKET_REGION", "us-central1"),
                    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                ),
                canva=CanvaConfig(
                    client_id=os.getenv("CANVA_CLIENT_ID"),
                    client_secret=os.getenv("CANVA_CLIENT_SECRET"),
                    redirect_uri=os.getenv("CANVA_REDIRECT_URI"),
                ),
                adk=ADKConfig(
                    log_level=os.getenv("ADK_LOG_LEVEL", "INFO"),
                    retry_attempts=int(os.getenv("ADK_RETRY_ATTEMPTS", "3")),
                    timeout_seconds=int(os.getenv("ADK_TIMEOUT_SECONDS", "60")),
                ),
                app=AppConfig(
                    env=os.getenv("APP_ENV", "development"),
                    debug=os.getenv("DEBUG", "True").lower() == "true",
                    log_level=os.getenv("LOG_LEVEL", "INFO"),
                ),
            )
            
            logger.info("configuration_loaded", env=config.app.env)
            return config
            
        except Exception as e:
            logger.error("configuration_load_failed", error=str(e))
            raise


# Global configuration instance
# This will be loaded once and reused throughout the application
_config: Optional[GTMForgeConfig] = None


def get_config() -> GTMForgeConfig:
    """
    Get the global configuration instance.
    Loads from environment on first call.
    
    Returns:
        GTMForgeConfig instance
    """
    global _config
    if _config is None:
        _config = GTMForgeConfig.load_from_env()
    return _config


def reload_config() -> GTMForgeConfig:
    """
    Force reload configuration from environment.
    Useful for testing or configuration updates.
    
    Returns:
        Fresh GTMForgeConfig instance
    """
    global _config
    _config = GTMForgeConfig.load_from_env()
    return _config