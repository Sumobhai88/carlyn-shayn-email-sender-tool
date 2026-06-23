import { useRef } from 'react';
import { Upload as UploadIcon, X } from 'lucide-react';
import { motion } from 'framer-motion';

const Upload = ({ 
  label, 
  accept, 
  onChange, 
  value,
  onRemove,
  className = '' 
}) => {
  const inputRef = useRef(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}
      
      {!value ? (
        <motion.div
          whileHover={{ scale: 1.01 }}
          onClick={handleClick}
          className="glass glass-hover rounded-lg p-8 cursor-pointer text-center border-2 border-dashed"
        >
          <UploadIcon className="w-12 h-12 mx-auto mb-4 text-gold" />
          <p className="text-gray-300 mb-1">Click to upload or drag and drop</p>
          <p className="text-sm text-gray-500">
            {accept || 'Any file type'}
          </p>
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={onChange}
            className="hidden"
          />
        </motion.div>
      ) : (
        <div className="glass rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gold/20 flex items-center justify-center">
              <UploadIcon className="w-5 h-5 text-gold" />
            </div>
            <div>
              <p className="text-white font-medium">{value.name}</p>
              <p className="text-sm text-gray-400">
                {(value.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>
          <button
            onClick={onRemove}
            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-red-400" />
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;
