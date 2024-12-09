'use client';

import React from 'react';
import ProductList from '../components/Product/ProductList';

export default function ProductsPage() {
    return (
        <div className="container mx-auto px-4 py-8">
           
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                

                {/* Products */}
                <div className="md:col-span-3">   
                    <ProductList />
                </div>
            </div>
        </div>
    );
}