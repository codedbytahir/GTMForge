"""
GTMForge Orchestrator
Manages the multi-agent pipeline for GTM asset generation.
"""

import uuid
from datetime import datetime
from typing import Optional
import structlog

from app.core.schemas import (
    StartupIdeaInput,
    PipelineState,
    IdeationOutput,
    ComparativeInsightOutput,
    PitchNarrativeOutput,
    PromptForgeOutput,
    QAValidationOutput,
    MediaGenerationOutput,
    PublisherOutput
)
from app.core.mcp import MCPRegistry
from app.agents.ideation_agent.agent import IdeationAgent
from app.agents.comparative_insight_agent.agent import ComparativeInsightAgent
from app.agents.pitch_writer_agent.agent import PitchWriterAgent
from app.agents.prompt_forge_agent.agent import PromptForgeAgent
from app.agents.qa_agent.agent import QAAgent
from app.agents.imagen_agent.agent import ImagenAgent
from app.agents.veo_agent.agent import VeoAgent
from app.agents.canva_agent.agent import CanvaAgent
from app.agents.publisher_agent.agent import PublisherAgent


class GTMForgeOrchestrator:
    """
    GTMForge Orchestrator manages the complete multi-agent pipeline.
    
    Phase 1 Pipeline Flow (Sequential):
    1. Ideation Agent: Expand idea into ICPs and market context
    2. Comparative Insight Agent: Benchmark vs. successful startups
    3. Pitch Writer Agent: Create slide-by-slide narrative
    4. Prompt Forge Agent: Generate Imagen/Veo prompts (with loop refinement)
    5. QA Agent: Validate all content and assets
    
    Phase 2 Pipeline Extension (Media Generation):
    6. Media Generation Stage (sequential):
       - Imagen Agent: Generate images from prompts
       - Veo Agent: Generate video trailer from images
       - Canva Agent: Create pitch deck with images
    7. Publisher Agent: Publish to GCS and Canva (Phase 3)
    
    Execution Patterns:
    - Sequential: All stages run sequentially
    - Refinement Loops: Imagen/Veo retry if quality below threshold
    - Asset Aggregation: Media stage builds manifest of all assets
    
    Phase 2: Sequential media generation with mock API calls
    Phase 3: Full GCS upload and Canva Connect integration
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents and services."""
        self.logger = structlog.get_logger(__name__)
        
        # Phase 1 agents
        self.ideation_agent = IdeationAgent()
        self.comparative_agent = ComparativeInsightAgent()
        self.pitch_writer = PitchWriterAgent()
        self.prompt_forge = PromptForgeAgent(max_refinement_cycles=3)
        self.qa_agent = QAAgent()
        
        # Phase 2 media agents
        self.imagen_agent = ImagenAgent(quality_threshold=0.85, max_retries=3)
        self.veo_agent = VeoAgent(quality_threshold=0.80, max_retries=2)
        self.canva_agent = CanvaAgent(theme="dark_steel_tech_blue")
        
        # Phase 3 publisher
        self.publisher_agent = PublisherAgent()
        
        # Initialize MCP registry
        self.mcp_registry = MCPRegistry()
        
        # Session tracking
        self._current_session: Optional[str] = None
        self._pipeline_state: Optional[PipelineState] = None
        
        self.logger.info(
            "orchestrator_initialized",
            agents=[
                self.ideation_agent.name,
                self.comparative_agent.name,
                self.pitch_writer.name,
                self.prompt_forge.name,
                self.qa_agent.name,
                self.imagen_agent.name,
                self.veo_agent.name,
                self.canva_agent.name,
                self.publisher_agent.name
            ]
        )
    
    async def initialize(self) -> None:
        """
        Initialize orchestrator services (MCP connections, etc.).
        Call this before running the pipeline.
        """
        self.logger.info("orchestrator_initializing")
        
        # Initialize MCP registry
        await self.mcp_registry.initialize()
        
        self.logger.info("orchestrator_initialized_complete")
    
    async def run_pipeline(
        self,
        startup_idea: StartupIdeaInput,
        session_id: Optional[str] = None
    ) -> PipelineState:
        """
        Execute the complete GTMForge pipeline.
        
        Args:
            startup_idea: Initial startup idea input
            session_id: Optional session ID for tracking (generated if not provided)
            
        Returns:
            Complete pipeline state with all agent outputs
        """
        # Create session
        session_id = session_id or f"session_{uuid.uuid4().hex[:12]}"
        self._current_session = session_id
        
        # Initialize pipeline state
        self._pipeline_state = PipelineState(
            session_id=session_id,
            input_data=startup_idea,
            current_stage="initialized"
        )
        
        self.logger.info(
            "pipeline_started",
            session_id=session_id,
            idea_preview=startup_idea.idea[:100]
        )
        
        try:
            # Stage 1: Ideation
            await self._run_ideation_stage()
            
            # Stage 2: Comparative Insight
            await self._run_comparative_stage()
            
            # Stage 3: Pitch Writing
            await self._run_pitch_writing_stage()
            
            # Stage 4: Prompt Forge (with loop refinement)
            await self._run_prompt_forge_stage()
            
            # Stage 5: QA Validation
            await self._run_qa_stage()
            
            # Stage 6: Media Generation
            await self._run_media_generation_stage()
            
            # Stage 7: Publisher (Phase 3)
            await self._run_publisher_stage()
            
            # Mark pipeline as completed
            self._pipeline_state.current_stage = "completed"
            self._pipeline_state.completed_at = datetime.now()
            
            self.logger.info(
                "pipeline_completed",
                session_id=session_id,
                duration_seconds=(
                    self._pipeline_state.completed_at - 
                    self._pipeline_state.started_at
                ).total_seconds()
            )
            
            return self._pipeline_state
            
        except Exception as e:
            self._pipeline_state.current_stage = "failed"
            self.logger.error(
                "pipeline_failed",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__,
                failed_at_stage=self._pipeline_state.current_stage
            )
            raise
    
    async def _run_ideation_stage(self) -> None:
        """Execute the Ideation Agent stage."""
        self._pipeline_state.current_stage = "ideation"
        self.logger.info("stage_started", stage="ideation")
        
        output = await self.ideation_agent.execute(self._pipeline_state.input_data)
        self._pipeline_state.ideation_output = output
        
        self.logger.info("stage_completed", stage="ideation")
    
    async def _run_comparative_stage(self) -> None:
        """Execute the Comparative Insight Agent stage."""
        self._pipeline_state.current_stage = "comparative_insight"
        self.logger.info("stage_started", stage="comparative_insight")
        
        # Pass output from previous stage as input
        output = await self.comparative_agent.execute(
            self._pipeline_state.ideation_output
        )
        self._pipeline_state.comparative_output = output
        
        # TODO Phase 2: Use MCP for GTM playbook data
        # playbook_data = await self.mcp_registry.query_playbook({
        #     "industry": self._pipeline_state.input_data.industry,
        #     "stage": "early"
        # })
        
        self.logger.info("stage_completed", stage="comparative_insight")
    
    async def _run_pitch_writing_stage(self) -> None:
        """Execute the Pitch Writer Agent stage."""
        self._pipeline_state.current_stage = "pitch_writing"
        self.logger.info("stage_started", stage="pitch_writing")
        
        output = await self.pitch_writer.execute(
            self._pipeline_state.comparative_output
        )
        self._pipeline_state.pitch_output = output
        
        # TODO Phase 2: Use MCP for VC profiling
        # vc_profile = await self.mcp_registry.query_vcprofile("Series A")
        
        self.logger.info("stage_completed", stage="pitch_writing")
    
    async def _run_prompt_forge_stage(self) -> None:
        """Execute the Prompt Forge Agent stage (with loop logic)."""
        self._pipeline_state.current_stage = "prompt_forge"
        self.logger.info("stage_started", stage="prompt_forge")
        
        # Phase 1: Single execution
        # Phase 2: Will implement actual loop refinement based on quality
        output = await self.prompt_forge.execute(
            self._pipeline_state.pitch_output
        )
        self._pipeline_state.prompt_output = output
        
        # TODO Phase 2: Implement loop refinement
        # while refinement_needed and cycles < max_cycles:
        #     quality = await self._assess_prompt_quality(output)
        #     if quality > threshold:
        #         break
        #     output = await self.prompt_forge.execute(feedback)
        #     cycles += 1
        
        # TODO Phase 2: Use MCP for prompt optimization
        # for prompt in output.image_prompts:
        #     optimized = await self.mcp_registry.optimize_prompt(
        #         prompt.prompt_text,
        #         "image"
        #     )
        
        self.logger.info(
            "stage_completed",
            stage="prompt_forge",
            refinement_cycles=output.total_refinement_cycles
        )
    
    async def _run_qa_stage(self) -> None:
        """Execute the QA Agent stage."""
        self._pipeline_state.current_stage = "qa_validation"
        self.logger.info("stage_started", stage="qa_validation")
        
        output = await self.qa_agent.execute(
            self._pipeline_state.prompt_output
        )
        self._pipeline_state.qa_output = output
        
        # Log validation results
        if not output.validation_passed:
            self.logger.warning(
                "qa_validation_issues",
                critical_issues=len([i for i in output.issues if i.severity == "critical"]),
                total_issues=len(output.issues)
            )
        
        self.logger.info("stage_completed", stage="qa_validation")
    
    async def _run_media_generation_stage(self) -> None:
        """
        Execute the Media Generation stage (Phase 2).
        Runs Imagen → Veo → Canva sequentially to generate media assets.
        """
        stage_start_time = datetime.now()
        self._pipeline_state.current_stage = "media_generation"
        self.logger.info(
            "stage_started",
            stage="media_generation",
            note="Phase 2: Sequential media generation"
        )
        
        try:
            # Stage 6a: Imagen - Generate slide images
            self.logger.info("media_substage_started", substage="imagen_generation")
            imagen_output = await self.imagen_agent.execute(
                self._pipeline_state.prompt_output
            )
            self._pipeline_state.media_output = MediaGenerationOutput(
                imagen_output=imagen_output,
                total_stage_time_seconds=0.0,
                refinement_cycles_performed=0,
                stage_complete=False,
                asset_manifest={}
            )
            self.logger.info(
                "media_substage_completed",
                substage="imagen_generation",
                images_generated=len(imagen_output.images),
                average_quality=imagen_output.average_quality_score
            )
            
            # Stage 6b: Veo - Generate video trailer from images
            self.logger.info("media_substage_started", substage="veo_generation")
            veo_output = await self.veo_agent.execute(imagen_output)
            self._pipeline_state.media_output.veo_output = veo_output
            self.logger.info(
                "media_substage_completed",
                substage="veo_generation",
                videos_generated=len(veo_output.videos),
                average_quality=veo_output.average_quality_score
            )
            
            # Stage 6c: Canva - Create pitch deck
            self.logger.info("media_substage_started", substage="canva_deck_creation")
            canva_output = await self.canva_agent.execute(imagen_output)
            self._pipeline_state.media_output.canva_output = canva_output
            self.logger.info(
                "media_substage_completed",
                substage="canva_deck_creation",
                pages_created=canva_output.total_pages,
                deck_id=canva_output.deck_id
            )
            
            # Build asset manifest from all media outputs
            asset_manifest = self._build_media_manifest(
                imagen_output, veo_output, canva_output
            )
            self._pipeline_state.media_output.asset_manifest = asset_manifest
            
            # Update final stage state
            stage_completion_time = (datetime.now() - stage_start_time).total_seconds()
            self._pipeline_state.media_output.total_stage_time_seconds = stage_completion_time
            self._pipeline_state.media_output.stage_complete = (
                imagen_output.generation_complete and
                veo_output.generation_complete and
                canva_output.creation_complete
            )
            
            self.logger.info(
                "stage_completed",
                stage="media_generation",
                stage_complete=self._pipeline_state.media_output.stage_complete,
                total_time_seconds=stage_completion_time,
                assets_in_manifest=len(asset_manifest)
            )
        
        except Exception as e:
            self.logger.error(
                "media_generation_stage_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def _build_media_manifest(
        self,
        imagen_output,
        veo_output,
        canva_output
    ) -> dict:
        """
        Build a temporary manifest of all generated assets.
        
        Returns:
            Dictionary mapping asset IDs to metadata
        """
        manifest = {}
        
        # Add images
        for image in imagen_output.images:
            manifest[image.image_id] = {
                "type": "image",
                "slide_number": image.slide_number,
                "local_path": image.local_path,
                "quality_score": image.quality_score,
                "refinement_iteration": image.refinement_iteration
            }
        
        # Add videos
        for video in veo_output.videos:
            manifest[video.video_id] = {
                "type": "video",
                "local_path": video.local_path,
                "duration_seconds": video.duration_seconds,
                "quality_score": video.quality_score,
            }
        
        # Add Canva deck info
        manifest["canva_deck"] = {
            "type": "presentation",
            "deck_id": canva_output.deck_id,
            "total_pages": canva_output.total_pages,
            "theme": canva_output.design_theme
        }
        
        self.logger.info(
            "media_manifest_built",
            total_assets=len(manifest),
            images=len(imagen_output.images),
            videos=len(veo_output.videos),
            pages=canva_output.total_pages
        )
        
        return manifest
    
    async def _run_publisher_stage(self) -> None:
        """Execute the Publisher Agent stage (Phase 3)."""
        self._pipeline_state.current_stage = "publishing"
        self.logger.info("stage_started", stage="publishing")
        
        output = await self.publisher_agent.execute(
            self._pipeline_state.qa_output
        )
        self._pipeline_state.publisher_output = output
        
        # TODO Phase 3: Actual asset generation and upload
        # TODO: Generate images with Imagen
        # TODO: Generate videos with Veo
        # TODO: Upload to GCS
        # TODO: Create Canva deck
        # TODO: Generate manifest.json
        
        self.logger.info("stage_completed", stage="publishing")
    
    async def get_pipeline_state(self, session_id: str) -> Optional[PipelineState]:
        """
        Retrieve pipeline state for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Pipeline state if found, None otherwise
        """
        # Phase 1: Only current session
        # Phase 2+: Implement session persistence/retrieval
        if session_id == self._current_session:
            return self._pipeline_state
        return None
    
    async def shutdown(self) -> None:
        """
        Shutdown orchestrator and clean up resources.
        """
        self.logger.info("orchestrator_shutting_down")
        
        # Close MCP connections
        await self.mcp_registry.close()
        
        self.logger.info("orchestrator_shutdown_complete")
    
    def get_agent_metadata(self) -> dict:
        """
        Get metadata for all agents in the pipeline.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "ideation": self.ideation_agent.get_metadata(),
            "comparative_insight": self.comparative_agent.get_metadata(),
            "pitch_writer": self.pitch_writer.get_metadata(),
            "prompt_forge": self.prompt_forge.get_metadata(),
            "qa": self.qa_agent.get_metadata(),
            "publisher": self.publisher_agent.get_metadata()
        }