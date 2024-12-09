import { Box, Button, Toolbar, Typography } from '@mui/material';
import { useSession, signOut, signIn } from 'next-auth/react';
import Link from 'next/link';
import SearchBar from './search/SearchBar';

export default function Navigation() {
  const { data: session } = useSession();

  return (
    <nav className="bg-gray-800 text-white p-4">
      <Toolbar>
        <Typography variant="h6" component={Link} href="/" style={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
          EasyMarket
        </Typography>
        <SearchBar />
        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
	        <Button color="inherit" component={Link} href="/">Home</Button>
          <Button color="inherit" component={Link} href="/product">
            Products
          </Button>
          <Button color="inherit" component={Link} href="/textbook-exchange">
            Textbook Exchange
          </Button>
          <Button color="inherit" component={Link} href="/cart">
            Cart
          </Button>
          <Button color="inherit" component={Link} href="/wishlist">
            Wishlist
          </Button>
          {session ? (
            <>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Welcome, {session.user?.name}
              </Typography>
              <Button color="inherit" onClick={() => signOut()}>
                Sign Out
              </Button>
            </>
          ) : (
            <Button color="inherit" onClick={() => signIn()}>
              Sign In
            </Button>
          )}
        </Box>
      </Toolbar>
    </nav>
  );
}
