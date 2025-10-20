"""Semantic preservation checks using SBERT and optional NLI."""

import torch
from typing import Optional, Tuple, List, Dict
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F


class SemanticChecker:
    """Check semantic preservation between original and edited sentences."""
    
    def __init__(
        self,
        sbert_model: str = "all-MiniLM-L6-v2",
        nli_model: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize semantic checker.
        
        Args:
            sbert_model: Sentence-BERT model name
            nli_model: Optional NLI model name (e.g., "roberta-large-mnli")
            device: "cpu" or "cuda"
        """
        self.device = device
        
        # Load SBERT for semantic similarity
        self.sbert = SentenceTransformer(sbert_model, device=device)
        
        # Optionally load NLI model for entailment checking
        self.use_nli = nli_model is not None
        if self.use_nli:
            self.nli_tokenizer = AutoTokenizer.from_pretrained(nli_model)
            self.nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model)
            self.nli_model.to(device)
            self.nli_model.eval()
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two sentences.
        
        Args:
            text1: First sentence
            text2: Second sentence
        
        Returns:
            Cosine similarity score [0, 1]
        """
        # Encode sentences
        embeddings = self.sbert.encode(
            [text1, text2],
            convert_to_tensor=True,
            device=self.device
        )
        
        # Compute cosine similarity
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
        
        return similarity
    
    def check_entailment(self, premise: str, hypothesis: str) -> Tuple[str, float]:
        """
        Check if hypothesis is entailed by premise using NLI.
        
        Args:
            premise: Original sentence
            hypothesis: Modified sentence
        
        Returns:
            Tuple of (label, confidence) where label is one of:
            "entailment", "neutral", "contradiction"
        """
        if not self.use_nli:
            return "neutral", 0.0
        
        # Tokenize
        inputs = self.nli_tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.nli_model(**inputs)
            logits = outputs.logits
        
        # Get probabilities
        probs = F.softmax(logits, dim=-1)[0]
        
        # Labels for RoBERTa-MNLI: 0=contradiction, 1=neutral, 2=entailment
        labels = ["contradiction", "neutral", "entailment"]
        pred_idx = torch.argmax(probs).item()
        confidence = probs[pred_idx].item()
        
        return labels[pred_idx], confidence
    
    def is_semantically_preserved(
        self,
        original: str,
        modified: str,
        min_similarity: float = 0.95,
        allow_contradiction: bool = False
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if semantic meaning is preserved in modified sentence.
        
        Args:
            original: Original sentence
            modified: Modified sentence
            min_similarity: Minimum required cosine similarity
            allow_contradiction: Whether to allow NLI contradictions
        
        Returns:
            Tuple of (is_preserved, details_dict)
        """
        # Compute similarity
        similarity = self.compute_similarity(original, modified)
        
        details = {
            "similarity": similarity,
            "nli_label": None,
            "nli_confidence": None
        }
        
        # Check similarity threshold
        if similarity < min_similarity:
            return False, details
        
        # Check NLI if available
        if self.use_nli:
            nli_label, nli_confidence = self.check_entailment(original, modified)
            details["nli_label"] = nli_label
            details["nli_confidence"] = nli_confidence
            
            # Reject contradictions
            if not allow_contradiction and nli_label == "contradiction":
                return False, details
        
        return True, details
    
    def batch_compute_similarity(
        self,
        original: str,
        candidates: List[str]
    ) -> List[float]:
        """
        Compute similarities for multiple candidates efficiently.
        
        Args:
            original: Original sentence
            candidates: List of candidate sentences
        
        Returns:
            List of similarity scores
        """
        if not candidates:
            return []
        
        # Encode all sentences at once
        all_texts = [original] + candidates
        embeddings = self.sbert.encode(
            all_texts,
            convert_to_tensor=True,
            device=self.device
        )
        
        # Compute similarities
        original_embedding = embeddings[0]
        similarities = []
        
        for candidate_embedding in embeddings[1:]:
            similarity = util.cos_sim(original_embedding, candidate_embedding).item()
            similarities.append(similarity)
        
        return similarities

