import axios from 'axios';
import type { Product } from '../../types/product';
import type { ApiResponse, SingleResponse, SearchParams } from '../../types/common';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/products/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Products
export const fetchProducts = async (): Promise<Product[]> => {
  const { data } = await apiClient.get<ApiResponse<Product>>('/products/');
  return data.results || [];
};

/**
 * Fetch a product by its ID
 * @param {number} id The product ID.
 * @returns {Promise<Product>} The product.
 */
export const fetchProductById = async (id: number): Promise<Product> => {
  const { data } = await apiClient.get<SingleResponse<Product>>(`/products/${id}/`);
  return data.data;
};

/**
 * Fetch a product by its slug.
 * @param {string} slug The product slug.
 * @returns {Promise<Product>} The product object.
 */
export const fetchProductBySlug = async (slug: string): Promise<Product> => {
  const { data } = await apiClient.get<SingleResponse<Product>>(`/products/${slug}/`);
  return data.data;
};

// Search
export const searchProducts = async (params: SearchParams): Promise<Product[]> => {
  const { data } = await apiClient.get<ApiResponse<Product>>('/products/search/', { params });
  return data.results || [];
};

// Featured Products
export const fetchFeaturedProducts = async (): Promise<Product[]> => {
  const { data } = await apiClient.get<ApiResponse<Product>>('/products/featured/');
  return data.results || [];
};

// Trending Products
export const fetchTrendingProducts = async (): Promise<Product[]> => {
  const { data } = await apiClient.get<ApiResponse<Product>>('/products/trending/');
  return data.results || [];
};

export default apiClient;