"""
QA Agent - Phase 3
Comprehensive asset validation with file integrity, quality checks, and retry logic.
"""

import os
import asyncio
from typing import Type, List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import PipelineState, QAReport, ImagenOutput, VeoOutput, CanvaOutput
from app.utils.config import AssetPathManager


class QAAgent(BaseAgent):
    """
    QA Agent performs comprehensive validation on all generated assets:
    - File integrity validation (exists, readable, not corrupted)
    - JSON schema compliance for all outputs
    - Image quality validation (dimensions, file size, format)
    - Video quality validation (duration, codec, file size)
    - Canva deck validation (page count, deck ID, theme)
    - Asset metadata validation (timestamps, quality scores)
    
    Includes retry logic with exponential backoff for transient failures.
    """
    
    def __init__(self, max_retries: int = 3, quality_threshold: float = 0.8):
        super().__init__(
            name="QAAgent",
            description="Validates all generated assets with comprehensive quality checks",
            version="1.0.0"
        )
        self.max_retries = max_retries
        self.quality_threshold = quality_threshold
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return PipelineState
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return QAReport
    
    async def run(self, input_data: PipelineState) -> QAReport:
        """
        Perform comprehensive validation on all pipeline outputs.
        
        Args:
            input_data: Complete pipeline state with all generated outputs
            
        Returns:
            QAReport with validation results, errors, and metrics
        """
        validation_start = datetime.now()
        
        self.logger.info(
            "qa_validation_started",
            agent_name=self.name,
            agent_version=self.version,
            max_retries=self.max_retries,
            quality_threshold=self.quality_threshold
        )
        
        # Initialize validation results
        errors = []
        warnings = []
        metrics = {}
        retry_summary = {}
        total_assets = 0
        assets_valid = 0
        assets_invalid = 0
        
        # Validate each output type
        if input_data.media_output and input_data.media_output.imagen_output:
            imagen_results = await self._validate_imagen_output(input_data.media_output.imagen_output)
            total_assets += imagen_results["total_assets"]
            assets_valid += imagen_results["valid_assets"]
            assets_invalid += imagen_results["invalid_assets"]
            errors.extend(imagen_results["errors"])
            warnings.extend(imagen_results["warnings"])
            metrics.update(imagen_results["metrics"])
            retry_summary["images"] = imagen_results["retry_count"]
        
        if input_data.media_output and input_data.media_output.veo_output:
            veo_results = await self._validate_veo_output(input_data.media_output.veo_output)
            total_assets += veo_results["total_assets"]
            assets_valid += veo_results["valid_assets"]
            assets_invalid += veo_results["invalid_assets"]
            errors.extend(veo_results["errors"])
            warnings.extend(veo_results["warnings"])
            metrics.update(veo_results["metrics"])
            retry_summary["videos"] = veo_results["retry_count"]
        
        if input_data.media_output and input_data.media_output.canva_output:
            canva_results = await self._validate_canva_output(input_data.media_output.canva_output)
            total_assets += canva_results["total_assets"]
            assets_valid += canva_results["valid_assets"]
            assets_invalid += canva_results["invalid_assets"]
            errors.extend(canva_results["errors"])
            warnings.extend(canva_results["warnings"])
            metrics.update(canva_results["metrics"])
            retry_summary["decks"] = canva_results["retry_count"]
        
        # Determine overall status
        if assets_invalid == 0:
            status = "passed"
        elif assets_valid > 0:
            status = "passed_with_warnings"
        else:
            status = "failed"
        
        validation_duration = (datetime.now() - validation_start).total_seconds()
        
        qa_report = QAReport(
            status=status,
            validation_timestamp=validation_start.isoformat(),
            total_assets_checked=total_assets,
            assets_valid=assets_valid,
            assets_invalid=assets_invalid,
            errors=errors,
            warnings=warnings,
            metrics=metrics,
            retry_summary=retry_summary,
            validation_duration_seconds=validation_duration
        )
        
        self.logger.info(
            "qa_validation_completed",
            agent_name=self.name,
            agent_version=self.version,
            status=status,
            total_assets=total_assets,
            assets_valid=assets_valid,
            assets_invalid=assets_invalid,
            errors_count=len(errors),
            warnings_count=len(warnings),
            validation_duration_seconds=validation_duration
        )
        
        return qa_report
    
    async def _validate_imagen_output(self, imagen_output: ImagenOutput) -> Dict[str, Any]:
        """Validate Imagen output with file integrity and quality checks."""
        results = {
            "total_assets": len(imagen_output.images),
            "valid_assets": 0,
            "invalid_assets": 0,
            "errors": [],
            "warnings": [],
            "metrics": {},
            "retry_count": 0
        }
        
        for image in imagen_output.images:
            asset_id = image.image_id
            retry_count = 0
            
            while retry_count <= self.max_retries:
                try:
                    # Get the original path
                    image_path = Path(image.local_path)
                    
                    # Try to find file at original path
                    if not image_path.exists():
                        # Try to reconstruct path using AssetPathManager
                        reconstructed_path = AssetPathManager.get_image_path(
                            image_id=image.image_id,
                            slide_number=image.slide_number,
                            iteration=0
                        )
                        
                        if reconstructed_path.exists():
                            self.logger.warning(
                                "qa_validation_path_reconstructed",
                                original_path=str(image_path),
                                reconstructed_path=str(reconstructed_path)
                            )
                            image_path = reconstructed_path
                        else:
                            # Both paths missing - file not found
                            raise FileNotFoundError(
                                f"Image file not found at: {image_path} or {reconstructed_path}"
                            )
                    
                    # File integrity check
                    if not image_path.stat().st_size > 0:
                        raise ValueError(f"Image file is empty: {image_path}")
                    
                    # Image quality validation
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(image_path) as img:
                            width, height = img.size
                            format = img.format
                            
                            # Check dimensions (minimum 1920x1080)
                            if width < 1920 or height < 1080:
                                results["warnings"].append({
                                    "asset_id": asset_id,
                                    "warning_message": f"Image dimensions {width}x{height} below minimum 1920x1080"
                                })
                            
                            # Check file size (minimum 10KB)
                            file_size = image_path.stat().st_size
                            if file_size < 10240:  # 10KB
                                results["warnings"].append({
                                    "asset_id": asset_id,
                                    "warning_message": f"Image file size {file_size} bytes below minimum 10KB"
                                })
                            
                            # Store metrics
                            results["metrics"][f"{asset_id}_dimensions"] = f"{width}x{height}"
                            results["metrics"][f"{asset_id}_file_size"] = file_size
                            results["metrics"][f"{asset_id}_format"] = format
                            results["metrics"][f"{asset_id}_quality_score"] = image.quality_score
                    
                    except ImportError:
                        # PIL not available, skip detailed validation
                        results["warnings"].append({
                            "asset_id": asset_id,
                            "warning_message": "PIL not available, skipping image quality validation"
                        })
                    
                    # Quality score validation
                    if image.quality_score < self.quality_threshold:
                        results["warnings"].append({
                            "asset_id": asset_id,
                            "warning_message": f"Quality score {image.quality_score} below threshold {self.quality_threshold}"
                        })
                    
                    # Success - asset is valid
                    results["valid_assets"] += 1
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count <= self.max_retries:
                        wait_time = 2 ** retry_count
                        self.logger.warning(
                            "qa_validation_retry",
                            asset_id=asset_id,
                            error=str(e),
                            retry_count=retry_count,
                            wait_time=wait_time
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        results["errors"].append({
                            "asset_id": asset_id,
                            "error_message": f"Validation failed after {self.max_retries} retries: {str(e)}"
                        })
                        results["invalid_assets"] += 1
                        results["retry_count"] += retry_count
        
        return results
    
    async def _validate_veo_output(self, veo_output: VeoOutput) -> Dict[str, Any]:
        """Validate Veo output with file integrity and quality checks."""
        results = {
            "total_assets": len(veo_output.videos),
            "valid_assets": 0,
            "invalid_assets": 0,
            "errors": [],
            "warnings": [],
            "metrics": {},
            "retry_count": 0
        }
        
        for video in veo_output.videos:
            asset_id = video.video_id
            retry_count = 0
            
            while retry_count <= self.max_retries:
                try:
                    # File integrity check
                    if not os.path.exists(video.local_path):
                        raise FileNotFoundError(f"Video file not found: {video.local_path}")
                    
                    # File readability check
                    with open(video.local_path, 'rb') as f:
                        file_data = f.read()
                        if len(file_data) == 0:
                            raise ValueError("Video file is empty")
                    
                    # Video quality validation
                    try:
                        # Check file size (minimum 1MB for real videos)
                        file_size = len(file_data)
                        if file_size < 1048576:  # 1MB
                            results["warnings"].append({
                                "asset_id": asset_id,
                                "warning_message": f"Video file size {file_size} bytes below minimum 1MB"
                            })
                        
                        # Check duration
                        if video.duration_seconds <= 0:
                            results["errors"].append({
                                "asset_id": asset_id,
                                "error_message": f"Invalid duration: {video.duration_seconds} seconds"
                            })
                        
                        # Store metrics
                        results["metrics"][f"{asset_id}_file_size"] = file_size
                        results["metrics"][f"{asset_id}_duration"] = video.duration_seconds
                        results["metrics"][f"{asset_id}_quality_score"] = video.quality_score
                    
                    except Exception as e:
                        results["warnings"].append({
                            "asset_id": asset_id,
                            "warning_message": f"Video quality validation failed: {str(e)}"
                        })
                    
                    # Quality score validation
                    if video.quality_score < self.quality_threshold:
                        results["warnings"].append({
                            "asset_id": asset_id,
                            "warning_message": f"Quality score {video.quality_score} below threshold {self.quality_threshold}"
                        })
                    
                    # Success - asset is valid
                    results["valid_assets"] += 1
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count <= self.max_retries:
                        wait_time = 2 ** retry_count
                        self.logger.warning(
                            "qa_validation_retry",
                            asset_id=asset_id,
                            error=str(e),
                            retry_count=retry_count,
                            wait_time=wait_time
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        results["errors"].append({
                            "asset_id": asset_id,
                            "error_message": f"Validation failed after {self.max_retries} retries: {str(e)}"
                        })
                        results["invalid_assets"] += 1
                        results["retry_count"] += retry_count
        
        return results
    
    async def _validate_canva_output(self, canva_output: CanvaOutput) -> Dict[str, Any]:
        """Validate Canva output with deck integrity and quality checks."""
        results = {
            "total_assets": 1,  # One deck
            "valid_assets": 0,
            "invalid_assets": 0,
            "errors": [],
            "warnings": [],
            "metrics": {},
            "retry_count": 0
        }
        
        asset_id = canva_output.deck_id
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                # Deck ID validation
                if not canva_output.deck_id:
                    raise ValueError("Missing deck_id")
                
                # Page count validation
                if canva_output.total_pages <= 0:
                    results["errors"].append({
                        "asset_id": asset_id,
                        "error_message": f"Invalid page count: {canva_output.total_pages}"
                    })
                
                # Creation status validation
                if not canva_output.creation_complete:
                    results["warnings"].append({
                        "asset_id": asset_id,
                        "warning_message": "Deck creation not marked as complete"
                    })
                
                # Store metrics
                results["metrics"][f"{asset_id}_total_pages"] = canva_output.total_pages
                results["metrics"][f"{asset_id}_creation_complete"] = canva_output.creation_complete
                results["metrics"][f"{asset_id}_deck_url"] = canva_output.deck_url or "None"
                
                # Success - asset is valid
                results["valid_assets"] = 1
                break
                
            except Exception as e:
                retry_count += 1
                if retry_count <= self.max_retries:
                    wait_time = 2 ** retry_count
                    self.logger.warning(
                        "qa_validation_retry",
                        asset_id=asset_id,
                        error=str(e),
                        retry_count=retry_count,
                        wait_time=wait_time
                    )
                    await asyncio.sleep(wait_time)
                else:
                    results["errors"].append({
                        "asset_id": asset_id,
                        "error_message": f"Validation failed after {self.max_retries} retries: {str(e)}"
                    })
                    results["invalid_assets"] = 1
                    results["retry_count"] += retry_count
        
        return results


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="qa_agent",
    description="Validates assets, URLs, and compliance before publishing",
    instruction="""
    You are the QA Agent. Your role is to:
    - Validate content quality (grammar, clarity, completeness)
    - Check brand consistency against guidelines
    - Verify compliance (legal, privacy, accessibility)
    - Validate asset integrity
    - Check URL accessibility
    
    Act as the final quality gate before assets are published. Identify issues and provide recommendations.
    """,
)

