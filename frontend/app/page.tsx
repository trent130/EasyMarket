"use client";

// import './globals.css'
import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Book,
  TrendingUp,
  ShoppingCart,
  Star,
  Users,
  CheckCircle,
  Notebook,
  Calculator,
  Backpack,
  ChevronRight,
} from "lucide-react";
import { Button } from "./components/ui/button";
import {
  fetchFeaturedProducts,
  fetchTrendingProducts,
} from "./services/api/products";
import ProductCard from "./components/Product/ProductCard";
import type { Product } from "./types/product";
import Footer from "./components/Footer";
// import { Height } from '@mui/icons-material';

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [trendingProducts, setTrendingProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const [featured, trending] = await Promise.all([
          fetchFeaturedProducts(),
          fetchTrendingProducts(),
        ]);

        setFeaturedProducts(featured);
        setTrendingProducts(trending);
      } catch (error) {
        console.error("Failed to load products", error);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  return (
    <main className="w-full bg-gray-50">
      {/* Hero Section */}
      <section className="h-[100vh] relative bg-white text-gray-900 flex items-center justify-center">
        <div className="mx-auto px-6 md:px-12 lg:px-16 py-16 grid md:grid-cols-2 items-center gap-8">
          <div className="animate-fadeIn">
            <div className="text-sm text-blue-500 uppercase font-semibold mb-2">
              Your Trusted Marketplace
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Campus Marketplace, Reimagined
            </h1>
            <p className="text-lg md:text-xl mb-6 text-gray-700 tracking-wide leading-relaxed">
              Buy, sell, and exchange textbooks and academic resources with
              students across your campus.
            </p>
            <div className="flex space-x-4">
              <Link href="/product">
                <Button
                  variant="destructive"
                  size="lg"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <ShoppingCart className="mr-2" /> Browse Products
                </Button>
              </Link>
              <Link href="/textbook-exchange">
                <Button
                  variant="outline"
                  size="lg"
                  className="border-gray-300 hover:bg-gray-100"
                >
                  <Book className="mr-2" /> Textbook Exchange
                </Button>
              </Link>
            </div>
          </div>
          <div className="hidden md:block">
            <Image
              src="/hero.jpg"
              alt="Campus Marketplace"
              width={800}
              height={400}
              className="mx-auto rounded-lg shadow-lg border border-gray-200"
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
              description:
                "Connect with fellow students and trade resources seamlessly.",
            },
            {
              icon: <CheckCircle className="w-12 h-12 text-green-500" />,
              title: "Verified Listings",
              description:
                "Every product goes through a rigorous verification process.",
            },
            {
              icon: <Star className="w-12 h-12 text-yellow-500" />,
              title: "Trusted Platform",
              description:
                "Safe, secure, and designed specifically for students.",
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg shadow-md text-center hover:shadow-xl transition-all"
            >
              {feature.icon}
              <h3 className="text-xl font-semibold mt-4 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
          Popular Categories
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: Book,
              name: "Textbooks",
              description: "New & used course materials",
            },
            {
              icon: Notebook,
              name: "Stationery",
              description: "Notes & organization",
            },
            {
              icon: Calculator,
              name: "Electronics",
              description: "Calculators & gadgets",
            },
            {
              icon: Backpack,
              name: "Accessories",
              description: "Bags & student gear",
            },
          ].map(({ icon: Icon, name, description }) => (
            <div
              key={name}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Icon className="h-8 w-8 text-blue-600 dark:text-blue-400 mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {name}
              </h4>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {description}
              </p>
              <a
                href="#"
                className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline"
              >
                Browse <ChevronRight className="h-4 w-4 ml-1" />
              </a>
            </div>
          ))}
        </div>
      </div>

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
            {featuredProducts.slice(0, 4).map((product) => (
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
            {trendingProducts.slice(0, 4).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* Call to Action */}
      <section className=" text-black py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Start Buying and Selling Today
          </h2>
          <p className="text-xl mb-8">
            Join thousands of students who have found their perfect academic
            resources.
          </p>
          <div className="flex justify-center space-x-4">
            {/* <Link href="/auth/signup">
              <Button size="lg" variant="secondary">
                Create Account
              </Button>
            </Link> */}
            <Link href="/product">
              <Button
                size="lg"
                variant="outline"
                className="text-black border-black"
              >
                Browse Marketplace
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
