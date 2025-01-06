'use client';

import React from 'react';
import { useAppContext } from '../AppContext';
import { Typography, List, ListItem, ListItemText, ListItemSecondaryAction, IconButton, Button } from '@mui/material';
import { Delete, ShoppingCart } from '@mui/icons-material';
import Layout from '../layout';

export default function WishlistPage() {
  const { wishlist, removeFromWishlist, addToCart } = useAppContext();

  const handleAddToCart = (item) => {
    addToCart(item);
    removeFromWishlist(item.id);
  };

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom>
        Wishlist
      </Typography>
      {wishlist.length === 0 ? (
        <Typography>Your wishlist is empty.</Typography>
      ) : (
        <List>
          {wishlist.map((item) => (
            <ListItem key={item.id}>
              <ListItemText
                primary={item.name}
                secondary={`$${item.price.toFixed(2)}`}
              />
              <ListItemSecondaryAction>
                <IconButton 
                  edge="end" 
                  aria-label="add to cart" 
                  onClick={() => handleAddToCart(item)} 
                  sx={{ mr: 1 }}
                >
                  <ShoppingCart />
                </IconButton>
                <IconButton 
                  edge="end" 
                  aria-label="delete" 
                  onClick={() => removeFromWishlist(item.id)}
                >
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Layout>
  );
}