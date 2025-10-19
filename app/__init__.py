"""
GTMForge Application Package
Multi-agent AI system for Go-To-Market automation.
"""

from app.core.orchestrator import GTMForgeOrchestrator
from app.core.schemas import StartupIdeaInput, PipelineState
from app.utils.config import get_config, GTMForgeConfig
from app.utils.logger import configure_logging, get_logger

__version__ = "1.0.0"
__author__ = "Daniel Efres"

__all__ = [
    "GTMForgeOrchestrator",
    "StartupIdeaInput",
    "PipelineState",
    "get_config",
    "GTMForgeConfig",
    "configure_logging",
    "get_logger"
]