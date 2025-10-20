#!/usr/bin/env python3
"""
FastAPI server for Flow highlight functionality.
Provides REST API for the frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import asyncio
import json

from .config import FlowConfig
from .refinement_pipeline import RefinementPipeline

# Initialize FastAPI app
app = FastAPI(title="Flow Highlight API", version="1.0.0")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (initialized on startup)
pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize the Flow pipeline on server startup."""
    global pipeline
    print("Initializing Flow pipeline...")
    config = FlowConfig(
        roberta_model="roberta-base",  # Use base model for faster responses
        device="cpu",
        min_entropy=4.0,
        min_pll_gain=1.5,
        min_sbert_cosine=0.95
    )
    pipeline = RefinementPipeline(config)
    print("✓ Pipeline initialized and ready!")


# Request/Response models
class HighlightRequest(BaseModel):
    text: str
    min_entropy: Optional[float] = 4.0
    max_rank: Optional[int] = 50
    top_suggestions: Optional[int] = 3


class Suggestion(BaseModel):
    text: str
    pll_gain: float
    similarity: float
    log_prob: float
    passes_thresholds: bool
    rank: int


class HighlightedWord(BaseModel):
    word: str
    start_pos: int
    end_pos: int
    entropy: float
    rank: int
    log_prob: float
    flagged_reasons: List[str]
    suggestions: List[Suggestion]


class HighlightResponse(BaseModel):
    original_text: str
    highlighted_words: List[HighlightedWord]
    total_highlighted: int
    sentence_count: int


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Flow Highlight API",
        "version": "1.0.0"
    }


class ProgressUpdate(BaseModel):
    stage: str
    progress: float  # 0-1
    current: int
    total: int
    message: str


async def send_progress(stage: str, current: int, total: int, message: str):
    """Helper to create progress update."""
    return {
        "stage": stage,
        "progress": current / total if total > 0 else 0,
        "current": current,
        "total": total,
        "message": message
    }


