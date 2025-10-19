"""
Veo Agent
Generates cinematic video trailers from pitch deck images using Veo 3.1.
Phase 2: Uses mock google_clients with placeholder implementations.
Phase 3: Will integrate real Veo API calls.
"""

from typing import Type
from pydantic import BaseModel
from datetime import datetime
import time

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import ImagenOutput, VeoOutput, GeneratedVideo
from app.utils.google_clients import VeoClient


class VeoAgent(BaseAgent):
    """
    Veo Agent generates cinematic video trailers from pitch deck images.
    
    Pipeline Position: Runs after Imagen agent, before Canva agent
    
    Input: ImagenOutput containing generated slide images
    Output: VeoOutput with generated video metadata and local paths
    
    Features:
    - Sequential video generation from image sequences
    - Quality-based refinement loop (retry if quality < threshold)
    - Structured logging for generation phases
    - Asset organization into /output/videos/
    - Cinematic trailer creation with transitions
    
    Phase 2: Mock implementation with placeholder client calls
    Phase 3: Replace with real Vertex AI Veo 3.1 API
    """
    
    def __init__(self, quality_threshold: float = 0.80, max_retries: int = 2):
        super().__init__(
            name="VeoAgent",
            description="Generates cinematic video trailers from slide images using Veo",
            version="1.0.0"
        )
        self.veo_client = VeoClient()
        self.quality_threshold = quality_threshold
        self.max_retries = max_retries
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return ImagenOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return VeoOutput
    
    async def run(self, input_data: ImagenOutput) -> VeoOutput:
        """
        Generate video trailer from slide images.
        
        Args:
            input_data: ImagenOutput with generated images for all slides
            
        Returns:
            VeoOutput with generated video metadata and quality scores
        """
        stage_start_time = datetime.now()
        generated_videos = []
        errors = []
        total_generation_time = 0.0
        quality_scores = []
        
        self.logger.info(
            "veo_generation_stage_started",
            source_images=len(input_data.images),
            quality_threshold=self.quality_threshold,
            max_retries=self.max_retries
        )
        
        # Extract image paths from Imagen output
        image_paths = [img.local_path for img in input_data.images]
        
        if not image_paths:
            self.logger.warning(
                "veo_no_source_images",
                message="No images provided by Imagen Agent"
            )
            errors.append("No source images provided for video generation")
        
        # Generate trailer video with refinement loop
        retry_count = 0
        video_generated = False
        last_quality_score = 0.0
        
        while retry_count <= self.max_retries and not video_generated:
            try:
                gen_start_time = datetime.now()
                
                # Generate video using client
                video_result = await self.veo_client.generate_video(
                    prompt="Cinematic trailer opening with problem visualization, transitioning to solution, showing momentum. Professional, inspiring, modern tech aesthetic.",
                    source_images=image_paths,
                    duration_seconds=45,
                    quality="high",
                    retry_count=retry_count,
                    max_retries=self.max_retries
                )
                
                generation_time = (datetime.now() - gen_start_time).total_seconds()
                last_quality_score = video_result.get("quality_score", 0.0)
                
                self.logger.info(
                    "video_generated",
                    video_id=video_result["video_id"],
                    quality_score=last_quality_score,
                    generation_time_seconds=generation_time,
                    duration_seconds=video_result.get("duration_seconds"),
                    retry_attempt=retry_count
                )
                
                # Check if quality meets threshold
                if last_quality_score >= self.quality_threshold:
                    # Quality acceptable, add to results
                    generated_video = GeneratedVideo(
                        video_id=video_result["video_id"],
                        local_path=video_result["local_path"],
                        url=video_result.get("url"),
                        duration_seconds=video_result.get("duration_seconds", 45),
                        quality_score=last_quality_score,
                        generation_time_seconds=generation_time,
                        prompt_used="Cinematic trailer with professional transitions",
                        source_images=[img.image_id for img in input_data.images[:5]]
                    )
                    generated_videos.append(generated_video)
                    quality_scores.append(last_quality_score)
                    total_generation_time += generation_time
                    video_generated = True
                    
                    self.logger.info(
                        "video_accepted",
                        video_id=video_result["video_id"],
                        quality_score=last_quality_score
                    )
                
                else:
                    # Quality below threshold, check if should retry
                    should_retry = self.veo_client.should_retry_video(
                        quality_score=last_quality_score,
                        quality_threshold=self.quality_threshold,
                        retry_count=retry_count,
                        max_retries=self.max_retries
                    )
                    
                    if should_retry:
                        self.logger.info(
                            "video_retry_queued",
                            quality_score=last_quality_score,
                            next_retry=retry_count + 1
                        )
                        retry_count += 1
                        await self._async_sleep(2.0)
                    
                    else:
                        # Max retries reached, accept current video
                        generated_video = GeneratedVideo(
                            video_id=video_result["video_id"],
                            local_path=video_result["local_path"],
                            url=video_result.get("url"),
                            duration_seconds=video_result.get("duration_seconds", 45),
                            quality_score=last_quality_score,
                            generation_time_seconds=generation_time,
                            prompt_used="Cinematic trailer with professional transitions",
                            source_images=[img.image_id for img in input_data.images[:5]]
                        )
                        generated_videos.append(generated_video)
                        quality_scores.append(last_quality_score)
                        total_generation_time += generation_time
                        video_generated = True
                        
                        self.logger.info(
                            "video_accepted_max_retries",
                            quality_score=last_quality_score,
                            retries_used=retry_count
                        )
            
            except Exception as e:
                error_msg = f"Video generation failed: {str(e)}"
                self.logger.error(
                    "video_generation_error",
                    error_message=error_msg,
                    error_type=type(e).__name__,
                    retry_attempt=retry_count
                )
                errors.append(error_msg)
                
                if retry_count < self.max_retries:
                    retry_count += 1
                    await self._async_sleep(2.0)
                else:
                    video_generated = True  # Give up after max retries
        
        # Calculate aggregate statistics
        average_quality_score = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )
        
        stage_completion_time = (datetime.now() - stage_start_time).total_seconds()
        
        # Build output
        output = VeoOutput(
            videos=generated_videos,
            total_generation_time_seconds=total_generation_time,
            average_quality_score=average_quality_score,
            generation_complete=len(errors) == 0,
            errors=errors
        )
        
        self.logger.info(
            "veo_generation_stage_completed",
            videos_generated=len(generated_videos),
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
    name="veo_agent",
    description="Generates cinematic video trailers using Veo 3.1",
    instruction="""
    You are the Veo Agent. Your role is to:
    - Generate cinematic video trailers from pitch deck images
    - Create compelling visual storytelling with transitions
    - Apply professional editing and pacing
    - Match video to overall pitch narrative
    - Ensure consistent visual style with generated images
    
    Transform static images into dynamic, engaging video content.
    """,
)
