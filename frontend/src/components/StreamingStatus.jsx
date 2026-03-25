import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Search, BarChart2, PenTool, CheckCircle, GitBranch, Circle } from 'lucide-react';

const STAGE_META = {
  analyzing:      { icon: Brain,       label: 'Analyzing' },
  planning:       { icon: Brain,       label: 'Planning' },
  searching:      { icon: Search,      label: 'Searching' },
  scoring:        { icon: BarChart2,   label: 'Scoring' },
  synthesizing:   { icon: PenTool,     label: 'Synthesizing' },
  thinking:       { icon: Brain,       label: 'Thinking' },
  react_step:     { icon: Brain,       label: 'Reasoning' },
  disambiguating: { icon: GitBranch,   label: 'Disambiguating' },
  done:           { icon: CheckCircle, label: 'Done' },
};

function StageRow({ stage, message, isCurrent, isComplete, index }) {
  const meta = STAGE_META[stage] || { icon: Circle, label: stage };
  const Icon = meta.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="flex items-start gap-3 py-1.5"
    >
      <div className="flex-shrink-0 mt-0.5">
        {stage === 'done' ? (
          <CheckCircle size={16} className="text-green-400" />
        ) : isCurrent ? (
          <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
        ) : isComplete ? (
          <CheckCircle size={16} className="text-green-500" />
        ) : (
          <Circle size={16} className="text-gray-600" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        {stage === 'react_step' ? (
          <p className="text-gray-300 text-sm"><span className="text-purple-400 font-medium">Step {index + 1}:</span> {message}</p>
        ) : (
          <>
            <span className={`text-sm font-medium ${isCurrent ? 'text-white' : isComplete ? 'text-gray-400' : 'text-gray-600'}`}>
              {meta.label}
            </span>
            {message && (
              <p className={`text-xs mt-0.5 ${isCurrent ? 'text-gray-300' : 'text-gray-500'}`}>{message}</p>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}

export default function StreamingStatus({ stages, isComplete, mode }) {
  const borderColor = mode === 'react' ? 'border-purple-500' : 'border-blue-500';

  return (
    <div className={`border-l-2 ${borderColor} pl-4 py-2`}>
      <AnimatePresence>
        {stages.map((s, i) => (
          <StageRow
            key={`${s.stage}-${i}`}
            stage={s.stage}
            message={s.message}
            isCurrent={!isComplete && i === stages.length - 1}
            isComplete={isComplete || i < stages.length - 1}
            index={i}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
