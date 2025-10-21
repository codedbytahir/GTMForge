"""
GTMForge Application Package
Multi-agent AI system for Go-To-Market automation.
"""

from app.core.orchestrator import GTMForgeOrchestrator
from app.core.schemas import StartupIdeaInput, PipelineState
from app.utils.config import AssetPathManager
from app.utils.logger import setup_task_logging

__version__ = "1.0.0"
__author__ = "Daniel Efres"

__all__ = [
    "GTMForgeOrchestrator",
    "StartupIdeaInput",
    "PipelineState",
    "AssetPathManager",
    "setup_task_logging"
]