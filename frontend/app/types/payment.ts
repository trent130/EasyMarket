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

export interface Transaction {
  id: number;
  order_id: number;
  amount: number;
  payment_method: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  created_at: string;
  checkout_request_id?: string;
  payment_details?: any;
}

export interface PaymentVerification {
  transaction_id: string;
  order_id: number;
}

export interface PaymentResponse {
  message: string;
  transaction_id: string;
  checkout_request_id?: string;
  status?: string;
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
  status: string;
  date: string;
  customer: {
    name: string;
    email: string;
    phone?: string;
  };
}
