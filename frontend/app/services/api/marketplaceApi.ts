import { fetchWrapper } from '../../utils/fetchWrapper';
import { MarketplaceListing, SearchParams } from '../../types/marketplace';

export const marketplaceApi = {
    getListings: (params: Record<string, string | number>) =>
        fetchWrapper<MarketplaceListing[]>('/api/marketplace/listings', { params }),
    
    createListing: (data: Partial<MarketplaceListing>) =>
        fetchWrapper('/api/marketplace/listings', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    
    updateListing: (id: number, data: Partial<MarketplaceListing>) =>
        fetchWrapper(`/api/marketplace/listings/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    
    deleteListing: (id: number) =>
        fetchWrapper(`/api/marketplace/listings/${id}`, {
            method: 'DELETE'
        })
};

export type MarketplaceApi = typeof marketplaceApi;
// to be removed definately
