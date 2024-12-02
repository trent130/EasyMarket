'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PaymentForm } from '../../components/Payment/PaymentForm';

interface Order {
  id: number;
  total_amount: number;
  status: string;
}

export default function PaymentPage({ params }: { params: { orderId: string } }) {
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch order details
    const fetchOrder = async () => {
      try {
        const response = await fetch(`/api/orders/${params.orderId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch order details');
        }
        const data = await response.json();
        setOrder(data);
      } catch (error) {
        setError('Failed to load order details');
      }
    };

    fetchOrder();
  }, [params.orderId]);

  const handlePaymentSuccess = (transactionId: string) => {
    // Redirect to success page
    router.push(`/payment/success?transactionId=${transactionId}&orderId=${params.orderId}`);
  };

  const handlePaymentError = (error: string) => {
    setError(error);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-md">
          <h1 className="text-red-600 text-xl font-semibold mb-4">Error</h1>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={() => router.back()}
            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900">Complete Your Payment</h1>
              <p className="text-gray-600">Order #{params.orderId}</p>
            </div>

            <div className="border-t border-gray-200 pt-8">
              <div className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Order Summary</h2>
                <div className="bg-gray-50 rounded-md p-4">
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-600">Order Total</span>
                    <span className="font-semibold">KES {order.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <PaymentForm
                orderId={order.id}
                amount={order.total_amount}
                onSuccess={handlePaymentSuccess}
                onError={handlePaymentError}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
