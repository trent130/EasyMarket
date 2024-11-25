
import React from 'react';
import Layout from '../components/Layout';
import { Typography, Grid, Card, CardContent, CardMedia, Button, Box } from '@mui/material';
import Link from 'next/link';

// Sample product data (in a real app, this would come from a database)
const products = [
  { id: 1, name: 'Textbook Bundle', price: 150, image: 'https://placehold.co/200x300?text=Textbook+Bundle' },
  { id: 2, name: 'Laptop', price: 800, image: 'https://placehold.co/200x300?text=Laptop' },
  { id: 3, name: 'Backpack', price: 40, image: 'https://placehold.co/200x300?text=Backpack' },
  { id: 4, name: 'Scientific Calculator', price: 20, image: 'https://placehold.co/200x300?text=Calculator' },
];

export default function Home() {
  return (
    <Layout>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to Student Marketplace
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          Your one-stop shop for all your academic needs!
        </Typography>
      </Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Featured Products
        </Typography>
        <Grid container spacing={4}>
          {products.map((product) => (
            <Grid item key={product.id} xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardMedia
                  component="img"
                  height="200"
                  image={product.image}
                  alt={product.name}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h6" component="div">
                    {product.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ${product.price.toFixed(2)}
                  </Typography>
                </CardContent>
                <Button component={Link} href={`/products/${product.id}`} sx={{ m: 2 }}>
                  View Details
                </Button>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          New Feature: Textbook Exchange
        </Typography>
        <Typography variant="body1" paragraph>
          Save money on textbooks by using our new Textbook Exchange feature! Buy, sell, or trade textbooks with other students.
        </Typography>
        <Button component={Link} href="/textbook-exchange" variant="contained" color="primary">
          Go to Textbook Exchange
        </Button>
      </Box>
    </Layout>
  );
}
