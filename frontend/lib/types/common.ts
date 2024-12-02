export type SortOption = 'price_asc' | 'price_desc' | 'newest' | 'rating' | 'popularity';

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
  sort_by?: SortOption;
}
