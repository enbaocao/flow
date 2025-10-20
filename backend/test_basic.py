#!/usr/bin/env python3
"""
Basic functionality test for Flow system.
This is a simple smoke test to verify the system works.
"""

import sys
from .config import FlowConfig
from .tokenizer_utils import TokenizerAligner
from .scorer import BidirectionalScorer
from .linguistic_constraints import LinguisticConstraints


def test_tokenizer():
    """Test tokenizer alignment functionality."""
    print("Testing tokenizer alignment...")
    
    aligner = TokenizerAligner("roberta-base")
    text = "The quick brown fox jumps."
    words = ["The", "quick", "brown", "fox", "jumps", "."]
    
    alignments = aligner.align_words_to_tokens(text, words)
    
    assert len(alignments) > 0, "Should find word alignments"
    assert alignments[0].word_text == "The", "First word should be 'The'"
    
    print("✓ Tokenizer alignment works")


def test_linguistic_constraints():
    """Test linguistic constraints functionality."""
    print("Testing linguistic constraints...")
    
    constraints = LinguisticConstraints()
    
    # Test word analysis
    words = constraints.extract_words("The cat is sleeping.")
    assert "cat" in words, "Should extract 'cat' from sentence"
    
    # Test word info
    info = constraints.get_word_info("running")
    assert info.pos in ["VERB", "ADJ"], f"'running' should be VERB or ADJ, got {info.pos}"
    
    print("✓ Linguistic constraints work")


def test_scorer():
    """Test basic scoring functionality."""
    print("Testing scorer (this may take a moment)...")
    
    scorer = BidirectionalScorer("roberta-base", device="cpu")
    
    # Test sentence scoring
    text = "The utilize of technology is important."
    words = ["The", "utilize", "of", "technology", "is", "important", "."]
    
    scores = scorer.score_sentence(text, words, min_entropy=2.0, max_rank=100)
    
    assert len(scores) > 0, "Should return word scores"
    
    # Find 'utilize' score - it should be flagged as clunky
    utilize_score = None
    for score in scores:
        if score.word_text == "utilize":
            utilize_score = score
            break
    
    assert utilize_score is not None, "Should find 'utilize' in scores"
    print(f"  'utilize' entropy: {utilize_score.entropy:.2f} bits")
    print(f"  'utilize' rank: {utilize_score.rank}")
    
    print("✓ Scorer works")


def test_config():
    """Test configuration."""
    print("Testing configuration...")
    
    config = FlowConfig()
    assert config.min_entropy >= 0, "min_entropy should be non-negative"
    assert 0 <= config.min_sbert_cosine <= 1, "min_sbert_cosine should be in [0,1]"
    
    print("✓ Configuration works")


def main():
    """Run basic tests."""
    print("=" * 60)
    print("Flow Basic Functionality Test")
    print("=" * 60)
    print()
    
    try:
        test_config()
        test_tokenizer()
        test_linguistic_constraints()
        test_scorer()  # This one downloads models
        
        print("\n" + "=" * 60)
        print("✓ All basic tests passed!")
        print("=" * 60)
        print("\nThe Flow system appears to be working correctly.")
        print("You can now run:")
        print('  python flow.py "The utilize of technology is important."')
        print("  python example.py")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Run install script: python install_models.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
