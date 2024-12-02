'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  Typography, 
  Rating, 
  Chip, 
  Skeleton,
  IconButton,
  CardActionArea,
} from '@mui/material';
import { Favorite, FavoriteBorder } from '@mui/icons-material';
import { fetchProducts } from '../lib/api-client';
import { formatPrice, formatNumber, getConditionInfo, getStockStatus } from '../lib/utils';
import type { Product } from '../lib/types';

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  const [isWishlisted, setIsWishlisted] = useState(product.is_wishlisted);
  const { color: conditionColor, label: conditionLabel } = getConditionInfo(product.condition);
  const stockStatus = getStockStatus(product.available_stock);

  const handleWishlistClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsWishlisted(!isWishlisted);
    // TODO: Implement wishlist API call
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <Link href={`/products/${product.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
        <CardActionArea>
          <CardMedia
            component="img"
            height="200"
            image={product.image_url || '/placeholder.jpg'}
            alt={product.title}
            sx={{ objectFit: 'cover' }}
          />
          <CardContent sx={{ flexGrow: 1 }}>
            <Typography gutterBottom variant="h6" component="h2" noWrap>
              {product.title}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Rating 
                value={product.average_rating} 
                readOnly 
                size="small"
                precision={0.5}
              />
              <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                ({formatNumber(product.total_sales)} sold)
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary" noWrap>
              {product.description}
            </Typography>

            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" color="primary">
                {formatPrice(product.price)}
              </Typography>
              <Box>
                {product.has_variants && (
                  <Chip 
                    label="Multiple Options" 
                    size="small" 
                    color="info"
                    sx={{ mr: 1 }}
                  />
                )}
                <Chip 
                  label={conditionLabel}
                  size="small"
                  color={conditionColor as any}
                />
              </Box>
            </Box>

            <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {product.category_name}
              </Typography>
              <Chip 
                label={stockStatus.message}
                size="small"
                color={stockStatus.color as any}
              />
            </Box>
          </CardContent>
        </CardActionArea>
      </Link>
      <IconButton
        sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
        onClick={handleWishlistClick}
      >
        {isWishlisted ? <Favorite color="error" /> : <FavoriteBorder />}
      </IconButton>
    </Card>
  );
};

const LoadingSkeleton: React.FC = () => (
  <Card sx={{ height: '100%' }}>
    <Skeleton variant="rectangular" height={200} />
    <CardContent>
      <Skeleton variant="text" height={32} sx={{ mb: 1 }} />
      <Skeleton variant="text" width="60%" />
      <Skeleton variant="text" width="40%" />
      <Box sx={{ mt: 2 }}>
        <Skeleton variant="text" width="30%" />
      </Box>
    </CardContent>
  </Card>
);

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await fetchProducts();
        setProducts(data);
      } catch (err) {
        setError('Failed to fetch products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  if (error) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        {loading
          ? Array.from(new Array(8)).map((_, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                <LoadingSkeleton />
              </Grid>
            ))
          : products.map((product) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                <ProductCard product={product} />
              </Grid>
            ))}
      </Grid>
    </Box>
  );
};

export default ProductList;
