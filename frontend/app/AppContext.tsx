'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { WebSocketService, WebSocketMessageType } from '../lib/websocket';
import { 
 /*  fetchProducts,  */
  fetchWishlists,
  addProductToWishlist as apiAddToWishlist,
  removeProductFromWishlist as apiRemoveFromWishlist,
  createOrder as apiCreateOrder
} from '../app/services/api';
import { WishList } from './types/api';


interface Product {
  id: number;
  name: string;
  price: number;
}


interface CartItem extends Product {
  quantity: number;
}

interface AppContextType {
  cart: CartItem[];
  wishlist: Product[];
  addToCart: (product: Product) => void;
  removeFromCart: (productId: number) => void;
  addToWishlist: (product: Product) => Promise<void>;
  removeFromWishlist: (productId: number) => Promise<void>;
  checkout: () => Promise<void>;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [wishlist, setWishlist] = useState<Product[]>([]);
  const [wsService, setWsService] = useState<WebSocketService | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocketService('ws://localhost:8000/ws/marketplace/');
    ws.connect();
    setWsService(ws);

    // Subscribe to real-time updates
    ws.subscribe<{ products: Product[] }>(WebSocketMessageType.PRODUCT_UPDATE, (data) => {
      const updatedProducts = data.products;
      setCart(prevCart => 
        prevCart.map(item => {
          const updatedProduct = updatedProducts.find((p: Product) => p.id === item.id);
          return updatedProduct ? { ...updatedProduct, quantity: item.quantity } : item;
        })
      );
    });

    return () => ws.disconnect();
  }, []);

  // Initialize wishlist from backend
// Assuming the API response structure includes a list of wishlists, each containing a list of products
useEffect(() => {
  const initializeData = async () => {
    try {
      const wishlistData: WishList[] = await fetchWishlists();
      
      // Extract products from the first wishlist (or handle multiple wishlists as needed)
      const products: Product[] = wishlistData.flatMap(wishlist => wishlist.products);

      setWishlist(products);
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  };
  initializeData();
}, []);

  /**
   * Adds a product to the cart or increments its quantity if it already exists
   * @param {Product} product The product to add
   */
  const addToCart = (product: Product) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === product.id);
      if (existingItem) {
        return prevCart.map((item) =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prevCart, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId: number) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== productId));
  };

  const addToWishlist = async (product: Product) => {
    try {
      await apiAddToWishlist(1, product.id); // Assuming wishlist ID 1 for now
      setWishlist((prevWishlist) => {
        if (!prevWishlist.some((item) => item.id === product.id)) {
          return [...prevWishlist, product];
        }
        return prevWishlist;
      });
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      throw error;
    }
  };

  const removeFromWishlist = async (productId: number) => {
    try {
      await apiRemoveFromWishlist(1, productId); // Assuming wishlist ID 1 for now
      setWishlist((prevWishlist) => prevWishlist.filter((item) => item.id !== productId));
    } catch (error) {
      console.error('Failed to remove from wishlist:', error);
      throw error;
    }
  };

  const checkout = async () => {
    try {
      const orderData = {
        items: cart.map(item => ({
          id: item.id,
          product: item.product,
          quantity: item.quantity,
          price: item.price,
        }))
      };
      await apiCreateOrder(orderData);
      setCart([]); // Clear cart after successful checkout
      // Notify websocket about order
      wsService?.send(WebSocketMessageType.ORDER_UPDATE, { status: 'created' });
    } catch (error) {
      console.error('Checkout failed:', error);
      throw error;
    }
  };

  const value = {
    cart,
    wishlist,
    addToCart,
    removeFromCart,
    addToWishlist,
    removeFromWishlist,
    checkout
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
