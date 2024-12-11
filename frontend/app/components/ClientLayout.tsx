'use client';

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useSession, signIn, signOut } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar'; // Assuming you have a SearchBar component

export default function ClientLayout() {
  const { data: session } = useSession();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={Link} href="/" sx={{ flexGrow: 1, color: 'white', textDecoration: 'none' }}>
          EasyMarket
        </Typography>
        
        {/* Search Bar */}
        <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
          <SearchBar />
        </Box>

        {/* User Authentication Buttons */}
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
      </Toolbar>
    </AppBar>
  );
}