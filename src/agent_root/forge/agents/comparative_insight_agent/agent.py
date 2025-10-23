"""
Comparative Insight Agent
Benchmarks ideas against successful startups using GTM playbook data.
"""

from typing import Type
from pydantic import BaseModel

from google.adk import Agent

from app.core.base_agent import BaseAgent
from app.core.schemas import IdeationOutput, ComparativeInsightOutput, BenchmarkCompany


class ComparativeInsightAgent(BaseAgent):
    """
    Comparative Insight Agent analyzes the startup idea against successful companies
    and provides GTM strategy recommendations based on historical data.
    
    Key functions:
    - Identify similar successful companies
    - Extract proven GTM strategies
    - Recommend market positioning
    - Identify competitive advantages
    - Surface potential challenges
    - Highlight investor appeal factors
    
    Phase 1: Returns mock benchmark data
    Phase 2: Will integrate with playbook.mcp for real GTM playbook data
    """
    
    def __init__(self):
        super().__init__(
            name="ComparativeInsightAgent",
            description="Benchmarks ideas vs. successful startups using GTM playbook data",
            version="1.0.0"
        )
    
    @property
    def input_schema(self) -> Type[BaseModel]:
        return IdeationOutput
    
    @property
    def output_schema(self) -> Type[BaseModel]:
        return ComparativeInsightOutput
    
    async def run(self, input_data: IdeationOutput) -> ComparativeInsightOutput:
        """
        Perform comparative analysis against successful startups.
        
        Args:
            input_data: Ideation output with ICPs and market context
            
        Returns:
            Comparative insights with benchmarks and GTM strategies
        """
        self.logger.info(
            "comparative_analysis_started",
            idea_preview=input_data.expanded_idea[:100]
        )
        
        # TODO Phase 2: Integrate playbook.mcp for GTM strategy database
        # TODO: Query similar companies from YC, Sequoia, a16z portfolios
        # TODO: Use Gemini to extract and synthesize GTM strategies
        # TODO: Integrate vcprofile.mcp for investor preference tuning
        
        # Phase 1: Return structured mock data
        output = ComparativeInsightOutput(
            benchmark_companies=[
                BenchmarkCompany(
                    company_name="Benchmark Company A",
                    similarity_score=0.87,
                    key_strategies=[
                        "Direct B2B sales approach",
                        "Strategic partnerships with industry leaders",
                        "Product-led growth strategy"
                    ],
                    funding_stage="Series B",
                    market_approach="Enterprise-first, then SMB expansion"
                ),
                BenchmarkCompany(
                    company_name="Benchmark Company B",
                    similarity_score=0.76,
                    key_strategies=[
                        "Freemium model for user acquisition",
                        "Community-driven growth",
                        "Content marketing leadership"
                    ],
                    funding_stage="Series A",
                    market_approach="Bottom-up adoption, viral growth"
                )
            ],
            gtm_strategies=[
                "Start with a focused vertical market",
                "Build strategic partnerships early",
                "Implement product-led growth tactics",
                "Focus on customer success and retention"
            ],
            market_positioning="Premium solution targeting mid-market and enterprise customers",
            competitive_advantages=[
                "First-mover advantage in specific niche",
                "Superior technology stack",
                "Strong network effects potential",
                "Better unit economics than incumbents"
            ],
            potential_challenges=[
                "Market education required for new category",
                "Competition from established players",
                "Multi-sided marketplace dynamics",
                "Regulatory compliance considerations"
            ],
            investor_appeal_factors=[
                "Large addressable market ($XB TAM)",
                "High-growth trajectory potential",
                "Strong founder-market fit",
                "Proven GTM playbook from similar companies",
                "Recurring revenue business model",
                "Clear path to profitability"
            ]
        )
        
        self.logger.info(
            "comparative_analysis_completed",
            benchmarks_found=len(output.benchmark_companies),
            strategies_identified=len(output.gtm_strategies),
            avg_similarity_score=sum(
                c.similarity_score for c in output.benchmark_companies
            ) / len(output.benchmark_companies) if output.benchmark_companies else 0
        )
        
        return output


# ADK root_agent for A2A compatibility
root_agent = Agent(
    name="comparative_insight_agent",
    description="Benchmarks ideas vs. successful startups using GTM playbook data",
    instruction="""
    You are the Comparative Insight Agent. Your role is to:
    - Identify similar successful companies and startups
    - Extract proven GTM strategies from benchmark companies
    - Recommend market positioning based on analysis
    - Identify competitive advantages
    - Surface potential challenges
    - Highlight investor appeal factors
    
    Use your knowledge of successful startups and GTM strategies to provide actionable insights.
    """,
)

