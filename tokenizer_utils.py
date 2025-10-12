"""Tokenizer and alignment utilities for word-to-subword mapping."""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from transformers import AutoTokenizer


@dataclass
class WordAlignment:
    """Alignment between a word and its subword pieces."""
    word_idx: int  # word index in sentence
    word_text: str  # original word text
    char_start: int  # character offset start
    char_end: int  # character offset end
    token_start: int  # first subword token index
    token_end: int  # last subword token index (exclusive)
    token_ids: List[int]  # subword token IDs


class TokenizerAligner:
    """Handles tokenization and alignment between words and subword pieces."""
    
    def __init__(self, model_name: str = "roberta-large"):
        """
        Initialize the tokenizer aligner.
        
        Args:
            model_name: HuggingFace model name for tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_fast=True,
            add_prefix_space=True  # RoBERTa needs this for proper tokenization
        )
        self.mask_token_id = self.tokenizer.mask_token_id
        self.mask_token = self.tokenizer.mask_token
    
    def align_words_to_tokens(self, text: str, words: List[str]) -> List[WordAlignment]:
        """
        Align words to their subword token spans.
        
        Args:
            text: Original text
            words: List of words (e.g., from spaCy tokenization)
        
        Returns:
            List of WordAlignment objects
        """
        # Tokenize with offset mapping
        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            add_special_tokens=True
        )
        
        offset_mapping = encoding['offset_mapping']
        input_ids = encoding['input_ids']
        
        # Build character-to-token mapping
        char_to_token = {}
        for token_idx, (start, end) in enumerate(offset_mapping):
            for char_idx in range(start, end):
                char_to_token[char_idx] = token_idx
        
        # Find word positions in text
        alignments = []
        search_start = 0
        
        for word_idx, word in enumerate(words):
            # Find word in text (handles spaces and punctuation)
            char_start = text.find(word, search_start)
            if char_start == -1:
                # Handle edge cases where word might be slightly different
                continue
            
            char_end = char_start + len(word)
            search_start = char_end
            
            # Map character span to token span
            token_indices = set()
            for char_idx in range(char_start, char_end):
                if char_idx in char_to_token:
                    token_indices.add(char_to_token[char_idx])
            
            if not token_indices:
                continue
            
            token_start = min(token_indices)
            token_end = max(token_indices) + 1
            token_ids = input_ids[token_start:token_end]
            
            alignments.append(WordAlignment(
                word_idx=word_idx,
                word_text=word,
                char_start=char_start,
                char_end=char_end,
                token_start=token_start,
                token_end=token_end,
                token_ids=token_ids
            ))
        
        return alignments
    
    def mask_word_span(
        self,
        input_ids: List[int],
        word_alignment: WordAlignment,
        mask_position: Optional[int] = None
    ) -> List[int]:
        """
        Create a masked version of input_ids for a specific word.
        
        Args:
            input_ids: Original token IDs
            word_alignment: Word alignment info
            mask_position: If specified, only mask this position within the span
                          (for PLL computation). Otherwise mask entire span.
        
        Returns:
            Masked token IDs
        """
        masked_ids = input_ids.copy()
        
        if mask_position is not None:
            # Mask only one position (for PLL)
            if word_alignment.token_start + mask_position < word_alignment.token_end:
                masked_ids[word_alignment.token_start + mask_position] = self.mask_token_id
        else:
            # Mask entire word span
            for i in range(word_alignment.token_start, word_alignment.token_end):
                masked_ids[i] = self.mask_token_id
        
        return masked_ids
    
    def decode_tokens(self, token_ids: List[int]) -> str:
        """Decode token IDs to text."""
        return self.tokenizer.decode(token_ids, skip_special_tokens=False)
    
    def decode_clean(self, token_ids: List[int]) -> str:
        """Decode token IDs to clean text (no special tokens)."""
        return self.tokenizer.decode(token_ids, skip_special_tokens=True).strip()
    
    def encode_word(self, word: str) -> List[int]:
        """
        Encode a single word to token IDs.
        
        Args:
            word: Word to encode
        
        Returns:
            Token IDs (excluding special tokens)
        """
        # Add space prefix for RoBERTa
        encoding = self.tokenizer(
            word,
            add_special_tokens=False,
            add_prefix_space=True
        )
        return encoding['input_ids']
    
    def reconstruct_sentence(
        self,
        input_ids: List[int],
        replacement_text: str,
        word_alignment: WordAlignment
    ) -> Tuple[str, List[int]]:
        """
        Reconstruct sentence with a word replaced.
        
        Args:
            input_ids: Original token IDs
            replacement_text: New word to insert
            word_alignment: Alignment of word to replace
        
        Returns:
            Tuple of (reconstructed text, reconstructed token IDs)
        """
        # Encode the replacement
        replacement_ids = self.encode_word(replacement_text)
        
        # Build new token sequence
        new_ids = (
            input_ids[:word_alignment.token_start] +
            replacement_ids +
            input_ids[word_alignment.token_end:]
        )
        
        # Decode to text
        new_text = self.decode_clean(new_ids)
        
        return new_text, new_ids

