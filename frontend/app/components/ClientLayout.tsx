
'use client';

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
// import Link from 'next/link';
import { useSession, signIn, signOut } from 'next-auth/react';
// import SearchBar from './search/SearchBar';

export default function ClientLayout() {
  const { data: session } = useSession();

  return (
    <AppBar position="static">
      
    </AppBar>
  );
}
