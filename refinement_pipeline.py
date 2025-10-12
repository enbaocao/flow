"""Main refinement pipeline for text improvement."""

from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass
import re

from config import FlowConfig
from scorer import BidirectionalScorer, WordScore
from candidate_generator import CandidateGenerator, Candidate
from semantic_checker import SemanticChecker
from linguistic_constraints import LinguisticConstraints
from tokenizer_utils import TokenizerAligner

if TYPE_CHECKING:
    from tokenizer_utils import WordAlignment


@dataclass
class Edit:
    """Represents a proposed edit."""
    word_idx: int
    original_word: str
    replacement: str
    original_score: WordScore
    pll_gain: float
    similarity: float
    reason: str
    top_alternatives: List[Tuple[str, float]]  # (word, pll_gain)


@dataclass
class RefinementResult:
    """Result of refining a sentence."""
    original: str
    refined: str
    edits: List[Edit]
    scores: List[WordScore]


class RefinementPipeline:
    """Main pipeline for text refinement."""
    
    def __init__(self, config: FlowConfig):
        """
        Initialize the refinement pipeline.
        
        Args:
            config: FlowConfig object
        """
        self.config = config
        
        # Initialize components
        print(f"Loading models (this may take a moment)...")
        
        self.scorer = BidirectionalScorer(
            model_name=config.roberta_model,
            device=config.device,
            pll_method=config.pll_method
        )
        
        self.generator = CandidateGenerator(
            scorer=self.scorer,
            top_k=config.top_k_candidates
        )
        
        self.semantic_checker = SemanticChecker(
            sbert_model=config.sbert_model,
            nli_model=config.nli_model if config.use_nli_check else None,
            device=config.device
        )
        
        self.constraints = LinguisticConstraints(
            model_name=config.spacy_model
        )
        
        self.aligner = self.scorer.aligner
        
        print("All models loaded successfully!")
    
    def refine_sentence(
        self,
        sentence: str,
        interactive: bool = False
    ) -> RefinementResult:
        """
        Refine a single sentence.
        
        Args:
            sentence: Sentence to refine
            interactive: If True, prompt for user approval of edits
        
        Returns:
            RefinementResult object
        """
        # Step 1: Extract words using spaCy
        words = self.constraints.extract_words(sentence)
        
        # Step 2: Score all words
        scores = self.scorer.score_sentence(
            sentence,
            words,
            min_entropy=self.config.min_entropy,
            max_rank=self.config.max_original_rank
        )
        
        # Step 3: Identify clunky words
        clunky_words = [s for s in scores if s.is_clunky]
        
        if not clunky_words:
            return RefinementResult(
                original=sentence,
                refined=sentence,
                edits=[],
                scores=scores
            )
        
        # Step 4: Process each clunky word (greedy left-to-right)
        current_text = sentence
        current_words = words.copy()
        edits = []
        edit_count = 0
        
        for score in clunky_words:
            # Check edit budget
            if edit_count >= self.config.max_edits_per_sentence:
                break
            
            # Get word alignment in current text
            alignments = self.aligner.align_words_to_tokens(
                current_text,
                current_words
            )
            
            # Find alignment for this word
            alignment = None
            for a in alignments:
                if a.word_idx == score.word_idx:
                    alignment = a
                    break
            
            if not alignment:
                continue
            
            # Generate candidates
            encoding = self.aligner.tokenizer(
                current_text,
                add_special_tokens=True
            )
            input_ids = encoding['input_ids']
            
            candidates = self.generator.generate_candidates(
                input_ids,
                alignment,
                score.word_text
            )
            
            if not candidates:
                continue
            
            # Filter by linguistic constraints
            candidate_texts = [c.text for c in candidates]
            filtered_texts = self.constraints.filter_candidates(
                score.word_text,
                candidate_texts,
                current_text,
                strict=True
            )
            
            filtered_candidates = [
                c for c in candidates if c.text in filtered_texts
            ]
            
            if not filtered_candidates:
                continue
            
            # Step 5: Re-rank candidates
            best_edit = self._find_best_edit(
                current_text,
                score,
                alignment,
                filtered_candidates,
                input_ids
            )
            
            if not best_edit:
                continue
            
            # Step 6: Apply edit (if interactive, ask for confirmation)
            if interactive:
                if not self._confirm_edit(best_edit):
                    continue
            
            # Apply the edit
            current_text, current_words = self._apply_edit(
                current_text,
                current_words,
                alignment,
                best_edit.replacement
            )
            
            edits.append(best_edit)
            edit_count += 1
        
        return RefinementResult(
            original=sentence,
            refined=current_text,
            edits=edits,
            scores=scores
        )
    
    def _find_best_edit(
        self,
        current_text: str,
        original_score: WordScore,
        alignment: 'WordAlignment',
        candidates: List[Candidate],
        input_ids: List[int]
    ) -> Optional[Edit]:
        """
        Find the best candidate edit based on PLL gain and semantic similarity.
        
        Args:
            current_text: Current sentence text
            original_score: Score of original word
            alignment: Word alignment
            candidates: List of candidate replacements
            input_ids: Current input IDs
        
        Returns:
            Best Edit if found, None otherwise
        """
        # Compute original windowed PLL
        original_pll = self.scorer.compute_windowed_pll(
            input_ids,
            alignment.token_start,
            window_size=self.config.pll_window_size
        )
        
        best_candidate = None
        best_pll_gain = -float('inf')
        best_similarity = 0.0
        alternatives = []
        
        for candidate in candidates[:10]:  # Limit to top 10 for efficiency
            # Reconstruct sentence with candidate
            new_text, new_ids = self.aligner.reconstruct_sentence(
                input_ids,
                candidate.text,
                alignment
            )
            
            # Compute new PLL
            # Need to adjust position if token count changed
            token_diff = len(new_ids) - len(input_ids)
            new_pos = alignment.token_start
            
            new_pll = self.scorer.compute_windowed_pll(
                new_ids,
                new_pos,
                window_size=self.config.pll_window_size
            )
            
            pll_gain = new_pll - original_pll
            
            # Compute semantic similarity
            similarity = self.semantic_checker.compute_similarity(
                current_text,
                new_text
            )
            
            # Store for alternatives list
            alternatives.append((candidate.text, pll_gain))
            
            # Check thresholds
            if pll_gain < self.config.min_pll_gain:
                continue
            
            if similarity < self.config.min_sbert_cosine:
                continue
            
            # Optional NLI check
            if self.config.use_nli_check:
                is_preserved, details = self.semantic_checker.is_semantically_preserved(
                    current_text,
                    new_text,
                    min_similarity=self.config.min_sbert_cosine,
                    allow_contradiction=False
                )
                if not is_preserved:
                    continue
            
            # Track best candidate
            if pll_gain > best_pll_gain:
                best_pll_gain = pll_gain
                best_similarity = similarity
                best_candidate = candidate
        
        if not best_candidate:
            return None
        
        # Generate reason
        reason = self._generate_reason(original_score, best_pll_gain, best_similarity)
        
        # Sort alternatives by PLL gain
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return Edit(
            word_idx=original_score.word_idx,
            original_word=original_score.word_text,
            replacement=best_candidate.text,
            original_score=original_score,
            pll_gain=best_pll_gain,
            similarity=best_similarity,
            reason=reason,
            top_alternatives=alternatives[:3]
        )
    
    def _generate_reason(
        self,
        original_score: WordScore,
        pll_gain: float,
        similarity: float
    ) -> str:
        """Generate a human-readable reason for the edit."""
        reasons = []
        
        if original_score.entropy >= self.config.min_entropy:
            reasons.append(f"high uncertainty (H={original_score.entropy:.1f} bits)")
        
        if original_score.rank >= self.config.max_original_rank:
            reasons.append(f"low rank (#{original_score.rank})")
        
        reasons.append(f"improves fluency (+{pll_gain:.2f} PLL)")
        reasons.append(f"preserves meaning ({similarity:.3f} sim)")
        
        return "; ".join(reasons)
    
    def _apply_edit(
        self,
        text: str,
        words: List[str],
        alignment: 'WordAlignment',
        replacement: str
    ) -> Tuple[str, List[str]]:
        """
        Apply an edit to the text and word list.
        
        Args:
            text: Current text
            words: Current word list
            alignment: Word alignment
            replacement: Replacement word
        
        Returns:
            Tuple of (new_text, new_words)
        """
        # Update text by character replacement
        new_text = (
            text[:alignment.char_start] +
            replacement +
            text[alignment.char_end:]
        )
        
        # Update word list
        new_words = words.copy()
        new_words[alignment.word_idx] = replacement
        
        return new_text, new_words
    
    def _confirm_edit(self, edit: Edit) -> bool:
        """
        Prompt user to confirm an edit (for interactive mode).
        
        Args:
            edit: Proposed edit
        
        Returns:
            True if user accepts, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Proposed edit:")
        print(f"  Original: '{edit.original_word}'")
        print(f"  Replacement: '{edit.replacement}'")
        print(f"  Reason: {edit.reason}")
        print(f"\nTop alternatives:")
        for i, (alt, gain) in enumerate(edit.top_alternatives, 1):
            print(f"  {i}. {alt} (ΔLL={gain:+.2f})")
        print(f"{'='*60}")
        
        response = input("Accept this edit? (y/n/1-3 for alternative): ").strip().lower()
        
        if response == 'y':
            return True
        elif response == 'n':
            return False
        elif response in ['1', '2', '3']:
            idx = int(response) - 1
            if idx < len(edit.top_alternatives):
                # Update edit with chosen alternative
                edit.replacement = edit.top_alternatives[idx][0]
                return True
        
        return False
    
    def refine_text(self, text: str, interactive: bool = False) -> str:
        """
        Refine a full text (multiple sentences).
        
        Args:
            text: Text to refine
            interactive: Interactive mode
        
        Returns:
            Refined text
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        
        refined_sentences = []
        all_edits = []
        
        for i, sentence in enumerate(sentences):
            if interactive:
                print(f"\n\nProcessing sentence {i+1}/{len(sentences)}")
                print(f"Original: {sentence}")
            
            result = self.refine_sentence(sentence, interactive=interactive)
            refined_sentences.append(result.refined)
            
            if result.edits and not interactive:
                print(f"\nSentence {i+1}: {len(result.edits)} edit(s)")
                for edit in result.edits:
                    print(f"  '{edit.original_word}' → '{edit.replacement}'")
            
            all_edits.extend(result.edits)
        
        return " ".join(refined_sentences)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter (can be improved with spaCy sentencizer)
        doc = self.constraints.nlp(text)
        return [sent.text.strip() for sent in doc.sents]
    
    def show_candidates_for_text(self, text: str, top_n: int = 5):
        """
        Show top N sentence-level modifications ranked by quality.
        
        Args:
            text: Text to analyze
            top_n: Number of top modifications to show for the entire sentence
        """
        sentences = self._split_sentences(text)
        
        for sent_idx, sentence in enumerate(sentences, 1):
            if len(sentences) > 1:
                print(f"\n{'='*70}")
                print(f"Sentence {sent_idx}:")
                print(f"{'='*70}")
                print(f"{sentence}\n")
            
            # Extract words
            words = self.constraints.extract_words(sentence)
            
            # Score all words
            scores = self.scorer.score_sentence(
                sentence,
                words,
                min_entropy=0.0,  # Score all words
                max_rank=100000
            )
            
            # Get alignments and encoding
            alignments = self.aligner.align_words_to_tokens(sentence, words)
            encoding = self.aligner.tokenizer(sentence, add_special_tokens=True)
            input_ids = encoding['input_ids']
            
            # Collect all possible modifications with their scores
            all_modifications = []
            
            for score, alignment in zip(scores, alignments):
                # Skip punctuation
                if score.word_text in ['.', ',', '!', '?', ';', ':', '"', "'", '(', ')']:
                    continue
                
                # Generate candidates
                candidates = self.generator.generate_candidates(
                    input_ids,
                    alignment,
                    score.word_text
                )
                
                if not candidates:
                    continue
                
                # Filter by linguistic constraints
                candidate_texts = [c.text for c in candidates]
                filtered_texts = self.constraints.filter_candidates(
                    score.word_text,
                    candidate_texts,
                    sentence,
                    strict=True
                )
                
                filtered_candidates = [
                    c for c in candidates if c.text in filtered_texts
                ]
                
                # Evaluate each candidate
                for candidate in filtered_candidates[:10]:  # Consider top 10 per word
                    # Reconstruct sentence
                    new_text, new_ids = self.aligner.reconstruct_sentence(
                        input_ids,
                        candidate.text,
                        alignment
                    )
                    
                    # Compute metrics
                    original_pll = self.scorer.compute_windowed_pll(
                        input_ids,
                        alignment.token_start,
                        window_size=self.config.pll_window_size
                    )
                    
                    new_pll = self.scorer.compute_windowed_pll(
                        new_ids,
                        alignment.token_start,
                        window_size=self.config.pll_window_size
                    )
                    
                    pll_gain = new_pll - original_pll
                    
                    similarity = self.semantic_checker.compute_similarity(
                        sentence,
                        new_text
                    )
                    
                    # Compute composite quality score
                    # Prioritize: high entropy words, positive PLL gain, high similarity
                    quality_score = (
                        score.entropy * 0.3 +           # Prioritize fixing "clunky" words
                        pll_gain * 2.0 +                 # Fluency improvement (most important)
                        similarity * 10.0 +              # Semantic preservation
                        candidate.log_prob * 0.1         # Candidate probability
                    )
                    
                    all_modifications.append({
                        'original_word': score.word_text,
                        'replacement': candidate.text,
                        'new_text': new_text,
                        'entropy': score.entropy,
                        'rank': score.rank,
                        'pll_gain': pll_gain,
                        'similarity': similarity,
                        'candidate_logprob': candidate.log_prob,
                        'quality_score': quality_score,
                        'passes_thresholds': (
                            pll_gain >= self.config.min_pll_gain and 
                            similarity >= self.config.min_sbert_cosine
                        )
                    })
            
            # Sort by quality score (descending)
            all_modifications.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Display results
            print(f"{'─'*70}")
            print(f"Top {top_n} most promising modifications:")
            print(f"{'─'*70}")
            print(f"Legend: ✓ = passes thresholds (ΔLL ≥ {self.config.min_pll_gain:.1f}, sim ≥ {self.config.min_sbert_cosine:.2f})")
            print(f"{'─'*70}\n")
            
            if not all_modifications:
                print("No linguistically compatible modifications found.\n")
                continue
            
            # Show top N modifications
            for i, mod in enumerate(all_modifications[:top_n], 1):
                status = "✓" if mod['passes_thresholds'] else " "
                
                print(f"{status} {i}. '{mod['original_word']}' → '{mod['replacement']}'")
                print(f"   Modified: {mod['new_text']}")
                print(f"   Quality: {mod['quality_score']:6.2f} | ΔLL: {mod['pll_gain']:+6.2f} | sim: {mod['similarity']:.3f}")
                print(f"   Original entropy: {mod['entropy']:.2f} bits | rank: #{mod['rank']}")
                print()

