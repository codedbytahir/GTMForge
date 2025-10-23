"""
GTMForge Core Module
Contains orchestrator, base agent, schemas, and MCP integration.
"""

from app.core.base_agent import BaseAgent
from app.core.orchestrator import GTMForgeOrchestrator
from app.core.schemas import (
    StartupIdeaInput,
    IdeationOutput,
    ComparativeInsightOutput,
    PitchNarrativeOutput,
    PromptForgeOutput,
    QAValidationOutput,
    PublisherOutput,
    PipelineState
)
from app.core.mcp import MCPRegistry

__all__ = [
    "BaseAgent",
    "GTMForgeOrchestrator",
    "StartupIdeaInput",
    "IdeationOutput",
    "ComparativeInsightOutput",
    "PitchNarrativeOutput",
    "PromptForgeOutput",
    "QAValidationOutput",
    "PublisherOutput",
    "PipelineState",
    "MCPRegistry"
]