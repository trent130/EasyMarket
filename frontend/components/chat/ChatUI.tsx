
'use client';

import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, Paper } from '@mui/material';

export default function ChatUI({ productId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    // In a real app, we would fetch previous messages from a backend
    const savedMessages = localStorage.getItem(`chat_${productId}`);
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, [productId]);

  const handleSendMessage = () => {
    if (newMessage.trim() !== '') {
      const updatedMessages = [
        ...messages,
        { text: newMessage, sender: 'buyer', timestamp: new Date().toISOString() }
      ];
      setMessages(updatedMessages);
      setNewMessage('');
      localStorage.setItem(`chat_${productId}`, JSON.stringify(updatedMessages));

      // Simulate seller response
      setTimeout(() => {
        const sellerResponse = {
          text: "Thank you for your message. How can I help you?",
          sender: 'seller',
          timestamp: new Date().toISOString()
        };
        const updatedMessagesWithResponse = [...updatedMessages, sellerResponse];
        setMessages(updatedMessagesWithResponse);
        localStorage.setItem(`chat_${productId}`, JSON.stringify(updatedMessagesWithResponse));
      }, 1000);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2, maxWidth: 400, margin: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Chat with Seller
      </Typography>
      <Box sx={{ height: 300, overflowY: 'auto', mb: 2, p: 1, border: '1px solid #e0e0e0' }}>
        {messages.map((message, index) => (
          <Box key={index} sx={{ mb: 1, textAlign: message.sender === 'buyer' ? 'right' : 'left' }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              {message.sender === 'buyer' ? 'You' : 'Seller'}:
            </Typography>
            <Typography variant="body1">{message.text}</Typography>
          </Box>
        ))}
      </Box>
      <Box sx={{ display: 'flex' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <Button variant="contained" onClick={handleSendMessage} sx={{ ml: 1 }}>
          Send
        </Button>
      </Box>
    </Paper>
  );
}
