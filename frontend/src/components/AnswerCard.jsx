import { motion } from 'framer-motion';
import CitationCard from './CitationCard';

function parseAnswer(text, onCitationClick) {
  const parts = text.split(/(\[\d+\])/g);
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (match) {
      const num = parseInt(match[1]);
      return (
        <button
          key={i}
          onClick={() => onCitationClick(num)}
          className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium bg-blue-600/20 text-blue-400 border border-blue-500/40 rounded mx-0.5 hover:bg-blue-600/40 transition-colors align-super"
          style={{ fontSize: '10px', lineHeight: 1 }}
        >
          {num}
        </button>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

function ConfidenceBar({ value }) {
  const color = value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-500 text-xs whitespace-nowrap">Confidence:</span>
      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
      <span className="text-gray-400 text-xs font-medium">{pct}%</span>
    </div>
  );
}

export default function AnswerCard({ result }) {
  const { answer, citations = [], confidence, query_type, resolved_meaning, react_steps, duration_seconds } = result;

  const scrollToCitation = (num) => {
    document.getElementById(`citation-${num}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-5"
    >
      {/* Answer text */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <p className="text-white text-sm leading-7">
          {parseAnswer(answer, scrollToCitation)}
        </p>

        {/* Metadata bar */}
        <div className="mt-4 pt-4 border-t border-gray-800 space-y-2">
          {confidence != null && <ConfidenceBar value={confidence} />}
          <div className="flex flex-wrap gap-2 items-center">
            {query_type && (
              <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">{query_type}</span>
            )}
            {react_steps != null && (
              <span className="text-xs bg-purple-900/50 text-purple-400 border border-purple-800 px-2 py-0.5 rounded-full">
                Deep reasoning: {react_steps} steps
              </span>
            )}
            {duration_seconds != null && (
              <span className="text-xs text-gray-500">Completed in {duration_seconds}s</span>
            )}
          </div>
          {resolved_meaning && (
            <p className="text-gray-400 text-xs italic">Interpreted as: {resolved_meaning}</p>
          )}
        </div>
      </div>

      {/* Citations */}
      {citations.length > 0 && (
        <div>
          <h3 className="text-gray-400 text-xs font-medium uppercase tracking-wide mb-2">
            Sources <span className="text-gray-600">({citations.length})</span>
          </h3>
          <div className="space-y-2">
            {citations.map((citation, i) => (
              <div key={citation.source_id || i} id={`citation-${i + 1}`}>
                <CitationCard citation={citation} index={i + 1} />
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
