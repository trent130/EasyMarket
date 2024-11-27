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
    image_url: string | null;
    student: number;
    student_name: string;
    average_rating: number;
    is_wishlisted: boolean;
    available_stock: number;
    condition: ProductCondition;
    created_at: string;
}

export interface ProductDetail extends Omit<ProductBase, 'category' | 'category_name'> {
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
