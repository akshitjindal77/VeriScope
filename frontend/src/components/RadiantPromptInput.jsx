import React, { useState } from 'react';
import { ArrowUp, Zap, Brain, Square } from 'lucide-react';

export default function RadiantPromptInput({
  placeholder = "Ask anything...",
  value: propValue,
  onChange: propOnChange,
  onSubmit,
  onStop,
  disabled = false,
  isResearching = false,
  mode = "linear",
  onModeToggle,
  className = "",
}) {
  const [internalValue, setInternalValue] = useState("");
  const isControlled = propValue !== undefined;
  const value = isControlled ? propValue : internalValue;

  const handleChange = (e) => {
    if (!isControlled) {
      setInternalValue(e.target.value);
    }
    propOnChange?.(e.target.value);
  };

  const handleSubmit = () => {
    if (value && !disabled && !isResearching) {
      onSubmit?.(value, mode);
      if (!isControlled) setInternalValue("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`relative w-full max-w-3xl mx-auto ${className}`}>
      {/* Custom CSS for the rotating conic gradient border */}
      <style>{`
        @property --rotation {
          syntax: '<angle>';
          inherits: false;
          initial-value: 0deg;
        }

        @keyframes rotate-gradient {
          to {
            --rotation: 360deg;
          }
        }

        .radiant-input-wrapper {
          --border-size: 2px;
          --gradient: conic-gradient(
            from var(--rotation)
            at 50% 50% in oklab,
            oklch(0.55 0.18 250) 27%,
            oklch(0.50 0.15 280) 33%,
            oklch(0.55 0.18 250) 41%,
            oklch(0.45 0.12 220) 49%,
            oklch(0.55 0.18 250) 65%,
            oklch(0.50 0.15 280) 93%,
            oklch(0.55 0.18 250)
          );
          animation: rotate-gradient 5s infinite linear;
        }

        .radiant-input-wrapper.researching {
          --gradient: conic-gradient(
            from var(--rotation)
            at 50% 50% in oklab,
            oklch(0.65 0.2 150) 27%,
            oklch(0.55 0.18 250) 33%,
            oklch(0.65 0.2 150) 41%,
            oklch(0.55 0.18 250) 49%,
            oklch(0.65 0.2 150) 65%,
            oklch(0.55 0.18 250) 93%,
            oklch(0.65 0.2 150)
          );
          animation: rotate-gradient 2s infinite linear;
        }

        .radiant-input-wrapper.deep-mode {
          --gradient: conic-gradient(
            from var(--rotation)
            at 50% 50% in oklab,
            oklch(0.55 0.2 300) 27%,
            oklch(0.50 0.18 280) 33%,
            oklch(0.60 0.22 320) 41%,
            oklch(0.50 0.18 260) 49%,
            oklch(0.55 0.2 300) 65%,
            oklch(0.50 0.18 280) 93%,
            oklch(0.55 0.2 300)
          );
        }

        /* Glowing border halo */
        .radiant-input-wrapper::before {
          content: '';
          position: absolute;
          inset: calc(var(--border-size) * -1);
          border-radius: inherit;
          background: var(--gradient);
          z-index: -1;
          filter: blur(10px);
          opacity: 0.4;
          transition: opacity 0.3s ease;
        }

        .radiant-input-wrapper:hover::before,
        .radiant-input-wrapper:focus-within::before {
          opacity: 0.7;
        }

        .radiant-input-wrapper.researching::before {
          opacity: 0.8;
          filter: blur(14px);
        }

        /* Sharp border mask */
        .radiant-input-border {
          position: absolute;
          inset: 0;
          border-radius: inherit;
          padding: var(--border-size);
          background: var(--gradient);
          -webkit-mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          pointer-events: none;
        }
      `}</style>

      <div
        className={`radiant-input-wrapper relative rounded-2xl bg-gray-900 transition-all duration-300 hover:shadow-lg ${
          isResearching ? 'researching' : ''
        } ${mode === 'react' ? 'deep-mode' : ''}`}
      >
        {/* Animated gradient border */}
        <div className="radiant-input-border rounded-2xl" />

        {/* Inner content */}
        <div className="relative z-10 flex items-center gap-2 p-2 pl-5 pr-2 h-14 md:h-16">

          {/* Mode toggle */}
          <button
            type="button"
            onClick={onModeToggle}
            disabled={isResearching}
            title={mode === 'react' ? 'Deep Reasoning (~10 min)' : 'Fast Research (~3 min)'}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 whitespace-nowrap ${
              mode === 'react'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30 hover:bg-purple-500/30'
                : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
            } ${isResearching ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {mode === 'react' ? (
              <>
                <Brain size={14} />
                <span className="hidden sm:inline">Deep</span>
              </>
            ) : (
              <>
                <Zap size={14} />
                <span className="hidden sm:inline">Fast</span>
              </>
            )}
          </button>

          {/* Text input */}
          <input
            type="text"
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={isResearching ? "Researching..." : placeholder}
            disabled={disabled || isResearching}
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-gray-500 text-base md:text-lg font-light tracking-wide h-full w-full min-w-0"
          />

          {/* Submit / Stop button */}
          {isResearching ? (
            <button
              type="button"
              onClick={onStop}
              aria-label="Stop research"
              className="flex items-center justify-center w-10 h-10 md:w-11 md:h-11 rounded-xl transition-all duration-300 bg-red-500/20 text-red-400 hover:bg-red-500/30 hover:scale-105 active:scale-95"
            >
              <Square size={16} />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!value || disabled}
              aria-label="Send message"
              className={`flex items-center justify-center w-10 h-10 md:w-11 md:h-11 rounded-xl transition-all duration-300 ${
                value && !disabled
                  ? 'bg-blue-600 text-white hover:bg-blue-500 hover:scale-105 active:scale-95 shadow-md shadow-blue-500/25'
                  : 'bg-gray-800 text-gray-600 cursor-not-allowed'
              }`}
            >
              <ArrowUp size={20} strokeWidth={2.5} />
            </button>
          )}
        </div>
      </div>

      {/* Mode description */}
      <div className="flex justify-center mt-2">
        <span className="text-xs text-gray-600">
          {mode === 'react'
            ? '🧠 Deep reasoning • ~10 min • Multi-step analysis'
            : '⚡ Fast research • ~3 min • Single-pass synthesis'}
        </span>
      </div>
    </div>
  );
}
