#!/usr/bin/env python3
"""
Benchmark the performance of Flow's highlight functionality.
"""

import time
from config import FlowConfig
from refinement_pipeline import RefinementPipeline


def benchmark_sentence(pipeline, text, description):
    """Benchmark a single sentence."""
    print(f"\n{description}")
    print(f"Text: \"{text}\"")
    print(f"Length: {len(text.split())} words")
    
    start = time.time()
    result = pipeline.refine_sentence(text)
    elapsed = time.time() - start
    
    print(f"⏱️  Time: {elapsed:.2f} seconds")
    print(f"📝 Flagged words: {len([s for s in result.scores if s.is_clunky])}")
    print(f"✏️  Edits suggested: {len(result.edits)}")
    return elapsed


def main():
    """Run performance benchmarks."""
    print("=" * 70)
    print("Flow Performance Benchmark")
    print("=" * 70)
    
    # Configuration
    config = FlowConfig(
        roberta_model="roberta-base",
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95
    )
    
    print("\nConfiguration:")
    print(f"  Model: {config.roberta_model}")
    print(f"  Device: {config.device}")
    print(f"  Min entropy: {config.min_entropy}")
    
    # Initialize (cold start)
    print("\n" + "=" * 70)
    print("COLD START (First Time Initialization)")
    print("=" * 70)
    start_init = time.time()
    pipeline = RefinementPipeline(config)
    init_time = time.time() - start_init
    print(f"⏱️  Model loading time: {init_time:.2f} seconds")
    
    # Test cases
    print("\n" + "=" * 70)
    print("WARM REQUESTS (Models Already Loaded)")
    print("=" * 70)
    
    test_cases = [
        # Clean text (no issues)
        ("This is a simple sentence.", 
         "1️⃣  SHORT - Clean (no issues)"),
        
        ("The quick brown fox jumps over the lazy dog.",
         "2️⃣  SHORT - Clean (no issues)"),
        
        # Text with issues
        ("The utilize of technology is important.",
         "3️⃣  SHORT - With issue (1 word)"),
        
        ("We should definately consider the utilize of advanced algorithms.",
         "4️⃣  MEDIUM - With issues (2 words)"),
        
        ("The research team analyzed the comprehensive data set and provided detailed results to stakeholders.",
         "5️⃣  MEDIUM - Clean (no issues)"),
        
        ("The utilize of advanced machine learning algorithms has revolutionized the way we process data.",
         "6️⃣  LONG - With issue (1 word)"),
        
        ("Due to the fact that we need to utilize more sophisticated methodologies, we should definately consider implementing these approaches.",
         "7️⃣  LONG - With multiple issues"),
        
        ("The quick brown fox jumps over the lazy dog while the cat sits quietly on the windowsill watching the birds.",
         "8️⃣  VERY LONG - Clean (no issues)"),
    ]
    
    times = []
    for text, description in test_cases:
        elapsed = benchmark_sentence(pipeline, text, description)
        times.append(elapsed)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Cold start (model loading): {init_time:.2f} seconds")
    print(f"\nWarm requests:")
    print(f"  Fastest: {min(times):.2f} seconds")
    print(f"  Slowest: {max(times):.2f} seconds")
    print(f"  Average: {sum(times)/len(times):.2f} seconds")
    print(f"  Median: {sorted(times)[len(times)//2]:.2f} seconds")
    
    print("\n" + "=" * 70)
    print("PERFORMANCE TIPS")
    print("=" * 70)
    print("🚀 To speed up:")
    print("   1. Use GPU: device='cuda' (3-5x faster)")
    print("   2. Reduce candidates: top_k_candidates=10")
    print("   3. Smaller window: pll_window_size=3")
    print("   4. Keep models loaded (don't restart server)")
    print("\n⚡ First request is always slower (loading models)")
    print("💡 Clean text (no issues) is 2-3x faster than text with issues")
    print("=" * 70)


if __name__ == "__main__":
    main()

