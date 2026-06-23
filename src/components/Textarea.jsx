import { forwardRef } from 'react';

const Textarea = forwardRef(({ 
  label, 
  error, 
  rows = 4,
  className = '', 
  ...props 
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-base font-bold text-gray-700 mb-2">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={`
          w-full px-4 py-3 
          bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-semibold placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-gold shadow-sm
          transition-all duration-300 resize-none
          ${error ? 'border-red-500 focus:ring-red-500/50' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

export default Textarea;
