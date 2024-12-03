# Marketplace API Documentation

## Authentication Endpoints

### Two-Factor Authentication (2FA)
```
GET  /api/auth/2fa-status/         - Get 2FA status
POST /api/auth/enable-2fa/         - Enable 2FA
POST /api/auth/verify-2fa/         - Verify 2FA token
POST /api/auth/disable-2fa/        - Disable 2FA
POST /api/auth/validate-backup-code/- Validate backup code
POST /api/auth/regenerate-backup-codes/ - Generate new backup codes
```

## Marketplace Endpoints

### Cart Operations
```
GET    /api/cart/                  - Get user's cart
POST   /api/cart/                  - Create new cart
GET    /api/cart/{id}/            - Get cart details
POST   /api/cart/{id}/add/        - Add item to cart
POST   /api/cart/{id}/remove/     - Remove item from cart
POST   /api/cart/{id}/clear/      - Clear cart
```

### Wishlist Operations
```
GET    /api/wishlist/             - Get user's wishlist
POST   /api/wishlist/             - Create new wishlist
GET    /api/wishlist/{id}/        - Get wishlist details
POST   /api/wishlist/{id}/add/    - Add product to wishlist
POST   /api/wishlist/{id}/remove/ - Remove product from wishlist
```

### Product Reviews
```
GET    /products/api/products/{id}/reviews/ - Get product reviews
POST   /products/api/products/{id}/reviews/ - Create product review
GET    /api/reviews/{id}/         - Get review details
PUT    /api/reviews/{id}/         - Update review
DELETE /api/reviews/{id}/         - Delete review
```

### Search and Recommendations
```
GET    /api/search/               - Search products
GET    /api/recommendations/      - Get product recommendations
```

## Frontend Integration

### API Client Setup
```typescript
// lib/api-client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### API Modules
1. `products.ts` - Product management
2. `orders.ts` - Order processing
3. `payment.ts` - Payment handling
4. `students.ts` - Student profiles
5. `admin.ts` - Admin operations
6. `marketplace.ts` - Cart and wishlist

### Example Usage
```typescript
// Using the marketplace API
import { api } from '@/lib/api';

// Cart operations
const cart = await api.marketplace.getCart();
await api.marketplace.addToCart(productId, quantity);

// Wishlist operations
const wishlist = await api.marketplace.getWishlist();
await api.marketplace.addToWishlist(productId);

// Search and recommendations
const results = await api.marketplace.search({ query: 'textbook' });
const recommendations = await api.marketplace.getRecommendations();
```

## Data Models

### Product
```typescript
interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  category: string;
  image?: string;
  student: number;
  created_at: string;
  updated_at: string;
  slug: string;
}
```

### Cart
```typescript
interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  added_at: string;
}

interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  total_amount: number;
}
```

### Wishlist
```typescript
interface WishlistItem {
  id: number;
  product: Product;
  added_at: string;
}
```

### Review
```typescript
interface Review {
  id: number;
  product: number;
  reviewer: {
    id: number;
    username: string;
    avatar?: string;
  };
  rating: number;
  comment: string;
  created_at: string;
}
```

## Security

### Authentication
- JWT token-based authentication
- Two-factor authentication (2FA)
- Backup codes for account recovery

### Protected Routes
- All API endpoints require authentication except:
  - Product search
  - Product listings
  - Category listings

### Request Headers
```typescript
{
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
}
```

## Error Handling

### Error Response Format
```typescript
interface ErrorResponse {
  error: string;
  code?: string;
  details?: any;
}
```

### Common Error Codes
- 401: Unauthorized
- 403: Forbidden (2FA required)
- 404: Not found
- 422: Validation error
- 500: Server error

## WebSocket Integration

### Real-time Updates
```typescript
const ws = new WebSocketService('ws://localhost:8000/ws/marketplace/');
ws.subscribe(WebSocketMessageType.PRODUCT_UPDATE, handleProductUpdate);
```

### Message Types
- PRODUCT_UPDATE
- ORDER_UPDATE
- NOTIFICATION
- CHAT_MESSAGE
