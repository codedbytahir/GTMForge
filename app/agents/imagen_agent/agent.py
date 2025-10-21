"""
Imagen Agent
Generates images for all pitch deck slides using Imagen via Gemini API.
Phase 2: Uses mock google_clients with placeholder implementations.
Phase 3: Will integrate real Imagen API calls.
"""

from typing import Type
from pydantic import BaseModel
from datetime import datetime
import time

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import PromptForgeOutput, ImagenOutput, GeneratedImage
from app.utils.google_clients import GeminiImagenClient
from app.utils.config import AssetPathManager


class ImagenAgent(BaseAgent):
    """
    Imagen Agent generates high-quality images for every slide in the pitch deck.
    
    Pipeline Position: Runs after QA validation, before Veo agent
    
    Input: PromptForgeOutput containing optimized image prompts
    Output: ImagenOutput with generated image metadata and local paths
    
    Features:
    - Sequential image generation from prompts
    - Quality-based refinement loop (retry if quality < threshold)
    - Structured logging for each generation phase
    - Asset organization into /output/images/
    - Metadata tracking (generation time, quality scores, iterations)
    
    Phase 2: Mock implementation with placeholder client calls
    Phase 3: Replace with real Vertex AI Imagen API
    """
    
    def __init__(self, quality_threshold: float = 0.85, max_retries: int = 3):
        super().__init__(
            name="ImagenAgent",
            description="Generates images for pitch deck slides using Imagen",
            version="1.0.0"
        )
        self.imagen_client = GeminiImagenClient()
        self.quality_threshold = quality_threshold
        self.max_retries = max_retries
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return PromptForgeOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return ImagenOutput
    
    async def run(self, input_data: PromptForgeOutput) -> ImagenOutput:
        """
        Generate images for all slide prompts in the pitch narrative.
        
        Args:
            input_data: PromptForgeOutput with optimized image prompts and style guidance
            
        Returns:
            ImagenOutput with generated images, quality scores, and metadata
        """
        stage_start_time = datetime.now()
        generated_images = []
        errors = []
        total_generation_time = 0.0
        quality_scores = []
        
        self.logger.info(
            "imagen_generation_stage_started",
            total_prompts=len(input_data.image_prompts),
            quality_threshold=self.quality_threshold,
            max_retries=self.max_retries
        )
        
        # Process each image prompt
        for prompt_spec in input_data.image_prompts:
            self.logger.info(
                "image_prompt_processing_started",
                prompt_id=prompt_spec.prompt_id,
                target_slide=prompt_spec.target_slide
            )
            
            # Attempt generation with refinement loop
            retry_count = 0
            image_generated = False
            last_quality_score = 0.0
            
            while retry_count <= self.max_retries and not image_generated:
                try:
                    gen_start_time = datetime.now()
                    
                    # Generate image using client
                    image_result = await self.imagen_client.generate_image(
                        prompt=prompt_spec.prompt_text,
                        slide_number=prompt_spec.target_slide,
                        quality="high",
                        aspect_ratio=prompt_spec.technical_params.get("aspect_ratio", "16:9"),
                        style_guidance=prompt_spec.style_guidance,
                        retry_count=retry_count,
                        max_retries=self.max_retries
                    )
                    
                    # Get absolute path using centralized manager
                    image_path = AssetPathManager.get_image_path(
                        image_id=image_result["image_id"],
                        slide_number=prompt_spec.target_slide,
                        iteration=retry_count
                    )
                    
                    # Ensure the file exists - write to disk if provided image data
                    if "image_data" in image_result:
                        image_path.write_bytes(image_result["image_data"])
                        self.logger.info(
                            "image_file_written",
                            path=str(image_path.absolute()),
                            size_bytes=image_path.stat().st_size
                        )
                    elif not image_path.exists():
                        # Create empty placeholder for mock
                        image_path.write_bytes(b"MOCK_IMAGE_DATA")
                        self.logger.info(
                            "mock_image_file_created",
                            path=str(image_path.absolute())
                        )
                    
                    generation_time = (datetime.now() - gen_start_time).total_seconds()
                    last_quality_score = image_result.get("quality_score", 0.0)
                    
                    self.logger.info(
                        "image_generated",
                        prompt_id=prompt_spec.prompt_id,
                        quality_score=last_quality_score,
                        generation_time_seconds=generation_time,
                        retry_attempt=retry_count
                    )
                    
                    # Check if quality meets threshold
                    if last_quality_score >= self.quality_threshold:
                        # Quality acceptable, add to results
                        generated_image = GeneratedImage(
                            image_id=image_result["image_id"],
                            slide_number=image_result["slide_number"],
                            local_path=str(image_path.absolute()),  # Use absolute path
                            url=image_result.get("url"),
                            quality_score=last_quality_score,
                            generation_time_seconds=generation_time,
                            prompt_used=prompt_spec.prompt_text,
                            refinement_iteration=retry_count
                        )
                        generated_images.append(generated_image)
                        quality_scores.append(last_quality_score)
                        total_generation_time += generation_time
                        image_generated = True
                        
                        self.logger.info(
                            "image_accepted",
                            prompt_id=prompt_spec.prompt_id,
                            quality_score=last_quality_score,
                            file_path=str(image_path.absolute())
                        )
                    
                    else:
                        # Quality below threshold, check if should retry
                        should_retry = self.imagen_client.should_retry_image(
                            quality_score=last_quality_score,
                            quality_threshold=self.quality_threshold,
                            retry_count=retry_count,
                            max_retries=self.max_retries
                        )
                        
                        if should_retry:
                            self.logger.info(
                                "image_retry_queued",
                                prompt_id=prompt_spec.prompt_id,
                                quality_score=last_quality_score,
                                next_retry=retry_count + 1
                            )
                            retry_count += 1
                            # Add small delay before retry
                            await self._async_sleep(1.0)
                        
                        else:
                            # Max retries reached, accept current image
                            generated_image = GeneratedImage(
                                image_id=image_result["image_id"],
                                slide_number=image_result["slide_number"],
                                local_path=str(image_path.absolute()),  # Use absolute path
                                url=image_result.get("url"),
                                quality_score=last_quality_score,
                                generation_time_seconds=generation_time,
                                prompt_used=prompt_spec.prompt_text,
                                refinement_iteration=retry_count
                            )
                            generated_images.append(generated_image)
                            quality_scores.append(last_quality_score)
                            total_generation_time += generation_time
                            image_generated = True
                            
                            self.logger.info(
                                "image_accepted_max_retries",
                                prompt_id=prompt_spec.prompt_id,
                                quality_score=last_quality_score,
                                retries_used=retry_count
                            )
                
                except Exception as e:
                    error_msg = f"Image generation failed for {prompt_spec.prompt_id}: {str(e)}"
                    self.logger.error(
                        "image_generation_error",
                        prompt_id=prompt_spec.prompt_id,
                        error_message=error_msg,
                        error_type=type(e).__name__,
                        retry_attempt=retry_count
                    )
                    errors.append(error_msg)
                    
                    if retry_count < self.max_retries:
                        retry_count += 1
                        await self._async_sleep(1.0)
                    else:
                        image_generated = True  # Give up after max retries
        
        # Calculate aggregate statistics
        average_quality_score = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )
        
        stage_completion_time = (datetime.now() - stage_start_time).total_seconds()
        
        # Build output
        output = ImagenOutput(
            images=generated_images,
            total_generation_time_seconds=total_generation_time,
            average_quality_score=average_quality_score,
            generation_complete=len(errors) == 0,
            errors=errors
        )
        
        self.logger.info(
            "imagen_generation_stage_completed",
            images_generated=len(generated_images),
            average_quality_score=average_quality_score,
            total_generation_time=total_generation_time,
            stage_completion_time_seconds=stage_completion_time,
            errors_encountered=len(errors),
            generation_complete=output.generation_complete
        )
        
        return output
    
    async def _async_sleep(self, seconds: float):
        """Async sleep wrapper for retry delays"""
        time.sleep(seconds)


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="imagen_agent",
    description="Generates images for pitch deck slides using Imagen",
    instruction="""
    You are the Imagen Agent. Your role is to:
    - Generate high-quality images for each slide in the pitch deck
    - Follow style guidance and brand guidelines
    - Ensure consistent visual theme across all images
    - Validate image quality and refine if needed
    - Organize generated assets for downstream processing
    
    Take pitch narrative prompts and transform them into professional, cohesive visuals.
    """,
)
