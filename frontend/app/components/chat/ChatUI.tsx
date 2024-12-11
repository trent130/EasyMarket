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
    <Paper elevation={3} sx={{ width: 300, maxHeight: 400, display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
  <div className="max-w-md mx-auto bg-white dark:bg-zinc-800 shadow-md rounded-lg overflow-hidden">
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b dark:border-zinc-700">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-zinc-800 dark:text-white">
            <Box sx={{ p: 2, backgroundColor: 'bg.secondary', color: 'black', borderRadius: 1 }}>
              <Typography variant="h6">Chat about {productName}</Typography>
            </Box>
          </h2>
        </div>
      </div>
      <div className="flex-1 p-3 overflow-y-auto flex flex-col space-y-2" id="chatDisplay">
        <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
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
                  bgcolor: msg.sender === 'buyer' ? 'primary.main' : 'grey.300',
                  color: msg.sender === 'buyer' ? 'white' : 'black',
                  p: 1.5,
                  borderRadius: 2,
                  boxShadow: 1,
                }}
              >
                {msg.text}
              </Typography>
            </Box>
          ))}
        </Box>
      </div>
      <div className="px-3 py-2 border-t dark:border-zinc-700">
        <div className="flex">
          <TextField
            className='flex-1 p-2 border rounded-lg dark:bg-zinc-700 dark:text-white dark:border-zinc-600 text-sm'
            fullWidth
            variant="outlined"
            placeholder="Type a message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            sx={{ mr: 1 }}
          />
          <button 
            onClick={handleSendMessage} 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1.5 px-3 rounded-lg transition duration-300 ease-in-out text-sm"
            id="sendButton"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</Paper>

  );
}



