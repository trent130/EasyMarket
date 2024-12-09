import apiClient from '../api-client';
// import { fetchWrapper } from '../../utils/fetchWrapper';
// import { Orders  } from '../../types/orders'; //OrderStatus

export interface OrderItem {
  id: number;
  product: number;
  quantity: number;
  price: number;
  total: number;
}

export interface Order {
  id: number;
  user: number;
  items: OrderItem[];
  total_amount: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  payment_status: 'pending' | 'completed' | 'failed';
  shipping_address: string;
  tracking_number?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderInput {
  items: { product_id: number; quantity: number }[];
  shipping_address: string;
}

export const ordersApi = {
  // Get all orders for current user
  getAll: async () => {
    const response = await apiClient.get<Order[]>('/orders/orders/');
    return response.data;
  },

  // Get single order by ID
  getById: async (id: number) => {
    const response = await apiClient.get<Order>(`/orders/orders/${id}/`);
    return response.data;
  },

  // Create new order
  create: async (data: CreateOrderInput) => {
    const response = await apiClient.post<Order>('/orders/orders/', data);
    return response.data;
  },

  // Cancel order
  cancel: async (id: number) => {
    const response = await apiClient.post<Order>(`/orders/orders/${id}/cancel/`);
    return response.data;
  },

  // Update shipping address
  updateShippingAddress: async (id: number, address: string) => {
    const response = await apiClient.patch<Order>(`/orders/orders/${id}/`, {
      shipping_address: address
    });
    return response.data;
  },

  // Get order history with filters
  getHistory: async (params?: {
    status?: Order['status'];
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Order[];
      total: number;
      page: number;
      total_pages: number;
    }>('/orders/orders/history/', { params });
    return response.data;
  },

  // Track order
  trackOrder: async (id: number) => {
    const response = await apiClient.get<{
      status: Order['status'];
      tracking_number?: string;
      tracking_url?: string;
      estimated_delivery?: string;
      tracking_history: {
        status: string;
        location: string;
        timestamp: string;
      }[];
    }>(`/orders/orders/${id}/track/`);
    return response.data;
  },

  // Get order summary/statistics
  getStats: async (params?: {
    period: 'day' | 'week' | 'month' | 'year';
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await apiClient.get<{
      total_orders: number;
      total_amount: number;
      average_order_value: number;
      orders_by_status: Record<Order['status'], number>;
    }>('/orders/orders/stats/', { params });
    return response.data;
  },

  // Generate order invoice
  generateInvoice: async (id: number) => {
    const response = await apiClient.get(`/orders/orders/${id}/invoice/`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Verify order payment
  verifyPayment: async (id: number, paymentId: string) => {
    const response = await apiClient.post<{
      verified: boolean;
      order: Order;
    }>(`/orders/orders/${id}/verify-payment/`, {
      payment_id: paymentId
    });
    return response.data;
  }
};

// Add any additional functions or logic as needed
