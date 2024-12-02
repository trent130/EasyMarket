import apiClient from '../../lib/api-client';
import { 
  Product, 
  Cart, 
  WishList, 
  Order, 
  LoginCredentials, 
  AuthTokens,
  ApiError 
} from '../types/api';

// interface ApiError {
//   message: string;
//   code?: string;
//   details?: Record<string, string[]>;
//   status?: number;
// }

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

const isApiError = (error: unknown): error is { response?: { data?: { message?: string }; status?: number } } => {
  return typeof error === 'object' && error !== null && 'response' in error;
};

// Auth
export const login = async (credentials: LoginCredentials): Promise<AuthTokens> => {
  try {
    const response = await apiClient.post<AuthTokens>('/token/', credentials);
    return response.data;
  } catch (error) {
    // Check if the error is of type ApiError and handle accordingly
    if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const refreshToken = async (refreshToken: string): Promise<AuthTokens> => {
  try {
    const response = await apiClient.post<AuthTokens>('/token/refresh/', { refresh: refreshToken });
    return response.data;
  } catch (error) {
    // Check if the error is of type ApiError and handle accordingly
    if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Products
export const fetchProducts = async (): Promise<Product[]> => {
  try {
    const response = await apiClient.get<Product[]>('/products/');
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const fetchProductById = async (id: number): Promise<Product> => {
  try {
    const response = await apiClient.get<Product>(`/products/${id}/`);
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Cart
export const fetchCart = async (): Promise<Cart> => {
  try {
    const response = await apiClient.get<Cart>('/carts/');
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
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
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const removeFromCart = async (cartId: number, cartItemId: number): Promise<Cart> => {
  try {
    const response = await apiClient.post<Cart>(`/carts/${cartId}/remove_item/`, {
      cart_item_id: cartItemId
    });
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Orders
export const createOrder = async (orderData: Partial<Order>): Promise<Order> => {
  try {
    const response = await apiClient.post<Order>('/orders/', orderData);
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const fetchOrders = async (): Promise<Order[]> => {
  try {
    const response = await apiClient.get<Order[]>('/orders/');
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

// Wishlists
export const fetchWishlists = async (): Promise<WishList[]> => {
  try {
    const response = await apiClient.get<WishList[]>('/wishlists/');
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const addProductToWishlist = async (wishlistId: number, productId: number): Promise<WishList> => {
  try {
    const response = await apiClient.post<WishList>(`/wishlists/${wishlistId}/add_product/`, {
      product_id: productId
    });
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

export const removeProductFromWishlist = async (wishlistId: number, productId: number): Promise<WishList> => {
  try {
    const response = await apiClient.post<WishList>(`/wishlists/${wishlistId}/remove_product/`, {
      product_id: productId
    });
    return response.data;
  } catch (error) {
     // Check if the error is of type ApiError and handle accordingly
     if (isApiError(error)) {
      throw handleApiError(error); // Pass the error directly without type assertion
    } else {
      // Handle unexpected error types
      throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
    }
  }
};

