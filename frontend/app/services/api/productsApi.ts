import { fetchWrapper } from '../../utils/fetchWrapper';
import { Product } from '../../types/common';
import { PaginatedResponse } from '../../types/common';

interface ProductQueryParams {
    page?: number;
    pageSize?: number;
    search?: string;
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    inStock?: boolean;
}

export const productsApi = {
    getProducts: (params?: Record<string, string | number>) =>
        fetchWrapper<PaginatedResponse<Product>>('/api/products', { params }),
    
    getProductDetails: (id: number) =>
        fetchWrapper<Product>(`/api/products/${id}`),
    createProduct: (data: Partial<Product>) =>
        fetchWrapper('/api/products', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    updateProduct: (id: number, data: Partial<Product>) =>
        fetchWrapper(`/api/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    deleteProduct: (id: number) =>
        fetchWrapper(`/api/products/${id}`, {
            method: 'DELETE'
        })
};

export type ProductsApi = typeof productsApi; 