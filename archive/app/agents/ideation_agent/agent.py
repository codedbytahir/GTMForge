"""
Ideation Agent
Expands user input into structured ICPs, pain points, and market context.
"""

from typing import Type
from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import StartupIdeaInput, IdeationOutput, ICP


class IdeationAgent(BaseAgent):
    """
    Ideation Agent expands a raw startup idea into structured components:
    - Ideal Customer Profiles (ICPs)
    - Key pain points being addressed
    - Market context and opportunity
    - Value proposition
    - Unique differentiators
    
    This is the first agent in the GTMForge pipeline, transforming user input
    into structured data for downstream agents.
    
    Phase 1: Returns mock data structure
    Phase 2: Will integrate with Gemini 2.0 for actual ideation
    """
    
    def __init__(self):
        super().__init__(
            name="IdeationAgent",
            description="Expands startup ideas into ICPs, pain points, and market context",
            version="1.0.0"
        )
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return StartupIdeaInput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return IdeationOutput
    
    async def run(self, input_data: StartupIdeaInput) -> IdeationOutput:
        """
        Execute ideation analysis on the startup idea.
        
        Args:
            input_data: User's startup idea with optional context
            
        Returns:
            Structured ideation output with ICPs, pain points, and context
        """
        self.logger.info(
            "ideation_started",
            idea_preview=input_data.idea[:100],
            industry=input_data.industry
        )
        
        # TODO Phase 2: Integrate Gemini 2.0 API for actual ideation
        # TODO: Use research.mcp for market context gathering
        # TODO: Apply prompt templates from /prompts directory
        
        # Phase 1: Return structured mock data
        output = IdeationOutput(
            expanded_idea=f"Enhanced version of: {input_data.idea}. "
                         f"This platform leverages AI and modern technology to solve critical "
                         f"challenges in the {input_data.industry or 'target'} industry.",
            icps=[
                ICP(
                    segment_name="Primary Customer Segment",
                    demographics="Target demographic profile based on industry analysis",
                    pain_points=[
                        "Primary pain point identified from idea",
                        "Secondary pain point affecting segment",
                        "Tertiary operational challenge"
                    ],
                    behaviors="Technology adoption patterns and decision-making processes"
                )
            ],
            key_pain_points=[
                f"Core problem in {input_data.industry or 'the market'}",
                "Inefficiency in current solutions",
                "Gap in market offerings"
            ],
            market_context=f"The {input_data.industry or 'target'} market is experiencing "
                          f"significant transformation. Key trends include digital adoption, "
                          f"changing customer expectations, and increased competition.",
            value_proposition=f"Unique solution addressing {input_data.idea}",
            unique_differentiators=[
                "AI-powered automation",
                "Modern technology stack",
                "Superior user experience"
            ]
        )
        
        self.logger.info(
            "ideation_completed",
            icps_generated=len(output.icps),
            pain_points_identified=len(output.key_pain_points),
            differentiators=len(output.unique_differentiators)
        )
        
        return output


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="ideation_agent",
    description="Expands startup ideas into ICPs, pain points, and market context",
    instruction="""
    You are the Ideation Agent. Your role is to expand raw startup ideas into structured components:
    - Identify and profile Ideal Customer Profiles (ICPs)
    - Extract and articulate key pain points
    - Analyze market context and opportunity
    - Define value proposition
    - Identify unique differentiators
    
    Take the user's input idea and transform it into a comprehensive, structured analysis.
    """,
)

