import { useState, useEffect, useRef } from 'react';
import { Send, Zap, Brain, Square } from 'lucide-react';

export default function SearchBar({ onSubmit, onStop, isResearching, disabled }) {
  const [prompt, setPrompt] = useState('');
  const [mode, setMode] = useState('linear');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!prompt.trim() || isResearching || disabled) return;
    onSubmit(prompt.trim(), mode);
    setPrompt('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) handleSubmit(e);
  };

  return (
    <div className="border-t border-gray-800 bg-gray-950 p-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 flex items-center gap-3">
          <input
            ref={inputRef}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            disabled={isResearching || disabled}
            className="flex-1 bg-transparent text-white text-sm focus:outline-none placeholder-gray-500 disabled:opacity-50"
          />

          {/* Mode toggle — hidden while researching */}
          {!isResearching && (
            <div className="flex-shrink-0">
              <button
                type="button"
                onClick={() => setMode(mode === 'linear' ? 'react' : 'linear')}
                title={mode === 'linear' ? 'Fast: ~3 min' : 'Deep: ~10 min'}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  mode === 'react'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {mode === 'linear' ? <><Zap size={12} /> Fast</> : <><Brain size={12} /> Deep</>}
              </button>
              <p className="text-gray-600 text-center mt-0.5" style={{ fontSize: '10px' }}>
                {mode === 'linear' ? '~3 min' : '~10 min'}
              </p>
            </div>
          )}

          {/* Stop button — visible while researching */}
          {isResearching ? (
            <button
              type="button"
              onClick={onStop}
              className="flex-shrink-0 flex items-center gap-2 px-3 py-2 bg-red-600/20 border border-red-600/40 text-red-400 rounded-lg text-xs font-medium hover:bg-red-600/30 hover:text-red-300 transition-all"
            >
              <Square size={13} fill="currentColor" />
              Stop
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={disabled || !prompt.trim()}
              className="flex-shrink-0 w-9 h-9 bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-full flex items-center justify-center hover:from-blue-500 hover:to-blue-400 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send size={15} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
