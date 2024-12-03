import { AxiosError } from 'axios';

export interface ApiError {
  message: string;
  code?: string;
  details?: never;
  status?: number;
}

export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  total_pages: number;
}

export function handleApiError(error: unknown): ApiError {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const data = error.response?.data;

    // Handle specific error cases
    switch (status) {
      case 401:
        return {
          message: 'Authentication required',
          code: 'UNAUTHORIZED',
          status: 401
        };
      case 403:
        return {
          message: data?.error || 'Access denied',
          code: 'FORBIDDEN',
          status: 403
        };
      case 404:
        return {
          message: 'Resource not found',
          code: 'NOT_FOUND',
          status: 404
        };
      case 422:
        return {
          message: 'Validation error',
          code: 'VALIDATION_ERROR',
          details: data?.errors,
          status: 422
        };
      default:
        return {
          message: data?.error || 'An unexpected error occurred',
          code: 'UNKNOWN_ERROR',
          status: status || 500
        };
    }
  }

  // Handle non-Axios errors
  return {
    message: error instanceof Error ? error.message : 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR',
    status: 500
  };
}

export function formatApiUrl(path: string, params?: Record<string, never>): string {
  const url = new URL(path, process.env.NEXT_PUBLIC_API_URL);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  return url.toString();
}

export function formatFormData(data: Record<string, unknown>): FormData {
  const formData = new FormData();
  
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (value instanceof File) {
        formData.append(key, value);
      } else if (Array.isArray(value)) {
        value.forEach((item, index) => {
          formData.append(`${key}[${index}]`, String(item));
        });
      } else if (typeof value === 'object') {
        formData.append(key, JSON.stringify(value));
      } else {
        formData.append(key, String(value));
      }
    }
  });
  
  return formData;
}

export function parseApiResponse<T>(data: unknown): T {
  // Add any common response parsing logic here
  return data as T;
}

export function isPaginatedResponse<T>(data: any): data is PaginatedResponse<T> {
  return (
    data &&
    Array.isArray(data.results) &&
    typeof data.total === 'number' &&
    typeof data.page === 'number' &&
    typeof data.total_pages === 'number'
  );
}

export function validatePhoneNumber(phoneNumber: string): boolean {
  // Validate Kenyan phone numbers (format: 254XXXXXXXXX)
  const regex = /^254[17][0-9]{8}$/;
  return regex.test(phoneNumber);
}

export function formatCurrency(amount: number, currency: string = 'KES'): string {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-KE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(date));
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> => {
  let retries = 0;
  
  while (true) {
    try {
      return await fn();
    } catch (error) {
      if (retries >= maxRetries) {
        throw error;
      }
      
      const delay = baseDelay * Math.pow(2, retries);
      await new Promise(resolve => setTimeout(resolve, delay));
      retries++;
    }
  }
};
