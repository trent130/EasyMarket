"use client";

import React, { useState } from 'react';
import { Container, Fab } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import ChatUI from './chat/ChatUI';
import ClientLayout from './ClientLayout';
import DashboardLayout from './DashboardLayout';
import { SidebarProvider } from './ui/sidebar';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <>
      <ClientLayout />
      <Container maxWidth={false} style={{ marginTop: '2rem', marginBottom: '5rem', position: 'relative', padding: 0 }}>
        <>
          <>
            {children} {/* This will render the specific page content */}
          </>
        </>
      </Container>
      <Fab 
        color="primary" 
        aria-label="chat"
        style={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setIsChatOpen(!isChatOpen)}
      >
        <ChatIcon />
      </Fab>
      {isChatOpen && (
        <div style={{ position: 'fixed', bottom: 80, right: 16, zIndex: 1000 }}>
          <ChatUI productId={''} sellerId={''} productName={''} />
        </div>
      )}
    </>
  );
}