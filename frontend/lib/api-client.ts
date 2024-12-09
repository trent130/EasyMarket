import axios from 'axios';
import type { Product, Category, ApiResponse, SearchParams } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
import { handleApiError } from '../app/utils/errorHandling';

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(handleApiError(error));
  }
);

// Products
export const fetchProducts = async (): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/api/products/');
  console.log('Fetched Products:', response.data); // Add this line for debugging
  return response.data.results || [];
};

export const fetchProductById = async (id: number): Promise<Product> => {
  const response = await apiClient.get<ApiResponse<Product>>(`/products/api/products/${id}/`);
  return response.data; // Adjusted to return the correct data structure
};

export const fetchProductBySlug = async (slug: string): Promise<Product> => {
  const response = await apiClient.get<ApiResponse<Product>>(`/products/api/products/${slug}/`);
  return response.data; // Adjusted to return the correct data structure
};

// Categories
export const fetchCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<ApiResponse<Category>>('/products/api/categories/');
  return response.data.results || [];
};

// Search
export const searchProducts = async (params: SearchParams): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/api/products/search/', { params });
  return response.data.results || [];
};

// Featured Products
export const fetchFeaturedProducts = async (): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/api/products/featured/');
  return response.data.results || [];
};

// Trending Products
export const fetchTrendingProducts = async (): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/api/products/trending/');
  return response.data.results || [];
};

export default apiClient;
