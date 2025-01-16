import { User } from "next-auth";
import { Orders } from "./orders";

export interface AdminDashboardData {
    totalUsers: number;
    totalOrders: number;
    totalRevenue: number;
    recentOrders: Orders[];
    userStats: UserStats;
}

export interface UserManagementData {
    users: User[];
    totalCount: number;
    pageCount: number;
}

export interface UserStats {
    newUsers: number;
    activeUsers: number;
    inactiveUsers: number;
}

export interface UserQueryParams {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: 'active' | 'inactive' | 'all';
} 
