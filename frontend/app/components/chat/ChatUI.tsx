// app/components/chat/ChatUI.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, Paper } from '@mui/material';

interface ChatUIProps {
  productId: number | string | undefined;
  sellerId: number | string;
  productName: string;
}

export default function ChatUI({ 
  productId, 
  sellerId, 
  productName 
}: ChatUIProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');

  interface Message {
    text: string;
    sender: 'buyer' | 'seller';
    timestamp: string;
  }

  useEffect(() => {
    // Fetch previous messages for this specific product-seller conversation
    const savedMessages = localStorage.getItem(`chat_${productId}_${sellerId}`);
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, [productId, sellerId]);

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;

    const message: Message = {
      text: newMessage,
      sender: 'buyer',
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, message];
    setMessages(updatedMessages);
    setNewMessage('');

    // Save to local storage
    localStorage.setItem(
      `chat_${productId}_${sellerId}`, 
      JSON.stringify(updatedMessages)
    );

    // Optional: Send message to backend
    try {
      await sendMessageToSeller(message);
    } catch (error) {
      console.error('Failed to send message', error);
    }
  };

  const sendMessageToSeller = async (message: Message) => {
    // Implement API call to send message to seller
    // This would be your actual backend endpoint
    await fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        productId,
        sellerId,
        message: message.text
      })
    });
  };

  return (
    <Paper elevation={3} sx={{ width: 300, maxHeight: 400, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h6">Chat about {productName}</Typography>
      </Box>
      
      <Box sx={{ 
        flexGrow: 1, 
        overflowY: 'auto', 
        p: 2 
      }}>
        {messages.map((msg, index) => (
          <Box 
            key={index} 
            sx={{ 
              textAlign: msg.sender === 'buyer' ? 'right' : 'left',
              mb: 1 
            }}
          >
            <Typography 
              variant="body2"
              sx={{ 
                display: 'inline-block',
                bgcolor: msg.sender === 'buyer' ? 'primary.light' : 'grey.300',
                color: msg.sender === 'buyer' ? 'white' : 'black',
                p: 1,
                borderRadius: 2 
              }}
            >
              {msg.text}
            </Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ p: 2, borderTop: '1px solid', display: 'flex' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type a message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          sx={{ mr: 1 }}
        />
        <Button 
          variant="contained" 
          onClick={handleSendMessage}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
}