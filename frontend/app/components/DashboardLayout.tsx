"use client";

import React from "react";
import { Sidebar } from "./app-sidebar";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

  return (
    <div className="relative flex h-screen">
      {/* Sidebar */}
      <aside
        className={`transition-all duration-300 bg-gray-100 ${
          isSidebarOpen ? "w-64" : "w-16"
        }`}
      >
        <Sidebar isSidebarOpen={isSidebarOpen} onToggleSidebar={setIsSidebarOpen} />
      </aside>

      {/* Main Content */}
      <main
        className={`flex-1 bg-white min-h-screen transition-all duration-300 ${
          isSidebarOpen ? "ml-64" : "ml-16"
        }`}
      >
        <div className="p-4 pt-16">{children}</div>
      </main>
    </div>
  );
};

export default DashboardLayout;
