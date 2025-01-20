"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/útils";
import { Button } from "@/components/ui/button";
import {
  Home,
  Settings,
  Users,
  BarChart3,
  Files,
  Calendar,
  MessagesSquare,
  LogOut,
  Menu,
} from "lucide-react";
import { NavLink } from "./nav-link";

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  isSidebarOpen: boolean;
  onToggleSidebar: (isOpen: boolean) => void;
}

const navigationLinks = [
  { href: "/", icon: <Home className="mr-2 h-5 w-5" />, label: "Home" },
  { href: "/analytics", icon: <BarChart3 className="mr-2 h-5 w-5" />, label: "Analytics" },
  { href: "/customers", icon: <Users className="mr-2 h-5 w-5" />, label: "Customers" },
  { href: "/addProduct", icon: <Users className="mr-2 h-5 w-5" />, label: "Product add" },
  { href: "/my-product", icon: <Files className="mr-2 h-5 w-5" />, label: "My Products" },
  { href: "/messages", icon: <MessagesSquare className="mr-2 h-5 w-5" />, label: "Messages" },
  { href: "/calendar", icon: <Calendar className="mr-2 h-5 w-5" />, label: "Calendar" },
];

const settingsLinks = [
  { href: "/settings", icon: <Settings className="mr-2 h-5 w-5 " />, label: "Settings" },
];

const SidebarHeader = () => (
  <div className="flex items-center px-4 py-6">
    <BarChart3 className="h-6 w-6 text-primary" />
    <h2 className="ml-3 text-xl font-semibold tracking-tight">Dashboard</h2>
  </div>
);

const NavigationLinks = ({ links }: { links: typeof navigationLinks }) => (
  <nav className="mt-4 space-y-1 ml-0">
    {links.map((link) => (
      <NavLink key={link.href} href={link.href} icon={link.icon}>
        <div className="flex items-center">{link.label}</div>
      </NavLink>
    ))}
  </nav>
);

// Custom hook to detect media query
function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);
    const listener = () => setMatches(media.matches);
    media.addEventListener("change", listener);

    return () => media.removeEventListener("change", listener);
  }, [query]);

  return matches;
}

export function Sidebar({ className, isSidebarOpen, onToggleSidebar }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const isMediumScreen = useMediaQuery("(min-width: 768px) and (max-width: 1024px)");

  useEffect(() => {
    // Automatically collapse the sidebar for medium screens
    if (isMediumScreen) {
      setIsOpen(false);
    }
  }, [isMediumScreen]);

  return (
    <div className="relative h-screen bg-slate-600 sm:flex sm:flex-col sm:w-0 mt-6 sm:z-auto">
      <>
        {/* Hamburger Menu for Mobile and Medium Screens */}
        <div className="relative top-4 left-4 z-10 sm:static">
          <Button
            variant="ghost"
            onClick={() => setIsOpen(!isOpen)}
            className="p-2"
          >
            <Menu className="h-6 w-6 text-primary" />
          </Button>
        </div>

        {/* Sidebar */}
        <div
          className={cn(
            "absolute top-0 left-0 z-40 h-screen w-64 bg-white text-black transition-transform sm:translate-x-0",
            isOpen ? "translate-x-0" : "-translate-x-full",
            className
          )}
        >
          <div className="flex flex-col justify-between h-full">
            {/* Header */}
            <div className="px-4 py-6">
              <SidebarHeader />
              <NavigationLinks links={navigationLinks} />
            </div>

            {/* Footer */}
            <div className="border-t px-4 py-6 mb-24">
              <h2 className="mb-2 text-lg font-semibold tracking-tight">Settings</h2>
              <NavigationLinks links={settingsLinks} />
            </div>
          </div>
        </div>

        {/* Overlay for Mobile */}
        {isOpen && (
          <div
            className="fixed inset-0 z-30 bg-black bg-opacity-50 sm:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </>
    </div>
  );
}
