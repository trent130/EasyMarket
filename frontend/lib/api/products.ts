import  apiClient  from '../api-client';

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  image?: string;
}

export const productApi = {
  fetchAll: async (): Promise<Product[]> => {
    const response = await apiClient.get('/products/');
    return response.data;
  },

  fetchById: async (id: number): Promise<Product> => {
    const response = await apiClient.get(`/products/${id}/`);
    return response.data;
  },

  search: async (query: string): Promise<Product[]> => {
    const response = await apiClient.get(`/products/search/?q=${encodeURIComponent(query)}`);
    return response.data;
  }
};
