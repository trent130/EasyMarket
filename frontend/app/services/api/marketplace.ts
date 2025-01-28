import apiClient from '../api-client';
import  { Product }  from '../../types/product'; // Ensure correct import
// import { fetchWrapper } from '../../utils/fetchWrapper';
// import { MarketplaceListing } from '../../types/marketplace';
import { ApiError, WishlistItem } from '../../types/api';
import { Category, Review, CartItem }  from '../../types/marketplace';

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

export const marketplaceApi = {
  // Categories
  getCategories: async (params?: {
    parent_id?: number;
    include_children?: boolean;
  }) => {
    const response = await apiClient.get<Category[]>('/marketplace/categories/', { params });
    return response; // Adjusted to return the correct data structure
  },

  getCategoryDetails: async (slug: string) => {
    const response = await apiClient.get<Category & {
      subcategories: Category[];
      featured_products: Product[];
    }>(`/marketplace/categories/${slug}/`);
    return response; // Adjusted to return the correct data structure
  },

  // Wishlist
  getWishlist: async (): Promise<WishlistItem[]> => {
    try {
      const response = await apiClient.get<WishlistItem[]>('/marketplace/api/wishlist/');
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  addToWishlist: async (productId: number): Promise<WishlistItem> => {
    try {
      const response = await apiClient.post<WishlistItem>('/marketplace/api/wishlist/productId/add/', { product_id: productId });
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  removeFromWishlist: async (productId: number): Promise<void> => {
    try {
      await apiClient.post('/marketplace/api/wishlist/productId/remove/', { product_id: productId });
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  // Cart
  getCart: async (): Promise<{
    items: CartItem[];
    total_items: number;
    total_amount: number;
  }> => {
    try {
      const response = await apiClient.get<{
        items: CartItem[];
        total_items: number;
        total_amount: number;
      }>('/marketplace/cart/');
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  addToCart: async (productId: number, quantity: number = 1): Promise<CartItem> => {
    try {
      const response = await apiClient.post<CartItem>('/marketplace/cart/add/', {
        product_id: productId,
        quantity
      });
      return response;
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  removeFromCart: async (itemId: number): Promise<void> => {
    try {
      await apiClient.delete(`/marketplace/cart/items/${itemId}/`);
    } catch (error) {
      if (isApiError(error)) {
        throw handleApiError(error);
      } else {
        throw handleApiError({ response: { data: { message: 'Unexpected error occurred' }, status: 500 } });
      }
    }
  },

  updateCartItem: async (itemId: number, quantity: number) => {
    const response = await apiClient.patch<CartItem>(`/marketplace/cart/items/${itemId}/`, {
      quantity
    });
    return response; // Adjusted to return the correct data structure
  },

  clearCart: async () => {
    await apiClient.post('/marketplace/cart/clear/');
  },

  // Reviews
  getProductReviews: async (productId: number, params?: {
    rating?: number;
    sort_by?: 'latest' | 'rating';
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Review[];
      total: number;
      average_rating: number;
      rating_distribution: Record<number, number>;
    }>(`/marketplace/products/${productId}/reviews/`, { params });
    return response; // Adjusted to return the correct data structure
  },

  addReview: async (productId: number, data: {
    rating: number;
    comment: string;
  }) => {
    const response = await apiClient.post<Review>(`/marketplace/products/${productId}/reviews/`, data);
    return response; // Adjusted to return the correct data structure
  },

  updateReview: async (reviewId: number, data: {
    rating?: number;
    comment?: string;
  }) => {
    const response = await apiClient.patch<Review>(`/marketplace/reviews/${reviewId}/`, data);
    return response; // Adjusted to return the correct data structure
  },

  deleteReview: async (reviewId: number) => {
    await apiClient.delete(`/marketplace/reviews/${reviewId}/`);
  },

  // Search
  search: async (params: {
    query: string;
    category?: string;
    min_price?: number;
    max_price?: number;
    sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'newest';
    page?: number;
  }) => {
    const response = await apiClient.get<{
      results: Product[];
      total: number;
      page: number;
      categories: Category[];
      price_range: { min: number; max: number };
    }>('/marketplace/search/', { params });
    return response; // Adjusted to return the correct data structure
  },

  // Recommendations
  getRecommendations: async (params?: {
    category?: string;
    limit?: number;
    exclude_ids?: number[];
  }) => {
    const response = await apiClient.get<Product[]>('/marketplace/recommendations/', { params });
    return response; // Adjusted to return the correct data structure
  }
};

// Add any additional functions or logic as needed
