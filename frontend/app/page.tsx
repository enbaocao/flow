'use client';

import { useState } from 'react';
import TextInput from './components/TextInput';
import HighlightedText from './components/HighlightedText';
import Controls from './components/Controls';
import { HighlightedWord } from './types';

export default function Home() {
  const [text, setText] = useState('');
  const [highlightedWords, setHighlightedWords] = useState<HighlightedWord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalHighlighted, setTotalHighlighted] = useState(0);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  
  // Configuration
  const [minEntropy, setMinEntropy] = useState(4.0);
  const [maxRank, setMaxRank] = useState(50);
  const [topSuggestions, setTopSuggestions] = useState(3);

  const analyzeText = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setHighlightedWords([]);
    setHasAnalyzed(false);

    try {
      const response = await fetch('http://localhost:8000/api/highlight', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          min_entropy: minEntropy,
          max_rank: maxRank,
          top_suggestions: topSuggestions,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze text');
      }

      const data = await response.json();
      setHighlightedWords(data.highlighted_words);
      setTotalHighlighted(data.total_highlighted);
      setHasAnalyzed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error analyzing text:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setText('');
    setHighlightedWords([]);
    setError(null);
    setTotalHighlighted(0);
    setHasAnalyzed(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Flow Highlight
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              AI-powered text analysis to identify words that need editing
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <Controls
          minEntropy={minEntropy}
          setMinEntropy={setMinEntropy}
          maxRank={maxRank}
          setMaxRank={setMaxRank}
          topSuggestions={topSuggestions}
          setTopSuggestions={setTopSuggestions}
        />

        {/* Main Content - Single Unified Box */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Input Section */}
          <div className="p-6 border-b border-gray-200">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  analyzeText();
                }
              }}
              placeholder="Type or paste your text here...

Example: 'The utilize of advanced technology has revolutionized the way we communicate.'"
              className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-sm"
              disabled={loading}
            />
            
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-500">
                {text.trim() ? text.trim().split(/\s+/).length : 0} words
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={clearAll}
                  disabled={loading || !text}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Clear
                </button>
                
                <button
                  onClick={analyzeText}
                  disabled={loading || !text.trim()}
                  className="px-6 py-2 text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span>Analyze Text</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Error Section */}
          {error && (
            <div className="p-6 bg-red-50 border-b border-red-200">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Section */}
          <HighlightedText
            originalText={text}
            highlightedWords={highlightedWords}
            totalHighlighted={totalHighlighted}
            hasAnalyzed={hasAnalyzed}
            loading={loading}
          />
        </div>

        {/* Legend */}
        <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Understanding the metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-900">Entropy (H):</span>
              <p className="text-gray-600">Higher = more uncertain word choice</p>
            </div>
            <div>
              <span className="font-medium text-gray-900">Rank:</span>
              <p className="text-gray-600">Position in probability distribution</p>
            </div>
            <div>
              <span className="font-medium text-gray-900">ΔLL:</span>
              <p className="text-gray-600">Fluency improvement (higher = better)</p>
            </div>
            <div>
              <span className="font-medium text-gray-900">sim:</span>
              <p className="text-gray-600">Semantic similarity (closer to 1 = preserved meaning)</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
