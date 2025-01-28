import { useState } from 'react';
import { Box, Typography } from '@mui/material';
import { useSession, signOut, signIn } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar';
import NotificationPopup from './NotificationPopup';
// import { getSession } from '@/utils/sessionManager'

const Navigation = () => {
  const { data: session } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };
 /*  const [isLoggedIn, setIsLoggedIn] = useState(false);

  React.useEffect(() => {
    const token = localStorage.getItem('authToken');

    if (token) {
      /* signIn('credentials', {
        token,
        callbackUrl: window.location.href,
      }); 
      setIsLoggedIn(true);
    }
  }, []); */

  return (
    <nav className="fixed top-0 left-0 w-full text-black bg-white shadow-lg border-gray-200 p-4 z-50 px-4 mb-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        <Typography
          variant="h6"
          component={Link}
          href="/"
          className="text-lg font-bold hover:text-gray-800"
        >
          EasyMarket
        </Typography>

        {/* Search Bar */}
        <div className="hidden  md:hidden flex-1 mx-[5%]">
          <SearchBar />
        </div>

        {/* Hamburger Menu */}
        <button aria-label='Menu'
          className="md:hidden text-black hover:bg-black hover:rounded hover:text-white focus:outline-none"
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
        <div className="hidden md:flex items-center space-x-4 text-black">
          <Link href="/">
            <button className="bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300">
              Home
            </button>
          </Link>
          <Link href="/product">
            <button className="bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300">
              Products
            </button>
          </Link>
          <Link href="/textbook-exchange">
            <button className="bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300">
              Dashboard
            </button>
          </Link>
          <Link href="/cart">
            <button type='button' className="relative bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300" aria-label='Cart'>
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
            <button type="button" aria-label='Wishlist' className="relative bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300">
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
          <NotificationPopup />
          {session ? (
            <div className="flex items-center">
              <Typography variant="body1" className="mr-2">
                Welcome, 
                <a href="/user/profile">{session.user?.name}</a>
              </Typography>
              <button
                className="bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300"
                onClick={() => signOut()}
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              className="bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4 rounded duration-300"
              onClick={() => signIn()}
            >
              Sign In
            </button>
          )}
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {menuOpen && (
        <div className="md:hidden bg-white text-black hover:text-black py-4">
          <Link href="/">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4">
              Home
            </button>
          </Link>
          <Link href="/product">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white  font-bold py-2 px-4">
              Products
            </button>
          </Link>
          <Link href="/textbook-exchange">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4">
              Textbook Exchange
            </button>
          </Link>
          <Link href="/cart">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4">
              Cart
            </button>
          </Link>
          <Link href="/wishlist">
            <button className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4">
              Wishlist
            </button>
          </Link>
          <NotificationPopup />
          {session /* && isLogggedIn */? (
            <button
              className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4"
              onClick={() => signOut()}
            >
              Logout
            </button>
          ) : (
            <button
              className="block w-full text-left bg-transparent hover:bg-gray-700 hover:text-white font-bold py-2 px-4"
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


// fix the notification dusplay on mobile devices to stop being and icon and just be a word notifications