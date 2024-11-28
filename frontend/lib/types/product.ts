export interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  price_adjustment: number;
  available_stock: number;
  final_price: number;
  is_active: boolean;
}

export interface ProductReview {
  id: number;
  rating: number;
  comment: string;
  reviewer_name: string;
  created_at: string;
}

export interface ProductStatistics {
  total_sales: number;
  total_revenue: number;
  last_sale_date: string;
  average_rating: number;
  review_count: number;
  views_count: number;
}

export interface ProductSeller {
  id: number;
  username: string;
  rating: number;
  products_count: number;
  joined_date: string;
}

export interface ProductReviews {
  average: number;
  count: number;
  recent: ProductReview[];
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
  is_wishlisted: boolean;
  statistics: ProductStatistics;
  student: ProductSeller;
  reviews: ProductReviews;
}
