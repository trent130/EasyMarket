'use client';

import React from 'react';
import ProductList from '../components/Product/ProductList';
import ProductSort from '../components/Product/ProductSort';
import ProductFilter from '../components/Product/ProductFilter';

export default function ProductsPage() {
    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Our Products</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                {/* Filters */}
                <div className="md:col-span-1">
                    <ProductFilter />
                </div>

                {/* Products */}
                <div className="md:col-span-3">
                    <div className="flex justify-between items-center mb-4">
                        <ProductSort />
                    </div>
                    
                    <ProductList />
                </div>
            </div>
        </div>
    );
}