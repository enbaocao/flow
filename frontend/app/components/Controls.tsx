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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <span className="text-sm font-medium text-gray-900">Analysis Settings</span>
          {!showAdvanced && (
            <span className="text-xs text-gray-500 ml-2">
              (Entropy: {minEntropy}, Rank: {maxRank}, Suggestions: {topSuggestions})
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showAdvanced && (
        <div className="px-4 pb-4 pt-2 border-t border-gray-200 space-y-4">
          {/* Sensitivity Presets */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sensitivity Presets
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => {
                  setMinEntropy(5.0);
                  setMaxRank(20);
                }}
                className="px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded hover:bg-gray-200 transition-colors"
              >
                Conservative
                <span className="block text-gray-500 text-[10px] mt-0.5">Only obvious issues</span>
              </button>
              <button
                onClick={resetToDefaults}
                className="px-3 py-2 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-300 rounded hover:bg-indigo-100 transition-colors"
              >
                Balanced
                <span className="block text-indigo-500 text-[10px] mt-0.5">Recommended</span>
              </button>
              <button
                onClick={() => {
                  setMinEntropy(3.5);
                  setMaxRank(100);
                }}
                className="px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded hover:bg-gray-200 transition-colors"
              >
                Aggressive
                <span className="block text-gray-500 text-[10px] mt-0.5">Catch more issues</span>
              </button>
            </div>
          </div>

          {/* Min Entropy Slider */}
          <div>
            <label htmlFor="entropy-slider" className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Entropy Threshold: {minEntropy.toFixed(1)} bits
            </label>
            <div className="flex items-center space-x-3">
              <span className="text-xs text-gray-500">3.0</span>
              <input
                id="entropy-slider"
                type="range"
                min="3.0"
                max="6.0"
                step="0.1"
                value={minEntropy}
                onChange={(e) => setMinEntropy(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <span className="text-xs text-gray-500">6.0</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Higher = only flag very uncertain words
            </p>
          </div>

          {/* Max Rank Slider */}
          <div>
            <label htmlFor="rank-slider" className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Original Rank: #{maxRank}
            </label>
            <div className="flex items-center space-x-3">
              <span className="text-xs text-gray-500">10</span>
              <input
                id="rank-slider"
                type="range"
                min="10"
                max="200"
                step="10"
                value={maxRank}
                onChange={(e) => setMaxRank(parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <span className="text-xs text-gray-500">200</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Lower = only flag words with low probability rank
            </p>
          </div>

          {/* Top Suggestions */}
          <div>
            <label htmlFor="suggestions-slider" className="block text-sm font-medium text-gray-700 mb-2">
              Suggestions per Word: {topSuggestions}
            </label>
            <div className="flex items-center space-x-3">
              <span className="text-xs text-gray-500">1</span>
              <input
                id="suggestions-slider"
                type="range"
                min="1"
                max="5"
                step="1"
                value={topSuggestions}
                onChange={(e) => setTopSuggestions(parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <span className="text-xs text-gray-500">5</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Number of replacement suggestions to show
            </p>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetToDefaults}
            className="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
          >
            Reset to Defaults
          </button>
        </div>
      )}
    </div>
  );
}

