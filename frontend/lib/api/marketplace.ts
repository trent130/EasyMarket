import { apiClient } from '../api-client';
import { Product } from './products';

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent?: number;
  image?: string;
  product_count: number;
}

export interface WishlistItem {
  id: number;
  product: Product;
  added_at: string;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  added_at: string;
}

export interface Review {
  id: number;
  product: number;
  reviewer: {
    id: number;
    username: string;
    avatar?: string;
  };
  rating: number;
  comment: string;
  created_at: string;
}

export const marketplaceApi = {
  // Categories
  getCategories: async (params?: {
    parent_id?: number;
    include_children?: boolean;
  }) => {
    const response = await apiClient.get<Category[]>('/marketplace/categories/', { params });
    return response.data;
  },

  getCategoryDetails: async (slug: string) => {
    const response = await apiClient.get<Category & {
      subcategories: Category[];
      featured_products: Product[];
    }>(`/marketplace/categories/${slug}/`);
    return response.data;
  },

  // Wishlist
  getWishlist: async () => {
    const response = await apiClient.get<WishlistItem[]>('/marketplace/wishlist/');
    return response.data;
  },

  addToWishlist: async (productId: number) => {
    const response = await apiClient.post<WishlistItem>('/marketplace/wishlist/add/', {
      product_id: productId
    });
    return response.data;
  },

  removeFromWishlist: async (productId: number) => {
    await apiClient.post('/marketplace/wishlist/remove/', {
      product_id: productId
    });
  },

  // Cart
  getCart: async () => {
    const response = await apiClient.get<{
      items: CartItem[];
      total_items: number;
      total_amount: number;
    }>('/marketplace/cart/');
    return response.data;
  },

  addToCart: async (productId: number, quantity: number = 1) => {
    const response = await apiClient.post<CartItem>('/marketplace/cart/add/', {
      product_id: productId,
      quantity
    });
    return response.data;
  },

  updateCartItem: async (itemId: number, quantity: number) => {
    const response = await apiClient.patch<CartItem>(`/marketplace/cart/items/${itemId}/`, {
      quantity
    });
    return response.data;
  },

  removeFromCart: async (itemId: number) => {
    await apiClient.delete(`/marketplace/cart/items/${itemId}/`);
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
    return response.data;
  },

  addReview: async (productId: number, data: {
    rating: number;
    comment: string;
  }) => {
    const response = await apiClient.post<Review>(`/marketplace/products/${productId}/reviews/`, data);
    return response.data;
  },

  updateReview: async (reviewId: number, data: {
    rating?: number;
    comment?: string;
  }) => {
    const response = await apiClient.patch<Review>(`/marketplace/reviews/${reviewId}/`, data);
    return response.data;
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
    return response.data;
  },

  // Recommendations
  getRecommendations: async (params?: {
    category?: string;
    limit?: number;
    exclude_ids?: number[];
  }) => {
    const response = await apiClient.get<Product[]>('/marketplace/recommendations/', { params });
    return response.data;
  }
};