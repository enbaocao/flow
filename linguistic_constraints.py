"""Linguistic constraints checking using spaCy."""

import spacy
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class WordInfo:
    """Linguistic information about a word."""
    text: str
    pos: str  # coarse POS tag
    tag: str  # fine-grained POS tag
    morph: Dict[str, str]  # morphological features
    is_proper: bool  # proper noun
    is_numeric: bool  # number


class LinguisticConstraints:
    """Check and enforce linguistic constraints."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize linguistic constraints checker.
        
        Args:
            model_name: spaCy model name
        """
        self.nlp = spacy.load(model_name)
    
    def analyze_text(self, text: str) -> List[WordInfo]:
        """
        Analyze text and extract linguistic features.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of WordInfo for each token
        """
        doc = self.nlp(text)
        
        word_infos = []
        for token in doc:
            # Skip punctuation and whitespace
            if token.is_punct or token.is_space:
                continue
            
            # Extract morphological features
            morph = {}
            if token.morph:
                for feature in token.morph:
                    key_value = str(feature).split("=")
                    if len(key_value) == 2:
                        morph[key_value[0]] = key_value[1]
            
            word_infos.append(WordInfo(
                text=token.text,
                pos=token.pos_,
                tag=token.tag_,
                morph=morph,
                is_proper=token.pos_ == "PROPN",
                is_numeric=token.like_num or token.is_digit
            ))
        
        return word_infos
    
    def get_word_info(self, word: str) -> WordInfo:
        """
        Get linguistic information for a single word.
        
        Args:
            word: Word to analyze
        
        Returns:
            WordInfo object
        """
        infos = self.analyze_text(word)
        return infos[0] if infos else WordInfo(
            text=word,
            pos="X",
            tag="X",
            morph={},
            is_proper=False,
            is_numeric=False
        )
    
    def is_compatible(
        self,
        original_info: WordInfo,
        candidate_info: WordInfo,
        strict_morph: bool = True
    ) -> bool:
        """
        Check if candidate is linguistically compatible with original.
        
        Args:
            original_info: Original word info
            candidate_info: Candidate word info
            strict_morph: Whether to enforce strict morphology matching
        
        Returns:
            True if compatible
        """
        # Don't replace proper nouns or numbers
        if original_info.is_proper or original_info.is_numeric:
            return False
        
        # Don't suggest proper nouns or numbers as replacements
        if candidate_info.is_proper or candidate_info.is_numeric:
            return False
        
        # Check coarse POS compatibility
        if not self._pos_compatible(original_info.pos, candidate_info.pos):
            return False
        
        # Check morphological features if strict
        if strict_morph:
            return self._morph_compatible(original_info.morph, candidate_info.morph)
        
        return True
    
    def _pos_compatible(self, pos1: str, pos2: str) -> bool:
        """
        Check if two POS tags are compatible.
        
        Args:
            pos1: First POS tag
            pos2: Second POS tag
        
        Returns:
            True if compatible
        """
        # Exact match is always compatible
        if pos1 == pos2:
            return True
        
        # Define compatible POS groups
        compatible_groups = [
            {"NOUN", "PROPN"},  # nouns can sometimes substitute
            {"ADJ", "ADV"},  # adjectives/adverbs sometimes interchangeable
        ]
        
        for group in compatible_groups:
            if pos1 in group and pos2 in group:
                return True
        
        return False
    
    def _morph_compatible(self, morph1: Dict[str, str], morph2: Dict[str, str]) -> bool:
        """
        Check if morphological features are compatible.
        
        Key features to match:
        - Number (Sing, Plur)
        - Tense (Past, Pres, Fut)
        - Person (1, 2, 3)
        - Mood (Ind, Imp, Sub)
        
        Args:
            morph1: First morphological features
            morph2: Second morphological features
        
        Returns:
            True if compatible
        """
        # Key features that should match
        key_features = ["Number", "Tense", "Person", "Mood", "VerbForm"]
        
        for feature in key_features:
            val1 = morph1.get(feature)
            val2 = morph2.get(feature)
            
            # If both have the feature, they must match
            if val1 and val2 and val1 != val2:
                return False
        
        return True
    
    def filter_candidates(
        self,
        original_word: str,
        candidates: List[str],
        original_context: str,
        strict: bool = True
    ) -> List[str]:
        """
        Filter candidates based on linguistic constraints.
        
        Args:
            original_word: Original word
            candidates: List of candidate words
            original_context: Full sentence for context
            strict: Whether to use strict morphology matching
        
        Returns:
            Filtered list of candidates
        """
        # Get original word info in context
        context_infos = self.analyze_text(original_context)
        
        # Find the original word in context
        original_info = None
        for info in context_infos:
            if info.text.lower() == original_word.lower():
                original_info = info
                break
        
        if not original_info:
            # Fallback: analyze word in isolation
            original_info = self.get_word_info(original_word)
        
        # Filter candidates
        filtered = []
        for candidate in candidates:
            candidate_info = self.get_word_info(candidate)
            
            if self.is_compatible(original_info, candidate_info, strict_morph=strict):
                filtered.append(candidate)
        
        return filtered
    
    def extract_words(self, text: str) -> List[str]:
        """
        Extract words from text (for tokenization).
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of words
        """
        doc = self.nlp(text)
        return [token.text for token in doc if not token.is_space]

