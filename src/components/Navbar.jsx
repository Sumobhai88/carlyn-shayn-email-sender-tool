import { Search, Bell, User, Menu, X, CheckCircle, AlertCircle, XCircle, Activity, ArrowRight, Zap, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

const Navbar = ({ 
  title, 
  subtitle, 
  onSearch, 
  notifications = [], 
  onNotificationClick,
  searchQuery: externalSearchQuery,
  searchResults = [],
  showSearchResults = false,
  onSearchResultClick,
  onCloseSearch
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    onSearch?.('');
    onCloseSearch?.();
  };

  const handleResultClick = (result) => {
    onSearchResultClick?.(result);
    setSearchQuery('');
  };

  const notificationCount = notifications.length;

  const getResultIcon = (type) => {
    if (type === 'page') return Menu;
    if (type === 'feature') return Zap;
    return FileText;
  };

  return (
    <nav className="sticky top-0 bg-white/95 backdrop-blur-xl border-b-2 border-gray-200 px-8 py-5 z-40 shadow-lg">
      <div className="flex items-center justify-between">
        {/* Title Section */}
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight">{title}</h2>
          {subtitle && (
            <p className="text-base font-semibold text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* Search Bar */}
          <div className="relative w-96 hidden md:block">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-500 z-10" />
            <input
              type="text"
              placeholder="Search campaigns, templates, contacts..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-14 pr-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-semibold placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-gold transition-all shadow-sm"
            />
            {searchQuery && (
              <button
                onClick={handleClearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-200 rounded-full transition-colors z-10"
              >
                <X className="w-4 h-4 text-gray-600" />
              </button>
            )}

            {/* Search Results Dropdown */}
            <AnimatePresence>
              {showSearchResults && searchResults.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-2xl shadow-2xl overflow-hidden z-50 max-h-96 overflow-y-auto"
                >
                  <div className="p-3 border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                    <p className="text-sm font-black text-gray-900">
                      {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
                    </p>
                  </div>
                  <div className="divide-y-2 divide-gray-100">
                    {searchResults.map((result) => {
                      const Icon = getResultIcon(result.type);
                      return (
                        <div
                          key={`${result.type}-${result.id}`}
                          onClick={() => handleResultClick(result)}
                          className="p-4 hover:bg-gray-50 transition-colors cursor-pointer group"
                        >
                          <div className="flex items-start gap-3">
                            <div className={`p-2 rounded-xl shadow-sm ${
                              result.type === 'page' ? 'bg-blue-100' : 'bg-gold/20'
                            }`}>
                              <Icon className={`w-5 h-5 ${
                                result.type === 'page' ? 'text-blue-600' : 'text-gold'
                              }`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="text-sm font-black text-gray-900">{result.name}</p>
                                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                                  {result.type}
                                </span>
                              </div>
                              <p className="text-xs font-bold text-gray-600">{result.description}</p>
                            </div>
                            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-gold transition-colors" />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              )}
              {showSearchResults && searchResults.length === 0 && searchQuery && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-2xl shadow-2xl p-8 text-center z-50"
                >
                  <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-900 font-bold">No results found</p>
                  <p className="text-sm text-gray-600 font-semibold mt-1">Try searching for campaigns, templates, or features</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Notifications */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-3 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 rounded-xl transition-all shadow-md hover:shadow-lg"
            >
              <Bell className="w-7 h-7 text-gray-700" />
              {notificationCount > 0 && (
                <motion.span 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-gold to-gold-light rounded-full flex items-center justify-center shadow-lg animate-pulse-gold"
                >
                  <span className="text-white text-xs font-black">{notificationCount}</span>
                </motion.span>
              )}
            </motion.button>

            {/* Notifications Dropdown */}
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 mt-2 w-96 bg-white border-2 border-gray-200 rounded-2xl shadow-2xl overflow-hidden z-50"
                >
                  <div className="p-4 border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-black text-gray-900">Notifications</h3>
                      <button
                        onClick={() => setShowNotifications(false)}
                        className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
                      >
                        <X className="w-5 h-5 text-gray-600" />
                      </button>
                    </div>
                  </div>

                  <div className="max-h-96 overflow-y-auto scrollbar-thin">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center">
                        <Bell className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600 font-bold">No new notifications</p>
                        <p className="text-sm text-gray-500 font-semibold mt-1">You're all caught up!</p>
                      </div>
                    ) : (
                      <div className="divide-y-2 divide-gray-100">
                        {notifications.map((notification) => (
                          <div 
                            key={notification.id}
                            onClick={() => {
                              onNotificationClick?.(notification);
                              setShowNotifications(false);
                            }}
                            className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded-xl shadow-sm ${
                                notification.type === 'success' ? 'bg-green-100' :
                                notification.type === 'warning' ? 'bg-yellow-100' :
                                notification.type === 'error' ? 'bg-red-100' :
                                'bg-blue-100'
                              }`}>
                                {notification.type === 'success' && <CheckCircle className="w-5 h-5 text-green-600" />}
                                {notification.type === 'warning' && <AlertCircle className="w-5 h-5 text-yellow-600" />}
                                {notification.type === 'error' && <XCircle className="w-5 h-5 text-red-600" />}
                                {notification.type === 'info' && <Activity className="w-5 h-5 text-blue-600" />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-black text-gray-900 mb-1">{notification.title}</p>
                                <p className="text-xs font-bold text-gray-700 line-clamp-2">{notification.message}</p>
                                <p className="text-xs font-semibold text-gray-500 mt-1">{notification.time}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Quick Actions Menu */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="p-2.5 hover:bg-gray-100 rounded-lg transition-colors hidden lg:block"
          >
            <Menu className="w-6 h-6 text-gray-600" />
          </motion.button>

          {/* User Profile */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-3 p-2 pr-4 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gold to-gold-light flex items-center justify-center ring-2 ring-gold/30 shadow-md">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-gray-900 font-black text-sm">Admin User</p>
              <p className="text-gray-600 text-xs font-bold">Pro Plan</p>
            </div>
          </motion.button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
