'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Heart } from 'lucide-react';
import type { ProductBase } from '../../types/product';
import { Button } from '../ui/button';
import { Card, CardContent, CardFooter } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../../lib/utils';

interface ProductCardProps {
    product: ProductBase;
}

export default function ProductCard({ product }: ProductCardProps) {
    const handleWishlistToggle = async (e: React.MouseEvent) => {
        e.preventDefault();
        // Wishlist functionality will be implemented later
    };

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'KES',
        }).format(price);
    };

    const getConditionColor = (condition: string) => {
        switch (condition) {
            case 'new':
                return 'bg-green-100 text-green-800';
            case 'like_new':
                return 'bg-blue-100 text-blue-800';
            case 'good':
                return 'bg-yellow-100 text-yellow-800';
            case 'fair':
                return 'bg-orange-100 text-orange-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <Card className="group relative overflow-hidden transition-all hover:shadow-lg">
            <Link href={`/products/${product.slug}`}>
                <div className="relative aspect-square overflow-hidden">
                    {product.image_url ? (
                        <Image
                            src={product.image_url}
                            alt={product.title}
                            fill
                            className="object-cover transition-transform group-hover:scale-105"
                            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        />
                    ) : (
                        <div className="flex h-full items-center justify-center bg-gray-100">
                            <span className="text-gray-400">No image</span>
                        </div>
                    )}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-2 top-2 z-10"
                        onClick={handleWishlistToggle}
                    >
                        <Heart
                            className={cn(
                                'h-5 w-5',
                                product.is_wishlisted ? 'fill-red-500 text-red-500' : 'text-gray-500'
                            )}
                        />
                    </Button>
                </div>

                <CardContent className="p-4">
                    <div className="mb-2 flex items-center justify-between">
                        <Badge variant="outline" className={cn('text-xs', getConditionColor(product.condition))}>
                            {product.condition.replace('_', ' ')}
                        </Badge>
                        {product.average_rating > 0 && (
                            <div className="flex items-center text-sm text-yellow-500">
                                ★ {product.average_rating.toFixed(1)}
                            </div>
                        )}
                    </div>
                    <h3 className="mb-1 text-lg font-semibold line-clamp-2">{product.title}</h3>
                    <p className="mb-2 text-sm text-gray-500">
                        by {product.student_name} in {product.category_name}
                    </p>
                    <div className="flex items-center justify-between">
                        <span className="text-lg font-bold">{formatPrice(product.price)}</span>
                        {!product.available_stock ? (
                            <Badge variant="destructive">Out of Stock</Badge>
                        ) : (
                            <Badge variant="secondary">{product.available_stock} left</Badge>
                        )}
                    </div>
                </CardContent>

                <CardFooter className="p-4 pt-0">
                    <Button
                        className="w-full"
                        variant={product.available_stock ? 'default' : 'outline'}
                        disabled={!product.available_stock}
                    >
                        {product.available_stock ? 'View Details' : 'Out of Stock'}
                    </Button>
                </CardFooter>
            </Link>
        </Card>
    );
}
