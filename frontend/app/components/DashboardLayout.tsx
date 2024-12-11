
import React from 'react';
import { Sidebar, SidebarProvider } from './ui/sidebar';

// Props type for layout
interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen">
      <SidebarProvider>
      
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 p-4">
            {children}
        </main>
      </SidebarProvider>
    </div>
  );
};

export default DashboardLayout;