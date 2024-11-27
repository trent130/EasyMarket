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