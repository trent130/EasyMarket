// Navigation.js
import { Box, Button as MUIButton, Toolbar, Typography } from '@mui/material';
import { useSession, signOut, signIn } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar';
import LogoutButton from './ui/LogoutButton';
import styled from 'styled-components';

export default function Navigation() {
  const { data: session } = useSession();

  return (
    <div className="relative z-10 p-6">
        <nav className="bg-gray-800 text-white p-4 fixed top-0 left-0 right-0">
      <Toolbar>
        <Typography
          variant="h6"
          component={Link}
          href="/"
          style={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}
        >
          EasyMarket
        </Typography>
        <SearchBar />
        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
          <MUIButton color="inherit" component={Link} href="/">
            Home
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/product">
            Products
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/textbook-exchange">
            Textbook Exchange
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/cart">
          <div className="relative cursor-pointer">
            <svg
              className="w-8 h-8 transform transition-transform duration-300 hover:-rotate-15"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M7 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-2h14v2H7v-2zm-2-4h2l.75-3H20c.7 0 1.2-.7 1-1.4l-2-7C18.9 0 18.5 0 18 0H6C5.5 0 5.1.3 5 1L2 8c-.3.7.1 1.4.9 1.4h2z"
                fill="#000"
              />
            </svg>
            <span className="absolute top-0 right-0 bg-green-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              
            </span>
          </div>

          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/wishlist">
          <div className="relative cursor-pointer group">
            <svg
              className="w-8 h-8 text-red-500 transform transition-transform duration-300 group-hover:scale-110"
              viewBox="0 0 24 24"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
              />
            </svg>
            <span
              className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full translate-x-1/2 -translate-y-1/2"
            >
              
            </span>
          </div>

          </MUIButton>
          {session ? (
            <>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Welcome, {session.user?.name}
              </Typography>
              <a onClick={() => signOut()}>
                <LogoutButton/>
              </a>
              
            </>
          ) : (
            <MUIButton color="inherit" onClick={() => signIn()}>
              Sign In
            </MUIButton>
          )}
        </Box>
      </Toolbar>
    </nav>
    </div>
  );
}
