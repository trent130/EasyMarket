export interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  price_adjustment: number;
  available_stock: number;
  final_price: number;
  is_active: boolean;
}

export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  image_url: string;
  category_name: string;
  average_rating: number;
  available_stock: number;
  has_variants: boolean;
  total_sales: number;
  condition: string;
  variants?: ProductVariant[];
  slug: string;
  created_at: string;
  updated_at: string;
  statistics: {
    total_sales: number;
    total_revenue: number;
    last_sale_date: string;
    average_rating: number;
    review_count: number;
    views_count: number;
  };
  student: {
    id: number;
    username: string;
    rating: number;
    products_count: number;
    joined_date: string;
  };
  reviews: {
    average: number;
    count: number;
    recent: Array<{
      id: number;
      rating: number;
      comment: string;
      reviewer_name: string;
      created_at: string;
    }>;
  };
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string;
  product_count: number;
  is_active: boolean;
}

export interface ApiResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface SearchParams {
  query?: string;
  category?: number;
  min_price?: number;
  max_price?: number;
  condition?: string;
  sort_by?: string;
  in_stock?: boolean;
}
