export interface PaymentMethod {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  currency: string;
}

export interface MpesaPaymentRequest {
  phone_number: string;
  order_id: number;
}

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';

export interface Transaction {
  id: number;
  order_id: number;
  amount: number;
  payment_method: string;
  status: PaymentStatus;
  created_at: string;
  checkout_request_id?: string;
  payment_details?: Record<string, unknown>;
}

export interface PaymentVerification {
  transaction_id: string;
  order_id: number;
}

export interface PaymentResponse {
  message: string;
  transaction_id: string;
  checkout_request_id?: string;
  status: PaymentStatus;
  redirect_url?: string;
}

export interface RefundRequest {
  amount?: number;
  reason: string;
}

export interface PaymentReceipt {
  transaction_id: string;
  order_id: number;
  amount: number;
  payment_method: string;
  status: PaymentStatus;
  date: string;
  customer: {
    name: string;
    email: string;
    phone?: string;
  };
}

// Cache types
export interface StatusCacheEntry {
  status: PaymentStatus;
  timestamp: number;
}
