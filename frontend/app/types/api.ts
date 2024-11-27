// API Response Types
export interface ApiResponse<T> {
    data: T;
    message?: string;
    status: 'success' | 'error';
}

// User Types
export interface UserProfile {
    id: number;
    username: string;
    email: string;
    avatar?: string;
    // ... other profile fields
}

// Product Types
export interface Product {
    id: number;
    name: string;
    price: number;
    description: string;
    // ... other product fields
}

// Cart Types
export interface CartItem {
    id: number;
    productId: number;
    quantity: number;
    // ... other cart item fields
} 