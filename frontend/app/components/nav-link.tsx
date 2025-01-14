import { cn } from "@/lib/útils";
import { Button } from "@/components/ui/button";
import { ReactNode } from "react";

interface NavLinkProps {
  href: string;
  children: ReactNode;
  icon?: ReactNode;
  className?: string;
}

export function NavLink({ href, children, icon, className }: NavLinkProps) {
  const isActive = window.location.pathname === href;

  return (
    <Button
      variant={isActive ? "secondary" : "ghost"}
      className={cn(
        "w-full justify-start",
        isActive ? "bg-muted": "",
        className=""
      )}
      asChild
    >
      <a href={href}>
        {icon}
        {children}
      </a>
    </Button>
  );
}