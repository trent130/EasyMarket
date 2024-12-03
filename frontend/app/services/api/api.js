// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Reusable fetch wrapper with error handling
async function fetchWrapper(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        credentials: 'include', // For handling cookies/sessions
    });
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
}

// API service methods
export const apiService = {
    // User related endpoints
    user: {
        getProfile: () => fetchWrapper('/user/profile'),
        updateProfile: (data) => fetchWrapper('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    },
    
    // Product related endpoints
    products: {
        getList: (params) => fetchWrapper(`/products?${new URLSearchParams(params)}`),
        getDetail: (id) => fetchWrapper(`/products/${id}`),
        create: (data) => fetchWrapper('/products', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    },
    
    // Cart related endpoints
    cart: {
        get: () => fetchWrapper('/cart'),
        addItem: (data) => fetchWrapper('/cart/items', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        updateItem: (id, data) => fetchWrapper(`/cart/items/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
    }
}; 