"use client";

import React from "react";
import { Sidebar } from "./app-sidebar";

// Props type for layout
interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
  return (
    <div className="flex">
      {/* Sidebar */}
      <aside
        className={`transition-all ${
          isSidebarOpen ? "" : "w-16"
        } bg-gray-100`}
      >
        <Sidebar />
      </aside>

      {/* Main Content */}
      <main className={`flex-1 p-4 bg-white min-h-screen ${isSidebarOpen ? 'ml-64' : 'ml-16'} pt-16`}>{children}</main>
    </div>
  );
};

export default DashboardLayout;
