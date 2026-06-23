import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false,
  icon: Icon,
  className = '',
  ...props 
}) => {
  const variants = {
    primary: 'bg-gradient-to-r from-gold via-gold-light to-gold hover:from-gold-light hover:via-gold hover:to-gold-dark text-white font-bold shadow-xl hover:shadow-2xl transform hover:scale-105 border-2 border-gold-dark/20',
    secondary: 'bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-900 font-semibold border-2 border-gray-300 shadow-lg hover:shadow-xl transform hover:scale-105',
    outline: 'border-3 border-gold text-gold hover:bg-gold hover:text-white font-bold shadow-md hover:shadow-xl transform hover:scale-105',
    ghost: 'text-gold hover:bg-gold/20 font-semibold hover:shadow-lg transform hover:scale-105',
    danger: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-bold shadow-xl hover:shadow-2xl transform hover:scale-105',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        rounded-xl transition-all duration-300 
        inline-flex items-center justify-center gap-2
        disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : Icon ? (
        <Icon className="w-5 h-5" />
      ) : null}
      <span className="font-bold">{children}</span>
    </motion.button>
  );
};

export default Button;
