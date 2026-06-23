import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export const Spinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <Loader2 className={`${sizes[size]} text-gold animate-spin`} />
  );
};

export const LoadingScreen = ({ message = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 bg-dark flex items-center justify-center">
      <div className="text-center">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-400">{message}</p>
      </div>
    </div>
  );
};

export const LoadingCard = () => {
  return (
    <div className="glass rounded-xl p-6 animate-pulse">
      <div className="h-4 bg-white/10 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-white/10 rounded w-1/2"></div>
    </div>
  );
};

export const DotsLoader = () => {
  return (
    <div className="flex items-center gap-2">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.2,
          }}
          className="w-2 h-2 bg-gold rounded-full"
        />
      ))}
    </div>
  );
};
