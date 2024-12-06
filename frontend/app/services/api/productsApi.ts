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
    /**
     * Fetches a list of all categories.
     * 
     * @returns A list of categories.
     */
    getCategories: () =>
        fetchWrapper<Category[]>('/api/categories'), // Assuming this is the endpoint for categories
};

export const productsApi = {
/**
 * Fetches a paginated list of products with optional filtering parameters.
 * 
 * @param params - An optional object containing query parameters for filtering 
 *                 the products. Possible keys include:
 *                 - `page`: The page number to retrieve.
 *                 - `pageSize`: The number of products per page.
 *                 - `search`: A search term to filter products by name or description.
 *                 - `category`: The category to filter products by.
 *                 - `minPrice`: The minimum price of products to filter by.
 *                 - `maxPrice`: The maximum price of products to filter by.
 *                 - `inStock`: A boolean indicating whether to only include products in stock.
 * 
 * @returns A promise that resolves to a paginated response containing products.
 */
    getProducts: (params?: Record<string, string | number>) =>
        fetchWrapper<PaginatedResponse<Product>>('/products/api/products', { params }),
    
/**
 * Fetches detailed information about a product using its slug.
 * 
 * @param slug - The unique identifier for the product.
 * @returns A promise that resolves to a Product object containing detailed information.
 */
    getProductDetails: (slug: string) =>
        fetchWrapper<Product>(`/products/api/products/${slug}`),
    /**
     * Creates a new product using the provided data.
     * 
     * @param data - A partial Product object containing the fields to use when creating the product.
     * @returns A promise that resolves to the newly created Product object.
     */
    createProduct: (data: Partial<Product>) =>
        fetchWrapper('/products/api/products', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    /**
     * Updates a product by ID.
     * 
     * @param id - The ID of the product to update.
     * @param data - The partial Product object containing the fields to update.
     * @returns A promise that resolves to the updated Product object.
     */
    updateProduct: (slug: string, data: Partial<Product>) =>
        fetchWrapper(`/products/api/products/${slug}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    /**
     * Deletes a product by ID.
     * 
     * @param id - The ID of the product to delete.
     * @returns A promise that resolves to an empty response.
     */
    deleteProduct: (slug: string) =>
        fetchWrapper(`/products/api/products/${slug}`, {
            method: 'DELETE'
        })
};

export type ProductsApi = typeof productsApi; 