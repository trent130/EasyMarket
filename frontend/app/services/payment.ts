import apiClient from '../../lib/api-client';
import { 
  MpesaPaymentRequest, 
  PaymentVerification, 
  Transaction, 
  PaymentResponse,
  RefundRequest,
  PaymentReceipt
} from '../types/payment';

export const paymentService = {
  // Initiate M-Pesa payment
  initiateMpesaPayment: async (data: MpesaPaymentRequest): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>('/payment/mpesa/', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Payment initiation failed');
    }
  },

  // Verify payment status
  verifyPayment: async (data: PaymentVerification): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>('/payment/verify_payment/', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Payment verification failed');
    }
  },

  // Get payment history
  getPaymentHistory: async (): Promise<Transaction[]> => {
    try {
      const response = await apiClient.get<Transaction[]>('/payment/history/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch payment history');
    }
  },

  // Get payment receipt
  getPaymentReceipt: async (transactionId: string): Promise<PaymentReceipt> => {
    try {
      const response = await apiClient.get<PaymentReceipt>(`/payment/${transactionId}/receipt/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch receipt');
    }
  },

  // Request refund
  requestRefund: async (transactionId: string, data: RefundRequest): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>(`/payment/${transactionId}/refund/`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Refund request failed');
    }
  },

  // Poll payment status
  pollPaymentStatus: async (transactionId: string, orderId: number): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.get<PaymentResponse>(`/payment/check_payment_status/${transactionId}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to check payment status');
    }
  }
};
