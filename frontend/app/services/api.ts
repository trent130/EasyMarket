import apiClient from '../../lib/api-client';
import { 
  Order, 
  LoginCredentials, 
  AuthTokens,
  ApiError 
} from '../types/api';

// Error handler
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

// Auth
export const login = async (credentials: LoginCredentials): Promise<AuthTokens> => {
  try {
    const response = await apiClient.post<AuthTokens>('/token/', credentials);
    return response; // Assuming the API returns the tokens directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const refreshToken = async (refreshToken: string): Promise<AuthTokens> => {
  try {
    const response = await apiClient.post<AuthTokens>('/token/refresh/', { refresh: refreshToken });
    return response; // Assuming the API returns the tokens directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Orders
export const createOrder = async (orderData: Partial<Order>): Promise<Order> => {
  try {
    const response = await apiClient.post<Order>('/orders/', orderData);
    return response; // Return the created order directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const fetchOrders = async (): Promise<Order[]> => {
  try {
    const response = await apiClient.get<Order[]>('/orders/');
    return response; // Return the list of orders directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};
