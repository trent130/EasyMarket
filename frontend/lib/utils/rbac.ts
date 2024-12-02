import { UserRole } from '@/lib/models/user';

const roleHierarchy: Record<UserRole, number> = {
  'user': 1,
  'moderator': 2,
  'admin': 3
};

export function hasPermission(userRole: UserRole, requiredRole: UserRole): boolean {
  return roleHierarchy[userRole] >= roleHierarchy[requiredRole];
}

export function requireRole(requiredRole: UserRole) {
  return (req: any, res: any, next: () => void) => {
    const userRole = req.user?.role;
    if (!userRole || !hasPermission(userRole, requiredRole)) {
      return res.status(403).json({ error: 'Forbidden: Insufficient permissions' });
    }
    next();
  };
}
