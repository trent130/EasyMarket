import { User } from "next-auth";

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