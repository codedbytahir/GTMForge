"""
QA Agent
Validates assets, URLs, and ensures compliance before publishing.
"""

from typing import Type
from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import PromptForgeOutput, QAValidationOutput, ValidationIssue


class QAAgent(BaseAgent):
    """
    QA Agent performs comprehensive quality assurance on all generated content:
    - Content quality validation
    - Brand consistency checks
    - Compliance verification
    - Asset integrity validation
    - URL accessibility checks
    
    Acts as the final quality gate before assets are published.
    
    Phase 1: Returns mock validation results
    Phase 2: Will implement actual validation logic
    Phase 3: Will validate real URLs and generated assets
    """
    
    def __init__(self):
        super().__init__(
            name="QAAgent",
            description="Validates assets, URLs, and compliance before publishing",
            version="1.0.0"
        )
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return PromptForgeOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return QAValidationOutput
    
    async def run(self, input_data: PromptForgeOutput) -> QAValidationOutput:
        """
        Perform quality assurance on generated prompts and content.
        
        Args:
            input_data: Prompt specifications for all visual assets
            
        Returns:
            Validation results with quality scores and issues
        """
        self.logger.info(
            "qa_validation_started",
            image_prompts=len(input_data.image_prompts),
            video_prompts=len(input_data.video_prompts)
        )
        
        # TODO Phase 2: Implement actual validation logic
        # TODO: Content quality checks (grammar, clarity, completeness)
        # TODO: Brand consistency validation against guidelines
        # TODO: Compliance checks (legal, privacy, accessibility)
        # TODO Phase 3: Validate actual generated assets and URLs
        # TODO Phase 3: Check image/video quality and format
        
        # Phase 1: Mock validation with sample issues
        issues = []
        
        # Example validation checks
        if len(input_data.image_prompts) == 0:
            issues.append(ValidationIssue(
                severity="critical",
                category="content",
                description="No image prompts generated",
                affected_component="image_prompts",
                recommendation="Ensure Prompt Forge Agent generates image prompts for all slides"
            ))
        
        if len(input_data.video_prompts) == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="content",
                description="No video prompts generated",
                affected_component="video_prompts",
                recommendation="Consider adding video content for enhanced engagement"
            ))
        
        # Check prompt quality (mock validation)
        for prompt in input_data.image_prompts:
            if len(prompt.prompt_text) < 50:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="quality",
                    description=f"Prompt for slide {prompt.target_slide} may be too short",
                    affected_component=prompt.prompt_id,
                    recommendation="Expand prompt with more specific visual details"
                ))
        
        # Brand consistency check
        required_colors = ["steel", "blue"]
        theme_lower = input_data.visual_theme.lower()
        if not all(color in theme_lower for color in required_colors):
            issues.append(ValidationIssue(
                severity="info",
                category="brand",
                description="Visual theme may not fully align with brand colors",
                affected_component="visual_theme",
                recommendation="Ensure Dark Steel and Tech Blue are prominently featured"
            ))
        
        # Calculate quality scores (mock scoring)
        content_quality_score = 92.5 if len(issues) <= 2 else 85.0
        brand_consistency_score = 88.0 if len([i for i in issues if i.category == "brand"]) == 0 else 75.0
        
        # Determine if validation passed
        critical_issues = [i for i in issues if i.severity == "critical"]
        validation_passed = len(critical_issues) == 0
        
        output = QAValidationOutput(
            validation_passed=validation_passed,
            issues=issues,
            content_quality_score=content_quality_score,
            brand_consistency_score=brand_consistency_score,
            compliance_checks_passed=True,  # Mock: assumes compliance
            recommendations=[
                "All prompts should include specific visual details",
                "Maintain consistent visual theme across all assets",
                "Ensure accessibility standards are met in final renders",
                "Test all links and URLs before final publication"
            ]
        )
        
        self.logger.info(
            "qa_validation_completed",
            validation_passed=output.validation_passed,
            total_issues=len(output.issues),
            critical_issues=len(critical_issues),
            content_quality_score=output.content_quality_score,
            brand_consistency_score=output.brand_consistency_score
        )
        
        return output


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

