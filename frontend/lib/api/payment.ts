import { apiClient } from '../api-client';

export interface PaymentMethod {
  id: number;
  type: 'mpesa' | 'card' | 'bank';
  is_default: boolean;
  details: {
    last4?: string;
    brand?: string;
    phone_number?: string;
    bank_name?: string;
  };
}

export interface Transaction {
  id: number;
  order_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  payment_method: string;
  transaction_id: string;
  created_at: string;
}

export interface InitiatePaymentInput {
  order_id: number;
  payment_method: 'mpesa' | 'card' | 'bank';
  payment_details: {
    phone_number?: string;
    card_token?: string;
    bank_account?: string;
  };
}

export const paymentApi = {
  // Get saved payment methods
  getPaymentMethods: async () => {
    const response = await apiClient.get<PaymentMethod[]>('/payment/methods/');
    return response.data;
  },

  // Add new payment method
  addPaymentMethod: async (data: {
    type: PaymentMethod['type'];
    details: PaymentMethod['details'];
    is_default?: boolean;
  }) => {
    const response = await apiClient.post<PaymentMethod>('/payment/methods/', data);
    return response.data;
  },

  // Remove payment method
  removePaymentMethod: async (id: number) => {
    await apiClient.delete(`/payment/methods/${id}/`);
  },

  // Set default payment method
  setDefaultPaymentMethod: async (id: number) => {
    const response = await apiClient.post<PaymentMethod>(
      `/payment/methods/${id}/set-default/`
    );
    return response.data;
  },

  // Initiate payment
  initiatePayment: async (data: InitiatePaymentInput) => {
    const response = await apiClient.post<{
      transaction_id: string;
      checkout_url?: string;
      mpesa_prompt?: boolean;
    }>('/payment/initiate/', data);
    return response.data;
  },

  // Verify payment status
  verifyPayment: async (transactionId: string) => {
    const response = await apiClient.get<{
      status: Transaction['status'];
      message: string;
    }>(`/payment/verify/${transactionId}/`);
    return response.data;
  },

  // Get payment history
  getTransactionHistory: async (params?: {
    status?: Transaction['status'];
    start_date?: string;
    end_date?: string;
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Transaction[];
      total: number;
      page: number;
      total_pages: number;
    }>('/payment/transactions/', { params });
    return response.data;
  },

  // Get transaction details
  getTransactionDetails: async (id: string) => {
    const response = await apiClient.get<Transaction>(`/payment/transactions/${id}/`);
    return response.data;
  },

  // Request refund
  requestRefund: async (transactionId: string, data: {
    reason: string;
    amount?: number;
  }) => {
    const response = await apiClient.post<{
      refund_id: string;
      status: 'pending' | 'approved' | 'rejected';
      amount: number;
    }>(`/payment/transactions/${transactionId}/refund/`, data);
    return response.data;
  },

  // Get refund status
  getRefundStatus: async (refundId: string) => {
    const response = await apiClient.get<{
      status: 'pending' | 'approved' | 'rejected';
      amount: number;
      processed_at?: string;
      reason?: string;
    }>(`/payment/refunds/${refundId}/`);
    return response.data;
  },

  // Generate payment receipt
  generateReceipt: async (transactionId: string) => {
    const response = await apiClient.get(`/payment/transactions/${transactionId}/receipt/`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Validate M-Pesa number
  validateMpesaNumber: async (phoneNumber: string) => {
    const response = await apiClient.post<{
      valid: boolean;
      formatted_number?: string;
    }>('/payment/validate-mpesa/', { phone_number: phoneNumber });
    return response.data;
  }
};
