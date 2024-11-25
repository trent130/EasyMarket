
'use client';

import React, { useState } from 'react';
import { Typography, TextField, Button, Grid, Card, CardContent, CardActions } from '@mui/material';
import Layout from '../../components/Layout';

// Mock data for listed textbooks (in a real app, this would come from a database)
const initialTextbooks = [
  { id: 1, title: 'Introduction to Psychology', author: 'John Smith', condition: 'Good', price: 30, contact: 'john@example.com' },
  { id: 2, title: 'Calculus: Early Transcendentals', author: 'James Stewart', condition: 'Like New', price: 50, contact: 'sarah@example.com' },
];

export default function TextbookExchange() {
  const [textbooks, setTextbooks] = useState(initialTextbooks);
  const [newTextbook, setNewTextbook] = useState({ title: '', author: '', condition: '', price: '', contact: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTextbook({ ...newTextbook, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const textbookToAdd = {
      ...newTextbook,
      id: textbooks.length + 1,
      price: parseFloat(newTextbook.price)
    };
    setTextbooks([...textbooks, textbookToAdd]);
    setNewTextbook({ title: '', author: '', condition: '', price: '', contact: '' });
  };

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Textbook Exchange
      </Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            List a Textbook
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Title"
              name="title"
              value={newTextbook.title}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Author"
              name="author"
              value={newTextbook.author}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Condition"
              name="condition"
              value={newTextbook.condition}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Price"
              name="price"
              type="number"
              value={newTextbook.price}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Contact Email"
              name="contact"
              type="email"
              value={newTextbook.contact}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
              List Textbook
            </Button>
          </form>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Available Textbooks
          </Typography>
          <Grid container spacing={2}>
            {textbooks.map((textbook) => (
              <Grid item xs={12} key={textbook.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{textbook.title}</Typography>
                    <Typography variant="body2">Author: {textbook.author}</Typography>
                    <Typography variant="body2">Condition: {textbook.condition}</Typography>
                    <Typography variant="body2">Price: ${textbook.price}</Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" href={`mailto:${textbook.contact}`}>
                      Contact Seller
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Layout>
  );
}
