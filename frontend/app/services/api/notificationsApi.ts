import { fetchWrapper } from '../../utils/fetchWrapper';

interface Notification {
    id: number;
    userId: number;
    type: 'order' | 'payment' | 'system' | 'message';
    title: string;
    message: string;
    read: boolean;
    createdAt: string;
}

interface NotificationQueryParams {
    page?: number;
    pageSize?: number;
    type?: Notification['type'];
    read?: boolean;
}

export const notificationsApi = {
    getNotifications: (params?: Record<string, string | number>) =>
        fetchWrapper<Notification[]>('/api/notifications', { params }),
    
    markAsRead: (id: number) =>
        fetchWrapper<Notification>(`/api/notifications/${id}/read`, {
            method: 'PUT'
        }),
    
    markAllAsRead: () =>
        fetchWrapper<void>('/api/notifications/mark-all-read', {
            method: 'PUT'
        }),
    
    deleteNotification: (id: number) =>
        fetchWrapper(`/api/notifications/${id}`, {
            method: 'DELETE'
        })
};

export type NotificationsApi = typeof notificationsApi; 