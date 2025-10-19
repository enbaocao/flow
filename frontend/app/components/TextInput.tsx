'use client';

interface TextInputProps {
  text: string;
  setText: (text: string) => void;
  onAnalyze: () => void;
  onClear: () => void;
  loading: boolean;
}

export default function TextInput({ text, setText, onAnalyze, onClear, loading }: TextInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      onAnalyze();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="border-b border-gray-200 bg-gray-50 px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-900">Input Text</h2>
        <p className="text-sm text-gray-500 mt-1">Paste your text here for analysis</p>
      </div>
      
      <div className="p-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type or paste your text here...

Example: 'The utilize of advanced technology has revolutionized the way we communicate.'"
          className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none font-mono text-sm"
          disabled={loading}
        />
        
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500">
            {text.length} characters
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={onClear}
              disabled={loading || !text}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Clear
            </button>
            
            <button
              onClick={onAnalyze}
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
        
        <p className="text-xs text-gray-400 mt-2">
          Tip: Press Cmd/Ctrl + Enter to analyze
        </p>
      </div>
    </div>
  );
}

