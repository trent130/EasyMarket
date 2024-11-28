'use client'

import React, { useEffect, useState } from 'react';
import { fetchProducts } from '../lib/api';
import { Card, CardContent, CardMedia, Typography, Grid, Box, Rating, Chip, Badge } from '@mui/material';
import { formatPrice } from '../lib/utils';

interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  price_adjustment: number;
  available_stock: number;
  final_price: number;
}

interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  image_url: string;
  category_name: string;
  average_rating: number;
  available_stock: number;
  has_variants: boolean;
  total_sales: number;
  condition: string;
  variants?: ProductVariant[];
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await fetchProducts();
        setProducts(data as Product[]);
      } catch (err) {
        setError('Failed to fetch products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
      <Typography>Loading products...</Typography>
    </Box>
  );
  
  if (error) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
      <Typography color="error">{error}</Typography>
    </Box>
  );

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        {products.map((product) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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
                    ({product.total_sales} sold)
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
                      label={product.condition}
                      size="small"
                      color={product.condition === 'new' ? 'success' : 'default'}
                    />
                  </Box>
                </Box>

                <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    {product.category_name}
                  </Typography>
                  <Badge 
                    color={product.available_stock > 0 ? 'success' : 'error'}
                    badgeContent={product.available_stock > 0 ? 'In Stock' : 'Out of Stock'}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ProductList;
