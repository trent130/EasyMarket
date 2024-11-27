import { apiClient } from '../api-client';

export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  category: string;
  image?: string;
  student: number;
  created_at: string;
  updated_at: string;
  slug: string;
}

export interface ProductCreateInput {
  title: string;
  description: string;
  price: number;
  category: string;
  image?: File;
}

export interface ProductUpdateInput extends Partial<ProductCreateInput> {
  id: number;
}

export const productApi = {
  // Get all products with optional filters
  getAll: async (params?: { 
    category?: string; 
    search?: string;
    min_price?: number;
    max_price?: number;
    page?: number;
  }) => {
    const response = await apiClient.get<Product[]>('/products/', { params });
    return response.data;
  },

  // Get single product by ID
  getById: async (id: number) => {
    const response = await apiClient.get<Product>(`/products/${id}/`);
    return response.data;
  },

  // Create new product
  create: async (data: ProductCreateInput) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await apiClient.post<Product>('/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Update existing product
  update: async ({ id, ...data }: ProductUpdateInput) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await apiClient.patch<Product>(`/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete product
  delete: async (id: number) => {
    await apiClient.delete(`/products/${id}/`);
  },

  // Get product reviews
  getReviews: async (productId: number) => {
    const response = await apiClient.get(`/products/${productId}/reviews/`);
    return response.data;
  },

  // Add product review
  addReview: async (productId: number, data: { rating: number; comment: string }) => {
    const response = await apiClient.post(`/products/${productId}/reviews/`, data);
    return response.data;
  },

  // Get product categories
  getCategories: async () => {
    const response = await apiClient.get('/products/categories/');
    return response.data;
  },

  // Search products
  search: async (query: string) => {
    const response = await apiClient.get<Product[]>('/products/search/', {
      params: { q: query }
    });
    return response.data;
  },

  // Get recommended products
  getRecommended: async () => {
    const response = await apiClient.get<Product[]>('/products/recommended/');
    return response.data;
  },

  // Get products by student
  getByStudent: async (studentId: number) => {
    const response = await apiClient.get<Product[]>(`/products/student/${studentId}/`);
    return response.data;
  }
};
