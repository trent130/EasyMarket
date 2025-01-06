'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { WebSocketService, WebSocketMessageType } from '../lib/websocket';
import { 
 /*  fetchProducts,  */
  fetchWishlists,
  addProductToWishlist as apiAddToWishlist,
  removeProductFromWishlist as apiRemoveFromWishlist,
  createOrder as apiCreateOrder,
  addProductToWishlist,
  removeProductFromWishlist
} from '../app/services/api';
import { Wishlist } from './types/api';


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
  wishlistId: number | null;
  addToWishlist: (product: Product) => Promise<void>;
  removeFromWishlist: (productId: number) => Promise<void>;
  addToCart: (product: Product) => void;
  removeFromCart: (productId: number) => void;
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
  const [wishlistId, setWishlistId] = useState<number | null>(null);
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
  /**
   * Initializes the wishlist state by fetching the wishlist data from the backend.
   * 
   * @returns {Promise<void>} A promise that resolves when the data is fetched and the state is updated.
   * @throws {Error} If the API request fails. The error is logged to the console.
   */
  const initializeData = async () => {
    try {
      // Fetch user's wishlists
      const wishlists: Wishlist[] = await fetchWishlists();
      
      // Use the first wishlist or create a default one
      if (wishlists.length > 0) {
        const primaryWishlist = wishlists[0];
        setWishlistId(primaryWishlist.id);
        
        // Extract products from wishlist items
        const wishlistProducts = primaryWishlist.items.map(item => item.product);
        setWishlist(wishlistProducts);
      } else {
        // Handle case where no wishlist exists
        setWishlistId(null);
        setWishlist([]);
      }
    } catch (error) {
      console.error('Failed to fetch wishlist:', error);
      setWishlistId(null);
      setWishlist([]);
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

  /**
   * Removes a product from the cart by its ID
   * @param {number} productId The ID of the product to remove
   */
  const removeFromCart = (productId: number) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== productId));
  };

  const addToWishlist = async (product: Product) => {
    try {
      // Ensure we have a valid wishlist ID
      if (!wishlistId) {
        throw new Error('No wishlist available');
      }

      // Check if product is already in wishlist
      if (wishlist.some(item => item.id === product.id)) {
        return;
      }

      // Add product to wishlist via API
      await addProductToWishlist(wishlistId, product.id);
      
      // Update local state
      setWishlist(prevWishlist => [...prevWishlist, product]);
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      throw error;
    }
  };

  const removeFromWishlist = async (productId: number) => {
    try {
      // Ensure we have a valid wishlist ID
      if (!wishlistId) {
        throw new Error('No wishlist available');
      }

      // Remove product from wishlist via API
      await removeProductFromWishlist(wishlistId, productId);
      
      // Update local state
      setWishlist(prevWishlist => 
        prevWishlist.filter(item => item.id !== productId)
      );
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
          product: item.name,
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
    wishlistId,
    checkout
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
