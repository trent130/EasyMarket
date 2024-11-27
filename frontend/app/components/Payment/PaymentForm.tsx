'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { paymentService } from '../../services/payment';
import { MpesaPaymentRequest } from '../../types/payment';
import { Loader2 } from 'lucide-react';

interface PaymentFormProps {
  orderId: number;
  amount: number;
  onSuccess: (transactionId: string) => void;
  onError: (error: string) => void;
}

export function PaymentForm({ orderId, amount, onSuccess, onError }: PaymentFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<MpesaPaymentRequest>();

  const onSubmit = async (data: MpesaPaymentRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // Initiate payment
      const response = await paymentService.initiateMpesaPayment({
        ...data,
        order_id: orderId,
      });

      setIsProcessing(true);

      // Start polling for payment status
      const pollInterval = setInterval(async () => {
        try {
          const status = await paymentService.pollPaymentStatus(
            response.transaction_id,
            orderId
          );

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            onSuccess(response.transaction_id);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            setError('Payment failed. Please try again.');
          }
        } catch (error) {
          clearInterval(pollInterval);
          setIsProcessing(false);
          setError('Failed to verify payment status');
        }
      }, 5000); // Poll every 5 seconds

      // Stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isProcessing) {
          setIsProcessing(false);
          setError('Payment verification timeout. Please check your M-Pesa for the status.');
        }
      }, 120000);

    } catch (error: any) {
      setError(error.message || 'Payment initiation failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">M-Pesa Payment</h2>
        <p className="text-gray-600">Amount: KES {amount.toFixed(2)}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
          <p>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700">
            Phone Number
          </label>
          <input
            id="phone_number"
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="254XXXXXXXXX"
            {...register('phone_number', {
              required: 'Phone number is required',
              pattern: {
                value: /^254[17][0-9]{8}$/,
                message: 'Enter a valid Safaricom/Airtel number (254XXXXXXXXX)',
              },
            })}
          />
          {errors.phone_number && (
            <p className="text-sm text-red-500">{errors.phone_number.message}</p>
          )}
        </div>

        <button
          type="submit"
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            isLoading || isProcessing
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={isLoading || isProcessing}
        >
          {isLoading || isProcessing ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {isProcessing ? 'Processing Payment...' : 'Initiating Payment...'}
            </div>
          ) : (
            'Pay with M-Pesa'
          )}
        </button>
      </form>

      {isProcessing && (
        <div className="text-center text-sm text-gray-600">
          <p>Please check your phone for the M-Pesa prompt</p>
          <p>Enter your PIN to complete the payment</p>
        </div>
      )}
    </div>
  );
}
