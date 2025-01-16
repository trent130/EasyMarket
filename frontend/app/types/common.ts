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
export interface Review {
  id: number;
  productId: number;
  user: User;
  rating: number;
  comment: string;
  images?: string[];
  createdAt: string;
  updatedAt: string;
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
  
  export interface SecurityLog {
    id: string;
    userId: number;
    action: string;
    ipAddress: string;
    userAgent: string;
    location: string;
    timestamp: string;
    status: 'success' | 'failure';
    details?: Record<string, unknown>; // Updated to use 'unknown' instead of 'any'
}

export interface SecuritySettings {
    twoFactorEnabled: boolean;
    loginNotifications: boolean;
    trustedDevices: boolean;
    passwordLastChanged: string;
    securityQuestionsSet: boolean;
}

export interface Student {
  id: number;
  studentId: string;
  firstName: string;
  lastName: string;
  email: string;
  course: string;
  year: number;
  status: 'active' | 'inactive' | 'graduated';
}

export interface Message {
    id: number;
    senderId: number;
    receiverId: number;
    content: string;
    attachments?: string[];
    read: boolean;
    createdAt: string;
}

export interface Conversation {
    id: number;
    participants: User[];
    lastMessage: Message;
    unreadCount: number;
    updatedAt: string;
}

export interface GroupChat {
    id: number;
    name: string;
    description?: string;
    avatar?: string;
    members: User[];
    admins: User[];
    createdAt: string;
    updatedAt: string;
}

export interface GroupMessage {
    id: number;
    groupId: number;
    sender: User;
    content: string;
    attachments?: string[];
    reactions: MessageReaction[];
    createdAt: string;
}

export interface MessageReaction {
    userId: number;
    emoji: string;
    createdAt: string;
}
