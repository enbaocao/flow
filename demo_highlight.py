#!/usr/bin/env python3
"""
Demo of the highlight mode functionality.
"""

from config import FlowConfig
from refinement_pipeline import RefinementPipeline


def main():
    """Run a demo of highlight mode."""
    
    # Example paragraph with some clunky phrases
    demo_text = """
    The utilize of advanced algorithms in machine learning has revolutionized 
    the way we process data. We should definately consider implementing these 
    techniques in our workflow to enhance productivity and efficiency.
    """
    
    print("=" * 70)
    print("FLOW HIGHLIGHT MODE - DEMO")
    print("=" * 70)
    print("\nThis demo shows how Flow identifies words that need editing.")
    print("We'll analyze a paragraph with some awkward word choices.\n")
    input("Press Enter to continue...")
    
    # Configuration
    config = FlowConfig(
        roberta_model="roberta-base",  # Use base model for speed
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95
    )
    
    print("\nInitializing Flow...")
    pipeline = RefinementPipeline(config)
    
    # Run highlight analysis
    pipeline.highlight_clunky_words(demo_text.strip(), show_top_replacements=3)
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nTo use highlight mode with your own text:")
    print("  python flow.py 'Your text here' --highlight")
    print("  python highlight.py 'Your text here'")
    print()


if __name__ == "__main__":
    main()

