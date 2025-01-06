import { fetchWrapper } from '../../utils/fetchWrapper';
import { Order, OrderStatus } from '../../types/orders';

interface OrderQueryParams {
    page?: number;
    pageSize?: number;
    status?: Order['status'];
}

export const ordersApi = {
    getOrders: (params?: Record<string, string | number>) =>
        fetchWrapper<Order[]>('/api/orders', { params }),
    
    getOrderDetails: (orderId: number) =>
        fetchWrapper<Order>(`/api/orders/${orderId}`),
    updateOrderStatus: (orderId: number, status: OrderStatus) =>
        fetchWrapper(`/api/orders/${orderId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        }),
}; 

// backend and frontend sync of api urls needed for this
