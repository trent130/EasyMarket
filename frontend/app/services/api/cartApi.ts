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
        fetchWrapper<Cart>('/api/cart'),
    
    addItem: (productId: number, quantity: number) =>
        fetchWrapper<Cart>('/api/cart/items', {
            method: 'POST',
            body: JSON.stringify({ productId, quantity })
        }),
    
    updateItem: (itemId: number, quantity: number) =>
        fetchWrapper<Cart>(`/api/cart/items/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        }),
    
    removeItem: (itemId: number) =>
        fetchWrapper<Cart>(`/api/cart/items/${itemId}`, {
            method: 'DELETE'
        }),
    
    clearCart: () =>
        fetchWrapper<void>('/api/cart/clear', {
            method: 'POST'
        })
};

export type CartApi = typeof cartApi; 