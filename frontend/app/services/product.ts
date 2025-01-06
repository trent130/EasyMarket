import apiClient from '../../lib/api-client';
import type {
    ProductBase,
    ProductDetail,
    ProductSearchFilters,
    ProductSearchResponse,
    CreateProductData,
    UpdateProductData,
    BulkActionData,
    UpdateStockData,
    Category
} from '../types/product';

// Error handler
const handleApiError = (error: any): never => {
    const message = error.response?.data?.error || 'An error occurred';
    throw new Error(message);
};

export const productService = {
    // Get all products with pagination and caching
    getProducts: async (page = 1): Promise<ProductSearchResponse> => {
        try {
            const response = await apiClient.get<ProductSearchResponse>('/products/api/products/', {
                params: { page }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Get single product by ID or slug
    getProduct: async (identifier: number | string): Promise<ProductDetail> => {
        try {
            const response = await apiClient.get<ProductDetail>(`/products/api/products/${identifier}/`);
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Search products with filters
    searchProducts: async (filters: ProductSearchFilters): Promise<ProductSearchResponse> => {
        try {
            const response = await apiClient.get<ProductSearchResponse>('/products/api/products/search/', {
                params: filters
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Get featured products
    getFeaturedProducts: async (): Promise<ProductBase[]> => {
        try {
            const response = await apiClient.get<ProductBase[]>('/products/api/products/featured/');
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Get trending products
    getTrendingProducts: async (): Promise<ProductBase[]> => {
        try {
            const response = await apiClient.get<ProductBase[]>('/products/api/products/trending/');
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Create new product
    createProduct: async (data: CreateProductData): Promise<ProductDetail> => {
        try {
            // Handle file upload with FormData
            const formData = new FormData();
            Object.entries(data).forEach(([key, value]) => {
                if (value !== undefined) {
                    formData.append(key, value);
                }
            });

            const response = await apiClient.post<ProductDetail>('/products/api/products/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Update existing product
    updateProduct: async (id: number, data: UpdateProductData): Promise<ProductDetail> => {
        try {
            // Handle file upload with FormData
            const formData = new FormData();
            Object.entries(data).forEach(([key, value]) => {
                if (value !== undefined) {
                    formData.append(key, value);
                }
            });

            const response = await apiClient.patch<ProductDetail>(`/products/api/products/${id}/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Delete product (soft delete)
    deleteProduct: async (id: number): Promise<void> => {
        try {
            await apiClient.delete(`/products/api/products/${id}/`);
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Update product stock
    updateStock: async (id: number, data: UpdateStockData): Promise<ProductDetail> => {
        try {
            const response = await apiClient.post<ProductDetail>(
                `/products/api/products/${id}/update_stock/`,
                data
            );
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Perform bulk actions on products
    bulkAction: async (data: BulkActionData): Promise<void> => {
        try {
            await apiClient.post('/products/api/products/bulk_action/', data);
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Get all categories
    getCategories: async (): Promise<Category[]> => {
        try {
            const response = await apiClient.get<Category[]>('/products/api/categories/');
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Get products by category
    getProductsByCategory: async (slug: string, page = 1): Promise<ProductSearchResponse> => {
        try {
            const response = await apiClient.get<ProductSearchResponse>(
                `/products/api/categories/${slug}/products/`,
                {
                    params: { page }
                }
            );
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    // Cache management
    clearProductCache: async (): Promise<void> => {
        try {
            await apiClient.post('/products/api//products/clear_cache/');
        } catch (error) {
            throw handleApiError(error);
        }
    }
};
