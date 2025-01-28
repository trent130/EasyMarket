import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Add Bearer Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 and Refresh Tokens
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        console.warn('No refresh token. Redirecting to login.');
        handleLogout();
        return Promise.reject(error);
      }

      try {
        const response = await axios.post<{ access: string }>(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/marketplace/api/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('token', access);

        // Retry original request
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed. Redirecting to login.', refreshError);
        handleLogout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Utility: Handle Logout
function handleLogout() {
  
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');

  // Navigate to the sign-in page
  // navigate('/auth/signin/');
} 

export default apiClient;
