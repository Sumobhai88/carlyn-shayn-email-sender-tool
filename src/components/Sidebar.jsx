import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, User, LogOut } from 'lucide-react';

const Sidebar = ({ items, collapsed, onToggle, activeItem, onItemClick, user }) => {
  return (
    <motion.aside
      animate={{ width: collapsed ? '80px' : '280px' }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="bg-white h-screen border-r border-gray-200 flex flex-col relative shadow-sm"
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <AnimatePresence mode="wait">
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gold via-gold-light to-gold shadow-lg flex items-center justify-center animate-float">
                <span className="text-white font-black text-xl">CS</span>
              </div>
              <div>
                <h1 className="text-xl font-black text-gray-900">Carlyn Shayn</h1>
                <p className="text-sm font-semibold text-gray-600">Email Engine</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center"
            >
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gold via-gold-light to-gold shadow-lg flex items-center justify-center animate-float">
                <span className="text-white font-black text-xl">CS</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1 scrollbar-thin">
        {items.map((item) => {
          const isActive = activeItem === item.id;
          const Icon = item.icon;

          return (
            <motion.button
              key={item.id}
              onClick={() => onItemClick(item.id)}
              whileHover={{ scale: 1.05, x: 5 }}
              whileTap={{ scale: 0.95 }}
              className={`
                w-full flex items-center gap-4 px-5 py-4 rounded-xl
                transition-all duration-300 relative group font-semibold text-base
                ${isActive 
                  ? 'bg-gradient-to-r from-gold via-gold-light to-gold text-white shadow-xl border-2 border-gold-dark/30' 
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md border-2 border-transparent'
                }
              `}
            >
              <Icon className={`w-6 h-6 flex-shrink-0 ${isActive ? 'text-white drop-shadow-md' : 'text-gray-600'}`} />
              
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className="whitespace-nowrap font-bold"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>

              {/* Tooltip for collapsed state */}
              {collapsed && (
                <div className="absolute left-full ml-4 px-4 py-3 bg-gray-900 border-2 border-gray-700 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-2xl">
                  <p className="text-sm font-bold text-white">{item.label}</p>
                </div>
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-gray-200">
        <AnimatePresence mode="wait">
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold to-gold-light flex items-center justify-center shadow-md flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.name || 'Admin User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.email || 'admin@carlyshayn.com'}
                </p>
              </div>
              <button className="p-2 hover:bg-red-50 rounded-lg transition-colors group">
                <LogOut className="w-4 h-4 text-gray-400 group-hover:text-red-500" />
              </button>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold to-gold-light flex items-center justify-center shadow-md">
                <User className="w-5 h-5 text-white" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Toggle Button */}
      <motion.button
        onClick={onToggle}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="absolute -right-3 top-20 w-6 h-6 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-md hover:bg-gray-50 transition-colors z-20"
      >
        <motion.div
          animate={{ rotate: collapsed ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronLeft className="w-4 h-4 text-gray-600" />
        </motion.div>
      </motion.button>
    </motion.aside>
  );
};

export default Sidebar;
