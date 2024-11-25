import { fetchWrapper } from '../../utils/fetchWrapper';
import { AdminDashboardData, UserManagementData, UserQueryParams } from '../../types/admin';

export const adminApi = {
    getDashboardData: () => 
        fetchWrapper<AdminDashboardData>('/api/admin/dashboard'),
    getUsers: (params: Record<string, string | number>) => 
        fetchWrapper<UserManagementData>('/api/admin/users', { params }),
    
    updateUserStatus: (userId: number, status: string) =>
        fetchWrapper(`/api/admin/users/${userId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        }),
}; 