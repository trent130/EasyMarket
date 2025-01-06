import React from "react";
import { AppSidebar } from "./app-sidebar";

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
          isSidebarOpen ? "w-64" : "w-16"
        } bg-gray-100`}
      >
        <AppSidebar />
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 bg-white min-h-screen">{children}</main>
    </div>
  );
};

export default DashboardLayout;
