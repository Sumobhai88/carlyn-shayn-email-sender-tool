import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

const MainLayout = ({ children, sidebarItems, activePage, onPageChange, pageConfig, user }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-dark overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        items={sidebarItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        activeItem={activePage}
        onItemClick={onPageChange}
        user={user}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Sticky Navbar */}
        <Navbar 
          title={pageConfig[activePage]?.title}
          subtitle={pageConfig[activePage]?.subtitle}
          notificationCount={3}
        />

        {/* Page Content with Smooth Transitions */}
        <main className="flex-1 overflow-y-auto bg-dark scrollbar-thin scrollbar-thumb-gold/20">
          <div className="p-8">
            <div className="max-w-7xl mx-auto">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activePage}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {children}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
