import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

function ConfidenceBadge({ confidence }) {
  if (confidence == null) return null;
  if (confidence >= 0.7) return <span className="flex items-center gap-1 text-xs text-green-400"><span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />High</span>;
  if (confidence >= 0.4) return <span className="flex items-center gap-1 text-xs text-yellow-400"><span className="w-1.5 h-1.5 rounded-full bg-yellow-400 inline-block" />Medium</span>;
  return <span className="flex items-center gap-1 text-xs text-red-400"><span className="w-1.5 h-1.5 rounded-full bg-red-400 inline-block" />Low</span>;
}

function getDomain(url) {
  try { return new URL(url).hostname; } catch { return url; }
}

export default function CitationCard({ citation, index }) {
  const [expanded, setExpanded] = useState(false);
  const domain = getDomain(citation.url);

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-800/80 transition-colors"
      >
        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-400 text-xs flex items-center justify-center font-medium">
          {index}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium truncate">{citation.title}</p>
          <p className="text-gray-500 text-xs">{domain}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <ConfidenceBadge confidence={citation.confidence} />
          {expanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-gray-700/50 pt-3">
              <a
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 text-xs break-all transition-colors"
              >
                <ExternalLink size={11} />
                {citation.url}
              </a>
              {citation.evidence && (
                <div className="border-l-2 border-gray-600 pl-3">
                  <p className="text-gray-300 text-sm leading-relaxed">{citation.evidence}</p>
                </div>
              )}
              {citation.quotes && citation.quotes !== citation.evidence && (
                <p className="text-gray-400 text-xs italic">"{citation.quotes}"</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
