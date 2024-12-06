'use client';

import React from 'react';
import ProductList from './components/Product/ProductList';

/**
 * The home page of the app.
 *
 * Displays a list of products in a centered container.
 */
export default function HomePage() {
    return (
        <main className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-8">
                <h1 className="text-2xl font-bold mb-4">EasyMarket</h1>
                <ProductList />
            </div>
        </main>
    );
}
