import React from 'react';
import { useAppContext } from '../AppContext';
import { Typography, List, ListItem, ListItemText, ListItemSecondaryAction, IconButton, Button, Box, Avatar } from '@mui/material';
import { Delete, ShoppingCart } from '@mui/icons-material';
import Layout from '../layout';
import { Product } from '../../lib/types';

export default function WishlistPage() {
  const { wishlist, removeFromWishlist, addToCart } = useAppContext();

  const handleAddToCart = (item: Product) => {
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
          {wishlist.map((item: Product) => (
            <ListItem key={item.id} alignItems="flex-start">
              <Avatar 
                src={item.image_url} 
                alt={item.title}
                variant="rounded"
                sx={{ width: 80, height: 80, mr: 2 }}
              />
              <ListItemText
                primary={item.title}
                secondary={
                  <React.Fragment>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      ${item.price.toFixed(2)}
                    </Typography>
                    {` — ${item.description.substring(0, 100)}...`}
                  </React.Fragment>
                }
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