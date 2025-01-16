import axios from 'axios';
import type { Review, User } from '../../types/common';

interface ReviewQueryParams {
  productId?: number;
  userId?: number;
  minRating?: number;
  maxRating?: number;
  page?: number;
  pageSize?: number;
}

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

// Reviews
export const fetchReviews = async (params?: ReviewQueryParams): Promise<Review[]> => {
  const { data } = await apiClient.get<Review[]>('/products/reviews/', { params });
  return data;
};

// Create Review
export const createReview = async (data: Partial<Review>): Promise<Review> => {
  const { data: responseData } = await apiClient.post<Review>('/products/reviews/', data);
  return responseData;
};

// Update Review
export const updateReview = async (id: number, data: Partial<Review>): Promise<Review> => {
  const { data: responseData } = await apiClient.put<Review>(`/products/reviews/${id}`, data);
  return responseData;
};

// Delete Review
export const deleteReview = async (id: number): Promise<void> => {
  await apiClient.delete(`/products/reviews/${id}`);
};

export default apiClient;