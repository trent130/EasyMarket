'use client'

import React, { useEffect, useState } from 'react';
import { fetchProducts } from '../services/api';

/**
 * A component that displays a list of products.
 *
 * On initial load, the component fetches a list of products from the API and
 * displays them in a list. If the API request fails, the component displays
 * an error message. If the request is still in progress, the component displays
 * a "Loading..." message.
 *
 * @return {React.ReactElement} The component.
 */
const ProductList: React.FC = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    /**
     * Fetches a list of products from the API and updates the state with the
     * results. If the API request fails, the component displays an error
     * message. If the request is still in progress, the component displays a
     * "Loading..." message.
     */
    const loadProducts = async () => {
      try {
        const data = await fetchProducts();
        setProducts(data);
      } catch (err) {
        setError('Failed to fetch products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Product List</h1>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <h2>{product.title}</h2>
            <p>{product.description}</p>
            <p>Price: ${product.price}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductList;
