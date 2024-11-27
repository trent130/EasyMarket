import apiClient from './api-client';

// User Authentication
export const login = async (credentials: { username: string; password: string }) => {
  const response = await apiClient.post('/token/', credentials);
  return response.data;
};

export const refreshToken = async (refreshToken: string) => {
  const response = await apiClient.post('/token/refresh/', { refresh: refreshToken });
  return response.data;
};

// Products
export const fetchProducts = async () => {
  const response = await apiClient.get('/products/');
  return response.data;
};

export const fetchProductById = async (id: number) => {
  const response = await apiClient.get(`/products/${id}/`);
  return response.data;
};

// Orders
export const createOrder = async (orderData: any) => {
  const response = await apiClient.post('/orders/', orderData);
  return response.data;
};

export const fetchOrders = async () => {
  const response = await apiClient.get('/orders/');
  return response.data;
};

// Wishlists
export const fetchWishlists = async () => {
  const response = await apiClient.get('/wishlists/');
  return response.data;
};

export const addProductToWishlist = async (wishlistId: number, productId: number) => {
  const response = await apiClient.post(`/wishlists/${wishlistId}/add_product/`, { product_id: productId });
  return response.data;
};

export const removeProductFromWishlist = async (wishlistId: number, productId: number) => {
  const response = await apiClient.post(`/wishlists/${wishlistId}/remove_product/`, { product_id: productId });
  return response.data;
};
