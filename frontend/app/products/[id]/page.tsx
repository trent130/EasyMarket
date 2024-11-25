
'use client';

import React from 'react';
import { useRouter } from 'next/router';
import { Typography, Card, CardContent, CardMedia, Button, Box, Grid } from '@mui/material';
import { ShoppingCart, Favorite } from '@mui/icons-material';
import Layout from '../../../components/Layout';
import ChatUI from '../../../components/chat/ChatUI';
import { useAppContext } from '../../AppContext';

// Mock product data (in a real app, this would come from an API or database)
const products = [
  { id: 1, name: 'Textbook Bundle', price: 150, image: 'https://placehold.co/200x300?text=Textbook+Bundle', description: 'A comprehensive bundle of textbooks for your courses.' },
  { id: 2, name: 'Laptop', price: 800, image: 'https://placehold.co/200x300?text=Laptop', description: 'A powerful laptop for all your study needs.' },
  { id: 3, name: 'Backpack', price: 40, image: 'https://placehold.co/200x300?text=Backpack', description: 'A durable backpack to carry all your essentials.' },
  { id: 4, name: 'Scientific Calculator', price: 20, image: 'https://placehold.co/200x300?text=Calculator', description: 'An advanced calculator for complex calculations.' },
  { id: 5, name: 'Desk Lamp', price: 25, image: 'https://placehold.co/200x300?text=Desk+Lamp', description: 'A versatile lamp for late-night study sessions.' },
  { id: 6, name: 'Notebook Set', price: 15, image: 'https://placehold.co/200x300?text=Notebook+Set', description: 'A set of high-quality notebooks for all your classes.' },
];

export default function ProductPage({ params }) {
  const router = useRouter();
  const { addToCart, addToWishlist } = useAppContext();
  const product = products.find(p => p.id === parseInt(params.id));

  if (!product) {
    return <Typography variant="h4">Product not found</Typography>;
  }

  const handleAddToCart = () => {
    addToCart(product);
    // TODO: Add a toast notification for better user feedback
  };

  const handleAddToWishlist = () => {
    addToWishlist(product);
    // TODO: Add a toast notification for better user feedback
  };

  return (
    <Layout>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardMedia
              component="img"
              height="400"
              image={product.image}
              alt={product.name}
            />
            <CardContent>
              <Typography gutterBottom variant="h4" component="div">
                {product.name}
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                {product.description}
              </Typography>
              <Typography variant="h6" color="primary" gutterBottom>
                ${product.price.toFixed(2)}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Button variant="contained" color="primary" startIcon={<ShoppingCart />} onClick={handleAddToCart} sx={{ mr: 2 }}>
                  Add to Cart
                </Button>
                <Button variant="outlined" color="secondary" startIcon={<Favorite />} onClick={handleAddToWishlist}>
                  Add to Wishlist
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <ChatUI productId={product.id} />
        </Grid>
      </Grid>
    </Layout>
  );
}
