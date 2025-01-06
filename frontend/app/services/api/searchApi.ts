import { fetchWrapper } from '../../utils/fetchWrapper';
import { Product, PaginatedResponse } from '../../types/common';
import { MarketplaceListing } from '../../types/marketplace';

interface SearchResults {
    products: PaginatedResponse<Product>;
    listings: PaginatedResponse<MarketplaceListing>;
    categories: string[];
    suggestions: string[];
}

interface SearchParams {
    query: string;
    filters?: {
        category?: string[];
        priceRange?: [number, number];
        rating?: number;
        availability?: boolean;
    };
    sort?: 'price_asc' | 'price_desc' | 'rating' | 'newest';
    page?: number;
    pageSize?: number;
}

export const searchApi = {
    search: (params: SearchParams) =>
        fetchWrapper<SearchResults>('/marketplace/api/search', { 
            params: Object.fromEntries(
                Object.entries(params).map(([key, value]) => [
                    key, 
                    typeof value === 'object' ? JSON.stringify(value) : value
                ])
            )
        }),
    
    getAutoComplete: (query: string) =>
        fetchWrapper<string[]>('/marketplace/api/search/autocomplete', { 
            params: { query }
        }),
    
    getPopularSearches: () =>
        fetchWrapper<string[]>('/marketplace/api/search/popular'),
};

export type SearchApi = typeof searchApi; 
