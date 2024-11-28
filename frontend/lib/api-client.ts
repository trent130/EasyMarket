import axios from 'axios';
import type { Product, Category, ApiResponse, SearchParams } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

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
  const response = await apiClient.get<ApiResponse<Product>>('/products/');
  return response.data.results || [];
};

export const fetchProductById = async (id: number): Promise<Product> => {
  const response = await apiClient.get<ApiResponse<Product>>(`/products/${id}/`);
  return response.data;
};

export const fetchProductBySlug = async (slug: string): Promise<Product> => {
  const response = await apiClient.get<ApiResponse<Product>>(`/products/by-slug/${slug}/`);
  return response.data;
};

// Categories
export const fetchCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<ApiResponse<Category>>('/categories/');
  return response.data.results || [];
};

// Search
export const searchProducts = async (params: SearchParams): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/search/', { params });
  return response.data.results || [];
};

// Featured Products
export const fetchFeaturedProducts = async (): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/featured/');
  return response.data.results || [];
};

// Trending Products
export const fetchTrendingProducts = async (): Promise<Product[]> => {
  const response = await apiClient.get<ApiResponse<Product>>('/products/trending/');
  return response.data.results || [];
};

export default apiClient;
