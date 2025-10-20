#!/usr/bin/env python3
"""
Highlight Mode - Quick text analysis to identify words that need editing.

This is a simplified interface to Flow's highlight functionality for quick checks.
"""

import argparse
import sys

from .config import FlowConfig
from .refinement_pipeline import RefinementPipeline


def main():
    """Run highlight mode on provided text."""
    
    if len(sys.argv) < 2:
        print("Usage: python highlight.py 'Your text here'")
        print("       python highlight.py --file input.txt")
        print()
        print("This tool highlights words in your text that are most likely to need editing,")
        print("showing key metrics and top replacement suggestions.")
        sys.exit(1)
    
    # Get input text
    if sys.argv[1] == '--file' and len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = ' '.join(sys.argv[1:])
    
    # Configuration optimized for quick feedback
    config = FlowConfig(
        roberta_model="roberta-base",  # Faster model
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95,
        max_edits_per_sentence=5  # Show more potential issues
    )
    
    print("Initializing Flow highlight mode...")
    print(f"Using {config.roberta_model} for fast analysis\n")
    
    try:
        pipeline = RefinementPipeline(config)
    except Exception as e:
        print(f"Error initializing pipeline: {e}", file=sys.stderr)
        print("\nNote: Make sure required models are downloaded:", file=sys.stderr)
        print("  python -m spacy download en_core_web_sm", file=sys.stderr)
        sys.exit(1)
    
    # Run highlight analysis
    try:
        pipeline.highlight_clunky_words(text, show_top_replacements=3)
    except Exception as e:
        print(f"Error analyzing text: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

