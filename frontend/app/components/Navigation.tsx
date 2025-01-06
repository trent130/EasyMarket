import { useState } from 'react';
import { Box, Typography } from '@mui/material';
import { useSession, signOut, signIn } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar';

const Navigation = () => {
  const { data: session } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        <Typography
          variant="h6"
          component={Link}
          href="/"
          className="text-lg font-bold"
        >
          EasyMarket
        </Typography>

        {/* Search Bar */}
        <div className="hidden md:block flex-1 mx-[5%]">
          <SearchBar />
        </div>

        {/* Hamburger Menu */}
        <button
          className="md:hidden text-white focus:outline-none"
          onClick={toggleMenu}
        >
          <svg
            className="w-6 h-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        {/* Desktop Navigation Links */}
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/">
            <button className="bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              Home
            </button>
          </Link>
          <Link href="/product">
            <button className="bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              Products
            </button>
          </Link>
          <Link href="/textbook-exchange">
            <button className="bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              Dashboard
            </button>
          </Link>
          <Link href="/cart">
            <button className="relative bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              <svg
                className="w-6 h-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 3h18l-2 9H5L3 3zm0 0h18v2H3V3zm7 18a2 2 0 11-4 0 2 2 0 014 0zm10-2a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </button>
          </Link>
          <Link href="/wishlist">
            <button className="relative bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              <svg
                className="w-6 h-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 016.364 0L12 7.682l1.318-1.364a4.5 4.5 0 016.364 6.364L12 21.682l-7.682-7.682a4.5 4.5 0 010-6.364z"
                />
              </svg>
            </button>
          </Link>
          {session ? (
            <div className="flex items-center">
              <Typography variant="body1" className="mr-2">
                Welcome, {session.user?.name}
              </Typography>
              <button
                className="bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                onClick={() => signOut()}
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              className="bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
              onClick={() => signIn()}
            >
              Sign In
            </button>
          )}
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {menuOpen && (
        <div className="md:hidden bg-gray-900 text-white py-4">
          <Link href="/">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4">
              Home
            </button>
          </Link>
          <Link href="/product">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4">
              Products
            </button>
          </Link>
          <Link href="/textbook-exchange">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4">
              Textbook Exchange
            </button>
          </Link>
          <Link href="/cart">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4">
              Cart
            </button>
          </Link>
          <Link href="/wishlist">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4">
              Wishlist
            </button>
          </Link>
          {session ? (
            <button
              className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4"
              onClick={() => signOut()}
            >
              Logout
            </button>
          ) : (
            <button
              className="block w-full text-left bg-transparent hover:bg-gray-700 text-white font-bold py-2 px-4"
              onClick={() => signIn()}
            >
              Sign In
            </button>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navigation;