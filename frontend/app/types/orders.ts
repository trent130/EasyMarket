import { Address } from "cluster";
import { User } from "next-auth";
import { Product } from "./api";

export interface Order {
    id: number;
    user: User;
    items: OrderItem[];
    total: number;
    status: OrderStatus;
    paymentStatus: PaymentStatus;
    shippingAddress: Address;
    createdAt: string;
    updatedAt: string;
}

export interface OrderItem {
    id: number;
    product: Product;
    quantity: number;
    price: number;
}

export type OrderStatus = 
    | 'pending'
    | 'confirmed'
    | 'shipped'
    | 'delivered'
    | 'cancelled';

export type PaymentStatus = 
    | 'pending'
    | 'paid'
    | 'failed'
    | 'refunded';

export interface OrderQueryParams {
    page?: number;
    pageSize?: number;
    status?: OrderStatus;
    startDate?: string;
    endDate?: string;
    userId?: number;
} 