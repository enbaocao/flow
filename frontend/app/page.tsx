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
  const [progress, setProgress] = useState({ stage: '', progress: 0, message: '' });
  
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
    setProgress({ stage: '', progress: 0, message: '' });

    try {
      const response = await fetch('http://localhost:8000/api/highlight-stream', {
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
        const errorText = await response.text();
        throw new Error(`API error: ${errorText || response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'result') {
              // Final result
              setHighlightedWords(data.data.highlighted_words);
              setTotalHighlighted(data.data.total_highlighted);
              setHasAnalyzed(true);
              setLoading(false);
            } else if (data.type === 'error') {
              throw new Error(data.message);
            } else {
              // Progress update
              setProgress({
                stage: data.stage,
                progress: data.progress,
                message: data.message
              });
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error analyzing text:', err);
      setLoading(false);
    }
  };

  const clearAll = () => {
    setText('');
    setHighlightedWords([]);
    setError(null);
    setTotalHighlighted(0);
    setHasAnalyzed(false);
    setProgress({ stage: '', progress: 0, message: '' });
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F7F5F2' }}>
      <main className="max-w-4xl mx-auto px-12 py-20">
        {/* Header with mirrored layout */}
        <div className="mb-20 flex items-start justify-between">
          {/* Left side - Flow title */}
          <div>
            <h1 className="text-xs font-normal tracking-[0.3em] uppercase mb-3" style={{ color: '#1a1a1a', letterSpacing: '0.3em' }}>Flow</h1>
            <div className="w-16 h-[1px]" style={{ backgroundColor: '#1a1a1a' }}></div>
          </div>
          
          {/* Right side - Controls */}
          <div className="flex items-center space-x-4">
            <div className="text-[11px] font-light" style={{ color: '#999' }}>
              {text.trim() ? text.trim().split(/\s+/).length : 0} words
            </div>
            
            {!hasAnalyzed ? (
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
            ) : (
              <button
                onClick={clearAll}
                className="px-8 py-2.5 text-[11px] font-normal tracking-[0.15em] uppercase transition-all"
                style={{ 
                  backgroundColor: '#1a1a1a',
                  color: '#fff'
                }}
              >
                Reset
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
        </div>

        {/* Error */}
        {error && (
          <div className="mb-8 p-4 border-l-2 border-black">
            <p className="text-xs text-gray-700">{error}</p>
          </div>
        )}


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
                fontFamily: "'EB Garamond', serif",
                fontSize: '17px',
                fontWeight: 500,
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

        {/* Footer Actions */}
        {hasAnalyzed && (
          <div className="mt-8 flex items-center justify-between border-t pt-6" style={{ borderColor: '#e8e8e8' }}>
            <div className="text-[11px] font-light" style={{ color: '#999' }}>
              {totalHighlighted > 0 
                ? `${totalHighlighted} word${totalHighlighted !== 1 ? 's' : ''} highlighted · hover to view`
                : 'Analysis complete'
              }
            </div>
            <button
              onClick={clearAll}
              className="text-[11px] font-light tracking-wide uppercase transition-colors"
              style={{ color: '#999' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#1a1a1a'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#999'}
            >
              Analyze Another →
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
