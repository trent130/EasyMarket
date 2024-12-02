'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { debounce } from 'lodash';
import { productService } from '../../services/product';
import type { ProductBase, ProductSearchFilters, Category } from '../../types/product';
import ProductCard from './ProductCard';
import ProductFilter from './ProductFilter';
import { Input } from '../ui/input';
import { Button } from '../ui/button';

const ITEMS_PER_PAGE = 12;

export default function ProductList() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // State
    const [products, setProducts] = useState<ProductBase[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [totalItems, setTotalItems] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [filters, setFilters] = useState<ProductSearchFilters>({
        query: searchParams?.get('query') || undefined,
        category: Number(searchParams?.get('category')) || undefined,
        min_price: Number(searchParams?.get('min_price')) || undefined,
        max_price: Number(searchParams?.get('max_price')) || undefined,
        condition: searchParams?.get('condition') as any || undefined,
        sort_by: searchParams?.get('sort_by') as any || 'newest',
        in_stock: searchParams?.get('in_stock') === 'true'
    });

    // Load categories
    useEffect(() => {
        const loadCategories = async () => {
            try {
                const data = await productService.getCategories();
                setCategories(data);
            } catch (error) {
                console.error('Failed to load categories:', error);
            }
        };
        loadCategories();
    }, []);

    // Load products with current filters
    const loadProducts = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await productService.searchProducts({
                ...filters,
                page: currentPage
            });
            setProducts(response.results);
            setTotalItems(response.count);
        } catch (error) {
            setError('Failed to load products');
            console.error('Failed to load products:', error);
        } finally {
            setLoading(false);
        }
    }, [filters, currentPage]);

    useEffect(() => {
        loadProducts();
    }, [loadProducts]);

    // Update URL with filters
    useEffect(() => {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value !== undefined) {
                params.set(key, String(value));
            }
        });
        router.push(`?${params.toString()}`);
    }, [filters, router]);

    // Debounced search handler
    const debouncedSearch = useCallback(
        debounce((query: string) => {
            setFilters(prev => ({ ...prev, query }));
            setCurrentPage(1);
        }, 300),
        []
    );

    // Filter handlers
    const handleFilterChange = (newFilters: Partial<ProductSearchFilters>) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
        setCurrentPage(1);
    };

    // Sort handler
    const handleSortChange = (value: string) => {
        setFilters(prev => ({ ...prev, sort_by: value as any }));
    };

    // Pagination handler
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-500">{error}</p>
                <Button onClick={loadProducts} className="mt-4">
                    Try Again
                </Button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                {/* Filters */}
                <div className="md:col-span-1">
                    <ProductFilter
                        filters={filters}
                        categories={categories}
                        onChange={handleFilterChange}
                    />
                </div>

                {/* Products */}
                <div className="md:col-span-3">
                    {/* Search and Sort */}
                    <div className="mb-6">
                        <Input
                            type="search"
                            placeholder="Search products..."
                            defaultValue={filters.query}
                            onChange={e => debouncedSearch(e.target.value)}
                            className="max-w-sm mb-4"
                        />
                        <select
                            value={filters.sort_by}
                            onChange={e => handleSortChange(e.target.value)}
                            className="ml-auto h-10 rounded-md border px-3"
                        >
                            <option value="newest">Newest First</option>
                            <option value="price_asc">Price: Low to High</option>
                            <option value="price_desc">Price: High to Low</option>
                            <option value="rating">Highest Rated</option>
                            <option value="popularity">Most Popular</option>
                        </select>
                    </div>

                    {/* Product Grid */}
                    {loading ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Array.from({ length: ITEMS_PER_PAGE }).map((_, i) => (
                                <div
                                    key={i}
                                    className="h-[350px] rounded-lg bg-gray-100 animate-pulse"
                                />
                            ))}
                        </div>
                    ) : products.length > 0 ? (
                        <>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                {products.map(product => (
                                    <ProductCard key={product.id} product={product} />
                                ))}
                            </div>

                            {/* Pagination */}
                            <div className="mt-8 flex justify-center gap-2">
                                {Array.from(
                                    { length: Math.ceil(totalItems / ITEMS_PER_PAGE) },
                                    (_, i) => i + 1
                                ).map(page => (
                                    <Button
                                        key={page}
                                        variant={page === currentPage ? 'default' : 'outline'}
                                        onClick={() => handlePageChange(page)}
                                    >
                                        {page}
                                    </Button>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-12">
                            <p className="text-gray-500">No products found</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
