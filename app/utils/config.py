"""
GTMForge Configuration Management
Centralized configuration for paths, clients, and environment settings.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import structlog

logger = structlog.get_logger(__name__)

# Base directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Asset storage directories
ASSETS_DIR = OUTPUT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
VIDEOS_DIR = ASSETS_DIR / "videos"
DECKS_DIR = ASSETS_DIR / "decks"

# Ensure all directories exist
def ensure_directories():
    """Create all necessary directories"""
    for directory in [OUTPUT_DIR, LOGS_DIR, ASSETS_DIR, IMAGES_DIR, VIDEOS_DIR, DECKS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    logger.info("directories_ensured", directories=[
        str(OUTPUT_DIR),
        str(LOGS_DIR),
        str(ASSETS_DIR),
        str(IMAGES_DIR),
        str(VIDEOS_DIR),
        str(DECKS_DIR)
    ])

# Call on module load
ensure_directories()

class AssetPathManager:
    """Centralized asset path management"""
    
    @staticmethod
    def get_image_path(image_id: str, slide_number: int, iteration: int = 0) -> Path:
        """Get absolute path for an image file"""
        filename = f"imagen_slide_{slide_number}_{iteration}.png"
        return IMAGES_DIR / filename
    
    @staticmethod
    def get_video_path(video_id: str, iteration: int = 0) -> Path:
        """Get absolute path for a video file"""
        filename = f"{video_id}_{iteration}.mp4"
        return VIDEOS_DIR / filename
    
    @staticmethod
    def get_deck_path(deck_id: str) -> Path:
        """Get absolute path for a deck file"""
        filename = f"{deck_id}.pdf"
        return DECKS_DIR / filename
    
    @staticmethod
    def get_absolute_path(relative_path: str) -> Path:
        """Convert relative path to absolute"""
        if relative_path.startswith("/"):
            return Path(relative_path)
        return OUTPUT_DIR / relative_path.lstrip("./")
    
    @staticmethod
    def ensure_file_exists(path: Path, create_empty: bool = False) -> bool:
        """Check if file exists, optionally create empty file"""
        if path.exists():
            return True
        if create_empty:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            return True
        return False

# Google Cloud Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gtmforge-475520")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "gtmforge-assets")
GCS_LOCATION = os.getenv("GCS_LOCATION", "us-central1")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_LOG_FILES = int(os.getenv("MAX_LOG_FILES", "10"))
LOG_RETENTION_HOURS = int(os.getenv("LOG_RETENTION_HOURS", "24"))

# Task Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_BASE = float(os.getenv("RETRY_BACKOFF_BASE", "2.0"))
QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", "0.8"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "3600"))

logger.info(
    "config_loaded",
    project_root=str(PROJECT_ROOT),
    output_dir=str(OUTPUT_DIR),
    gcp_project=GCP_PROJECT_ID,
    gcs_bucket=GCS_BUCKET_NAME
)