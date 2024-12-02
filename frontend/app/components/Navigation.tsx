import React from 'react';
import Link from 'next/link';

const Navigation: React.FC = () => {
  const currentPath = window.location.pathname; // Get the current path
  return (
    <nav>
      <ul>
        <li>
          <Link href="/">Home</Link>
        </li>
        <li>
          <Link href="/products">Products</Link>
        </li>
        <li>
          <Link href="/marketplace">Marketplace</Link>
        </li>
        <li>
          <Link href="/orders">Orders</Link>
        </li>
        <li>
          <Link href="/wishlist">Wishlist</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;
