import { fetchWrapper } from '../../utils/fetchWrapper';
import { User } from '../../types/common';

interface Review {
    id: number;
    productId: number;
    user: User;
    rating: number;
    comment: string;
    images?: string[];
    createdAt: string;
    updatedAt: string;
}

// interface ReviewQueryParams {
//     productId?: number;
//     userId?: number;
//     minRating?: number;
//     maxRating?: number;
//     page?: number;
//     pageSize?: number;
// }

export const reviewsApi = {
    getReviews: (params?: Record<string, string | number>) =>
        fetchWrapper<Review[]>('products/api/products/reviews', { params }),
    
    createReview: (data: Partial<Review>) =>
        fetchWrapper('/products/api/products/reviews', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    updateReview: (id: number, data: Partial<Review>) =>
        fetchWrapper(`/products/api/products/reviews/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    deleteReview: (id: number) =>
        fetchWrapper(`/products/api/products/reviews/${id}`, {
            method: 'DELETE'
        })
};

export type ReviewsApi = typeof reviewsApi;
