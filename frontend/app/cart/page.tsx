'use client';

import React from 'react';
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Box,
  Divider,
  Grid,
  Card,
  CardContent,
  CardActions,
  Snackbar,
} from '@mui/material';
import { useAppContext } from '../AppContext';

export default function CartPage() {
  const { cart, removeFromCart } = useAppContext();

  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const [openSnackbar, setOpenSnackbar] = React.useState(false);
  const [snackbarMessage, setSnackbarMessage] = React.useState('');

  const handleRemoveFromCart = (productId: number) => {
  removeFromCart(productId);
  setSnackbarMessage('Item removed from cart');
  setOpenSnackbar(true);
};

   

  const handleCloseSnackbar = (event: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  return (
    <div className="cart-page lg:mt-20">
      <Typography variant="h4" gutterBottom>
        Your Shopping Cart
      </Typography>
      {cart.length === 0 ? (
        <Typography variant="h6" sx={{ mt: 2 }}>
          Your cart is empty
        </Typography>
      ) : (
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <List>
                  {cart.map((item) => (
                    <React.Fragment key={item.id}>
                      <ListItem>
                        <ListItemText
                          primary={item.name}
                          secondary={`Quantity: ${item.quantity} - ${(item.price * item.quantity).toFixed(2)}`}
                        />
                        <Button onClick={() => handleRemoveFromCart(item.id)} color="secondary">
                          Remove
                        </Button>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
              <CardActions>
                <Box sx={{ mt: 2, textAlign: 'right' }}>
                  <Typography variant="h6">
                    Total: ${totalPrice.toFixed(2)}
                  </Typography>
                  <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                    Proceed to Checkout
                  </Button>
                </Box>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Order Summary
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Subtotal" secondary={`${totalPrice.toFixed(2)}`} />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Tax (8%)" secondary={`${(totalPrice * 0.08).toFixed(2)}`} />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Total" secondary={`${(totalPrice * 1.08).toFixed(2)}`} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
        action={
          <Button
            color="secondary"
            size="small"
            onClick={(event) => handleCloseSnackbar(event, 'someReason')}
          >
            Close
          </Button>
        }
      />
    </div>
  );
}
