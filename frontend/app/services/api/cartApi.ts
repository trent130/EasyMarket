import { fetchWrapper } from '../../utils/fetchWrapper';
import { Product } from '../../types/common';

interface CartItem {
    id: number;
    product: Product;
    quantity: number;
    price: number;
}

interface Cart {
    id: number;
    items: CartItem[];
    totalItems: number;
    totalAmount: number;
    userId: number;
}

export const cartApi = {
    getCart: () => 
        fetchWrapper<Cart>('/marketplace/api/cart'),
    
    addItem: (productId: number, quantity: number) =>
        fetchWrapper<Cart>('/marketplace/api/cart/${productId}/add/', { // to be implimented this one
            method: 'POST',
            body: JSON.stringify({ productId, quantity })
        }),
    
    updateItem: (itemId: number, quantity: number) =>
        fetchWrapper<Cart>(`/marketplace/api/cart/items/${itemId}/update/`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        }),
    
    removeItem: (itemId: number) =>
        fetchWrapper<Cart>(`/marketplace/api/cart/${itemId}/remove/`, {
            method: 'DELETE'
        }),
    
    clearCart: () =>
        fetchWrapper<void>('/marketplace/api/clear', { // to be added in the cart functionalities in the backend
            method: 'POST'
        })
};

export type CartApi = typeof cartApi; 
