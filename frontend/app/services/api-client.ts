import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }

);

// Add a response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: any) => {
    const originalRequest = error.config as InternalAxiosRequestConfig;

    // If the error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post<{ access: string }>('/marketplace/api/token/refresh/', {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('token', access);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // If refresh token fails, logout user
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/marketplace/signin/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
