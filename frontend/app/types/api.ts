import { Decimal } from "@prisma/client/runtime/library";

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  // Add other product fields as needed
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  cart: number;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total: number;
  user: number;
}

export interface WishList {
  name: unknown;
  price: Decimal;
  id: number;
  products: Product[];
  user: number;
}

export interface ApiError {
  message: string;
  status: number;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface Order {
  id: number;
  items: OrderItem[];
  total: number;
  status: string;
  created_at: string;
}

export interface OrderItem {
  id: number;
  product: Product;
  quantity: number;
  price: number;
}

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

