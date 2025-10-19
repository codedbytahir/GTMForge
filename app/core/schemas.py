"""
GTMForge Pydantic Schemas
Defines all input/output models for agent communication in the pipeline.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Input Schemas
# ============================================================================

class StartupIdeaInput(BaseModel):
    """
    Initial user input containing the startup idea.
    This is the entry point for the entire GTMForge pipeline.
    """
    idea: str = Field(..., description="The core startup idea or problem being solved")
    industry: Optional[str] = Field(None, description="Target industry or sector")
    target_market: Optional[str] = Field(None, description="Initial target market or customer segment")
    additional_context: Optional[str] = Field(None, description="Any additional context or constraints")
    
    class Config:
        json_schema_extra = {
            "example": {
                "idea": "AI-powered restaurant staffing platform",
                "industry": "Restaurant & Hospitality",
                "target_market": "Small to medium restaurants in urban areas",
                "additional_context": "Focus on reducing no-show rates and improving shift coverage"
            }
        }


# ============================================================================
# Agent Output Schemas
# ============================================================================

class ICP(BaseModel):
    """Ideal Customer Profile definition"""
    segment_name: str = Field(..., description="Name of the customer segment")
    demographics: str = Field(..., description="Demographic characteristics")
    pain_points: List[str] = Field(default_factory=list, description="Key pain points for this segment")
    behaviors: str = Field(..., description="Behavioral patterns and preferences")


class IdeationOutput(BaseModel):
    """
    Output from Ideation Agent.
    Expands the initial idea into structured ICPs, pain points, and market context.
    """
    expanded_idea: str = Field(..., description="Expanded and refined version of the original idea")
    icps: List[ICP] = Field(default_factory=list, description="Identified Ideal Customer Profiles")
    key_pain_points: List[str] = Field(default_factory=list, description="Primary pain points being addressed")
    market_context: str = Field(..., description="Market landscape and opportunity context")
    value_proposition: str = Field(..., description="Core value proposition")
    unique_differentiators: List[str] = Field(default_factory=list, description="Key differentiating factors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expanded_idea": "AI-powered platform connecting restaurants with pre-vetted staff...",
                "icps": [
                    {
                        "segment_name": "Urban Restaurant Managers",
                        "demographics": "25-45 years old, managing 10-50 employee restaurants",
                        "pain_points": ["Last-minute no-shows", "High turnover", "Scheduling complexity"],
                        "behaviors": "Mobile-first, need quick solutions"
                    }
                ],
                "key_pain_points": ["Staff no-shows", "Hiring inefficiency", "Schedule gaps"],
                "market_context": "Restaurant industry facing chronic staffing shortages...",
                "value_proposition": "Reduce staffing gaps by 80% with AI-powered predictions",
                "unique_differentiators": ["Predictive no-show detection", "Real-time replacement"]
            }
        }


class BenchmarkCompany(BaseModel):
    """Benchmark company comparison data"""
    company_name: str = Field(..., description="Name of the benchmark company")
    similarity_score: float = Field(..., description="Similarity to target startup (0-1)")
    key_strategies: List[str] = Field(default_factory=list, description="Successful GTM strategies used")
    funding_stage: Optional[str] = Field(None, description="Funding stage achieved")
    market_approach: str = Field(..., description="How they approached the market")


class ComparativeInsightOutput(BaseModel):
    """
    Output from Comparative Insight Agent.
    Benchmarks the idea against successful startups using GTM playbook data.
    """
    benchmark_companies: List[BenchmarkCompany] = Field(default_factory=list, description="Similar successful companies")
    gtm_strategies: List[str] = Field(default_factory=list, description="Recommended GTM strategies based on benchmarks")
    market_positioning: str = Field(..., description="Recommended market positioning")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages identified")
    potential_challenges: List[str] = Field(default_factory=list, description="Anticipated challenges from analysis")
    investor_appeal_factors: List[str] = Field(default_factory=list, description="Factors that appeal to investors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "benchmark_companies": [
                    {
                        "company_name": "Shiftgig",
                        "similarity_score": 0.85,
                        "key_strategies": ["B2B SaaS model", "Marketplace approach"],
                        "funding_stage": "Series B",
                        "market_approach": "Enterprise-first, then SMB expansion"
                    }
                ],
                "gtm_strategies": ["B2B direct sales", "Strategic partnerships with POS providers"],
                "market_positioning": "Premium AI-powered staffing solution",
                "competitive_advantages": ["Predictive AI", "Network effects"],
                "potential_challenges": ["Market education needed", "Two-sided marketplace dynamics"],
                "investor_appeal_factors": ["Large TAM", "Recurring revenue", "AI differentiation"]
            }
        }


class SlideContent(BaseModel):
    """Content for a single pitch deck slide"""
    slide_number: int = Field(..., description="Slide sequence number")
    slide_title: str = Field(..., description="Title of the slide")
    key_message: str = Field(..., description="Core message to convey")
    talking_points: List[str] = Field(default_factory=list, description="Key talking points for this slide")
    content_direction: str = Field(..., description="Visual content direction and style")
    data_points: Optional[List[str]] = Field(None, description="Key data points or metrics to highlight")


class PitchNarrativeOutput(BaseModel):
    """
    Output from Pitch Writer Agent.
    Complete pitch deck narrative with slide-by-slide content.
    """
    deck_title: str = Field(..., description="Title of the pitch deck")
    elevator_pitch: str = Field(..., description="30-second elevator pitch")
    slides: List[SlideContent] = Field(default_factory=list, description="Slide-by-slide content")
    overall_narrative_arc: str = Field(..., description="The story arc connecting all slides")
    target_investor_profile: str = Field(..., description="Profile of target investors for this pitch")
    estimated_pitch_duration: int = Field(..., description="Estimated pitch duration in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "deck_title": "Revolutionizing Restaurant Staffing with AI",
                "elevator_pitch": "We use AI to predict staff no-shows and instantly connect restaurants...",
                "slides": [
                    {
                        "slide_number": 1,
                        "slide_title": "The Problem",
                        "key_message": "Restaurants lose $10B annually to staffing issues",
                        "talking_points": ["40% no-show rate during peak times", "Average 3-hour gap to fill"],
                        "content_direction": "Bold statistic with restaurant imagery",
                        "data_points": ["$10B annual loss", "40% no-show rate"]
                    }
                ],
                "overall_narrative_arc": "Problem → Solution → Market → Traction → Vision",
                "target_investor_profile": "Series A investors in marketplace/SaaS",
                "estimated_pitch_duration": 12
            }
        }


class PromptSpec(BaseModel):
    """Specification for an Imagen or Veo generation prompt"""
    prompt_id: str = Field(..., description="Unique identifier for this prompt")
    target_slide: int = Field(..., description="Associated slide number")
    media_type: str = Field(..., description="Type of media: 'image' or 'video'")
    prompt_text: str = Field(..., description="The actual generation prompt")
    style_guidance: str = Field(..., description="Style and aesthetic guidance")
    technical_params: Dict[str, Any] = Field(default_factory=dict, description="Technical parameters for generation")
    refinement_iteration: int = Field(default=0, description="Refinement iteration count")


class PromptForgeOutput(BaseModel):
    """
    Output from Prompt Forge Agent.
    Optimized prompts for Imagen and Veo generation.
    """
    image_prompts: List[PromptSpec] = Field(default_factory=list, description="Image generation prompts")
    video_prompts: List[PromptSpec] = Field(default_factory=list, description="Video generation prompts")
    visual_theme: str = Field(..., description="Overall visual theme and style")
    brand_guidelines: str = Field(..., description="Brand consistency guidelines")
    total_refinement_cycles: int = Field(default=0, description="Number of refinement cycles performed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_prompts": [
                    {
                        "prompt_id": "img_slide_1",
                        "target_slide": 1,
                        "media_type": "image",
                        "prompt_text": "Professional restaurant manager looking stressed at empty stations...",
                        "style_guidance": "Cinematic, modern, tech blue and dark steel palette",
                        "technical_params": {"aspect_ratio": "16:9", "quality": "high"},
                        "refinement_iteration": 0
                    }
                ],
                "video_prompts": [],
                "visual_theme": "Modern tech aesthetic with restaurant authenticity",
                "brand_guidelines": "Dark Steel backgrounds, Tech Blue accents, clean typography",
                "total_refinement_cycles": 0
            }
        }


class ValidationIssue(BaseModel):
    """A validation issue found during QA"""
    severity: str = Field(..., description="Severity level: 'critical', 'warning', 'info'")
    category: str = Field(..., description="Category of issue")
    description: str = Field(..., description="Description of the issue")
    affected_component: str = Field(..., description="Which component is affected")
    recommendation: Optional[str] = Field(None, description="Recommended fix")


class QAValidationOutput(BaseModel):
    """
    Output from QA Agent.
    Validation results for all generated assets and content.
    """
    validation_passed: bool = Field(..., description="Overall validation pass/fail")
    issues: List[ValidationIssue] = Field(default_factory=list, description="List of issues found")
    content_quality_score: float = Field(..., description="Content quality score 0-100")
    brand_consistency_score: float = Field(..., description="Brand consistency score 0-100")
    compliance_checks_passed: bool = Field(..., description="Whether compliance checks passed")
    recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "validation_passed": True,
                "issues": [
                    {
                        "severity": "warning",
                        "category": "content",
                        "description": "Slide 3 talking points exceed recommended length",
                        "affected_component": "slide_3",
                        "recommendation": "Reduce to 3-4 key points"
                    }
                ],
                "content_quality_score": 92.5,
                "brand_consistency_score": 88.0,
                "compliance_checks_passed": True,
                "recommendations": ["Consider adding more specific metrics to slide 5"]
            }
        }


class PublisherOutput(BaseModel):
    """
    Output from Publisher Agent.
    Final manifest with URLs to all generated assets.
    """
    manifest_id: str = Field(..., description="Unique manifest identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    canva_deck_url: Optional[str] = Field(None, description="URL to Canva pitch deck")
    veo_video_url: Optional[str] = Field(None, description="URL to Veo-generated trailer video")
    image_urls: Dict[str, str] = Field(default_factory=dict, description="Map of image IDs to GCS URLs")
    video_urls: Dict[str, str] = Field(default_factory=dict, description="Map of video IDs to GCS URLs")
    manifest_json_url: Optional[str] = Field(None, description="URL to the full manifest JSON")
    gcs_bucket: Optional[str] = Field(None, description="GCS bucket name where assets are stored")
    status: str = Field(default="published", description="Publication status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "manifest_id": "gtmforge_20250619_abc123",
                "created_at": "2025-06-19T10:30:00Z",
                "canva_deck_url": "https://canva.com/design/xyz",
                "veo_video_url": "https://storage.googleapis.com/gtmforge-assets/videos/trailer.mp4",
                "image_urls": {
                    "img_slide_1": "https://storage.googleapis.com/gtmforge-assets/images/slide1.png"
                },
                "video_urls": {},
                "manifest_json_url": "https://storage.googleapis.com/gtmforge-assets/manifests/manifest.json",
                "gcs_bucket": "gtmforge-assets",
                "status": "published"
            }
        }

class GeneratedImage(BaseModel):
    """Metadata for a generated image"""
    image_id: str = Field(..., description="Unique identifier for this image")
    slide_number: int = Field(..., description="Associated slide number")
    local_path: str = Field(..., description="Local file path where image is saved")
    url: Optional[str] = Field(None, description="GCS URL (Phase 3)")
    quality_score: float = Field(default=0.0, description="Quality score 0-1")
    generation_time_seconds: float = Field(..., description="Time taken to generate")
    prompt_used: str = Field(..., description="The actual prompt used for generation")
    refinement_iteration: int = Field(default=0, description="Which refinement cycle this came from")


class ImagenOutput(BaseModel):
    """
    Output from Imagen Agent.
    Generated images for all pitch deck slides.
    """
    images: List[GeneratedImage] = Field(default_factory=list, description="Generated images")
    total_generation_time_seconds: float = Field(..., description="Total time for all image generations")
    average_quality_score: float = Field(..., description="Average quality across all images")
    generation_complete: bool = Field(default=True, description="Whether all requested images were generated")
    errors: List[str] = Field(default_factory=list, description="Any generation errors encountered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "images": [
                    {
                        "image_id": "img_slide_1",
                        "slide_number": 1,
                        "local_path": "/output/images/imagen_slide_1_0.png",
                        "url": None,
                        "quality_score": 0.92,
                        "generation_time_seconds": 3.5,
                        "prompt_used": "Professional restaurant manager looking stressed...",
                        "refinement_iteration": 0
                    }
                ],
                "total_generation_time_seconds": 38.5,
                "average_quality_score": 0.89,
                "generation_complete": True,
                "errors": []
            }
        }


class GeneratedVideo(BaseModel):
    """Metadata for a generated video"""
    video_id: str = Field(..., description="Unique identifier for this video")
    local_path: str = Field(..., description="Local file path where video is saved")
    url: Optional[str] = Field(None, description="GCS URL (Phase 3)")
    duration_seconds: int = Field(..., description="Duration of video in seconds")
    quality_score: float = Field(default=0.0, description="Quality score 0-1")
    generation_time_seconds: float = Field(..., description="Time taken to generate")
    prompt_used: str = Field(..., description="The actual prompt used for generation")
    source_images: List[str] = Field(default_factory=list, description="Image IDs used as source")


class VeoOutput(BaseModel):
    """
    Output from Veo Agent.
    Generated video trailer from pitch deck imagery.
    """
    videos: List[GeneratedVideo] = Field(default_factory=list, description="Generated videos")
    total_generation_time_seconds: float = Field(..., description="Total time for all video generations")
    average_quality_score: float = Field(..., description="Average quality across all videos")
    generation_complete: bool = Field(default=True, description="Whether video generation succeeded")
    errors: List[str] = Field(default_factory=list, description="Any generation errors encountered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "videos": [
                    {
                        "video_id": "veo_trailer",
                        "local_path": "/output/videos/veo_trailer_0.mp4",
                        "url": None,
                        "duration_seconds": 45,
                        "quality_score": 0.88,
                        "generation_time_seconds": 120.0,
                        "prompt_used": "Cinematic trailer opening with problem visualization...",
                        "source_images": ["img_slide_1", "img_slide_2", "img_slide_3"]
                    }
                ],
                "total_generation_time_seconds": 120.0,
                "average_quality_score": 0.88,
                "generation_complete": True,
                "errors": []
            }
        }


class CanvaPage(BaseModel):
    """Metadata for a Canva deck page"""
    page_number: int = Field(..., description="Page sequence number")
    page_id: str = Field(..., description="Canva page ID")
    slide_title: str = Field(..., description="Title of the slide")
    has_image: bool = Field(default=False, description="Whether image was added")
    has_text: bool = Field(default=False, description="Whether text content was added")
    design_applied: bool = Field(default=False, description="Whether visual design was applied")


class CanvaOutput(BaseModel):
    """
    Output from Canva Agent.
    Pitch deck created and formatted via Canva Connect API.
    """
    deck_id: str = Field(..., description="Canva design ID")
    deck_url: Optional[str] = Field(None, description="Canva shareable URL")
    pages: List[CanvaPage] = Field(default_factory=list, description="Pages in the deck")
    total_pages: int = Field(..., description="Total number of pages created")
    creation_complete: bool = Field(default=True, description="Whether deck creation succeeded")
    design_theme: str = Field(..., description="Applied design theme (e.g., Dark Steel + Tech Blue)")
    errors: List[str] = Field(default_factory=list, description="Any creation errors encountered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "deck_id": "canva_design_abc123",
                "deck_url": None,
                "pages": [
                    {
                        "page_number": 1,
                        "page_id": "page_1",
                        "slide_title": "The Problem",
                        "has_image": True,
                        "has_text": True,
                        "design_applied": True
                    }
                ],
                "total_pages": 11,
                "creation_complete": True,
                "design_theme": "Dark Steel + Tech Blue",
                "errors": []
            }
        }


class MediaGenerationOutput(BaseModel):
    """
    Aggregated output from entire media generation stage.
    Contains results from Imagen, Veo, and Canva agents.
    """
    imagen_output: Optional[ImagenOutput] = Field(None, description="Image generation results")
    veo_output: Optional[VeoOutput] = Field(None, description="Video generation results")
    canva_output: Optional[CanvaOutput] = Field(None, description="Canva deck creation results")
    total_stage_time_seconds: float = Field(..., description="Total time for entire media stage")
    refinement_cycles_performed: int = Field(default=0, description="Number of prompt refinement cycles")
    stage_complete: bool = Field(default=True, description="Whether entire stage succeeded")
    asset_manifest: Dict[str, str] = Field(default_factory=dict, description="Temporary manifest of all assets")


# ============================================================================
# Pipeline State Schema
# ============================================================================

class PipelineState(BaseModel):
    """
    Tracks the complete state of the GTMForge pipeline execution.
    Used for passing data between agents and tracking progress.
    """
    session_id: str = Field(..., description="Unique session identifier")
    input_data: StartupIdeaInput = Field(..., description="Original input")
    ideation_output: Optional[IdeationOutput] = None
    comparative_output: Optional[ComparativeInsightOutput] = None
    pitch_output: Optional[PitchNarrativeOutput] = None
    prompt_output: Optional[PromptForgeOutput] = None
    qa_output: Optional[QAValidationOutput] = None
    media_output: Optional[MediaGenerationOutput] = None
    publisher_output: Optional[PublisherOutput] = None
    current_stage: str = Field(default="initialized", description="Current pipeline stage")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True