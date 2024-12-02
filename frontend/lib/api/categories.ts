import axios from 'axios';
import type { ApiResponse } from '../types/common';

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string;
  product_count: number;
  is_active: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Categories
export const fetchCategories = async (): Promise<Category[]> => {
  const { data } = await apiClient.get<ApiResponse<Category>>('/categories/');
  return data.results || [];
};

export const fetchCategoryBySlug = async (slug: string): Promise<Category> => {
  const { data } = await apiClient.get<Category>(`/categories/${slug}/`);
  return data;
};

// Category Products
export const fetchCategoryProducts = async (categoryId: number) => {
  const { data } = await apiClient.get<ApiResponse<Category>>(`/categories/${categoryId}/products/`);
  return data.results || [];
};

// Featured Categories
export const fetchFeaturedCategories = async (): Promise<Category[]> => {
  const { data } = await apiClient.get<ApiResponse<Category>>('/categories/featured/');
  return data.results || [];
};

// Category Statistics
export interface CategoryStats {
  total_products: number;
  active_products: number;
  total_sales: number;
  average_price: number;
}

export const fetchCategoryStats = async (categoryId: number): Promise<CategoryStats> => {
  const { data } = await apiClient.get<CategoryStats>(`/categories/${categoryId}/stats/`);
  return data;
};
