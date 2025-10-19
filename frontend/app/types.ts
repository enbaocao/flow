export interface Suggestion {
  text: string;
  pll_gain: number;
  similarity: number;
  log_prob: number;
  passes_thresholds: boolean;
  rank: number;
}

export interface HighlightedWord {
  word: string;
  start_pos: number;
  end_pos: number;
  entropy: number;
  rank: number;
  log_prob: number;
  flagged_reasons: string[];
  suggestions: Suggestion[];
}

export interface HighlightResponse {
  original_text: string;
  highlighted_words: HighlightedWord[];
  total_highlighted: number;
  sentence_count: number;
}

