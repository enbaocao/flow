#!/usr/bin/env python3
"""
Flow - Bidirectional Text Refinement using RoBERTa

Main CLI interface for the Flow text refinement system.
"""

import argparse
import sys
from typing import Optional

from config import FlowConfig
from refinement_pipeline import RefinementPipeline


def main():
    """Main entry point for Flow CLI."""
    parser = argparse.ArgumentParser(
        description="Flow - Bidirectional Text Refinement using RoBERTa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Refine text from command line
  python flow.py "The utilize of technology is becoming more prevalent."
  
  # Interactive mode with confirmation prompts
  python flow.py "Your text here" --interactive
  
  # Use smaller/faster model
  python flow.py "Your text" --model roberta-base
  
  # Adjust thresholds
  python flow.py "Your text" --min-entropy 3.5 --min-pll-gain 1.0
  
  # Enable NLI entailment checking
  python flow.py "Your text" --use-nli
        """
    )
    
    # Input
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to refine (or use --file)"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Read text from file instead of command line"
    )
    
    # Interaction mode
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode with user approval for each edit"
    )
    
    # Model selection
    parser.add_argument(
        "--model",
        default="roberta-large",
        choices=["roberta-base", "roberta-large"],
        help="RoBERTa model to use (default: roberta-large)"
    )
    
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to run models on (default: cpu)"
    )
    
    # Thresholds
    parser.add_argument(
        "--min-entropy",
        type=float,
        default=4.0,
        help="Minimum entropy threshold for flagging words (default: 4.0)"
    )
    
    parser.add_argument(
        "--max-rank",
        type=int,
        default=50,
        help="Maximum original word rank for flagging (default: 50)"
    )
    
    parser.add_argument(
        "--min-pll-gain",
        type=float,
        default=1.5,
        help="Minimum PLL gain required for accepting edits (default: 1.5)"
    )
    
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.95,
        help="Minimum SBERT similarity required (default: 0.95)"
    )
    
    parser.add_argument(
        "--pll-window",
        type=int,
        default=5,
        help="PLL window size in tokens (default: 5)"
    )
    
    parser.add_argument(
        "--max-edits",
        type=int,
        default=2,
        help="Maximum edits per sentence (default: 2)"
    )
    
    # Features
    parser.add_argument(
        "--use-nli",
        action="store_true",
        help="Enable NLI entailment checking (slower but more conservative)"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of candidate replacements to consider (default: 20)"
    )
    
    # Output
    parser.add_argument(
        "-o", "--output",
        help="Write refined text to file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed scoring information"
    )
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        return 1
    
    # Create configuration
    config = FlowConfig(
        roberta_model=args.model,
        device=args.device,
        min_entropy=args.min_entropy,
        max_original_rank=args.max_rank,
        min_pll_gain=args.min_pll_gain,
        min_sbert_cosine=args.min_similarity,
        pll_window_size=args.pll_window,
        max_edits_per_sentence=args.max_edits,
        use_nli_check=args.use_nli,
        top_k_candidates=args.top_k
    )
    
    # Initialize pipeline
    print("Initializing Flow text refinement system...")
    print(f"Configuration:")
    print(f"  Model: {config.roberta_model}")
    print(f"  Device: {config.device}")
    print(f"  Min entropy: {config.min_entropy} bits")
    print(f"  Min PLL gain: {config.min_pll_gain}")
    print(f"  Min similarity: {config.min_sbert_cosine}")
    print()
    
    try:
        pipeline = RefinementPipeline(config)
    except Exception as e:
        print(f"Error initializing pipeline: {e}", file=sys.stderr)
        print("\nNote: Make sure required models are downloaded:", file=sys.stderr)
        print("  python -m spacy download en_core_web_sm", file=sys.stderr)
        return 1
    
    # Process text
    print(f"\n{'='*70}")
    print("ORIGINAL TEXT:")
    print(f"{'='*70}")
    print(text)
    print()
    
    try:
        refined_text = pipeline.refine_text(text, interactive=args.interactive)
    except Exception as e:
        print(f"Error refining text: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    # Output results
    print(f"\n{'='*70}")
    print("REFINED TEXT:")
    print(f"{'='*70}")
    print(refined_text)
    print()
    
    # Write to file if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(refined_text)
            print(f"Refined text written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

