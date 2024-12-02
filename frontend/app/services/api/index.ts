import { adminApi } from './adminApi';
import { marketplaceApi } from './marketplaceApi';
import { ordersApi } from './ordersApi';
import { productsApi } from './productsApi';
import { paymentsApi } from './paymentsApi';
import { studentsApi } from './studentsApi';
import { cartApi } from './cartApi';
import { reviewsApi } from './reviewsApi';
import { notificationsApi } from './notificationsApi';
import { searchApi } from './searchApi';
import { analyticsApi } from './analyticsApi';
import { chatApi } from './chatApi';
import { groupChatApi } from './groupChatApi';

export type { StudentsApi } from './studentsApi';
export type { ProductsApi } from './productsApi';
export type { PaymentsApi } from './paymentsApi';
export type { CartApi } from './cartApi';
export type { ReviewsApi } from './reviewsApi';
export type { NotificationsApi } from './notificationsApi';
export type { MarketplaceApi } from './marketplaceApi';
export type { SearchApi } from './searchApi';
export type { AnalyticsApi } from './analyticsApi';
export type { ChatApi } from './chatApi';
export type { GroupChatApi } from './groupChatApi';

export const api = {
    admin: adminApi,
    marketplace: marketplaceApi,
    orders: ordersApi,
    products: productsApi,
    payments: paymentsApi,
    students: studentsApi,
    cart: cartApi,
    reviews: reviewsApi,
    notifications: notificationsApi,
    search: searchApi,
    analytics: analyticsApi,
    chat: chatApi,
    groupChat: groupChatApi,
};

export type Api = typeof api; 