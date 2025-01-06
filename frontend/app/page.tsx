'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { 
  Book, 
  TrendingUp, 
  ShoppingCart, 
  Star, 
  Users, 
  CheckCircle 
} from 'lucide-react';
import { Button } from './components/ui/button';
import { 
  fetchFeaturedProducts, 
  fetchTrendingProducts 
} from './services/api/products';
import ProductCard from './components/Product/ProductCard';
import type { ProductBase } from './types/product';

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState<ProductBase[]>([]);
  const [trendingProducts, setTrendingProducts] = useState<ProductBase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const [featured, trending] = await Promise.all([
          fetchFeaturedProducts(),
          fetchTrendingProducts()
        ]);
        
        setFeaturedProducts(featured);
        setTrendingProducts(trending);
      } catch (error) {
        console.error('Failed to load products', error);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  return (
    <main className="w-full bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <div className="container mx-auto px-4 py-16 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Campus Marketplace, Reimagined
            </h1>
            <p className="text-xl mb-6">
              Buy, sell, and exchange textbooks and academic resources 
              with students across your campus.
            </p>
            <div className="flex space-x-4">
              <Link href="/product">
                <Button variant="secondary" size="lg">
                  <ShoppingCart className="mr-2" /> Browse Products
                </Button>
              </Link>
              <Link href="/textbook-exchange">
                <Button variant="outline" size="lg" className="text-white border-white">
                  <Book className="mr-2" /> Textbook Exchange
                </Button>
              </Link>
            </div>
          </div>
          <div className="hidden md:block">
            <Image 
              src="/hero-illustration.svg" 
              alt="Campus Marketplace" 
              width={500} 
              height={400} 
              className="mx-auto"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Why Choose EasyMarket?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <Users className="w-12 h-12 text-blue-500" />,
              title: "Campus Community",
              description: "Connect with fellow students and trade resources seamlessly."
            },
            {
              icon: <CheckCircle className="w-12 h-12 text-green-500" />,
              title: "Verified Listings",
              description: "Every product goes through a rigorous verification process."
            },
            {
              icon: <Star className="w-12 h-12 text-yellow-500" />,
              title: "Trusted Platform",
              description: "Safe, secure, and designed specifically for students."
            }
          ].map((feature, index) => (
            <div 
              key={index} 
              className="bg-white p-6 rounded-lg shadow-md text-center hover:shadow-xl transition-all"
            >
              {feature.icon}
              <h3 className="text-xl font-semibold mt-4 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      <section className="container mx-auto px-4 py-16 bg-gray-100">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold flex items-center">
            <TrendingUp className="mr-3 text-blue-600" /> Featured Products
          </h2>
          <Link href="/product">
            <Button variant="outline">View All</Button>
          </Link>
        </div>
        
        {loading ? (
          <div className="grid md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div 
                key={i} 
                className="bg-white h-[400px] animate-pulse rounded-lg"
              />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-4 gap-6">
            {featuredProducts.slice(0, 4).map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* Trending Products */}
      <section className="container mx-auto px-4 py-16">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold flex items-center">
            <Star className="mr-3 text-yellow-600" /> Trending Now
          </h2>
          <Link href="/product">
            <Button variant="outline">Explore More</Button>
          </Link>
        </div>
        
        {loading ? (
          <div className="grid md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div 
                key={i} 
                className="bg-white h-[400px] animate-pulse rounded-lg"
              />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-4 gap-6">
            {trendingProducts.slice(0, 4).map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* Call to Action */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Start Buying and Selling Today
          </h2>
          <p className="text-xl mb-8">
            Join thousands of students who have found their perfect academic resources.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/auth/signup">
              <Button size="lg" variant="secondary">
                Create Account
              </Button>
            </Link>
            <Link href="/product">
              <Button size="lg" variant="outline" className="text-white border-white">
                Browse Marketplace
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}