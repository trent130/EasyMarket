
'use client';

import React from 'react';
import { useSearchParams } from 'next/navigation';
import { Typography, Grid, Card, CardContent, CardMedia, Button, Box } from '@mui/material';
import { ShoppingCart, Favorite } from '@mui/icons-material';
import Layout from '../../components/Layout';
import { useAppContext } from '../AppContext';
import Link from 'next/link';

// Mock product data (in a real app, this would come from an API or database)
const products = [
  { id: 1, name: 'Textbook Bundle', price: 150, image: 'https://placehold.co/200x300?text=Textbook+Bundle', description: 'A comprehensive bundle of textbooks for your courses.' },
  { id: 2, name: 'Laptop', price: 800, image: 'https://placehold.co/200x300?text=Laptop', description: 'A powerful laptop for all your study needs.' },
  { id: 3, name: 'Backpack', price: 40, image: 'https://placehold.co/200x300?text=Backpack', description: 'A durable backpack to carry all your essentials.' },
  { id: 4, name: 'Scientific Calculator', price: 20, image: 'https://placehold.co/200x300?text=Calculator', description: 'An advanced calculator for complex calculations.' },
  { id: 5, name: 'Desk Lamp', price: 25, image: 'https://placehold.co/200x300?text=Desk+Lamp', description: 'A versatile lamp for late-night study sessions.' },
  { id: 6, name: 'Notebook Set', price: 15, image: 'https://placehold.co/200x300?text=Notebook+Set', description: 'A set of high-quality notebooks for all your classes.' },
];

export default function SearchPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q');
  const { addToCart, addToWishlist } = useAppContext();

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(query.toLowerCase()) ||
    product.description.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Search Results for "{query}"
      </Typography>
      {filteredProducts.length === 0 ? (
        <Typography>No products found matching your search.</Typography>
      ) : (
        <Grid container spacing={4}>
          {filteredProducts.map((product) => (
            <Grid item key={product.id} xs={12} sm={6} md={4}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image={product.image}
                  alt={product.name}
                />
                <CardContent>
                  <Typography gutterBottom variant="h5" component="div">
                    {product.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {product.description}
                  </Typography>
                  <Typography variant="h6" color="primary" gutterBottom>
                    ${product.price.toFixed(2)}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<ShoppingCart />}
                      onClick={() => addToCart(product)}
                      sx={{ mr: 1 }}
                    >
                      Add to Cart
                    </Button>
                    <Button
                      variant="outlined"
                      color="secondary"
                      startIcon={<Favorite />}
                      onClick={() => addToWishlist(product)}
                    >
                      Wishlist
                    </Button>
                  </Box>
                  <Button component={Link} href={`/products/${product.id}`} sx={{ mt: 1 }}>
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Layout>
  );
}
