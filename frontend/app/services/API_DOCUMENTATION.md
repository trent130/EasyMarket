# Frontend API Integration Documentation

## API Modules

### 1. Products API
```typescript
import { productsApi } from '@/lib/api';

// Get all products
const products = await productsApi.getAll();

// Search products
const results = await productsApi.search({
  query: 'textbook',
  category: 1,
  min_price: 100,
  max_price: 1000,
  sort_by: 'price_asc'
});

// Create product
const newProduct = await productsApi.create({
  title: 'Product Title',
  description: 'Description',
  price: 100,
  category: 1,
  image: file
});
```

### 2. Orders API
```typescript
import { orderApi } from '@/lib/api';

// Create order
const order = await orderApi.create({
  items: [{ product_id: 1, quantity: 2 }],
  shipping_address: 'Address'
});

// Get order history
const orders = await orderApi.getHistory();

// Track order
const status = await orderApi.trackOrder(orderId);
```

### 3. Payment API
```typescript
import { paymentApi } from '@/lib/api';

// Initiate M-Pesa payment
const payment = await paymentApi.mpesa.initiate({
  phone_number: '254712345678',
  order_id: 123,
  amount: 1000
});

// Verify payment
const status = await paymentApi.verifyPayment(transactionId);

// Get payment receipt
const receipt = await paymentApi.generateReceipt(transactionId);
```

### 4. Static Pages API
```typescript
import { staticPagesApi } from '@/lib/api';

// Get page content
const page = await staticPagesApi.getPage('about-us');

// Get FAQs
const faqs = await staticPagesApi.getFAQsByCategory();

// Send contact message
const response = await staticPagesApi.sendContactMessage({
  name: 'John Doe',
  email: 'john@example.com',
  subject: 'Query',
  message: 'Message content'
});
```

### 5. Marketplace API
```typescript
import { marketplaceApi } from '@/lib/api';

// Get cart
const cart = await marketplaceApi.getCart();

// Add to wishlist
await marketplaceApi.addToWishlist(productId);

// Get product reviews
const reviews = await marketplaceApi.getProductReviews(productId);
```

## Authentication

All authenticated requests should include a JWT token:
```typescript
// api-client.ts
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Error Handling

API errors are handled consistently:
```typescript
try {
  const result = await api.products.create(data);
} catch (error) {
  if (error.response?.status === 401) {
    // Handle unauthorized
  } else if (error.response?.status === 400) {
    // Handle validation errors
    const errors = error.response.data;
  } else {
    // Handle other errors
  }
}
```

## Real-time Updates

WebSocket integration for real-time updates:
```typescript
import { WebSocketService } from '@/lib/websocket';

const ws = new WebSocketService('ws://localhost:8000/ws/marketplace/');

// Subscribe to updates
ws.subscribe(WebSocketMessageType.PRODUCT_UPDATE, (data) => {
  // Handle product update
});

ws.subscribe(WebSocketMessageType.ORDER_UPDATE, (data) => {
  // Handle order update
});
```

## Type Safety

All API responses are properly typed:
```typescript
interface Product {
  id: number;
  title: string;
  price: number;
  // ...other fields
}

const products: Product[] = await api.products.getAll();
```

## Best Practices

1. Use the unified API interface:
```typescript
import { api } from '@/lib/api';

// Instead of importing individual APIs
api.products.getAll();
api.orders.create();
api.payment.verifyPayment();
```

2. Handle loading states:
```typescript
const [loading, setLoading] = useState(false);

try {
  setLoading(true);
  await api.products.create(data);
} finally {
  setLoading(false);
}
```

3. Cache responses when appropriate:
```typescript
const { data: products, mutate } = useSWR(
  '/api/products',
  () => api.products.getAll()
);
```

4. Use proper error boundaries:
```typescript
<ErrorBoundary fallback={<ErrorComponent />}>
  <ProductList />
</ErrorBoundary>
```

## Integration Examples

### Product Listing Page
```typescript
export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await api.products.getAll();
        setProducts(data);
      } catch (error) {
        console.error('Failed to load products:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  return (
    <div>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <ProductGrid products={products} />
      )}
    </div>
  );
}
```

### Checkout Flow
```typescript
async function handleCheckout(cart: CartItem[]) {
  try {
    // 1. Create order
    const order = await api.orders.create({
      items: cart.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
      }))
    });

    // 2. Initialize payment
    const payment = await api.payment.mpesa.initiate({
      order_id: order.id,
      amount: order.total_amount
    });

    // 3. Verify payment
    const status = await api.payment.verifyPayment(
      payment.transaction_id
    );

    if (status.verified) {
      // 4. Clear cart
      await api.marketplace.clearCart();
      
      // 5. Show success
      router.push(`/orders/${order.id}/success`);
    }
  } catch (error) {
    console.error('Checkout failed:', error);
  }
}
