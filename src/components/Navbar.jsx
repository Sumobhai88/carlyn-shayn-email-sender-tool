import { Search, Bell, User, Menu, X, CheckCircle, AlertCircle, XCircle, Activity, ArrowRight, Zap, FileText, LogOut, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

const Navbar = ({ 
  title, 
  subtitle, 
  onSearch,
  searchResults = [],
  showSearchResults = false,
  onSearchResultClick,
  onCloseSearch,
  onLogout,
  user
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Fetch notifications on mount and every 30s
  const fetchNotifications = useCallback(async () => {
    try {
      const res = await api.get('/api/v1/settings/notifications');
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (e) {
      // ignore if not logged in yet
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const handleMarkRead = async (e, notifId) => {
    e.stopPropagation();
    try {
      await api.post(`/api/v1/settings/notifications/${notifId}/read`);
      setNotifications(prev => prev.map(n => n.id === notifId ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {}
  };

  const handleMarkAllRead = async () => {
    try {
      await api.post('/api/v1/settings/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) {}
  };

  const handleDeleteNotif = async (e, notifId) => {
    e.stopPropagation();
    try {
      await api.delete(`/api/v1/settings/notifications/${notifId}`);
      setNotifications(prev => prev.filter(n => n.id !== notifId));
      setUnreadCount(prev => {
        const wasUnread = notifications.find(n => n.id === notifId && !n.is_read);
        return wasUnread ? Math.max(0, prev - 1) : prev;
      });
    } catch (e) {}
  };

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
              {unreadCount > 0 && (
                <motion.span 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-gold to-gold-light rounded-full flex items-center justify-center shadow-lg animate-pulse-gold"
                >
                  <span className="text-white text-xs font-black">{unreadCount > 9 ? '9+' : unreadCount}</span>
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
                      <div className="flex items-center gap-2">
                        {unreadCount > 0 && (
                          <button
                            onClick={handleMarkAllRead}
                            className="text-xs font-bold text-gold hover:underline px-2 py-1"
                          >
                            Mark all read
                          </button>
                        )}
                        <button
                          onClick={() => setShowNotifications(false)}
                          className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                          <X className="w-5 h-5 text-gray-600" />
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="max-h-96 overflow-y-auto scrollbar-thin">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center">
                        <Bell className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600 font-bold">No notifications yet</p>
                        <p className="text-sm text-gray-500 font-semibold mt-1">Campaign updates will appear here</p>
                      </div>
                    ) : (
                      <div className="divide-y-2 divide-gray-100">
                        {notifications.map((notification) => (
                          <div 
                            key={notification.id}
                            className={`p-4 transition-colors group relative ${notification.is_read ? 'bg-white' : 'bg-blue-50/50 hover:bg-blue-50'}`}
                          >
                            <div className="flex items-start gap-3">
                              {/* unread dot */}
                              {!notification.is_read && (
                                <span className="absolute top-4 right-4 w-2 h-2 bg-gold rounded-full" />
                              )}

                              <div className={`p-2 rounded-xl shadow-sm flex-shrink-0 ${
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

                              <div className="flex-1 min-w-0 pr-6">
                                <p className="text-sm font-black text-gray-900 mb-0.5">{notification.title}</p>
                                <p className="text-xs font-semibold text-gray-600 line-clamp-2">{notification.message}</p>
                                <p className="text-xs text-gray-400 font-semibold mt-1">{notification.time}</p>
                              </div>
                            </div>

                            {/* Action buttons - show on hover */}
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center gap-1">
                              {!notification.is_read && (
                                <button
                                  onClick={(e) => handleMarkRead(e, notification.id)}
                                  title="Mark as read"
                                  className="p-1.5 bg-white rounded-lg shadow border border-gray-200 hover:bg-green-50 hover:border-green-300 transition-colors"
                                >
                                  <Check className="w-3.5 h-3.5 text-green-600" />
                                </button>
                              )}
                              <button
                                onClick={(e) => handleDeleteNotif(e, notification.id)}
                                title="Delete"
                                className="p-1.5 bg-white rounded-lg shadow border border-gray-200 hover:bg-red-50 hover:border-red-300 transition-colors"
                              >
                                <X className="w-3.5 h-3.5 text-red-500" />
                              </button>
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

          {/* User Profile with Dropdown */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowNotifications(false)}
              className="flex items-center gap-3 p-2 pr-4 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {user?.picture ? (
                <img 
                  src={user.picture} 
                  alt={user.name} 
                  className="w-9 h-9 rounded-full ring-2 ring-gold/30 shadow-md"
                />
              ) : (
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gold to-gold-light flex items-center justify-center ring-2 ring-gold/30 shadow-md">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
              <div className="hidden lg:block text-left">
                <p className="text-gray-900 font-black text-sm">{user?.name || 'User'}</p>
                <p className="text-gray-600 text-xs font-bold">{user?.email || ''}</p>
              </div>
            </motion.button>
          </div>

          {/* Logout Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onLogout}
            className="flex items-center gap-2 p-2.5 px-4 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors border-2 border-red-200"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
            <span className="hidden lg:inline font-bold text-sm">Logout</span>
          </motion.button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
