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
