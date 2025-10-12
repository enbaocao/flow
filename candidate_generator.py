"""Candidate generation using RoBERTa's fill-mask predictions."""

import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple
from dataclasses import dataclass

from tokenizer_utils import TokenizerAligner, WordAlignment
from scorer import BidirectionalScorer


@dataclass
class Candidate:
    """A candidate replacement for a word."""
    text: str
    log_prob: float
    rank: int  # rank in the distribution


class CandidateGenerator:
    """Generate candidate replacements for words."""
    
    def __init__(self, scorer: BidirectionalScorer, top_k: int = 20):
        """
        Initialize candidate generator.
        
        Args:
            scorer: BidirectionalScorer instance
            top_k: Number of top candidates to generate
        """
        self.scorer = scorer
        self.aligner = scorer.aligner
        self.tokenizer = scorer.tokenizer
        self.top_k = top_k
    
    def generate_candidates(
        self,
        input_ids: List[int],
        word_alignment: WordAlignment,
        original_word: str
    ) -> List[Candidate]:
        """
        Generate candidate replacements for a word.
        
        For simplicity, we focus on single-token replacements to avoid
        multi-token decoding complexity. For multi-piece original words,
        we still generate single-token candidates (which often work well).
        
        Args:
            input_ids: Full sentence token IDs
            word_alignment: Word to replace
            original_word: Original word text (for filtering)
        
        Returns:
            List of candidate replacements
        """
        # Mask the entire word span
        masked_ids = self.aligner.mask_word_span(input_ids, word_alignment)
        
        # Get logits at the first masked position
        with torch.no_grad():
            input_tensor = torch.tensor([masked_ids]).to(self.scorer.device)
            outputs = self.scorer.model(input_tensor)
            logits = outputs.logits[0, word_alignment.token_start]
        
        # Get top-k tokens
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        
        top_probs, top_indices = torch.topk(probs, k=self.top_k)
        
        # Decode candidates
        candidates = []
        for rank, (prob, idx) in enumerate(zip(top_probs, top_indices)):
            token_id = idx.item()
            log_prob = log_probs[token_id].item()
            
            # Decode token
            token_text = self.tokenizer.decode([token_id]).strip()
            
            # Basic filtering
            if self._is_valid_candidate(token_text, original_word):
                candidates.append(Candidate(
                    text=token_text,
                    log_prob=log_prob,
                    rank=rank + 1
                ))
        
        return candidates
    
    def _is_valid_candidate(self, candidate: str, original: str) -> bool:
        """
        Apply basic filtering to candidate.
        
        Args:
            candidate: Candidate word
            original: Original word
        
        Returns:
            True if candidate passes basic filters
        """
        # Don't suggest the same word
        if candidate.lower() == original.lower():
            return False
        
        # Must be a proper word (no empty, no special chars only)
        if not candidate or not candidate.replace("-", "").replace("'", "").isalpha():
            return False
        
        # Filter out very short replacements (likely artifacts)
        if len(candidate) < 2:
            return False
        
        # Filter out tokens that are clearly subword pieces (start with special chars)
        if candidate.startswith("##") or candidate.startswith("Ġ"):
            return False
        
        return True
    
    def preserve_capitalization(self, candidate: str, original: str) -> str:
        """
        Preserve capitalization style of original word.
        
        Args:
            candidate: Candidate word
            original: Original word
        
        Returns:
            Candidate with capitalization adjusted
        """
        if not original or not candidate:
            return candidate
        
        # All caps
        if original.isupper():
            return candidate.upper()
        
        # Title case
        if original[0].isupper() and original[1:].islower():
            return candidate.capitalize()
        
        # First char capitalized
        if original[0].isupper():
            return candidate[0].upper() + candidate[1:]
        
        # Otherwise use candidate as-is (lowercase)
        return candidate.lower()
    
    def filter_by_constraints(
        self,
        candidates: List[Candidate],
        original: str,
        constraints: Dict[str, any]
    ) -> List[Candidate]:
        """
        Filter candidates based on linguistic constraints.
        
        Args:
            candidates: List of candidates
            original: Original word
            constraints: Dictionary of constraints (POS, morphology, etc.)
        
        Returns:
            Filtered list of candidates
        """
        filtered = []
        
        for candidate in candidates:
            # Preserve capitalization
            adjusted_text = self.preserve_capitalization(candidate.text, original)
            
            # Additional constraint checks (POS, etc.) will be done later
            # by the linguistic constraints module
            
            filtered.append(Candidate(
                text=adjusted_text,
                log_prob=candidate.log_prob,
                rank=candidate.rank
            ))
        
        return filtered

