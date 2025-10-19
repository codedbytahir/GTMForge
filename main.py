#!/usr/bin/env python3
"""
GTMForge Main Entry Point
CLI interface for testing the Phase 1 pipeline.
"""

import asyncio
import sys
import json
from typing import Optional

from app import GTMForgeOrchestrator, StartupIdeaInput, configure_logging, get_logger
from app.utils.config import get_config


def print_banner():
    """Print GTMForge banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ██████╗ ████████╗███╗   ███╗███████╗ ██████╗ ██████╗    ║
    ║  ██╔════╝ ╚══██╔══╝████╗ ████║██╔════╝██╔═══██╗██╔══██╗   ║
    ║  ██║  ███╗   ██║   ██╔████╔██║█████╗  ██║   ██║██████╔╝   ║
    ║  ██║   ██║   ██║   ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██╗   ║
    ║  ╚██████╔╝   ██║   ██║ ╚═╝ ██║██║     ╚██████╔╝██║  ██║   ║
    ║   ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ║
    ║                                                           ║
    ║            Multi-Agent GTM Automation Platform            ║
    ║                                                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def run_pipeline(
    idea: str,
    industry: Optional[str] = None,
    target_market: Optional[str] = None,
    additional_context: Optional[str] = None,
    output_file: Optional[str] = None
) -> None:
    """
    Run the GTMForge pipeline with the given startup idea.
    
    Args:
        idea: The core startup idea
        industry: Target industry (optional)
        target_market: Target market (optional)
        additional_context: Additional context (optional)
        output_file: Path to save output JSON (optional)
    """
    logger = get_logger(__name__)
    
    print_banner()
    print_section("Input Validation")
    
    # Create input
    startup_input = StartupIdeaInput(
        idea=idea,
        industry=industry,
        target_market=target_market,
        additional_context=additional_context
    )
    
    print(f"Idea: {startup_input.idea}")
    if startup_input.industry:
        print(f"Industry: {startup_input.industry}")
    if startup_input.target_market:
        print(f"Target Market: {startup_input.target_market}")
    
    print_section("Initializing GTMForge")
    
    # Initialize orchestrator
    orchestrator = GTMForgeOrchestrator()
    await orchestrator.initialize()
    
    print("✓ Orchestrator initialized")
    print("✓ All agents loaded")
    print("✓ MCP registry ready")
    
    # Display agent metadata
    print("\nAgent Pipeline:")
    agents = orchestrator.get_agent_metadata()
    for i, (name, metadata) in enumerate(agents.items(), 1):
        print(f"  {i}. {metadata['name']} v{metadata['version']}")
        print(f"     → {metadata['description']}")
    
    print_section("Running Pipeline")
    
    try:
        # Run the pipeline
        print("Starting pipeline execution...\n")
        pipeline_state = await orchestrator.run_pipeline(startup_input)
        
        print_section("Pipeline Results")
        
        # Display results
        print(f"✓ Session ID: {pipeline_state.session_id}")
        print(f"✓ Status: {pipeline_state.current_stage}")
        print(f"✓ Duration: {(pipeline_state.completed_at - pipeline_state.started_at).total_seconds():.2f}s")
        
        # Stage results
        print("\nStage Outputs:")
        
        if pipeline_state.ideation_output:
            print(f"\n  1. Ideation Agent")
            print(f"     - ICPs identified: {len(pipeline_state.ideation_output.icps)}")
            print(f"     - Pain points: {len(pipeline_state.ideation_output.key_pain_points)}")
            print(f"     - Differentiators: {len(pipeline_state.ideation_output.unique_differentiators)}")
        
        if pipeline_state.comparative_output:
            print(f"\n  2. Comparative Insight Agent")
            print(f"     - Benchmark companies: {len(pipeline_state.comparative_output.benchmark_companies)}")
            print(f"     - GTM strategies: {len(pipeline_state.comparative_output.gtm_strategies)}")
            print(f"     - Investor appeal factors: {len(pipeline_state.comparative_output.investor_appeal_factors)}")
        
        if pipeline_state.pitch_output:
            print(f"\n  3. Pitch Writer Agent")
            print(f"     - Deck title: {pipeline_state.pitch_output.deck_title}")
            print(f"     - Total slides: {len(pipeline_state.pitch_output.slides)}")
            print(f"     - Duration: {pipeline_state.pitch_output.estimated_pitch_duration} minutes")
        
        if pipeline_state.prompt_output:
            print(f"\n  4. Prompt Forge Agent")
            print(f"     - Image prompts: {len(pipeline_state.prompt_output.image_prompts)}")
            print(f"     - Video prompts: {len(pipeline_state.prompt_output.video_prompts)}")
            print(f"     - Refinement cycles: {pipeline_state.prompt_output.total_refinement_cycles}")
        
        if pipeline_state.qa_output:
            print(f"\n  5. QA Agent")
            print(f"     - Validation passed: {'✓' if pipeline_state.qa_output.validation_passed else '✗'}")
            print(f"     - Content quality: {pipeline_state.qa_output.content_quality_score:.1f}/100")
            print(f"     - Brand consistency: {pipeline_state.qa_output.brand_consistency_score:.1f}/100")
            print(f"     - Issues found: {len(pipeline_state.qa_output.issues)}")
        
        if pipeline_state.publisher_output:
            print(f"\n  6. Publisher Agent")
            print(f"     - Manifest ID: {pipeline_state.publisher_output.manifest_id}")
            print(f"     - Status: {pipeline_state.publisher_output.status}")
            print(f"     - Note: Phase 3 feature (mock output)")
        
        # Save output if requested
        if output_file:
            print_section("Saving Output")
            output_data = {
                "session_id": pipeline_state.session_id,
                "input": startup_input.model_dump(),
                "ideation": pipeline_state.ideation_output.model_dump() if pipeline_state.ideation_output else None,
                "comparative": pipeline_state.comparative_output.model_dump() if pipeline_state.comparative_output else None,
                "pitch": pipeline_state.pitch_output.model_dump() if pipeline_state.pitch_output else None,
                "prompts": pipeline_state.prompt_output.model_dump() if pipeline_state.prompt_output else None,
                "qa": pipeline_state.qa_output.model_dump() if pipeline_state.qa_output else None,
                "publisher": pipeline_state.publisher_output.model_dump() if pipeline_state.publisher_output else None,
                "metadata": {
                    "started_at": pipeline_state.started_at.isoformat(),
                    "completed_at": pipeline_state.completed_at.isoformat() if pipeline_state.completed_at else None,
                    "duration_seconds": (pipeline_state.completed_at - pipeline_state.started_at).total_seconds() if pipeline_state.completed_at else None
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"✓ Output saved to: {output_file}")
        
        print_section("Success")
        print("Pipeline completed successfully!")
        print("\nNext Steps:")
        print("  • Phase 2: Integrate Gemini 2.0 for actual content generation")
        print("  • Phase 2: Connect Imagen and Veo for media assets")
        print("  • Phase 2: Implement MCP integrations for real data")
        print("  • Phase 3: Add publisher with GCS and Canva integration")
        
    except Exception as e:
        print_section("Error")
        print(f"✗ Pipeline failed: {e}")
        logger.exception("pipeline_execution_failed")
        sys.exit(1)
    
    finally:
        # Cleanup
        await orchestrator.shutdown()


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GTMForge - Multi-Agent GTM Automation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python main.py --idea "AI-powered restaurant staffing platform"
  
  # With additional context
  python main.py --idea "AI for restaurant staffing" \\
                 --industry "Restaurant & Hospitality" \\
                 --target-market "Urban SMB restaurants" \\
                 --output results.json
  
  # Using example from implementation.md
  python main.py --idea "AI for restaurant staffing" --output test_output.json
        """
    )
    
    parser.add_argument(
        "--idea",
        type=str,
        required=True,
        help="The core startup idea or problem being solved"
    )
    parser.add_argument(
        "--industry",
        type=str,
        help="Target industry or sector"
    )
    parser.add_argument(
        "--target-market",
        type=str,
        help="Initial target market or customer segment"
    )
    parser.add_argument(
        "--context",
        type=str,
        help="Additional context or constraints"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save output JSON file"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(log_level=args.log_level, json_format=False)
    
    # Run pipeline
    asyncio.run(run_pipeline(
        idea=args.idea,
        industry=args.industry,
        target_market=args.target_market,
        additional_context=args.context,
        output_file=args.output
    ))


if __name__ == "__main__":
    main()


