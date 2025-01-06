import { User } from "next-auth";
import { Product } from "./product";

export interface MarketplaceListing {
    id: number;
    title: string;
    description: string;
    price: number;
    category: string;
    seller: User;
    images: string[];
    status: ListingStatus;
    createdAt: string;
    updatedAt: string;
}

export interface Category {
    id: number;
    name: string;
    slug: string;
    description?: string;
    parent?: number;
    image?: string;
    product_count: number;
  }
  
  
  export interface CartItem {
    id: number;
    product: Product;
    quantity: number;
    added_at: string;
  }
  
  export interface Review {
    id: number;
    product: number;
    reviewer: {
      id: number;
      username: string;
      avatar?: string;
    };
    rating: number;
    comment: string;
    created_at: string;
  }
  

export type ListingStatus = 'active' | 'sold' | 'suspended';

export interface SearchParams {
    query?: string;
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    status?: ListingStatus;
    page?: number;
    pageSize?: number;
} 