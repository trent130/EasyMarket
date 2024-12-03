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
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Error Request:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error Message:', error.message);
    }
    console.error('API Error Config:', error.config);
    return Promise.reject(error);
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
  const response = await apiClient.get<ApiResponse<Product>>(`/products/api/products/by-slug/${slug}/`);
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
