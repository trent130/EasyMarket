export type ProductCondition = 'new' | 'like_new' | 'good' | 'fair';

export interface Category {
    id: number;
    name: string;
    slug: string;
    description: string;
    image: string;
    product_count: number;
    is_active: boolean;
}

export interface ProductReview {
    id: number;
    rating: number;
    comment: string;
    reviewer_name: string;
    created_at: string;
}

export interface ProductReviews {
    average: number;
    count: number;
    recent: ProductReview[];
}

export interface ProductStudent {
    id: number;
    username: string;
    rating: number;
    products_count: number;
    joined_date: string;
}

export interface ProductBase {
    id: number;
    title: string;
    slug: string;
    price: number;
    category: number;
    category_name: string;
    image_url: string;
    is_active: boolean;
    student_name: string;
    average_rating: number;
    is_wishlisted: boolean;
    available_stock: number;
    condition: ProductCondition;
    created_at: string;
}


export interface Product extends ProductBase {
    description: string;
    image_url: string;
    category_name: string;
    average_rating: number;
    available_stock: number;
    has_variants: boolean;
    total_sales: number;
    variants?: ProductVariant[];
    updated_at: string;
    statistics: ProductStatistics;
    student: ProductSeller;
    reviews: ProductReviews;
}
  

export interface ProductDetail extends Omit<ProductBase, 'category' | 'category_name' | 'student'> {
    description: string;
    category: Category;
    student: ProductStudent;
    reviews: ProductReviews;
    related_products: ProductBase[];
    views_count: number;
    updated_at: string;
}

export interface ProductSearchFilters {
    query?: string;
    category?: number;
    min_price?: number;
    max_price?: number;
    condition?: ProductCondition;
    sort_by?: 'price_asc' | 'price_desc' | 'newest' | 'rating' | 'popularity';
    in_stock?: boolean;
    page?: number;
    page_size?: number;
}

export interface ProductSearchResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: ProductBase[];
}

export interface CreateProductData {
    title: string;
    description: string;
    price: number;
    category: number;
    image?: File;
    condition: ProductCondition;
    stock: number;
}

export interface UpdateProductData extends Partial<CreateProductData> {
    is_active?: boolean;
}

export interface BulkActionData {
    product_ids: number[];
    action: 'delete' | 'activate' | 'deactivate';
}

export interface UpdateStockData {
    stock: number;
}

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
  

