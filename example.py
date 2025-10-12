#!/usr/bin/env python3
"""
Example usage of the Flow text refinement system.
"""

from config import FlowConfig
from refinement_pipeline import RefinementPipeline


def main():
    """Run example refinements."""
    
    # Example sentences with common issues
    examples = [
        "The utilize of advanced technology has revolutionized the way we communicate.",
        "We definately need to consider all the available options before making a decision.",  
        "The research team analyzed the data and provided comprehensive results.",
        "She was walking quick to catch the bus that was leaving soon.",
        "The meeting will be held on next Tuesday at 2 PM in the conference room.",
        "Due to the fact that it was raining, we decided to stay indoors.",
        "He has a lot of experience in the field of computer science and programming."
    ]
    
    print("=" * 80)
    print("Flow Text Refinement Examples")
    print("=" * 80)
    print()
    
    # Configuration for examples (using base model for speed)
    config = FlowConfig(
        roberta_model="roberta-base",  # Faster for demo
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95,
        max_edits_per_sentence=3  # Allow more edits for demo
    )
    
    print("Initializing Flow pipeline...")
    print(f"Configuration: {config.roberta_model}, entropy≥{config.min_entropy}, PLL≥{config.min_pll_gain}")
    print()
    
    # Initialize pipeline
    pipeline = RefinementPipeline(config)
    
    # Process each example
    for i, text in enumerate(examples, 1):
        print(f"\n{'─' * 80}")
        print(f"Example {i}:")
        print("─" * 80)
        print(f"Original:  {text}")
        
        # Refine the text
        result = pipeline.refine_sentence(text)
        
        if result.edits:
            print(f"Refined:   {result.refined}")
            print()
            print("Edits made:")
            for edit in result.edits:
                print(f"  • '{edit.original_word}' → '{edit.replacement}'")
                print(f"    Reason: {edit.reason}")
                if edit.top_alternatives:
                    alts = [f"{alt[0]} ({alt[1]:+.2f})" for alt in edit.top_alternatives[:2]]
                    print(f"    Alternatives: {', '.join(alts)}")
        else:
            print("Refined:   [No changes needed]")
            
            # Show scores for clunky words that didn't meet thresholds
            clunky_scores = [s for s in result.scores if s.entropy >= 3.0 or s.rank >= 20]
            if clunky_scores:
                print()
                print("Words with elevated scores (but below thresholds):")
                for score in clunky_scores:
                    print(f"  • '{score.word_text}': H={score.entropy:.1f} bits, rank={score.rank}")
    
    print(f"\n{'─' * 80}")
    print("Demo complete!")
    print()
    print("To run interactively:")
    print('  python flow.py "Your text here" --interactive')
    print()
    print("To adjust sensitivity:")
    print('  python flow.py "Your text" --min-entropy 3.5 --min-pll-gain 1.0')


if __name__ == "__main__":
    main()
