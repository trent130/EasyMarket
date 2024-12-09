import apiClient from '../api-client';
import { Student } from './students';
import Product from './products';
import { Order } from './orders';

export interface AdminStats {
  total_users: number;
  total_products: number;
  total_orders: number;
  total_revenue: number;
  active_users: number;
  pending_verifications: number;
  recent_transactions: number;
  system_health: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    response_time: number;
  };
}

export interface UserManagementFilters {
  role?: 'student' | 'admin' | 'moderator';
  status?: 'active' | 'suspended' | 'pending';
  verified?: boolean;
  search?: string;
  page?: number;
}

export const adminApi = {
  // Dashboard Statistics
  getDashboardStats: async () => {
    const response = await apiClient.get<AdminStats>('/admin/dashboard/stats/');
    return response.data;
  },

  // User Management
  getUsers: async (filters?: UserManagementFilters) => {
    const response = await apiClient.get<{
      results: Student[];
      total: number;
      page: number;
      total_pages: number;
    }>('/admin/users/', { params: filters });
    return response.data;
  },

  // User Actions
  suspendUser: async (userId: number, reason: string) => {
    const response = await apiClient.post(`/admin/users/${userId}/suspend/`, { reason });
    return response.data;
  },

  activateUser: async (userId: number) => {
    const response = await apiClient.post(`/admin/users/${userId}/activate/`);
    return response.data;
  },

  // Product Management
  getProducts: async (params?: {
    status?: 'active' | 'reported' | 'suspended';
    category?: string;
    search?: string;
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Product[];
      total: number;
      page: number;
    }>('/admin/products/', { params });
    return response.data;
  },

  removeProduct: async (productId: number, reason: string) => {
    await apiClient.post(`/admin/products/${productId}/remove/`, { reason });
  },

  // Order Management
  getOrders: async (params?: {
    status?: Order['status'];
    payment_status?: 'pending' | 'completed' | 'failed';
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Order[];
      total: number;
      page: number;
    }>('/admin/orders/', { params });
    return response.data;
  },

  // Verification Requests
  getVerificationRequests: async (params?: {
    status?: 'pending' | 'approved' | 'rejected';
    page?: number;
  }) => {
    const response = await apiClient.get('/admin/verifications/', { params });
    return response.data;
  },

  handleVerificationRequest: async (requestId: number, action: 'approve' | 'reject', reason?: string) => {
    const response = await apiClient.post(`/admin/verifications/${requestId}/${action}/`, { reason });
    return response.data;
  },

  // Reports Management
  getReports: async (params?: {
    type?: 'user' | 'product' | 'review';
    status?: 'pending' | 'resolved';
    page?: number;
  }) => {
    const response = await apiClient.get('/admin/reports/', { params });
    return response.data;
  },

  handleReport: async (reportId: number, action: 'resolve' | 'dismiss', notes?: string) => {
    const response = await apiClient.post(`/admin/reports/${reportId}/${action}/`, { notes });
    return response.data;
  },

  // System Settings
  getSystemSettings: async () => {
    const response = await apiClient.get('/admin/settings/');
    return response.data;
  },

  updateSystemSettings: async (settings: {
    maintenance_mode?: boolean;
    registration_enabled?: boolean;
    max_file_size?: number;
    allowed_file_types?: string[];
    notification_settings?: Record<string, boolean>;
  }) => {
    const response = await apiClient.put('/admin/settings/', settings);
    return response.data;
  },

  // Audit Logs
  getAuditLogs: async (params?: {
    user_id?: number;
    action?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get('/admin/audit-logs/', { params });
    return response.data;
  },

  // Analytics
  getAnalytics: async (params: {
    metric: 'users' | 'orders' | 'revenue' | 'products';
    period: 'day' | 'week' | 'month' | 'year';
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await apiClient.get('/admin/analytics/', { params });
    return response.data;
  },

  // System Health
  getSystemHealth: async () => {
    const response = await apiClient.get('/admin/system/health/');
    return response.data;
  },

  // Backup Management
  createBackup: async () => {
    const response = await apiClient.post('/admin/system/backup/');
    return response.data;
  },

  restoreBackup: async (backupId: string) => {
    const response = await apiClient.post(`/admin/system/restore/${backupId}/`);
    return response.data;
  }
};
