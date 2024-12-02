
'use client';

import React from 'react';
import { Typography, List, ListItem, ListItemText, Button, Box, Divider } from '@mui/material';
import Layout from '../../components/Layout';
import { useAppContext } from '../AppContext';

export default function CartPage() {
  const { cart, removeFromCart } = useAppContext();

  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleRemoveFromCart = (productId) => {
    removeFromCart(productId);
    // TODO: Add a toast notification for better user feedback
  };

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Your Shopping Cart
      </Typography>
      {cart.length === 0 ? (
        <Typography>Your cart is empty</Typography>
      ) : (
        <>
          <List>
            {cart.map((item) => (
              <React.Fragment key={item.id}>
                <ListItem>
                  <ListItemText
                    primary={item.name}
                    secondary={`Quantity: ${item.quantity} - $${(item.price * item.quantity).toFixed(2)}`}
                  />
                  <Button onClick={() => handleRemoveFromCart(item.id)} color="secondary">
                    Remove
                  </Button>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
          <Box sx={{ mt: 2, textAlign: 'right' }}>
            <Typography variant="h6">
              Total: ${totalPrice.toFixed(2)}
            </Typography>
            <Button variant="contained" color="primary" sx={{ mt: 2 }}>
              Proceed to Checkout
            </Button>
          </Box>
        </>
      )}
    </Layout>
  );
}
