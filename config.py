"""Configuration for the Flow text refinement system."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FlowConfig:
    """Configuration for text refinement thresholds and model settings."""
    
    # Model selection
    roberta_model: str = "roberta-large"  # or "roberta-base" for speed
    sbert_model: str = "all-MiniLM-L6-v2"  # fast and effective
    nli_model: Optional[str] = "roberta-large-mnli"  # optional NLI check
    spacy_model: str = "en_core_web_sm"
    
    # Scoring thresholds
    min_entropy: float = 4.0  # bits - flag high-entropy positions
    max_original_rank: int = 50  # flag if original word ranks poorly
    
    # Re-ranking thresholds
    min_pll_gain: float = 1.5  # log-units improvement required
    min_sbert_cosine: float = 0.95  # semantic similarity threshold
    pll_window_size: int = 5  # tokens ±5 around edit
    
    # Candidate generation
    top_k_candidates: int = 20  # candidates to consider per position
    max_edits_per_sentence: int = 2  # conservative edit budget
    
    # Processing options
    use_nli_check: bool = False  # enable MNLI entailment check
    batch_size: int = 8  # for batched processing
    device: str = "cpu"  # or "cuda" if available
    
    # PLL computation
    pll_method: str = "word-l2r"  # "word-l2r" or "standard" for multi-piece
    
    def __post_init__(self):
        """Validate configuration."""
        if self.min_entropy < 0:
            raise ValueError("min_entropy must be non-negative")
        if self.min_sbert_cosine < 0 or self.min_sbert_cosine > 1:
            raise ValueError("min_sbert_cosine must be in [0, 1]")
        if self.pll_window_size < 1:
            raise ValueError("pll_window_size must be positive")

