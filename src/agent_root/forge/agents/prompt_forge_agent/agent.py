"""
Prompt Forge Agent
Generates and refines prompts for Imagen and Veo generation with loop logic.
"""

from typing import Type
from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import PitchNarrativeOutput, PromptForgeOutput, PromptSpec


class PromptForgeAgent(BaseAgent):
    """
    Prompt Forge Agent creates optimized prompts for visual asset generation:
    - Imagen prompts for slide images
    - Veo prompts for video content
    - Visual theme consistency
    - Brand guideline enforcement
    - Iterative refinement loop
    
    This agent uses loop logic to refine prompts based on quality checks
    and can iterate multiple times to achieve optimal results.
    
    Phase 1: Returns mock prompt specifications
    Phase 2: Will integrate with prompt.mcp for dynamic prompt optimization
    Phase 2: Will add actual loop refinement based on generated asset quality
    """
    
    def __init__(self, max_refinement_cycles: int = 3):
        super().__init__(
            name="PromptForgeAgent",
            description="Generates and refines prompts for Imagen and Veo output",
            version="1.0.0"
        )
        self.max_refinement_cycles = max_refinement_cycles
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return PitchNarrativeOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return PromptForgeOutput
    
    async def run(self, input_data: PitchNarrativeOutput) -> PromptForgeOutput:
        """
        Generate and refine prompts for visual asset creation.
        
        Args:
            input_data: Pitch narrative with slide-by-slide content
            
        Returns:
            Optimized prompts for Imagen and Veo generation
        """
        self.logger.info(
            "prompt_forge_started",
            total_slides=len(input_data.slides),
            max_refinement_cycles=self.max_refinement_cycles
        )
        
        # TODO Phase 2: Integrate prompt.mcp for prompt optimization
        # TODO: Implement actual loop logic for refinement
        # TODO: Quality assessment of generated prompts
        # TODO: Integrate with Gemini for prompt generation
        # TODO: Apply visual style guidelines from brand config
        
        # Phase 1: Generate mock prompts for each slide
        image_prompts = []
        
        for slide in input_data.slides:
            # Create image prompt for this slide
            prompt_spec = PromptSpec(
                prompt_id=f"img_slide_{slide.slide_number}",
                target_slide=slide.slide_number,
                media_type="image",
                prompt_text=(
                    f"Professional business presentation visual for '{slide.slide_title}'. "
                    f"{slide.content_direction}. Modern, clean aesthetic with "
                    f"technology focus. High quality, 16:9 aspect ratio."
                ),
                style_guidance=(
                    "Cinematic lighting, modern tech aesthetic, dark steel and tech blue "
                    "color palette, minimal text, professional photography style, "
                    "high contrast, sharp focus"
                ),
                technical_params={
                    "aspect_ratio": "16:9",
                    "quality": "high",
                    "style": "professional",
                    "color_palette": ["#1e3a5f", "#2d5f8d", "#ffffff", "#f0f0f0"]
                },
                refinement_iteration=0
            )
            image_prompts.append(prompt_spec)
        
        # Create video prompt for trailer/intro
        video_prompts = [
            PromptSpec(
                prompt_id="video_trailer",
                target_slide=0,  # Not tied to specific slide
                media_type="video",
                prompt_text=(
                    f"Cinematic trailer for '{input_data.deck_title}'. "
                    f"Opening with problem visualization, transitioning to solution, "
                    f"showing growth and momentum. Professional, inspiring, modern tech aesthetic. "
                    f"Duration: 30-60 seconds."
                ),
                style_guidance=(
                    "Cinematic camera movements, dynamic transitions, "
                    "modern tech aesthetic, inspiring music, fast-paced editing, "
                    "professional grade video production"
                ),
                technical_params={
                    "duration_seconds": 45,
                    "aspect_ratio": "16:9",
                    "quality": "high",
                    "include_music": True,
                    "pacing": "dynamic"
                },
                refinement_iteration=0
            )
        ]
        
        # TODO Phase 2: Implement loop refinement logic here
        # Placeholder for refinement cycles
        refinement_cycles = 0
        # In Phase 2, this would iterate based on quality checks:
        # while refinement_cycles < self.max_refinement_cycles:
        #     quality_score = self._assess_prompt_quality(prompts)
        #     if quality_score > threshold:
        #         break
        #     prompts = self._refine_prompts(prompts, feedback)
        #     refinement_cycles += 1
        
        output = PromptForgeOutput(
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            visual_theme=(
                "Modern technology aesthetic with professional business presentation style. "
                "Dark Steel (#1e3a5f) and Tech Blue (#2d5f8d) color palette. "
                "Clean typography, minimal text, high-quality photography and renders. "
                "Consistent lighting and visual language across all assets."
            ),
            brand_guidelines=(
                "1. Use Dark Steel and Tech Blue as primary colors\n"
                "2. Maintain high contrast for readability\n"
                "3. Keep text minimal and impactful\n"
                "4. Use professional photography or clean renders\n"
                "5. Ensure consistent lighting across all visuals\n"
                "6. Apply modern, sans-serif typography\n"
                "7. Maintain 16:9 aspect ratio for all slides\n"
                "8. Use white space effectively"
            ),
            total_refinement_cycles=refinement_cycles
        )
        
        self.logger.info(
            "prompt_forge_completed",
            image_prompts_generated=len(output.image_prompts),
            video_prompts_generated=len(output.video_prompts),
            refinement_cycles=refinement_cycles
        )
        
        return output
    
    # TODO Phase 2: Implement refinement helper methods
    # async def _assess_prompt_quality(self, prompts: List[PromptSpec]) -> float:
    #     """Assess quality of generated prompts"""
    #     pass
    # 
    # async def _refine_prompts(
    #     self, 
    #     prompts: List[PromptSpec], 
    #     feedback: dict
    # ) -> List[PromptSpec]:
    #     """Refine prompts based on quality feedback"""
    #     pass


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="prompt_forge_agent",
    description="Generates and refines prompts for Imagen and Veo output",
    instruction="""
    You are the Prompt Forge Agent. Your role is to:
    - Generate optimized prompts for Imagen image generation
    - Create prompts for Veo video generation
    - Ensure visual theme consistency across all assets
    - Enforce brand guidelines
    - Iteratively refine prompts for quality
    
    Take pitch narrative content and transform it into detailed, optimized prompts for media generation.
    """,
)

