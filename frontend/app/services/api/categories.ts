import apiClient from '../api-client';
import type { ApiResponse }  from '../../types/common';

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string;
  product_count: number;
  is_active: boolean;
}

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
export const fetchCategoryProducts = async (slug: string) => {
  const { data } = await apiClient.get<ApiResponse<Category>>(`/categories/${slug}/products/`);
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

// Add any additional functions or logic as needed
