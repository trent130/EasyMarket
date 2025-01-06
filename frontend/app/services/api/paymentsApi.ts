import { fetchWrapper } from '../../utils/fetchWrapper';

interface Payment {
    id: number;
    orderId: number;
    amount: number;
    currency: string;
    status: 'pending' | 'completed' | 'failed' | 'refunded';
    paymentMethod: string;
    createdAt: string;
    updatedAt: string;
}

interface PaymentIntent {
    clientSecret: string;
    paymentIntentId: string;
}

interface PaymentQueryParams {
    page?: number;
    pageSize?: number;
    status?: Payment['status'];
    startDate?: string;
    endDate?: string;
    orderId?: number;
}

export const paymentsApi = {
    getPayments: (params?: Record<string, string | number>) =>
        fetchWrapper<Payment[]>('/api/payments', { params }),
    
    getPaymentDetails: (id: number) =>
        fetchWrapper<Payment>(`/api/payments/${id}`),
    createPaymentIntent: (orderId: number, amount: number, currency: string) =>
        fetchWrapper<PaymentIntent>('/api/payments/create-intent', {
            method: 'POST',
            body: JSON.stringify({ orderId, amount, currency })
        }),
    
    processRefund: (paymentId: number, amount?: number) =>
        fetchWrapper(`/api/payments/${paymentId}/refund`, {
            method: 'POST',
            body: JSON.stringify({ amount })
        })
};

export type PaymentsApi = typeof paymentsApi;
// backend and frontend sync needed
