import { useState } from 'react';
import { 
  LayoutDashboard, Server, BarChart3, 
  Settings, FileDown, FileText, Zap
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { ToastProvider, useToast } from './components/Toast';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Page Components
import DashboardPage from './pages/Dashboard';
import CampaignBuilderPage from './pages/CampaignBuilder';
import SMTPSettingsPage from './pages/SMTPSettings';
import AnalyticsPage from './pages/Analytics';
import ExportReportsPage from './pages/ExportReports';
import TemplatesPage from './pages/Templates';
import SettingsPage from './pages/Settings';

function MainApp() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activePage, setActivePage] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const { addToast } = useToast();

  // Sample notifications
  const notifications = [
    {
      id: 1,
      type: 'success',
      title: 'Campaign Completed',
      message: 'Summer Sale campaign sent to 1,234 recipients',
      time: '5 minutes ago'
    },
    {
      id: 2,
      type: 'info',
      title: 'New Template Available',
      message: 'Check out the new promotional email template',
      time: '1 hour ago'
    },
    {
      id: 3,
      type: 'warning',
      title: 'SMTP Connection Issue',
      message: 'Your primary SMTP server is experiencing delays',
      time: '2 hours ago'
    }
  ];

  // Searchable items database
  const searchableItems = [
    // Pages
    { type: 'page', id: 'dashboard', name: 'Dashboard', description: 'View campaign overview and statistics', keywords: ['home', 'overview', 'stats', 'analytics'] },
    { type: 'page', id: 'campaign-builder', name: 'Campaign Builder', description: 'Create and launch email campaigns', keywords: ['create', 'send', 'email', 'campaign', 'new'] },
    { type: 'page', id: 'smtp-settings', name: 'SMTP Settings', description: 'Configure email sending servers', keywords: ['email', 'server', 'configuration', 'smtp'] },
    { type: 'page', id: 'analytics', name: 'Email Analytics', description: 'Track email performance metrics', keywords: ['stats', 'reports', 'metrics', 'tracking'] },
    { type: 'page', id: 'export-reports', name: 'Export Reports', description: 'Download campaign data', keywords: ['download', 'export', 'csv', 'excel', 'data'] },
    { type: 'page', id: 'templates', name: 'Templates', description: 'Manage email templates', keywords: ['email', 'design', 'template', 'content'] },
    { type: 'page', id: 'settings', name: 'Settings', description: 'Account and preferences', keywords: ['profile', 'account', 'preferences', 'config'] },
    
    // Features
    { type: 'feature', id: 'create-campaign', name: 'Create Campaign', description: 'Start a new email campaign', page: 'campaign-builder', keywords: ['new', 'create', 'start'] },
    { type: 'feature', id: 'upload-csv', name: 'Upload Recipients', description: 'Import contacts from CSV', page: 'campaign-builder', keywords: ['import', 'csv', 'contacts', 'recipients'] },
    { type: 'feature', id: 'add-smtp', name: 'Add SMTP Profile', description: 'Configure new email server', page: 'smtp-settings', keywords: ['add', 'new', 'server', 'smtp'] },
    { type: 'feature', id: 'create-template', name: 'Create Template', description: 'Design new email template', page: 'templates', keywords: ['new', 'design', 'template'] },
    { type: 'feature', id: 'export-data', name: 'Export Data', description: 'Download reports', page: 'export-reports', keywords: ['download', 'export', 'report'] },
    { type: 'feature', id: 'view-analytics', name: 'View Analytics', description: 'See email statistics', page: 'analytics', keywords: ['stats', 'metrics', 'performance'] },
  ];

  const handleSearch = (query) => {
    setSearchQuery(query);
    
    if (query.trim().length > 0) {
      // Search through all items
      const results = searchableItems.filter(item => {
        const searchLower = query.toLowerCase();
        return (
          item.name.toLowerCase().includes(searchLower) ||
          item.description.toLowerCase().includes(searchLower) ||
          item.keywords.some(keyword => keyword.includes(searchLower))
        );
      });
      
      setSearchResults(results);
      setShowSearchResults(true);
    } else {
      setSearchResults([]);
      setShowSearchResults(false);
    }
  };

  const handleSearchResultClick = (result) => {
    if (result.type === 'page') {
      setActivePage(result.id);
      setTimeout(() => {
        addToast(`Navigated to ${result.name}`, 'success');
      }, 0);
    } else if (result.type === 'feature' && result.page) {
      setActivePage(result.page);
      setTimeout(() => {
        addToast(`Opening ${result.name}`, 'info');
      }, 0);
    }
    setSearchQuery('');
    setShowSearchResults(false);
  };

  const handleNotificationClick = (notification) => {
    setTimeout(() => {
      addToast(`Opened: ${notification.title}`, 'info');
    }, 0);
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'campaign-builder', label: 'Campaign Builder', icon: Zap },
    { id: 'smtp-settings', label: 'SMTP Settings', icon: Server },
    { id: 'analytics', label: 'Email Analytics', icon: BarChart3 },
    { id: 'export-reports', label: 'Export Reports', icon: FileDown },
    { id: 'templates', label: 'Templates', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const user = {
    name: 'Admin User',
    email: 'admin@carlyshayn.com'
  };

  const pageConfig = {
    'dashboard': {
      title: 'Dashboard',
      subtitle: 'Welcome back! Here\'s an overview of your email campaigns'
    },
    'campaign-builder': {
      title: 'Campaign Builder',
      subtitle: 'Create and manage your email marketing campaigns'
    },
    'smtp-settings': {
      title: 'SMTP Settings',
      subtitle: 'Configure your email sending servers'
    },
    'analytics': {
      title: 'Email Analytics',
      subtitle: 'Track performance and engagement metrics'
    },
    'export-reports': {
      title: 'Export Reports',
      subtitle: 'Download and analyze your campaign data'
    },
    'templates': {
      title: 'Templates',
      subtitle: 'Manage your email templates and designs'
    },
    'settings': {
      title: 'Settings',
      subtitle: 'Configure your account and preferences'
    }
  };

  const handlePageChange = (pageId) => {
    setActivePage(pageId);
    addToast(`Navigating to ${pageConfig[pageId].title}`, 'success');
  };

  const renderPage = () => {
    const pageVariants = {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 }
    };

    const pages = {
      'dashboard': <DashboardPage />,
      'campaign-builder': <CampaignBuilderPage />,
      'smtp-settings': <SMTPSettingsPage />,
      'analytics': <AnalyticsPage />,
      'export-reports': <ExportReportsPage />,
      'templates': <TemplatesPage />,
      'settings': <SettingsPage />
    };

    return (
      <AnimatePresence mode="wait">
        <motion.div
          key={activePage}
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{ duration: 0.3 }}
        >
          {pages[activePage]}
        </motion.div>
      </AnimatePresence>
    );
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        items={sidebarItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        activeItem={activePage}
        onItemClick={handlePageChange}
        user={user}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Sticky Navbar */}
        <Navbar 
          title={pageConfig[activePage].title}
          subtitle={pageConfig[activePage].subtitle}
          notifications={notifications}
          onSearch={handleSearch}
          onNotificationClick={handleNotificationClick}
          searchQuery={searchQuery}
          searchResults={searchResults}
          showSearchResults={showSearchResults}
          onSearchResultClick={handleSearchResultClick}
          onCloseSearch={() => setShowSearchResults(false)}
        />

        {/* Page Content with Smooth Transitions */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-br from-gray-50 via-white to-gray-100 scrollbar-thin">
          <div className="p-8">
            <div className="max-w-7xl mx-auto">
              {renderPage()}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <MainApp />
    </ToastProvider>
  );
}
