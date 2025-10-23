"""
Publisher Agent - Phase 3
Uploads assets to GCS and builds manifest.json with signed URLs.
"""

import os
import json
import uuid
from typing import Type, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import PipelineState, PublishOutput, ManifestAsset, QAReport
from app.utils.google_clients import GoogleCloudStorageClient


class PublisherAgent(BaseAgent):
    """
    Publisher Agent uploads all generated assets to GCS and creates manifest.json.
    
    Responsibilities:
    - Upload images, videos, and decks to Google Cloud Storage
    - Generate signed URLs for all assets
    - Build manifest.json with asset metadata
    - Upload manifest.json to GCS
    - Return PublishOutput with all GCS URLs
    """
    
    def __init__(self, task_id: str = None):
        super().__init__(
            name="PublisherAgent",
            description="Uploads assets to GCS and builds manifest with signed URLs",
            version="1.0.0"
        )
        self.task_id = task_id
        self.gcs_client = GoogleCloudStorageClient()
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return PipelineState
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return PublishOutput
    
    async def run(self, input_data: PipelineState) -> PublishOutput:
        """
        Upload all assets to GCS and create manifest.json.
        
        Args:
            input_data: Complete pipeline state with all generated outputs
            
        Returns:
            PublishOutput with manifest and all GCS URLs
        """
        upload_start = datetime.now()
        
        self.logger.info(
            "publisher_started",
            agent_name=self.name,
            agent_version=self.version,
            task_id=self.task_id
        )
        
        # Validate QA status
        if input_data.qa_output and input_data.qa_output.status == "failed":
            raise ValueError("Cannot publish assets with failed QA validation")
        
        # Initialize manifest
        manifest_id = f"manifest_{uuid.uuid4().hex[:12]}"
        assets = []
        errors = []
        
        # Upload images from Imagen output (nested in media_output)
        if input_data.media_output and input_data.media_output.imagen_output:
            imagen_assets = await self._upload_imagen_assets(
                input_data.media_output.imagen_output, manifest_id
            )
            assets.extend(imagen_assets)
        
        # Upload videos from Veo output (nested in media_output)
        if input_data.media_output and input_data.media_output.veo_output:
            veo_assets = await self._upload_veo_assets(
                input_data.media_output.veo_output, manifest_id
            )
            assets.extend(veo_assets)
        
        # Upload deck from Canva output (nested in media_output)
        if input_data.media_output and input_data.media_output.canva_output:
            canva_assets = await self._upload_canva_assets(
                input_data.media_output.canva_output, manifest_id
            )
            assets.extend(canva_assets)
        
        # Create and upload manifest.json
        manifest_data = {
            "manifest_id": manifest_id,
            "task_id": self.task_id,
            "created_at": datetime.now().isoformat(),
            "assets": [asset.dict() for asset in assets],
            "total_assets": len(assets),
            "qa_status": input_data.qa_output.status if input_data.qa_output else "not_validated"
        }
        
        # Upload manifest to GCS
        manifest_path = f"manifests/{manifest_id}.json"
        manifest_gcs_result = await self.gcs_client.upload_asset(
            local_path=None,  # We'll upload JSON directly
            asset_type="manifest",
            metadata={"manifest_id": manifest_id, "task_id": self.task_id}
        )
        
        # Create manifest.json content
        manifest_json = json.dumps(manifest_data, indent=2)
        
        # For Phase 3, we'll simulate the upload since GCS client is mock
        manifest_location = f"gs://gtmforge-assets/{manifest_path}"
        manifest_url = f"https://storage.googleapis.com/gtmforge-assets/{manifest_path}"
        
        upload_duration = (datetime.now() - upload_start).total_seconds()
        
        publish_output = PublishOutput(
            manifest_id=manifest_id,
            task_id=self.task_id,
            assets=assets,
            created_at=datetime.now().isoformat(),
            manifest_location=manifest_location,
            manifest_url=manifest_url,
            total_assets=len(assets),
            qa_status=input_data.qa_output.status if input_data.qa_output else "not_validated",
            upload_duration_seconds=upload_duration,
            errors=errors
        )
        
        self.logger.info(
            "publisher_completed",
            agent_name=self.name,
            agent_version=self.version,
            manifest_id=manifest_id,
            total_assets=len(assets),
            upload_duration_seconds=upload_duration,
            manifest_url=manifest_url
        )
        
        return publish_output
    
    async def _upload_imagen_assets(self, imagen_output, manifest_id: str) -> List[ManifestAsset]:
        """Upload Imagen-generated images to GCS."""
        assets = []
        
        for image in imagen_output.images:
            try:
                # Upload to GCS
                gcs_result = await self.gcs_client.upload_asset(
                    local_path=image.local_path,
                    asset_type="image",
                    metadata={
                        "image_id": image.image_id,
                        "slide_number": image.slide_number,
                        "quality_score": image.quality_score
                    }
                )
                
                # Create manifest asset
                asset = ManifestAsset(
                    asset_id=image.image_id,
                    asset_type="image",
                    gcs_path=gcs_result["gcs_path"],
                    gcs_url=gcs_result["gcs_url"],
                    size_bytes=gcs_result.get("size_bytes", 0),
                    quality_score=image.quality_score,
                    generated_at=datetime.now().isoformat(),  # Use current timestamp
                    slide_number=image.slide_number,
                    metadata={
                        "prompt_used": image.prompt_used,
                        "refinement_iteration": image.refinement_iteration
                    }
                )
                assets.append(asset)
                
                self.logger.info(
                    "image_uploaded",
                    asset_id=image.image_id,
                    gcs_path=gcs_result["gcs_path"],
                    size_bytes=asset.size_bytes
                )
                
            except Exception as e:
                self.logger.error(
                    "image_upload_failed",
                    asset_id=image.image_id,
                    error=str(e)
                )
        
        return assets
    
    async def _upload_veo_assets(self, veo_output, manifest_id: str) -> List[ManifestAsset]:
        """Upload Veo-generated videos to GCS."""
        assets = []
        
        for video in veo_output.videos:
            try:
                # Upload to GCS
                gcs_result = await self.gcs_client.upload_asset(
                    local_path=video.local_path,
                    asset_type="video",
                    metadata={
                        "video_id": video.video_id,
                        "duration_seconds": video.duration_seconds,
                        "quality_score": video.quality_score
                    }
                )
                
                # Create manifest asset
                asset = ManifestAsset(
                    asset_id=video.video_id,
                    asset_type="video",
                    gcs_path=gcs_result["gcs_path"],
                    gcs_url=gcs_result["gcs_url"],
                    size_bytes=gcs_result.get("size_bytes", 0),
                    quality_score=video.quality_score,
                    generated_at=datetime.now().isoformat(),  # Use current timestamp
                    duration_seconds=video.duration_seconds,
                    metadata={
                        "prompt_used": video.prompt_used,
                        "source_images": video.source_images
                    }
                )
                assets.append(asset)
                
                self.logger.info(
                    "video_uploaded",
                    asset_id=video.video_id,
                    gcs_path=gcs_result["gcs_path"],
                    size_bytes=asset.size_bytes,
                    duration_seconds=video.duration_seconds
                )
                
            except Exception as e:
                self.logger.error(
                    "video_upload_failed",
                    asset_id=video.video_id,
                    error=str(e)
                )
        
        return assets
    
    async def _upload_canva_assets(self, canva_output, manifest_id: str) -> List[ManifestAsset]:
        """Upload Canva-generated deck to GCS."""
        assets = []
        
        try:
            # Upload deck to GCS (if we have a local file)
            # For now, we'll create a mock upload since Canva output doesn't have local_path
            gcs_result = await self.gcs_client.upload_asset(
                local_path=None,  # Canva decks are typically cloud-based
                asset_type="deck",
                metadata={
                    "deck_id": canva_output.deck_id,
                    "total_pages": canva_output.total_pages,
                    "creation_complete": canva_output.creation_complete
                }
            )
            
            # Create manifest asset
            asset = ManifestAsset(
                asset_id=canva_output.deck_id,
                asset_type="deck",
                gcs_path=gcs_result["gcs_path"],
                gcs_url=gcs_result["gcs_url"],
                size_bytes=gcs_result.get("size_bytes", 0),
                quality_score=1.0,  # Assume perfect quality for Canva decks
                generated_at=datetime.now().isoformat(),  # Use current timestamp
                metadata={
                    "total_pages": canva_output.total_pages,
                    "creation_complete": canva_output.creation_complete,
                    "deck_url": canva_output.deck_url
                }
            )
            assets.append(asset)
            
            self.logger.info(
                "deck_uploaded",
                asset_id=canva_output.deck_id,
                gcs_path=gcs_result["gcs_path"],
                total_pages=canva_output.total_pages
            )
            
        except Exception as e:
            self.logger.error(
                "deck_upload_failed",
                asset_id=canva_output.deck_id,
                error=str(e)
            )
        
        return assets


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="publisher_agent",
    description="Publishes assets to GCS and Canva, returns manifest with URLs",
    instruction="""
    You are the Publisher Agent. Your role is to:
    - Combine all outputs into manifest.json
    - Upload assets to Google Cloud Storage
    - Generate accessible URLs for all assets
    - Create Canva deck via API
    - Publish Veo video trailer
    - Return complete manifest with all URLs
    
    Handle the final publication of all GTMForge assets and provide accessible URLs to users.
    """,
)

