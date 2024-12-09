'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { productsApi } from '../../services/api/productsApi';
import type { Product } from '../../../app/types/product';
import ProductDetailView from '../../../app/components/Product/';


export async function generateMetadata({ params }: { params: { slug: string } }) {
    try {
        const product = await productsApi.getProductDetails(params.slug);
        return {
            title: product.title,
            description: product.description,
            openGraph: {
                title: product.title,
                description: product.description,
                images: [{ url: product.image_url }]
            }
        };
    } catch (error) {
        return {
            title: 'Product Not Found',
            description: 'The requested product could not be found'
        };
    }
}

export default function ProductDetailPage() {
    const params = useParams();
    const [product, setProduct] = useState<Product | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadProduct = async () => {
            try {
                if (typeof params.slug === 'string') {
                    const data = await productsApi.getProductDetails(params.slug);
                    setProduct(data);
                }
            } catch (error) {
                setError('Failed to load product details');
            } finally {
                setLoading(false);
            }
        };

        loadProduct();
    }, [params.slug]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!product) return <div>Product not found</div>;

    return <ProductDetailView product={product} />;
}