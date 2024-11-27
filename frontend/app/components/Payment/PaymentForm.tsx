'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { paymentService } from '../../services/payment';
import { MpesaPaymentRequest } from '../../types/payment';

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
  const [selectedMethod, setSelectedMethod] = useState('mpesa');

  const paymentMethods = [
    { id: 'mpesa', name: 'M-Pesa', description: 'Pay with M-Pesa mobile money' },
    { id: 'cash', name: 'Cash on Delivery', description: 'Pay when you receive your order' }
  ] as const;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<MpesaPaymentRequest>();

  const validatePhone = (phone: string) => {
    const phoneRegex = /^254[17][0-9]{8}$/;
    if (!phoneRegex.test(phone)) {
      return 'Please enter a valid Safaricom/Airtel number (254XXXXXXXXX)';
    }
    return true;
  };

  const onSubmit = async (data: MpesaPaymentRequest) => {
    // Validate phone number
    const phoneValidation = validatePhone(data.phone_number);
    if (phoneValidation !== true) {
      setError(phoneValidation);
      return;
    }
    setIsLoading(true);
    setError(null);

    try {
      // Initiate payment
      const response = await paymentService.initiateMpesaPayment({
        phone_number: data.phone_number,
        order_id: orderId
      });

      setIsProcessing(true);

      // Start polling with exponential backoff
      try {
        const status = await paymentService.pollPaymentStatus(
          response.transaction_id,
          orderId
        );

        if (status.status === 'completed') {
          setIsProcessing(false);
          onSuccess(response.transaction_id);
        } else {
          setIsProcessing(false);
          setError('Payment failed. Please try again.');
        }
      } catch (error: any) {
        setIsProcessing(false);
        setError(error.message || 'Failed to verify payment status');
      }

    } catch (error: any) {
      setError(error.message || 'Payment initiation failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Payment</h2>
        <p className="text-gray-600">Amount: KES {amount.toFixed(2)}</p>
      </div>

      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Select Payment Method
        </label>
        <div className="grid grid-cols-1 gap-3">
          {paymentMethods.map((method) => (
            <div
              key={method.id}
              className={`relative rounded-lg border p-4 cursor-pointer ${
                selectedMethod === method.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300'
              }`}
              onClick={() => setSelectedMethod(method.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">{method.name}</p>
                    <p className="text-gray-500">{method.description}</p>
                  </div>
                </div>
                <div
                  className={`h-5 w-5 rounded-full border flex items-center justify-center ${
                    selectedMethod === method.id
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}
                >
                  {selectedMethod === method.id && (
                    <div className="h-2.5 w-2.5 rounded-full bg-white"></div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
          <p>{error}</p>
        </div>
      )}

      {selectedMethod === 'mpesa' && (
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
            disabled={isLoading || isProcessing || selectedMethod !== 'mpesa'}
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
      )}

      {selectedMethod === 'cash' && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-md">
          <p className="text-yellow-700">
            You will pay for your order when it is delivered to you. Please have the exact amount ready.
          </p>
        </div>
      )}

      {isProcessing && selectedMethod === 'mpesa' && (
        <div className="text-center text-sm text-gray-600">
          <p>Please check your phone for the M-Pesa prompt</p>
          <p>Enter your PIN to complete the payment</p>
        </div>
      )}
    </div>
  );
}
