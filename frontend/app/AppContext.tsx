'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { WebSocketService, WebSocketMessageType } from '../lib/websocket';
import { 
 /*  fetchProducts,  */
  // fetchWishlists,
  // addProductToWishlist as apiAddToWishlist,
  // removeProductFromWishlist as apiRemoveFromWishlist,
  createOrder as apiCreateOrder,
  /* addProductToWishlist,
  removeProductFromWishlist */
} from '../app/services/api';
import { Wishlist, Product } from './types/api';
import {  marketplaceApi } from './services/api/marketplace';


// interface Product {
//   id: number;
//   name: string;
//   price: number;
// }


interface CartItem extends Product {
  quantity: number;
}

interface AppContextType {
  cart: CartItem[];
  wishlist: Product[];
  addToWishlist: (product: Product) => Promise<void>;
  removeFromWishlist: (productId: number) => Promise<void>;
  addToCart: (product: Product) => void;
  removeFromCart: (productId: number) => void;
  checkout: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

/**
 * Provides application-level context including cart and wishlist management.
 * Initializes and maintains WebSocket connection for real-time product updates.
 * 
 * @param {Object} props - The component props.
 * @param {ReactNode} props.children - The child components to render.
 * 
 * @returns {JSX.Element} The AppProvider component.
 * 
 * @description
 * Initializes the cart and wishlist states. Subscribes to WebSocket
 * for real-time product updates and updates cart items accordingly.
 * Provides functions to add/remove items from cart and wishlist, and
 * to perform checkout operations. Wraps children components with the
 * AppContext provider to make cart, wishlist, and related functions
 * available throughout the application.
 */
export function AppProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [wishlist, setWishlist] = useState<Product[]>([]);
  // const [wishlistId, setWishlistId] = useState<number | null>(null);
  const [wsService, setWsService] = useState<WebSocketService | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocketService('ws://localhost:8000/ws/marketplace/');
    ws.connect();
    setWsService(ws);

    ws.subscribe<{ products: Product[] }>(WebSocketMessageType.PRODUCT_UPDATE, (data) => {
      const updatedProducts = data.products;
      setCart(prevCart => 
        prevCart.map(item => {
          const updatedProduct = updatedProducts.find(p => p.id === item.id);
          return updatedProduct ? { ...updatedProduct, quantity: item.quantity } : item;
        })
      );
    });

    return () => ws.disconnect();
  }, []);

  useEffect(() => {
    const initializeWishlist = async () => {
      try {
        const wishlistItems = await marketplaceApi.getWishlist();
        const products = wishlistItems.map(item => item.product);
        setWishlist(products);
      } catch (error) {
        console.error('Failed to fetch wishlist:', error);
        setWishlist([]);
      }
    };
    initializeWishlist();
  }, []);

  /**
   * Adds a product to the cart or increments its quantity if it already exists
   * @param {Product} product The product to add
   */
 // Cart functions (to be synced with API)
 const addToCart = (product: Product) => {
  setCart(prevCart => {
    const existingItem = prevCart.find(item => item.id === product.id);
    if (existingItem) {
      return prevCart.map(item =>
        item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      );
    }
    return [...prevCart, { ...product, quantity: 1 }];
  });
};

  /**
   * Removes a product from the cart by its ID
   * @param {number} productId The ID of the product to remove
   */
  const removeFromCart = (productId: number) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  // Wishlist functions
  const addToWishlist = async (product: Product) => {
    try {
      if (wishlist.some(item => item.id === product.id)) return;
      await marketplaceApi.addToWishlist(product.id);
      setWishlist(prev => [...prev, product]);
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      throw error;
    }
  };

  const removeFromWishlist = async (productId: number) => {
    try {
      await marketplaceApi.removeFromWishlist(productId);
      setWishlist(prev => prev.filter(item => item.id !== productId));
    } catch (error) {
      console.error('Failed to remove from wishlist:', error);
      throw error;
    }
  };

  // Checkout function
  const checkout = async () => {
    try {
      //TODO: create the checkout api call from the marketplace
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
    checkout,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}