@app.post("/api/highlight-stream")
async def highlight_text_stream(request: HighlightRequest):
    """
    Highlight text with progress updates via Server-Sent Events.
    """
    async def generate():
        try:
            # Send initial progress
            yield f"data: {json.dumps(await send_progress('init', 0, 5, 'Starting analysis'))}\n\n"
            await asyncio.sleep(0.1)
            
            # Split sentences
            sentences = pipeline._split_sentences(request.text)
            yield f"data: {json.dumps(await send_progress('split', 1, 5, f'Found {len(sentences)} sentence(s)'))}\n\n"
            await asyncio.sleep(0.1)
            
            highlighted_words = []
            char_offset = 0
            total_words_to_check = 0
            
            # Count total words to check
            all_sentence_data = []
            for sentence in sentences:
                words = pipeline.constraints.extract_words(sentence)
                scores = pipeline.scorer.score_sentence(
                    sentence, words, 
                    min_entropy=request.min_entropy,
                    max_rank=request.max_rank
                )
                clunky_scores = [
                    s for s in scores 
                    if s.is_clunky and s.word_text not in ['.', ',', '!', '?', ';', ':', '"', "'", '(', ')']
                ]
                total_words_to_check += len(clunky_scores)
                all_sentence_data.append((sentence, words, scores, clunky_scores))
            
            yield f"data: {json.dumps(await send_progress('scoring', 2, 5, f'Found {total_words_to_check} word(s) to check'))}\n\n"
            await asyncio.sleep(0.05)
            
            # Process sentences with granular progress
            words_processed = 0
            char_offset = 0
            
            for sentence, words, scores, clunky_scores in all_sentence_data:
                # Find the actual position of this sentence in the original text
                sentence_start = request.text.find(sentence, char_offset)
                if sentence_start == -1:
                    # Fallback to char_offset if not found
                    sentence_start = char_offset
                if clunky_scores:
                    alignments = pipeline.aligner.align_words_to_tokens(sentence, words)
                    encoding = pipeline.aligner.tokenizer(sentence, add_special_tokens=True)
                    input_ids = encoding['input_ids']
                    
                    for score in clunky_scores:
                        words_processed += 1
                        
                        # Calculate granular progress (spread across stages 3-4)
                        base_progress = 2 + (words_processed / total_words_to_check) * 2  # 2.0 to 4.0
                        
                        # Send progress for this word
                        yield f"data: {json.dumps(await send_progress('candidates', int(base_progress), 5, f'Analyzing \"{score.word_text}\" ({words_processed}/{total_words_to_check})'))}\n\n"
                        
                        alignment = next((a for a in alignments if a.word_idx == score.word_idx), None)
                        if not alignment:
                            continue
                        
                        flagged_reasons = []
                        if score.entropy >= request.min_entropy:
                            flagged_reasons.append(f"high uncertainty (H≥{request.min_entropy})")
                        if score.rank >= request.max_rank:
                            flagged_reasons.append(f"low rank (rank≥{request.max_rank})")
                        
                        candidates = pipeline.generator.generate_candidates(
                            input_ids, alignment, score.word_text
                        )
                        
                        suggestions = []
                        if candidates:
                            candidate_texts = [c.text for c in candidates]
                            filtered_texts = pipeline.constraints.filter_candidates(
                                score.word_text, candidate_texts, sentence, strict=True
                            )
                            filtered_candidates = [c for c in candidates if c.text in filtered_texts]
                            
                            # Send update for candidate generation
                            yield f"data: {json.dumps(await send_progress('candidates', int(base_progress), 5, f'Generating replacements for \"{score.word_text}\"'))}\n\n"
                            
                            for cand_idx, cand in enumerate(filtered_candidates[:10], 1):
                                # Granular progress for each candidate
                                sub_progress = base_progress + (cand_idx / 10) * 0.1
                                yield f"data: {json.dumps(await send_progress('evaluating', int(sub_progress), 5, f'Evaluating \"{cand.text}\" for \"{score.word_text}\"'))}\n\n"
                                
                                new_text, new_ids = pipeline.aligner.reconstruct_sentence(
                                    input_ids, cand.text, alignment
                                )
                                
                                original_pll = pipeline.scorer.compute_windowed_pll(
                                    input_ids, alignment.token_start,
                                    window_size=pipeline.config.pll_window_size
                                )
                                new_pll = pipeline.scorer.compute_windowed_pll(
                                    new_ids, alignment.token_start,
                                    window_size=pipeline.config.pll_window_size
                                )
                                pll_gain = new_pll - original_pll
                                
                                if pll_gain < 0.5:
                                    continue
                                
                                similarity = pipeline.semantic_checker.compute_similarity(
                                    sentence, new_text
                                )
                                passes = (
                                    pll_gain >= pipeline.config.min_pll_gain and 
                                    similarity >= pipeline.config.min_sbert_cosine
                                )
                                
                                suggestions.append(Suggestion(
                                    text=cand.text,
                                    pll_gain=round(pll_gain, 2),
                                    similarity=round(similarity, 3),
                                    log_prob=round(cand.log_prob, 2),
                                    passes_thresholds=passes,
                                    rank=cand.rank
                                ))
                            
                            suggestions = suggestions[:request.top_suggestions]
                        
                        if suggestions:
                            word_start = sentence_start + alignment.char_start
                            word_end = sentence_start + alignment.char_end
                            highlighted_words.append(HighlightedWord(
                                word=score.word_text,
                                start_pos=word_start,
                                end_pos=word_end,
                                entropy=round(score.entropy, 2),
                                rank=score.rank,
                                log_prob=round(score.log_prob, 2),
                                flagged_reasons=flagged_reasons,
                                suggestions=suggestions
                            ))
                
                # Update char_offset to the end of this sentence in the original text
                char_offset = sentence_start + len(sentence)
            
            # Send final progress
            yield f"data: {json.dumps(await send_progress('complete', 5, 5, 'Analysis complete'))}\n\n"
            await asyncio.sleep(0.1)
            
            # Send final result
            result = HighlightResponse(
                original_text=request.text,
                highlighted_words=highlighted_words,
                total_highlighted=len(highlighted_words),
                sentence_count=len(sentences)
            )
            yield f"data: {json.dumps({'type': 'result', 'data': result.model_dump()})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/highlight", response_model=HighlightResponse)
