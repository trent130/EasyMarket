import React from 'react';
import ProductList from '../src/components/ProductList';

const HomePage: React.FC = () => {
  return (
    <div>
      <h1>Welcome to the Marketplace</h1>
      <ProductList />
    </div>
  );
};

export default HomePage;
