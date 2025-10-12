#!/usr/bin/env python3
"""Debug script to see what's happening in the pipeline."""

from config import FlowConfig
from refinement_pipeline import RefinementPipeline

def debug_refinement():
    """Debug the refinement process step by step."""
    
    text = "The utilize of technology is becoming more prevalent."
    
    config = FlowConfig(
        roberta_model="roberta-base",
        device="cpu",
        min_entropy=2.0,
        max_original_rank=10000,
        min_pll_gain=0.5,
        min_sbert_cosine=0.90
    )
    
    print("Creating pipeline...")
    pipeline = RefinementPipeline(config)
    
    print(f"\nOriginal text: {text}")
    
    # Step 1: Extract words
    words = pipeline.constraints.extract_words(text)
    print(f"Words: {words}")
    
    # Step 2: Score words
    scores = pipeline.scorer.score_sentence(
        text,
        words,
        min_entropy=config.min_entropy,
        max_rank=config.max_original_rank
    )
    
    print(f"\nWord scores:")
    for score in scores:
        flag = "🔥" if score.is_clunky else "  "
        print(f"{flag} '{score.word_text}': H={score.entropy:.2f} bits, rank={score.rank}, clunky={score.is_clunky}")
    
    # Find clunky words
    clunky_words = [s for s in scores if s.is_clunky]
    print(f"\nClunky words found: {len(clunky_words)}")
    
    if clunky_words:
        for score in clunky_words:
            print(f"  - '{score.word_text}': H={score.entropy:.2f}, rank={score.rank}")
    
    # Full refinement
    print(f"\nRunning full refinement...")
    result = pipeline.refine_sentence(text)
    
    print(f"Original: {result.original}")
    print(f"Refined:  {result.refined}")
    print(f"Edits made: {len(result.edits)}")
    
    for edit in result.edits:
        print(f"  - '{edit.original_word}' → '{edit.replacement}' (PLL: {edit.pll_gain:+.2f}, sim: {edit.similarity:.3f})")

if __name__ == "__main__":
    debug_refinement()
