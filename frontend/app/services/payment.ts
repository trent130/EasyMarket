import apiClient from '../../lib/api-client';
import type { 
  MpesaPaymentRequest, 
  PaymentVerification, 
  Transaction, 
  PaymentResponse,
  RefundRequest,
  PaymentReceipt,
  PaymentStatus,
  StatusCacheEntry
} from '../types/payment';

// Constants for configuration
const POLL_MAX_ATTEMPTS = 24; // 2 minutes total with exponential backoff
const POLL_MAX_DELAY = 10000; // 10 seconds
const POLL_BASE_DELAY = 1000; // 1 second
const CACHE_TTL = 5000; // Cache valid for 5 seconds

// Error messages
const ERROR_MESSAGES = {
  PAYMENT_TIMEOUT: 'Payment timeout. Please try again.',
  PAYMENT_FAILED: 'Payment failed. Please try again.',
  VERIFICATION_FAILED: 'Failed to verify payment status',
  RECEIPT_FAILED: 'Failed to fetch receipt',
  REFUND_FAILED: 'Refund request failed',
  HISTORY_FAILED: 'Failed to fetch payment history',
} as const;

// Create a singleton cache instance
const statusCache = new Map<string, StatusCacheEntry>();

// Helper function to check if status is final
const isFinalStatus = (status: PaymentStatus): boolean => 
  status === 'completed' || status === 'failed';

export const paymentService = {
  // Initiate M-Pesa payment
  initiateMpesaPayment: async (data: MpesaPaymentRequest): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>('payment/api/payment/mpesa/', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || ERROR_MESSAGES.PAYMENT_FAILED);
    }
  },

  // Verify payment status
  verifyPayment: async (data: PaymentVerification): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>('/payment/api/payment/verify/', data);
      return response.data;
    } catch (error: any) {
i      throw new Error(error.response?.data?.error || ERROR_MESSAGES.VERIFICATION_FAILED);
    }
  },

  // Get payment history
  getPaymentHistory: async (): Promise<Transaction[]> => {
    try {
      const response = await apiClient.get<Transaction[]>('payment/api/payment/history/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || ERROR_MESSAGES.HISTORY_FAILED);
    }
  },

  // Get payment receipt
  getPaymentReceipt: async (transactionId: string): Promise<PaymentReceipt> => {
    try {
      const response = await apiClient.get<PaymentReceipt>(`/payment/api/payment/transactions/${transactionId}/receipt/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || ERROR_MESSAGES.RECEIPT_FAILED);
    }
  },

  // Request refund
  requestRefund: async (transactionId: string, data: RefundRequest): Promise<PaymentResponse> => {
    try {
      const response = await apiClient.post<PaymentResponse>(`payment/api/payment/${transactionId}/refund/`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || ERROR_MESSAGES.REFUND_FAILED);
    }
  },

  // Optimized payment status polling with caching and exponential backoff
  pollPaymentStatus: async (transactionId: string, orderId: number): Promise<PaymentResponse> => {
    let attempts = 0;

    const poll = async (): Promise<PaymentResponse> => {
      try {
        // Check cache first
        const cached = statusCache.get(transactionId);
        const now = Date.now();
        
        if (cached && (now - cached.timestamp) < CACHE_TTL) {
          if (isFinalStatus(cached.status)) {
            return {
              message: `Payment ${cached.status}`,
              transaction_id: transactionId,
              status: cached.status
            };
          }
        }

        const response = await apiClient.get<PaymentResponse>(`/payment/check_payment_status/${transactionId}/`);
        
        // Update cache if status is present
        if (response.data.status) {
          statusCache.set(transactionId, {
            status: response.data.status,
            timestamp: now
          });
        }

        if (response.data.status && isFinalStatus(response.data.status)) {
          return response.data;
        }

        attempts++;
        if (attempts >= POLL_MAX_ATTEMPTS) {
          throw new Error(ERROR_MESSAGES.PAYMENT_TIMEOUT);
        }

        // Exponential backoff
        const delay = Math.min(POLL_BASE_DELAY * Math.pow(2, attempts), POLL_MAX_DELAY);
        await new Promise(resolve => setTimeout(resolve, delay));
        
        return poll();
      } catch (error: any) {
        if (error.response?.status === 408) {
          throw new Error(ERROR_MESSAGES.PAYMENT_TIMEOUT);
        }
        throw new Error(error.response?.data?.error || ERROR_MESSAGES.VERIFICATION_FAILED);
      }
    };

    return poll();
  },

  // Clear cache when no longer needed
  clearStatusCache: (transactionId: string) => {
    statusCache.delete(transactionId);
  },

  // Clear expired cache entries (can be called periodically)
  clearExpiredCache: () => {
    const now = Date.now();
    // Convert Map entries to array to avoid iterator issues
    Array.from(statusCache.entries()).forEach(([key, value]) => {
      if (now - value.timestamp > CACHE_TTL) {
        statusCache.delete(key);
      }
    });
  }
};
