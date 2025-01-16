import axios from 'axios';
import type { Category, Product, ProductBase } from '../../types/product';
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

// Categories
export const fetchCategories = async (): Promise<Category[]> => {
  const { data } = await apiClient.get<Category[]>('/categories/');
  return data;
};

// Create Product
export const createProduct = async (data: Partial<Product>): Promise<Product> => {
  const { data: responseData } = await apiClient.post<SingleResponse<Product>>('/products/', data);
  return responseData.data;
};

// Update Product
export const updateProduct = async (id: number, data: Partial<Product>): Promise<Product> => {
  const { data: responseData } = await apiClient.put<SingleResponse<Product>>(`/products/${id}/`, data);
  return responseData.data;
};

// Delete Product
export const deleteProduct = async (id: number): Promise<void> => {
  await apiClient.delete(`/products/${id}/`);
};

// Get Product Details
export const getProductDetails = async (slug: string): Promise<Product> => {
  try {
    const response = await apiClient.get<Product>(`/products/${slug}/`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Product not found');
    }
    throw error;
  }
};

export default apiClient;