async def highlight_text(request: HighlightRequest):
    """
    Highlight clunky words in the provided text.
    
    Returns detailed information about each highlighted word including
    suggestions for replacements.
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Split into sentences
        sentences = pipeline._split_sentences(request.text)
        
        highlighted_words = []
        char_offset = 0
        
        for sentence in sentences:
            # Find the actual position of this sentence in the original text
            sentence_start = request.text.find(sentence, char_offset)
            if sentence_start == -1:
                # Fallback to char_offset if not found
                sentence_start = char_offset
            # Extract words
            words = pipeline.constraints.extract_words(sentence)
            
            # Score all words
            scores = pipeline.scorer.score_sentence(
                sentence,
                words,
                min_entropy=request.min_entropy,
                max_rank=request.max_rank
            )
            
            # Filter to clunky words
            clunky_scores = [
                s for s in scores 
                if s.is_clunky and s.word_text not in ['.', ',', '!', '?', ';', ':', '"', "'", '(', ')']
            ]
            
            if not clunky_scores:
                # Update char offset for next sentence
                char_offset = sentence_start + len(sentence)
                continue
            
            # Get alignments and encoding
            alignments = pipeline.aligner.align_words_to_tokens(sentence, words)
            encoding = pipeline.aligner.tokenizer(sentence, add_special_tokens=True)
            input_ids = encoding['input_ids']
            
            # Process each clunky word
            for score in clunky_scores:
                # Find alignment
                alignment = next((a for a in alignments if a.word_idx == score.word_idx), None)
                if not alignment:
                    continue
                
                # Determine why it's flagged
                flagged_reasons = []
                if score.entropy >= request.min_entropy:
                    flagged_reasons.append(f"high uncertainty (H≥{request.min_entropy})")
                if score.rank >= request.max_rank:
                    flagged_reasons.append(f"low rank (rank≥{request.max_rank})")
                
                # Generate candidates
                candidates = pipeline.generator.generate_candidates(
                    input_ids,
                    alignment,
                    score.word_text
                )
                
                suggestions = []
                
                if candidates:
                    # Filter by linguistic constraints
                    candidate_texts = [c.text for c in candidates]
                    filtered_texts = pipeline.constraints.filter_candidates(
                        score.word_text,
                        candidate_texts,
                        sentence,
                        strict=True
                    )
                    
                    filtered_candidates = [
                        c for c in candidates if c.text in filtered_texts
                    ]
                    
                # Evaluate each candidate
                for cand in filtered_candidates[:10]:  # Check more candidates, filter later
                    # Reconstruct sentence
                    new_text, new_ids = pipeline.aligner.reconstruct_sentence(
                        input_ids,
                        cand.text,
                        alignment
                    )
                    
                    # Compute PLL gain
                    original_pll = pipeline.scorer.compute_windowed_pll(
                        input_ids,
                        alignment.token_start,
                        window_size=pipeline.config.pll_window_size
                    )
                    
                    new_pll = pipeline.scorer.compute_windowed_pll(
                        new_ids,
                        alignment.token_start,
                        window_size=pipeline.config.pll_window_size
                    )
                    
                    pll_gain = new_pll - original_pll
                    
                    # Skip suggestions that decrease fluency
                    if pll_gain < 0.5:
                        continue
                    
                    # Compute similarity
                    similarity = pipeline.semantic_checker.compute_similarity(
                        sentence,
                        new_text
                    )
                    
                    # Check if passes thresholds
                    passes = (
                        pll_gain >= pipeline.config.min_pll_gain and 
                        similarity >= pipeline.config.min_sbert_cosine
                    )
                    
                    suggestions.append(Suggestion(
                        text=cand.text,
                        pll_gain=round(pll_gain, 2),
                        similarity=round(similarity, 3),
                        log_prob=round(cand.log_prob, 2),
                        passes_thresholds=passes,
                        rank=cand.rank
                    ))
                
                # Only keep top N suggestions after filtering
                suggestions = suggestions[:request.top_suggestions]
                
                # Only highlight words that have viable suggestions
                if suggestions:
                    # Calculate absolute position in original text
                    word_start = sentence_start + alignment.char_start
                    word_end = sentence_start + alignment.char_end
                    
                    highlighted_words.append(HighlightedWord(
                        word=score.word_text,
                        start_pos=word_start,
                        end_pos=word_end,
                        entropy=round(score.entropy, 2),
                        rank=score.rank,
                        log_prob=round(score.log_prob, 2),
                        flagged_reasons=flagged_reasons,
                        suggestions=suggestions
                    ))
            
            # Update char offset for next sentence
            char_offset = sentence_start + len(sentence)
        
        return HighlightResponse(
            original_text=request.text,
            highlighted_words=highlighted_words,
            total_highlighted=len(highlighted_words),
            sentence_count=len(sentences)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "pipeline_loaded": pipeline is not None,
        "model": pipeline.config.roberta_model if pipeline else None
    }


if __name__ == "__main__":
    print("Starting Flow Highlight API Server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

