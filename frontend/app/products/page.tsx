
'use client';

import React from 'react';
import Layout from '../../components/Layout';
import { Typography } from '@mui/material';

export default function Products() {
  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom>
        Products Page
      </Typography>
      <Typography variant="body1">
        This is where we'll display all available products.
      </Typography>
    </Layout>
  );
}
