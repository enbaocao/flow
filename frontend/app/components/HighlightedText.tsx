'use client';

import { useState } from 'react';
import { HighlightedWord } from '../types';

interface HighlightedTextProps {
  originalText: string;
  highlightedWords: HighlightedWord[];
  totalHighlighted: number;
  hasAnalyzed: boolean;
  loading: boolean;
}

interface WordTooltipProps {
  word: HighlightedWord;
}

function WordTooltip({ word }: WordTooltipProps) {
  const getConfidenceLabel = (suggestion: any) => {
    if (suggestion.passes_thresholds && suggestion.pll_gain > 3.0) return 'high confidence';
    if (suggestion.passes_thresholds) return 'recommended';
    return 'consider';
  };

  const getReasonText = (suggestion: any) => {
    const reasons = [];
    if (suggestion.pll_gain >= 1.5) {
      reasons.push('improves fluency');
    }
    if (suggestion.similarity >= 0.95) {
      reasons.push('preserves meaning');
    }
    if (reasons.length === 0) return 'alternative option';
    return reasons.join(', ');
  };

  return (
    <div 
      className="absolute w-80 bg-white p-6 mt-3 left-0 shadow-xl"
      style={{ 
        maxWidth: 'calc(100vw - 2rem)',
        border: '1px solid #e0e0e0',
        zIndex: 100
      }}
    >
      <div className="space-y-4">
        {/* Word with context */}
        <div>
          <div className="font-normal text-[13px] tracking-wide mb-2" style={{ color: '#1a1a1a' }}>
            {word.word}
          </div>
          <div className="text-[10px] font-light" style={{ color: '#999' }}>
            Entropy: {word.entropy.toFixed(1)} bits · Rank #{word.rank}
          </div>
        </div>
        
        {/* Suggestions with detailed metrics */}
        {word.suggestions.length > 0 && (
          <div className="space-y-3 border-t pt-4" style={{ borderColor: '#e8e8e8' }}>
            {word.suggestions.map((suggestion, idx) => (
              <div 
                key={idx} 
                className="group pb-3 border-b last:border-b-0"
                style={{ borderColor: '#f0f0f0' }}
              >
                <div className="flex items-baseline justify-between mb-2">
                  <span className="font-normal text-[14px]" style={{ color: '#1a1a1a' }}>
                    {suggestion.text}
                  </span>
                  <span 
                    className="text-[9px] font-light tracking-wide uppercase px-2 py-0.5"
                    style={{ 
                      color: suggestion.passes_thresholds ? '#1a1a1a' : '#999',
                      backgroundColor: suggestion.passes_thresholds ? '#f0f0f0' : 'transparent'
                    }}
                  >
                    {getConfidenceLabel(suggestion)}
                  </span>
                </div>
                
                {/* Metrics */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-light" style={{ color: '#999' }}>Fluency gain</span>
                    <span 
                      className="font-normal"
                      style={{ 
                        color: suggestion.pll_gain >= 1.5 ? '#1a1a1a' : '#999'
                      }}
                    >
                      {suggestion.pll_gain >= 0 ? '+' : ''}{suggestion.pll_gain.toFixed(1)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-light" style={{ color: '#999' }}>Meaning preserved</span>
                    <span 
                      className="font-normal"
                      style={{ 
                        color: suggestion.similarity >= 0.95 ? '#1a1a1a' : '#999'
                      }}
                    >
                      {(suggestion.similarity * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Reason */}
                <div className="mt-2 text-[10px] font-light italic" style={{ color: '#666' }}>
                  {getReasonText(suggestion)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function HighlightedText({
  originalText,
  highlightedWords,
  totalHighlighted,
  hasAnalyzed,
  loading,
}: HighlightedTextProps) {
  const [hoveredWord, setHoveredWord] = useState<number | null>(null);

  // Show loading state
  if (loading) {
    return (
      <div className="p-16 min-h-[600px] flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin mx-auto h-8 w-8 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" style={{ color: '#ccc' }}>
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-[11px] font-light" style={{ color: '#999' }}>Analyzing</p>
        </div>
      </div>
    );
  }

  // Build the highlighted text (only called if hasAnalyzed is true)
  const renderHighlightedText = () => {
    if (highlightedWords.length === 0 && hasAnalyzed) {
      return (
        <div className="space-y-8">
          <div className="whitespace-pre-wrap" style={{ 
            fontFamily: "'EB Garamond', serif",
            fontSize: '17px',
            fontWeight: 500,
            lineHeight: '1.8',
            color: '#1a1a1a'
          }}>
            {originalText}
          </div>
          <div className="text-[11px] font-light border-t pt-6" style={{ 
            color: '#999',
            borderColor: '#e8e8e8'
          }}>
            No edits suggested
          </div>
        </div>
      );
    }

    const parts: JSX.Element[] = [];
    let lastIndex = 0;

    // Sort highlighted words by position
    const sortedWords = [...highlightedWords].sort((a, b) => a.start_pos - b.start_pos);

    sortedWords.forEach((word, idx) => {
      // Add text before highlighted word
      if (word.start_pos > lastIndex) {
        parts.push(
          <span key={`text-${idx}`}>
            {originalText.substring(lastIndex, word.start_pos)}
          </span>
        );
      }

      // Add highlighted word with tooltip
      parts.push(
        <span
          key={`word-${idx}`}
          className="relative inline-block"
          style={{ zIndex: hoveredWord === idx ? 50 : 1 }}
          onMouseEnter={() => setHoveredWord(idx)}
          onMouseLeave={() => setHoveredWord(null)}
        >
          <span 
            className="cursor-pointer transition-all px-1"
            style={{ 
              backgroundColor: 'rgba(208, 255, 99, 0.3)',
              borderRadius: '2px'
            }}
          >
            {word.word}
          </span>
          {hoveredWord === idx && <WordTooltip word={word} />}
        </span>
      );

      lastIndex = word.end_pos;
    });

    // Add remaining text
    if (lastIndex < originalText.length) {
      parts.push(
        <span key="text-end">
          {originalText.substring(lastIndex)}
        </span>
      );
    }

    return parts;
  };

  return (
    <div className="p-16 min-h-[600px]">
      <div className="whitespace-pre-wrap overflow-visible" style={{ 
        fontFamily: "'EB Garamond', serif", 
        fontSize: '17px',
        fontWeight: 500,
        lineHeight: '1.8',
        color: '#1a1a1a'
      }}>
        {renderHighlightedText()}
      </div>
    </div>
  );
}

