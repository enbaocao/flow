#!/usr/bin/env python3
"""
Test the highlight mode functionality.
"""

from .config import FlowConfig
from .refinement_pipeline import RefinementPipeline


def test_highlight_mode():
    """Test that highlight mode works without errors."""
    
    print("Testing highlight mode...")
    
    # Simple configuration for fast testing
    config = FlowConfig(
        roberta_model="roberta-base",
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95
    )
    
    # Initialize pipeline
    print("Initializing pipeline...")
    pipeline = RefinementPipeline(config)
    
    # Test text with known issue
    test_text = "The utilize of technology is becoming more prevalent in our society."
    
    print("\nTest 1: Single sentence with known issue")
    print("-" * 70)
    pipeline.highlight_clunky_words(test_text, show_top_replacements=2)
    
    # Test text with multiple sentences
    test_text2 = "This is a good sentence. The utilize of algorithms is important. Another good sentence here."
    
    print("\n\nTest 2: Multiple sentences")
    print("-" * 70)
    pipeline.highlight_clunky_words(test_text2, show_top_replacements=2)
    
    # Test text with no issues
    test_text3 = "This is a very clear and simple sentence."
    
    print("\n\nTest 3: Text with no issues")
    print("-" * 70)
    pipeline.highlight_clunky_words(test_text3, show_top_replacements=2)
    
    print("\n" + "=" * 70)
    print("✓ All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_highlight_mode()

