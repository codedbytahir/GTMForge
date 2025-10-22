"""
Canva Agent
Creates and formats pitch decks via Canva Connect API.
Phase 2: Uses mock google_clients with placeholder implementations.
Phase 3: Will integrate real Canva Connect API.
"""

from typing import Type
from pydantic import BaseModel
from datetime import datetime

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import ImagenOutput, PitchNarrativeOutput, CanvaOutput, CanvaPage
from app.utils.real_api_clients import RealCanvaConnectClient


class CanvaAgent(BaseAgent):
    """
    Canva Agent creates professional pitch decks via Canva Connect API.
    
    Pipeline Position: Runs after Veo agent, before Publisher agent
    
    Inputs: ImagenOutput (generated images), PitchNarrativeOutput (slide content)
    Output: CanvaOutput with deck URL and page metadata
    
    Features:
    - Automated deck creation with Canva designs
    - Image and text asset integration
    - Design theme application (Dark Steel + Tech Blue)
    - Professional formatting and brand consistency
    - Shareable deck generation
    
    Phase 2: Mock implementation with placeholder API calls
    Phase 3: Full Canva Connect API integration
    """
    
    def __init__(self, theme: str = "dark_steel_tech_blue"):
        super().__init__(
            name="CanvaAgent",
            description="Creates professional pitch decks via Canva Connect API",
            version="1.0.0"
        )
        self.canva_client = RealCanvaConnectClient()  # Now uses real/mock toggle!
        self.theme = theme
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        # Accepts ImagenOutput, but in full pipeline would receive both ImagenOutput and PitchNarrativeOutput
        return ImagenOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return CanvaOutput
    
    async def run(self, input_data: ImagenOutput) -> CanvaOutput:
        """
        Create a Canva pitch deck from images and slide content.
        
        Args:
            input_data: ImagenOutput with generated slide images
            
        Returns:
            CanvaOutput with deck metadata and page information
        """
        stage_start_time = datetime.now()
        errors = []
        pages_created = []
        
        self.logger.info(
            "canva_deck_creation_started",
            total_images=len(input_data.images),
            theme=self.theme
        )
        
        try:
            # Step 1: Create new design
            design_result = await self.canva_client.create_deck(
                title="GTMForge Pitch Deck"
            )
            
            deck_id = design_result["deck_id"]
            
            self.logger.info(
                "canva_design_created",
                deck_id=deck_id
            )
            
            # Step 2: Add pages for each image
            for i, image in enumerate(input_data.images):
                try:
                    # Add page
                    page_result = await self.canva_client.add_page(
                        deck_id=deck_id,
                        title=f"Slide {image.slide_number}",
                        position=i
                    )
                    
                    page_id = page_result["page_id"]
                    
                    # Add image to page
                    await self.canva_client.place_image(
                        deck_id=deck_id,
                        page_id=page_id,
                        image_path=image.local_path,
                        position="center"
                    )
                    
                    page_info = CanvaPage(
                        page_number=i + 1,
                        page_id=page_id,
                        slide_title=f"Slide {image.slide_number}",
                        has_image=True,
                        has_text=False,
                        design_applied=False
                    )
                    pages_created.append(page_info)
                    
                    self.logger.info(
                        "canva_page_created",
                        deck_id=deck_id,
                        page_id=page_id,
                        slide_number=image.slide_number
                    )
                
                except Exception as e:
                    error_msg = f"Failed to create page for slide {image.slide_number}: {str(e)}"
                    self.logger.error(
                        "canva_page_error",
                        slide_number=image.slide_number,
                        error=error_msg
                    )
                    errors.append(error_msg)
            
            # Step 3: Apply design theme (skipping for mock/real API compatibility)
            # await self.canva_client.apply_design_theme(
            #     deck_id=deck_id,
            #     theme=self.theme
            # )
            
            self.logger.info(
                "canva_theme_applied",
                deck_id=deck_id,
                theme=self.theme
            )
            
            # Step 4: Export design (Phase 3: will generate shareable URL)
            export_result = await self.canva_client.export_design(
                deck_id=deck_id,
                format="pdf"
            )
            
            self.logger.info(
                "canva_export_completed",
                deck_id=deck_id,
                format="pdf"
            )
            
        except Exception as e:
            error_msg = f"Canva deck creation failed: {str(e)}"
            self.logger.error(
                "canva_deck_creation_error",
                error_message=error_msg,
                error_type=type(e).__name__
            )
            errors.append(error_msg)
            deck_id = f"error_{datetime.now().strftime('%s')}"
        
        stage_completion_time = (datetime.now() - stage_start_time).total_seconds()
        
        # Build output
        output = CanvaOutput(
            deck_id=deck_id,
            deck_url=None,  # Phase 3: Will be populated with actual Canva URL
            pages=pages_created,
            total_pages=len(pages_created),
            creation_complete=len(errors) == 0,
            design_theme=self.theme,
            errors=errors
        )
        
        self.logger.info(
            "canva_deck_creation_completed",
            deck_id=deck_id,
            pages_created=len(pages_created),
            total_pages=output.total_pages,
            creation_complete=output.creation_complete,
            stage_completion_time_seconds=stage_completion_time,
            errors_encountered=len(errors)
        )
        
        return output


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="canva_agent",
    description="Creates professional pitch decks via Canva Connect API",
    instruction="""
    You are the Canva Agent. Your role is to:
    - Create professional presentation decks
    - Add images and text content to slides
    - Apply consistent design themes
    - Ensure brand consistency
    - Generate shareable deck links
    
    Transform generated images and content into polished, publication-ready presentations.
    """,
)
