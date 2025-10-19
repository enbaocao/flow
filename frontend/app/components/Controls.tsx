'use client';

import { useState } from 'react';

interface ControlsProps {
  minEntropy: number;
  setMinEntropy: (value: number) => void;
  maxRank: number;
  setMaxRank: (value: number) => void;
  topSuggestions: number;
  setTopSuggestions: (value: number) => void;
}

export default function Controls({
  minEntropy,
  setMinEntropy,
  maxRank,
  setMaxRank,
  topSuggestions,
  setTopSuggestions,
}: ControlsProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const resetToDefaults = () => {
    setMinEntropy(4.0);
    setMaxRank(50);
    setTopSuggestions(3);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-[11px] font-light transition-colors"
        style={{ color: '#666' }}
        onMouseEnter={(e) => e.currentTarget.style.color = '#1a1a1a'}
        onMouseLeave={(e) => e.currentTarget.style.color = '#666'}
      >
        Settings
      </button>

      {showAdvanced && (
        <div 
          className="absolute top-full right-0 mt-2 w-80 bg-white p-6 shadow-xl"
          style={{ border: '1px solid #e0e0e0' }}
        >
          <div className="space-y-6">
            {/* Presets */}
            <div>
              <div className="text-[10px] font-light tracking-wide uppercase mb-3" style={{ color: '#999' }}>
                Presets
              </div>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => {
                    setMinEntropy(5.0);
                    setMaxRank(20);
                  }}
                  className="py-2 text-[11px] font-light border transition-colors"
                  style={{ borderColor: '#e0e0e0', color: '#666' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9f9f9';
                    e.currentTarget.style.color = '#1a1a1a';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.color = '#666';
                  }}
                >
                  Conservative
                </button>
                <button
                  onClick={resetToDefaults}
                  className="py-2 text-[11px] font-normal border transition-colors"
                  style={{ borderColor: '#1a1a1a', color: '#1a1a1a', backgroundColor: '#f9f9f9' }}
                >
                  Balanced
                </button>
                <button
                  onClick={() => {
                    setMinEntropy(3.5);
                    setMaxRank(100);
                  }}
                  className="py-2 text-[11px] font-light border transition-colors"
                  style={{ borderColor: '#e0e0e0', color: '#666' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9f9f9';
                    e.currentTarget.style.color = '#1a1a1a';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.color = '#666';
                  }}
                >
                  Aggressive
                </button>
              </div>
            </div>

            {/* Entropy */}
            <div>
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-[10px] font-light tracking-wide uppercase" style={{ color: '#999' }}>
                  Entropy Threshold
                </span>
                <span className="text-[11px] font-normal" style={{ color: '#1a1a1a' }}>
                  {minEntropy.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="3.0"
                max="6.0"
                step="0.1"
                value={minEntropy}
                onChange={(e) => setMinEntropy(parseFloat(e.target.value))}
                className="w-full h-px appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #1a1a1a 0%, #1a1a1a ${((minEntropy - 3.0) / 3.0) * 100}%, #e0e0e0 ${((minEntropy - 3.0) / 3.0) * 100}%, #e0e0e0 100%)`
                }}
              />
              <div className="flex justify-between mt-1">
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>3.0</span>
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>6.0</span>
              </div>
            </div>

            {/* Rank */}
            <div>
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-[10px] font-light tracking-wide uppercase" style={{ color: '#999' }}>
                  Max Rank
                </span>
                <span className="text-[11px] font-normal" style={{ color: '#1a1a1a' }}>
                  #{maxRank}
                </span>
              </div>
              <input
                type="range"
                min="10"
                max="200"
                step="10"
                value={maxRank}
                onChange={(e) => setMaxRank(parseInt(e.target.value))}
                className="w-full h-px appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #1a1a1a 0%, #1a1a1a ${((maxRank - 10) / 190) * 100}%, #e0e0e0 ${((maxRank - 10) / 190) * 100}%, #e0e0e0 100%)`
                }}
              />
              <div className="flex justify-between mt-1">
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>10</span>
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>200</span>
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-[10px] font-light tracking-wide uppercase" style={{ color: '#999' }}>
                  Suggestions
                </span>
                <span className="text-[11px] font-normal" style={{ color: '#1a1a1a' }}>
                  {topSuggestions}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={topSuggestions}
                onChange={(e) => setTopSuggestions(parseInt(e.target.value))}
                className="w-full h-px appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #1a1a1a 0%, #1a1a1a ${((topSuggestions - 1) / 4) * 100}%, #e0e0e0 ${((topSuggestions - 1) / 4) * 100}%, #e0e0e0 100%)`
                }}
              />
              <div className="flex justify-between mt-1">
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>1</span>
                <span className="text-[9px] font-light" style={{ color: '#ccc' }}>5</span>
              </div>
            </div>

            {/* Reset */}
            <button
              onClick={resetToDefaults}
              className="w-full pt-4 mt-2 text-[10px] font-light border-t transition-colors"
              style={{ borderColor: '#e8e8e8', color: '#999' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#1a1a1a'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#999'}
            >
              Reset to defaults
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

