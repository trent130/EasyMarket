import { fetchWrapper } from '../../utils/fetchWrapper';

interface AnalyticsData {
    views: number;
    uniqueVisitors: number;
    averageTime: number;
    bounceRate: number;
    topProducts: Array<{
        productId: number;
        name: string;
        views: number;
        conversions: number;
    }>;
    salesTrends: Array<{
        date: string;
        revenue: number;
        orders: number;
    }>;
}

interface AnalyticsParams {
    startDate: string;
    endDate: string;
    granularity?: 'day' | 'week' | 'month';
}

export const analyticsApi = {
    getDashboardMetrics: (params: Record<string, string | number>) =>
        fetchWrapper<AnalyticsData>('/api/analytics/dashboard', { params }),
    
    getProductMetrics: (productId: number, params: Record<string, string | number>) =>
        fetchWrapper<AnalyticsData>(`/api/analytics/products/${productId}`, { params }),
    getUserBehavior: (params: Record<string, string | number>) =>
        fetchWrapper<AnalyticsData>('/api/analytics/user-behavior', { params }),
    
    exportReport: (params: Record<string, string | number>) =>
        fetchWrapper<Blob>('/api/analytics/export', { 
            params
        }),
};

export type AnalyticsApi = typeof analyticsApi;

// backend implimentations needed here 
