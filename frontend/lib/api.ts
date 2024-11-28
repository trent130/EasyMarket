import axios from 'axios';

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
export const fetchProducts = async () => {
  const response = await apiClient.get('/products/');
  return response.data.results || [];
};

export const fetchProductById = async (id: number) => {
  const response = await apiClient.get(`/products/${id}/`);
  return response.data;
};

export const fetchProductBySlug = async (slug: string) => {
  const response = await apiClient.get(`/products/by-slug/${slug}/`);
  return response.data;
};

// Categories
export const fetchCategories = async () => {
  const response = await apiClient.get('/categories/');
  return response.data.results || [];
};

// Search
export const searchProducts = async (params: {
  query?: string;
  category?: number;
  min_price?: number;
  max_price?: number;
  condition?: string;
  sort_by?: string;
  in_stock?: boolean;
}) => {
  const response = await apiClient.get('/products/search/', { params });
  return response.data.results || [];
};

// Featured Products
export const fetchFeaturedProducts = async () => {
  const response = await apiClient.get('/products/featured/');
  return response.data.results || [];
};

// Trending Products
export const fetchTrendingProducts = async () => {
  const response = await apiClient.get('/products/trending/');
  return response.data.results || [];
};

export default apiClient;
