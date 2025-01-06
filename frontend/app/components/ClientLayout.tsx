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
      {/*  */}
    </AppBar>
  );
}