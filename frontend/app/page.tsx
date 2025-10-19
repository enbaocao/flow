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
    <div className="min-h-screen" style={{ backgroundColor: '#F7F5F2' }}>
      <main className="max-w-4xl mx-auto px-12 py-20">
        {/* Minimal Header */}
        <div className="mb-20">
          <h1 className="text-xs font-normal tracking-[0.3em] uppercase mb-3" style={{ color: '#1a1a1a', letterSpacing: '0.3em' }}>Flow</h1>
          <div className="w-16 h-[1px]" style={{ backgroundColor: '#1a1a1a' }}></div>
        </div>

        {/* Controls - Floating Top Right */}
        <div className="fixed top-10 right-12 z-10 flex items-center space-x-4">
          <div className="text-[11px] font-light" style={{ color: '#999' }}>
            {text.trim() ? text.trim().split(/\s+/).length : 0} words
          </div>
          <button
            onClick={analyzeText}
            disabled={loading || !text.trim()}
            className="px-8 py-2.5 text-[11px] font-normal tracking-[0.15em] uppercase transition-all relative overflow-hidden"
            style={{ 
              backgroundColor: '#1a1a1a',
              color: '#fff',
              opacity: loading || !text.trim() ? 0.3 : 1
            }}
          >
            {loading && (
              <span 
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20"
                style={{ animation: 'shimmer 1.5s infinite' }}
              />
            )}
            <span className="relative">{loading ? 'Analyzing' : 'Analyze'}</span>
          </button>
          {hasAnalyzed && (
            <button
              onClick={clearAll}
              className="text-[11px] font-light transition-colors"
              style={{ color: '#666' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#1a1a1a'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#666'}
            >
              Clear
            </button>
          )}
          <Controls
            minEntropy={minEntropy}
            setMinEntropy={setMinEntropy}
            maxRank={maxRank}
            setMaxRank={setMaxRank}
            topSuggestions={topSuggestions}
            setTopSuggestions={setTopSuggestions}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-8 p-4 border-l-2 border-black">
            <p className="text-xs text-gray-700">{error}</p>
          </div>
        )}

        {/* Progress Indicator - Always rendered to prevent layout shift */}
        <div className="mb-6 overflow-hidden" style={{ 
          height: '1px', 
          backgroundColor: loading ? '#e8e8e8' : 'transparent'
        }}>
          {loading && (
            <div 
              className="h-full"
              style={{ 
                backgroundColor: '#1a1a1a',
                animation: 'progress 2s ease-in-out infinite',
                width: '30%'
              }}
            />
          )}
        </div>

        {/* Editor - Pure Minimalism */}
        <div className="bg-white" style={{ border: '1px solid #e0e0e0' }}>
          {!hasAnalyzed ? (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  analyzeText();
                }
              }}
              placeholder="Type or paste text"
              className="w-full min-h-[600px] p-16 resize-none leading-loose border-none focus:outline-none"
              style={{ 
                fontFamily: "'Libre Baskerville', serif",
                fontSize: '17px',
                backgroundColor: 'white',
                color: '#1a1a1a',
                lineHeight: '1.8'
              }}
              disabled={loading}
            />
          ) : (
            <HighlightedText
              originalText={text}
              highlightedWords={highlightedWords}
              totalHighlighted={totalHighlighted}
              hasAnalyzed={hasAnalyzed}
              loading={loading}
            />
          )}
        </div>

        {/* Minimal Status */}
        {hasAnalyzed && totalHighlighted > 0 && (
          <div className="mt-6 text-[11px] font-light" style={{ color: '#999' }}>
            {totalHighlighted} highlighted · hover to view
          </div>
        )}
      </main>
    </div>
  );
}
