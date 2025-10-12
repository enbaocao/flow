"""Bidirectional scoring using RoBERTa for entropy and PLL computation."""

import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from transformers import AutoModelForMaskedLM, AutoTokenizer

from tokenizer_utils import TokenizerAligner, WordAlignment


@dataclass
class WordScore:
    """Scoring information for a word."""
    word_idx: int
    word_text: str
    entropy: float  # bits
    log_prob: float  # log probability of original word
    rank: int  # rank of original word in distribution
    is_clunky: bool  # whether this word is flagged for replacement


class BidirectionalScorer:
    """Score words using RoBERTa's masked language modeling."""
    
    def __init__(
        self,
        model_name: str = "roberta-large",
        device: str = "cpu",
        pll_method: str = "word-l2r"
    ):
        """
        Initialize the scorer.
        
        Args:
            model_name: HuggingFace model name
            device: "cpu" or "cuda"
            pll_method: "word-l2r" (recommended) or "standard"
        """
        self.device = device
        self.pll_method = pll_method
        
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()
        
        self.aligner = TokenizerAligner(model_name)
        self.tokenizer = self.aligner.tokenizer
    
    def compute_entropy(self, logits: torch.Tensor) -> float:
        """
        Compute entropy of a probability distribution.
        
        Args:
            logits: Logits for a single position [vocab_size]
        
        Returns:
            Entropy in bits
        """
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        entropy_nats = -(probs * log_probs).sum().item()
        entropy_bits = entropy_nats / np.log(2)  # convert to bits
        return entropy_bits
    
    def score_word(
        self,
        input_ids: List[int],
        word_alignment: WordAlignment,
        return_distribution: bool = False
    ) -> Tuple[WordScore, Optional[torch.Tensor]]:
        """
        Score a single word by masking and computing entropy/probability.
        
        For multi-piece words, uses pseudo-log-likelihood (PLL).
        
        Args:
            input_ids: Full sentence token IDs
            word_alignment: Word to score
            return_distribution: Whether to return the probability distribution
        
        Returns:
            Tuple of (WordScore, optional distribution tensor)
        """
        num_pieces = word_alignment.token_end - word_alignment.token_start
        
        if num_pieces == 1:
            # Single piece - straightforward masking
            return self._score_single_piece(
                input_ids,
                word_alignment,
                return_distribution
            )
        else:
            # Multi-piece - use PLL
            return self._score_multi_piece(
                input_ids,
                word_alignment,
                return_distribution
            )
    
    def _score_single_piece(
        self,
        input_ids: List[int],
        word_alignment: WordAlignment,
        return_distribution: bool
    ) -> Tuple[WordScore, Optional[torch.Tensor]]:
        """Score a single-piece word."""
        # Mask the word
        masked_ids = self.aligner.mask_word_span(input_ids, word_alignment)
        
        # Get logits
        with torch.no_grad():
            input_tensor = torch.tensor([masked_ids]).to(self.device)
            outputs = self.model(input_tensor)
            logits = outputs.logits[0, word_alignment.token_start]  # [vocab_size]
        
        # Compute entropy
        entropy = self.compute_entropy(logits)
        
        # Get probability and rank of original token
        probs = F.softmax(logits, dim=-1)
        original_token_id = word_alignment.token_ids[0]
        log_prob = F.log_softmax(logits, dim=-1)[original_token_id].item()
        
        # Rank (how many tokens are more probable)
        rank = (probs > probs[original_token_id]).sum().item() + 1
        
        distribution = probs if return_distribution else None
        
        return WordScore(
            word_idx=word_alignment.word_idx,
            word_text=word_alignment.word_text,
            entropy=entropy,
            log_prob=log_prob,
            rank=int(rank),
            is_clunky=False  # will be set by caller based on thresholds
        ), distribution
    
    def _score_multi_piece(
        self,
        input_ids: List[int],
        word_alignment: WordAlignment,
        return_distribution: bool
    ) -> Tuple[WordScore, Optional[torch.Tensor]]:
        """
        Score a multi-piece word using pseudo-log-likelihood.
        
        PLL = sum of log P(piece_i | context, other pieces in word)
        """
        num_pieces = word_alignment.token_end - word_alignment.token_start
        total_log_prob = 0.0
        entropies = []
        distributions = []
        
        for i in range(num_pieces):
            if self.pll_method == "word-l2r":
                # Mask current piece and pieces to the right within the word
                masked_ids = input_ids.copy()
                for j in range(i, num_pieces):
                    masked_ids[word_alignment.token_start + j] = self.aligner.mask_token_id
            else:
                # Standard: mask only current piece
                masked_ids = self.aligner.mask_word_span(
                    input_ids,
                    word_alignment,
                    mask_position=i
                )
            
            # Get logits for this position
            with torch.no_grad():
                input_tensor = torch.tensor([masked_ids]).to(self.device)
                outputs = self.model(input_tensor)
                logits = outputs.logits[0, word_alignment.token_start + i]
            
            # Entropy
            entropy = self.compute_entropy(logits)
            entropies.append(entropy)
            
            # Log probability of actual token
            original_token_id = word_alignment.token_ids[i]
            log_prob = F.log_softmax(logits, dim=-1)[original_token_id].item()
            total_log_prob += log_prob
            
            if return_distribution and i == 0:
                # Return distribution for first piece (for candidate generation)
                distributions.append(F.softmax(logits, dim=-1))
        
        # Average entropy across pieces
        avg_entropy = np.mean(entropies)
        
        # Approximate rank based on total log prob
        # For multi-piece, rank is less meaningful, so we use a heuristic
        if total_log_prob > -2.0:
            rank = 1
        elif total_log_prob > -5.0:
            rank = 10
        elif total_log_prob > -10.0:
            rank = 50
        else:
            rank = 100
        
        distribution = distributions[0] if distributions else None
        
        return WordScore(
            word_idx=word_alignment.word_idx,
            word_text=word_alignment.word_text,
            entropy=avg_entropy,
            log_prob=total_log_prob,
            rank=rank,
            is_clunky=False
        ), distribution
    
    def score_sentence(
        self,
        text: str,
        words: List[str],
        min_entropy: float = 4.0,
        max_rank: int = 50
    ) -> List[WordScore]:
        """
        Score all words in a sentence.
        
        Args:
            text: Sentence text
            words: List of words
            min_entropy: Threshold for flagging high entropy
            max_rank: Threshold for flagging poor ranking
        
        Returns:
            List of WordScore objects
        """
        # Get alignments
        alignments = self.aligner.align_words_to_tokens(text, words)
        
        # Tokenize sentence
        encoding = self.tokenizer(text, add_special_tokens=True)
        input_ids = encoding['input_ids']
        
        # Score each word
        scores = []
        for alignment in alignments:
            score, _ = self.score_word(input_ids, alignment, return_distribution=False)
            
            # Flag as clunky if meets criteria
            score.is_clunky = (
                score.entropy >= min_entropy or
                score.rank >= max_rank
            )
            
            scores.append(score)
        
        return scores
    
    def compute_windowed_pll(
        self,
        input_ids: List[int],
        center_pos: int,
        window_size: int = 5
    ) -> float:
        """
        Compute PLL for a window around a position.
        
        Args:
            input_ids: Token IDs
            center_pos: Center position
            window_size: Window size (±window_size tokens)
        
        Returns:
            Total log probability for the window
        """
        # Define window boundaries
        start = max(1, center_pos - window_size)  # skip [CLS]
        end = min(len(input_ids) - 1, center_pos + window_size + 1)  # skip [SEP]
        
        total_log_prob = 0.0
        
        # Mask each position in window and compute log prob
        for pos in range(start, end):
            masked_ids = input_ids.copy()
            masked_ids[pos] = self.aligner.mask_token_id
            
            with torch.no_grad():
                input_tensor = torch.tensor([masked_ids]).to(self.device)
                outputs = self.model(input_tensor)
                logits = outputs.logits[0, pos]
            
            original_token_id = input_ids[pos]
            log_prob = F.log_softmax(logits, dim=-1)[original_token_id].item()
            total_log_prob += log_prob
        
        return total_log_prob

