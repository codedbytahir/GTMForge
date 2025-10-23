"""
Pitch Writer Agent
Builds slide-by-slide narratives and talking points for pitch decks.
"""

from typing import Type
from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import ComparativeInsightOutput, PitchNarrativeOutput, SlideContent


class PitchWriterAgent(BaseAgent):
    """
    Pitch Writer Agent creates compelling pitch deck narratives with:
    - Slide-by-slide structure
    - Key messages and talking points
    - Visual content direction
    - Overall narrative arc
    - Target investor profiling
    
    Synthesizes insights from ideation and comparative analysis into
    a cohesive investor-ready story.
    
    Phase 1: Returns mock pitch structure
    Phase 2: Will integrate with Gemini 2.0 for narrative generation
    """
    
    def __init__(self):
        super().__init__(
            name="PitchWriterAgent",
            description="Builds slide narratives, talking points, and content direction",
            version="1.0.0"
        )
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return ComparativeInsightOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return PitchNarrativeOutput
    
    async def run(self, input_data: ComparativeInsightOutput) -> PitchNarrativeOutput:
        """
        Generate pitch deck narrative and slide structure dynamically based on input.
        
        Args:
            input_data: Comparative insights with GTM strategies
            
        Returns:
            Complete pitch narrative with slide-by-slide content
        """
        self.logger.info(
            "pitch_writing_started",
            benchmark_companies=len(input_data.benchmark_companies),
            gtm_strategies=len(input_data.gtm_strategies)
        )
        
        # TODO Phase 2: Integrate Gemini 2.0 for narrative generation
        # TODO: Use vcprofile.mcp to tailor pitch for specific investor types
        # TODO: Apply storytelling frameworks from prompts
        # TODO: Generate data visualizations recommendations
        
        # Phase 1: Dynamically generate slides based on input data
        slides = []
        slide_num = 1
        
        # Slide 1: The Problem (derived from challenges)
        if input_data.potential_challenges:
            slides.append(SlideContent(
                slide_number=slide_num,
                slide_title="The Problem",
                key_message=f"Critical challenges in the market: {input_data.potential_challenges[0]}",
                talking_points=input_data.potential_challenges[:3],
                content_direction="Bold problem statement with compelling statistics and visuals",
                data_points=None
            ))
            slide_num += 1
        
        # Slide 2: Our Solution (derived from market positioning)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="Our Solution",
            key_message=input_data.market_positioning,
            talking_points=input_data.competitive_advantages[:3] if len(input_data.competitive_advantages) >= 3 else input_data.competitive_advantages,
            content_direction="Product screenshots or demo flow, clean and modern",
            data_points=None
        ))
        slide_num += 1
        
        # Slide 3: Market Opportunity (always include)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="Market Opportunity",
            key_message="Large addressable market with strong growth trajectory",
            talking_points=[
                "Significant TAM in target market",
                "Multiple expansion opportunities identified",
                "Proven willingness to pay from similar companies"
            ],
            content_direction="Market sizing visualization, growth charts",
            data_points=["TAM analysis", "Growth rate", "Market segments"]
        ))
        slide_num += 1
        
        # Slide 4: Why Now (if we have benchmark companies showing timing)
        if input_data.benchmark_companies:
            why_now_points = []
            for company in input_data.benchmark_companies[:2]:
                why_now_points.append(f"{company.company_name} proved market timing with {company.funding_stage} funding")
            
            slides.append(SlideContent(
                slide_number=slide_num,
                slide_title="Why Now",
                key_message="Market conditions are optimal for this solution",
                talking_points=why_now_points + ["Technology enablers now mature", "Customer behavior has shifted"],
                content_direction="Timeline showing market evolution and key milestones",
                data_points=None
            ))
            slide_num += 1
        
        # Slide 5: Traction (placeholder for Phase 2)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="Traction",
            key_message="Early validation of product-market fit",
            talking_points=[
                "Initial customer validation underway",
                "Key partnerships in development",
                "Product development milestones achieved"
            ],
            content_direction="Growth charts, customer logos, key metrics",
            data_points=["Customer count", "Growth rate", "Engagement metrics"]
        ))
        slide_num += 1
        
        # Slide 6: Competitive Advantages (derived from input)
        if input_data.competitive_advantages:
            slides.append(SlideContent(
                slide_number=slide_num,
                slide_title="Competitive Advantages",
                key_message="Clear differentiation in the market",
                talking_points=input_data.competitive_advantages,
                content_direction="Competitive matrix or positioning map",
                data_points=None
            ))
            slide_num += 1
        
        # Slide 7: Go-to-Market Strategy (derived from benchmarks)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="Go-to-Market Strategy",
            key_message="Proven playbook from successful companies",
            talking_points=input_data.gtm_strategies,
            content_direction="GTM timeline and channel strategy",
            data_points=None
        ))
        slide_num += 1
        
        # Slide 8: Business Model (standard for all pitches)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="Business Model",
            key_message="Scalable revenue model with strong unit economics",
            talking_points=[
                "Revenue streams and pricing strategy",
                "Customer acquisition and lifetime value",
                "Path to profitability"
            ],
            content_direction="Revenue model breakdown, pricing tiers",
            data_points=["ARR", "Gross margin", "CAC/LTV ratio"]
        ))
        slide_num += 1
        
        # Slide 9: The Team (standard)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="The Team",
            key_message="Experienced team with domain expertise",
            talking_points=[
                "Founders with relevant background",
                "Advisory board with industry connections",
                "Key hires planned for growth"
            ],
            content_direction="Team photos, experience highlights",
            data_points=None
        ))
        slide_num += 1
        
        # Slide 10: Investor Appeal (derived from input)
        if input_data.investor_appeal_factors:
            slides.append(SlideContent(
                slide_number=slide_num,
                slide_title="Investment Opportunity",
                key_message="Compelling opportunity for investors",
                talking_points=input_data.investor_appeal_factors[:4],
                content_direction="Key investment highlights with visual emphasis",
                data_points=None
            ))
            slide_num += 1
        
        # Slide 11: The Ask (standard closing)
        slides.append(SlideContent(
            slide_number=slide_num,
            slide_title="The Ask",
            key_message="Seeking investment to accelerate growth",
            talking_points=[
                "Funding amount and allocation",
                "Key milestones to be achieved",
                "Expected runway and next funding stage"
            ],
            content_direction="Use of funds breakdown, milestone timeline",
            data_points=["Raise amount", "Runway months", "Key hires"]
        ))
        slide_num += 1
        
        # Generate elevator pitch dynamically
        elevator_pitch = (
            f"We're addressing {input_data.potential_challenges[0] if input_data.potential_challenges else 'critical market challenges'} "
            f"with {input_data.market_positioning}. "
            f"We're leveraging proven strategies from {input_data.benchmark_companies[0].company_name if input_data.benchmark_companies else 'successful companies'}, "
            f"and we're positioned to capture significant market share."
        )
        
        # Build narrative arc based on slides included
        narrative_components = [slide.slide_title for slide in slides[:6]]  # First 6 slides define the arc
        narrative_arc = " → ".join(narrative_components)
        
        # Determine target investor based on benchmark funding stages
        if input_data.benchmark_companies:
            stages = [c.funding_stage for c in input_data.benchmark_companies if c.funding_stage]
            common_stage = stages[0] if stages else "Series A"
            target_profile = f"{common_stage} investors focused on similar market opportunities"
        else:
            target_profile = "Series A investors focused on high-growth opportunities"
        
        output = PitchNarrativeOutput(
            deck_title=f"Pitch Deck - {input_data.market_positioning[:50]}",
            elevator_pitch=elevator_pitch,
            slides=slides,
            overall_narrative_arc=narrative_arc,
            target_investor_profile=target_profile,
            estimated_pitch_duration=len(slides)  # ~1 minute per slide
        )
        
        self.logger.info(
            "pitch_writing_completed",
            total_slides=len(output.slides),
            estimated_duration_minutes=output.estimated_pitch_duration,
            slides_generated_dynamically=True
        )
        
        return output


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="pitch_writer_agent",
    description="Builds slide narratives, talking points, and content direction",
    instruction="""
    You are the Pitch Writer Agent. Your role is to:
    - Create compelling pitch deck narratives
    - Build slide-by-slide structure with key messages
    - Develop talking points for each slide
    - Provide visual content direction
    - Craft overall narrative arc
    - Profile target investors
    
    Synthesize insights from previous agents into a cohesive, investor-ready story.
    """,
)

