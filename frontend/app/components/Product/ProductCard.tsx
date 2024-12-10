'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Heart, MessageCircle, ShoppingCart } from 'lucide-react';
import type { ProductBase } from '../../types/product';
import { Button } from '../ui/button';
import { Card, CardContent, CardFooter } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../../lib/utils';
import { useAppContext } from '../../AppContext';
import ChatUI from '../chat/ChatUI';

interface ProductCardProps {
    product: ProductBase;
}

export default function ProductCard({ product }: ProductCardProps) {
    const { wishlist, addToWishlist, removeFromWishlist, addToCart } = useAppContext();
    const [isChatOpen, setIsChatOpen] = useState(false);

    const handleWishlistToggle = async (e: React.MouseEvent) => {
        e.preventDefault();
        try {
            const isInWishlist = wishlist.some(item => item.id === product.id);

            if (isInWishlist) {
                await removeFromWishlist(product.id);
            } else {
                await addToWishlist(product);
            }
        } catch (error) {
            console.error('Wishlist toggle failed:', error);
        }
    };

    const handleAddToCart = (e: React.MouseEvent) => {
        e.preventDefault();
        addToCart(product);
    };

    const handleChatToggle = (e: React.MouseEvent) => {
        e.preventDefault();
        setIsChatOpen(!isChatOpen);
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
            <Link href={`/product/${product.slug}`} className="block">
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
                    <div className="absolute top-2 right-2 z-10 flex space-x-2">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleWishlistToggle}
                        >
                            <Heart
                                className={cn(
                                    'h-5 w-5',
                                    wishlist.some(item => item.id === product.id) 
                                    ? 'fill-red-500 text-red-500' 
                                    : 'text-gray-500'
                                )}
                            />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleChatToggle}
                        >
                            <MessageCircle className="h-5 w-5 text-gray-500" />
                        </Button>
                    </div>
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

                <CardFooter className="p-4 pt-0 flex space-x-2">
                    <Button
                        className="flex-1"
                        variant={product.available_stock ? 'default' : 'outline'}
                        disabled={!product.available_stock}
                        onClick={handleAddToCart}
                    >
                        <ShoppingCart className="mr-2 h-4 w-4" />
                        {product.available_stock ? 'Add to Cart' : 'Out of Stock'}
                    </Button>
                    <Button
                        className="flex-1"
                        variant="secondary"
                        onClick={(e) => {
                            e.preventDefault();
                            window.location.href = `/product/${product.slug}`;
                        }}
                    >
                        View Details
                    </Button>
                </CardFooter>
            </Link>

            {isChatOpen && (
                <div className="fixed bottom-20 right-4 z-50">
                    <ChatUI 
                        productId={product.id} 
                        sellerId={product.student} 
                        productName={product.title} 
                    />
                </div>
            )}
        </Card>
    );
}