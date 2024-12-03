import { fetchWrapper } from '../../utils/fetchWrapper';
import { Product } from '../../types/common';
import { PaginatedResponse } from '../../types/common';
import { Category } from '../../types/product';

// interface ProductQueryParams {
//     page?: number;
//     pageSize?: number;
//     search?: string;
//     category?: string;
//     minPrice?: number;
//     maxPrice?: number;
//     inStock?: boolean;
// }

export const categoriesApi = {
    getCategories: () =>
        fetchWrapper<Category[]>('/api/categories'), // Assuming this is the endpoint for categories
};

export const productsApi = {
    getProducts: (params?: Record<string, string | number>) =>
        fetchWrapper<PaginatedResponse<Product>>('/products/api/products', { params }),
    
    getProductDetails: (id: number) =>
        fetchWrapper<Product>(`/products/api/products/${id}`),
    createProduct: (data: Partial<Product>) =>
        fetchWrapper('/products/api/products', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    updateProduct: (id: number, data: Partial<Product>) =>
        fetchWrapper(`/products/api/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    deleteProduct: (id: number) =>
        fetchWrapper(`/products/api/products/${id}`, {
            method: 'DELETE'
        })
};

export type ProductsApi = typeof productsApi; 