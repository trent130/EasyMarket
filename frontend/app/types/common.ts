export type SortOption = 'price_asc' | 'price_desc' | 'newest' | 'rating' | 'popularity';

export interface User {
    id: number;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    avatar?: string;
    role: UserRole;
    status: UserStatus;
}

export interface ApiResponse<T> {
    results: T[];
    count: number;
    next: string | null;
    previous: string | null;
  }

export interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    stock: number;
    category: string;
    images: string[];
}

export interface Address {
    street: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
}

export type UserRole = 'admin' | 'seller' | 'buyer';
export type UserStatus = 'active' | 'inactive' | 'suspended';

export interface PaginatedResponse<T> {
    data: T[];
    totalCount: number;
    pageCount: number;
    currentPage: number;
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
  