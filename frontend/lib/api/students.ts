import { apiClient } from '../api-client';

export interface Student {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  };
  first_name: string;
  last_name: string;
  email: string;
  bio: string;
  avatar?: string;
  two_factor_enabled: boolean;
  two_factor_verified: boolean;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  avatar: string;
  products_count: number;
  orders_count: number;
  rating_average: number;
  joined_date: string;
  total_sales: number;
}

export interface UpdateProfileInput {
  first_name?: string;
  last_name?: string;
  bio?: string;
  avatar?: File;
}

export const studentApi = {
  // Get current student profile
  getCurrentProfile: async () => {
    const response = await apiClient.get<Student>('/students/profile/');
    return response.data;
  },

  // Get student by ID
  getById: async (id: number) => {
    const response = await apiClient.get<Student>(`/students/${id}/`);
    return response.data;
  },

  // Update profile
  updateProfile: async (data: UpdateProfileInput) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (value instanceof File) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      }
    });

    const response = await apiClient.patch<Student>('/students/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get student statistics
  getStats: async () => {
    const response = await apiClient.get<{
      total_products: number;
      total_sales: number;
      total_revenue: number;
      average_rating: number;
      products_by_category: Record<string, number>;
      sales_history: {
        date: string;
        sales: number;
        revenue: number;
      }[];
    }>('/students/stats/');
    return response.data;
  },

  // Get student's products
  getProducts: async (params?: {
    status?: 'active' | 'inactive' | 'sold';
    category?: string;
    page?: number;
  }) => {
    const response = await apiClient.get('/students/products/', { params });
    return response.data;
  },

  // Get student's reviews
  getReviews: async (params?: {
    rating?: number;
    page?: number;
  }) => {
    const response = await apiClient.get('/students/reviews/', { params });
    return response.data;
  },

  // Update notification preferences
  updateNotificationPreferences: async (preferences: {
    email_notifications: boolean;
    push_notifications: boolean;
    order_updates: boolean;
    marketing_emails: boolean;
  }) => {
    const response = await apiClient.put('/students/notifications/', preferences);
    return response.data;
  },

  // Get notification settings
  getNotificationPreferences: async () => {
    const response = await apiClient.get('/students/notifications/');
    return response.data;
  },

  // Delete account
  deleteAccount: async (password: string) => {
    await apiClient.post('/students/delete-account/', { password });
  },

  // Export student data
  exportData: async () => {
    const response = await apiClient.get('/students/export-data/', {
      responseType: 'blob'
    });
    return response.data;
  },

  // Get student's activity log
  getActivityLog: async (params?: {
    type?: 'product' | 'order' | 'review' | 'auth';
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get('/students/activity-log/', { params });
    return response.data;
  },

  // Update password
  updatePassword: async (data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    await apiClient.post('/students/update-password/', data);
  },

  // Request verification
  requestVerification: async (data: {
    document_type: 'student_id' | 'national_id';
    document_file: File;
  }) => {
    const formData = new FormData();
    formData.append('document_type', data.document_type);
    formData.append('document_file', data.document_file);

    const response = await apiClient.post('/students/request-verification/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};
