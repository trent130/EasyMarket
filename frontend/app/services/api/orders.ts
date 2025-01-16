import { fetchWrapper } from "@/utils/fetchWrapper";
import apiClient from "../api-client";
import { OrderStatus } from "@/types/orders";
import { ApiError, Order } from "@/types/api";
// import { handleApiError } from "@/utils/errorHandling";
// import { handleApiError } from "@/utils/errorHandling";
// import { fetchWrapper } from '../../utils/fetchWrapper';
// import { Orders  } from '../../types/orders'; //OrderStatus

const handleApiError = (error: { response?: { data?: { message?: string }; status?: number } }): never => {
  const apiError: ApiError = {
    message: error.response?.data?.message || 'An error occurred',
    status: error.response?.status || 500
  };

  if(isApiError(error)) {
    apiError.message = error.response?.data?.message || 'An error occurred';
    apiError.status = error.response?.status || apiError.status;
  }
  throw apiError;
};

/**
 * Checks if an error is an ApiError.
 *
 * @param error - The error to check.
 * @returns True if the error is an ApiError, false otherwise.
 */
const isApiError = (error: unknown): error is { response?: { data?: { message?: string }; status?: number } } => {
  return typeof error === 'object' && error !== null && 'response' in error;
};

export interface CreateOrderInput {
  items: { product_id: number; quantity: number }[];
  shipping_address: string;
}

export const ordersApi = {
  // Get all orders for current user
  getAll: async () => {
    const response = await apiClient.get<Order[]>("/orders/orders/");
    return response.data;
  },
  getOrders: async (params?: Record<string, string | number>): Promise<Order[]> => {
    try {
      const response = await apiClient.get<Order[]>('/api/orders', { params });
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  create: async (data: CreateOrderInput): Promise<Order> => {
    try {
      const response = await apiClient.post<Order>('/orders/orders/', data);
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  // Get single order by ID
  getById: async (id: number) => {
    const response = await apiClient.get<Order>(`/orders/orders/${id}/`);
    return response.data;
  },

  // Cancel order
  cancel: async (id: number) => {
    const response = await apiClient.post<Order>(
      `/orders/orders/${id}/cancel/`
    );
    return response.data;
  },

  // Update shipping address
  updateShippingAddress: async (id: number, address: string) => {
    const response = await apiClient.patch<Order>(`/orders/orders/${id}/`, {
      shipping_address: address,
    });
    return response.data;
  },

  // Get order history with filters
  getHistory: async (params?: {
    status?: Order["status"];
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Order[];
      total: number;
      page: number;
      total_pages: number;
    }>("/orders/orders/history/", { params });
    return response.data;
  },

  // Track order
  trackOrder: async (id: number) => {
    const response = await apiClient.get<{
      status: Order["status"];
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
    period: "day" | "week" | "month" | "year";
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await apiClient.get<{
      total_orders: number;
      total_amount: number;
      average_order_value: number;
      orders_by_status: Record<Order["status"], number>;
    }>("/orders/orders/stats/", { params });
    return response.data;
  },

  // Generate order invoice
  generateInvoice: async (id: number) => {
    const response = await apiClient.get(`/orders/orders/${id}/invoice/`, {
      responseType: "blob",
    });
    return response.data;
  },

  // Verify order payment
  verifyPayment: async (id: number, paymentId: string) => {
    const response = await apiClient.post<{
      verified: boolean;
      order: Order;
    }>(`/orders/orders/${id}/verify-payment/`, {
      payment_id: paymentId,
    });
    return response.data;
  },

  updateOrderStatus: (id: number, status: OrderStatus) =>
    fetchWrapper(`/api/orders/${id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
};

// Add any additional functions or logic as needed
