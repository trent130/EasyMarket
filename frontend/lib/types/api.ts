export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string;
  product_count: number;
  is_active: boolean;
}

export interface ApiResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface SingleResponse<T> {
  data: T;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface SearchParams {
  query?: string;
  category?: number;
  min_price?: number;
  max_price?: number;
  condition?: string;
  in_stock?: boolean;
}

export interface FilterParams extends PaginationParams, SearchParams {
  sort_by?: 'price_asc' | 'price_desc' | 'newest' | 'rating' | 'popularity';
}
