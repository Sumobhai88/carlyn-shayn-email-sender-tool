import { motion } from 'framer-motion';

const ProgressBar = ({ 
  value, 
  max = 100, 
  color = 'gold', 
  showLabel = true,
  height = 'md',
  animated = true 
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const heights = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
    xl: 'h-4'
  };

  const colorClasses = {
    gold: 'from-gold to-gold-light',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600'
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Progress</span>
          <span className="text-sm text-white font-semibold">
            {percentage.toFixed(0)}%
          </span>
        </div>
      )}
      <div className={`w-full ${heights[height]} bg-white/5 rounded-full overflow-hidden`}>
        {animated ? (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className={`h-full bg-gradient-to-r ${colorClasses[color]}`}
          />
        ) : (
          <div
            style={{ width: `${percentage}%` }}
            className={`h-full bg-gradient-to-r ${colorClasses[color]}`}
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
