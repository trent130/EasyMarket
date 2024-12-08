import apiClient from '../../lib/api-client';
import { 
  Cart, 
  WishList, 
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
    return response.data; // Assuming the API returns the tokens directly
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
    return response.data; // Assuming the API returns the tokens directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Cart
export const fetchCart = async (): Promise<Cart> => {
  try {
    const response = await apiClient.get<Cart>('/carts/');
    return response; // Return the cart directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const addToCart = async (cartId: number, productId: number, quantity: number = 1): Promise<Cart> => {
  try {
    const response = await apiClient.post<Cart>(`/carts/${cartId}/add_item/`, {
      product_id: productId,
      quantity
    });
    return response; // Return the updated cart directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const removeFromCart = async (cartId: number, cartItemId: number): Promise<Cart> => {
  try {
    const response = await apiClient.post<Cart>(`/carts/${cartId}/remove_item/`, {
      cart_item_id: cartItemId
    });
    return response; // Return the updated cart directly
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

// Wishlists
export const fetchWishlists = async (): Promise<WishList[]> => {
  try {
    const response = await apiClient.get<WishList[]>('/marketplace/api/wishlist/');
    return response; // Return the list of wishlists directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const addProductToWishlist = async (wishlistId: number, productId: number): Promise<WishList> => {
  try {
    const response = await apiClient.post<WishList>(`/marketplace/wishlist/${wishlistId}/add_product/`, {
      product_id: productId
    });
    return response; // Return the updated wishlist directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const removeProductFromWishlist = async (wishlistId: number, productId: number): Promise<WishList> => {
  try {
    const response = await apiClient.post<WishList>(`/marketplace/api/wishlist/${wishlistId}/remove_product/`, {
      product_id: productId
    });
    return response; // Return the updated wishlist directly
  } catch (error) {
    if (isApiError(error)) {
      throw handleApiError(error);
    } else {
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};
