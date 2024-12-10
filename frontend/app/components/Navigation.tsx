// Navigation.js
import { Box, Button as MUIButton, Toolbar, Typography } from '@mui/material';
import { useSession, signOut, signIn } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar';
import LogoutButton from './ui/LogoutButton';

export default function Navigation() {
  const { data: session } = useSession();

  return (
    <div className="relative z-10 p-6">
        <nav className="bg-gray-800 text-white p-4 fixed top-0 left-0 right-0">
      <Toolbar>
        <Typography
          variant="h6"
          component={Link}
          href="/"
          style={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}
        >
          EasyMarket
        </Typography>
        <SearchBar />
        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
          <MUIButton color="inherit" component={Link} href="/">
            Home
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/product">
            Products
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/textbook-exchange">
            Textbook Exchange
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/cart">
            Cart
          </MUIButton>
          <MUIButton color="inherit" component={Link} href="/wishlist">
            Wishlist
          </MUIButton>
          {session ? (
            <>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Welcome, {session.user?.name}
              </Typography>
              <a onClick={() => signOut()}>
                <LogoutButton/>
              </a>
              
            </>
          ) : (
            <MUIButton color="inherit" onClick={() => signIn()}>
              Sign In
            </MUIButton>
          )}
        </Box>
      </Toolbar>
    </nav>
    </div>
  );
}
