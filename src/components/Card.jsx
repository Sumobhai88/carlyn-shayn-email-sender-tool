import { motion } from 'framer-motion';

const Card = ({ 
  children, 
  hover = true, 
  padding = 'md',
  className = '' 
}) => {
  const paddings = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { 
        y: -8, 
        scale: 1.02,
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        borderColor: 'rgba(212, 175, 55, 0.4)',
        transition: { duration: 0.3 }
      } : {}}
      className={`
        bg-white rounded-2xl border-2 border-gray-200 shadow-lg
        ${hover ? 'cursor-pointer' : ''}
        ${paddings[padding]}
        ${className}
      `}
      style={{
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {children}
    </motion.div>
  );
};

export default Card;
