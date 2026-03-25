import { motion } from 'framer-motion';

const SIZES = {
  sm: { height: 'h-0.5', text: null },
  md: { height: 'h-1', text: 'text-xs' },
  lg: { height: 'h-1.5', text: 'text-sm' },
};

export default function ConfidenceMeter({ value, size = 'md' }) {
  const { height, text } = SIZES[size] || SIZES.md;
  const pct = Math.round((value ?? 0) * 100);
  const color = value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="space-y-1">
      <div className={`w-full bg-gray-800 rounded-full overflow-hidden ${height}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
      {text && (
        <p className={`${text} text-gray-400`}>{pct}%</p>
      )}
    </div>
  );
}
