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
  return (
    <div className="absolute z-[100] w-80 bg-white rounded-lg shadow-xl border border-gray-200 p-4 mt-2 left-0" style={{ maxWidth: 'calc(100vw - 2rem)' }}>
      <div className="space-y-3">
        {/* Word info */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">📝 &apos;{word.word}&apos;</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500">Entropy:</span>
              <span className="ml-1 font-medium text-gray-900">{word.entropy.toFixed(2)} bits</span>
            </div>
            <div>
              <span className="text-gray-500">Rank:</span>
              <span className="ml-1 font-medium text-gray-900">#{word.rank}</span>
            </div>
          </div>
          {word.flagged_reasons.length > 0 && (
            <div className="mt-2 text-xs">
              <span className="text-gray-500">Flagged:</span>
              <span className="ml-1 text-orange-600">{word.flagged_reasons.join(', ')}</span>
            </div>
          )}
        </div>

        {/* Suggestions */}
        {word.suggestions.length > 0 && (
          <div className="border-t border-gray-200 pt-3">
            <h5 className="text-xs font-semibold text-gray-700 mb-2">Top replacements:</h5>
            <div className="space-y-2">
              {word.suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded ${
                    suggestion.passes_thresholds
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-gray-50 border border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {suggestion.passes_thresholds && (
                        <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                      <span className="text-sm font-medium text-gray-900">{suggestion.text}</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-x-3 mt-1 text-xs text-gray-600">
                    <div>
                      <span className="text-gray-500">ΔLL:</span>
                      <span className={`ml-1 font-medium ${
                        suggestion.pll_gain >= 1.5 ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {suggestion.pll_gain >= 0 ? '+' : ''}{suggestion.pll_gain.toFixed(2)}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">sim:</span>
                      <span className={`ml-1 font-medium ${
                        suggestion.similarity >= 0.95 ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {suggestion.similarity.toFixed(3)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {word.suggestions.length === 0 && (
          <div className="text-xs text-gray-500 italic">
            No suitable replacements found
          </div>
        )}
      </div>
      
      {/* Tooltip arrow */}
      <div className="absolute -top-2 left-4 w-4 h-4 bg-white border-l border-t border-gray-200 transform rotate-45"></div>
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

  // Show empty state if no text or not yet analyzed
  if (!originalText || (!hasAnalyzed && !loading)) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-400">
          <svg className="mx-auto h-12 w-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">Analysis results will appear here</p>
          <p className="text-xs mt-1">Click &quot;Analyze Text&quot; to get started</p>
        </div>
      </div>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-500">
          <svg className="animate-spin mx-auto h-12 w-12 text-indigo-500 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-sm font-medium">Analyzing your text...</p>
          <p className="text-xs mt-1 text-gray-400">This may take a few seconds</p>
        </div>
      </div>
    );
  }

  // Build the highlighted text (only called if hasAnalyzed is true)
  const renderHighlightedText = () => {
    if (highlightedWords.length === 0 && hasAnalyzed) {
      return (
        <div className="space-y-3">
          <div className="text-gray-700 leading-relaxed whitespace-pre-wrap font-mono text-sm">
            {originalText}
          </div>
          <div className="flex items-center space-x-2 text-green-600 bg-green-50 border border-green-200 rounded-lg p-3">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium">No issues detected! Your text looks great.</span>
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
          className="relative inline-block z-10"
          onMouseEnter={() => setHoveredWord(idx)}
          onMouseLeave={() => setHoveredWord(null)}
        >
          <span className="bg-yellow-200 border-b-2 border-yellow-400 px-1 cursor-pointer hover:bg-yellow-300 transition-colors rounded">
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
    <>
      <div className="border-b border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
          <p className="text-sm text-gray-500 mt-1">
            {totalHighlighted > 0 
              ? `${totalHighlighted} word${totalHighlighted !== 1 ? 's' : ''} highlighted • Hover for suggestions`
              : 'No issues found'
            }
          </p>
        </div>
        {totalHighlighted > 0 && (
          <div className="text-xs bg-yellow-100 text-yellow-800 px-3 py-1.5 rounded-full font-medium">
            {totalHighlighted} issue{totalHighlighted !== 1 ? 's' : ''}
          </div>
        )}
      </div>
      
      <div className="p-6 overflow-visible">
        <div className="text-gray-700 leading-relaxed whitespace-pre-wrap text-sm overflow-visible">
          {renderHighlightedText()}
        </div>
      </div>

      {totalHighlighted > 0 && (
        <div className="border-t border-gray-200 bg-indigo-50/50 px-6 py-4">
          <div className="flex items-start space-x-2 text-xs text-gray-600">
            <svg className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div className="text-gray-700">
              <span className="bg-yellow-200 px-1.5 py-0.5 rounded">Yellow highlighting</span> indicates words that might need editing. 
              Hover over them to see suggestions. 
              <span className="text-green-600 font-medium ml-1">✓</span> means the suggestion passes all quality checks.
            </div>
          </div>
        </div>
      )}
    </>
  );
}

