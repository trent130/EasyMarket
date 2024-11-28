'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { 
  Box, 
  Container, 
  Grid, 
  Typography, 
  Rating, 
  Divider, 
  Chip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Alert,
} from '@mui/material';
import { 
  formatPrice, 
  formatDate, 
  formatNumber, 
  getConditionInfo,
  getStockStatus 
} from '../../../lib/utils';
import { fetchProductById } from '../../../lib/api-client';
import type { Product } from '../../../lib/types';

const ProductStatCard: React.FC<{
  title: string;
  value: string | number;
}> = ({ title, value }) => (
  <Grid item xs={6} sm={4} md={2}>
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">
          {title}
        </Typography>
        <Typography variant="h6">
          {value}
        </Typography>
      </CardContent>
    </Card>
  </Grid>
);

const ReviewCard: React.FC<{
  reviewer_name: string;
  created_at: string;
  rating: number;
  comment: string;
}> = ({ reviewer_name, created_at, rating, comment }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="subtitle2">
          {reviewer_name}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatDate(created_at)}
        </Typography>
      </Box>
      <Rating value={rating} size="small" readOnly />
      <Typography variant="body2" sx={{ mt: 1 }}>
        {comment}
      </Typography>
    </CardContent>
  </Card>
);

export default function ProductDetail() {
  const params = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        if (typeof params.id === 'string') {
          const data = await fetchProductById(parseInt(params.id));
          setProduct(data);
        }
      } catch (err) {
        setError('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [params.id]);

  if (loading) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography>Loading product details...</Typography>
      </Container>
    );
  }

  if (error || !product) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Product not found'}</Alert>
      </Container>
    );
  }

  const { color: conditionColor, label: conditionLabel } = getConditionInfo(product.condition);
  const stockStatus = getStockStatus(product.available_stock);

  return (
    <Container sx={{ py: 4 }}>
      <Grid container spacing={4}>
        {/* Product Image */}
        <Grid item xs={12} md={6}>
          <Box
            component="img"
            src={product.image_url || '/placeholder.jpg'}
            alt={product.title}
            sx={{
              width: '100%',
              height: 'auto',
              borderRadius: 2,
              boxShadow: 3,
            }}
          />
        </Grid>

        {/* Product Info */}
        <Grid item xs={12} md={6}>
          <Typography variant="h4" gutterBottom>
            {product.title}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Rating value={product.reviews.average} precision={0.5} readOnly />
            <Typography variant="body2" sx={{ ml: 1 }}>
              ({product.reviews.count} reviews)
            </Typography>
          </Box>

          <Typography variant="h5" color="primary" gutterBottom>
            {formatPrice(product.price)}
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Chip 
              label={conditionLabel} 
              color={conditionColor as any} 
            />
            <Chip 
              label={stockStatus.message}
              color={stockStatus.color as any}
            />
          </Box>

          <Typography variant="body1" paragraph>
            {product.description}
          </Typography>

          {/* Seller Info */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Seller Information
              </Typography>
              <Typography variant="body2">
                Seller: {product.student.username}
              </Typography>
              <Typography variant="body2">
                Rating: <Rating value={product.student.rating} size="small" readOnly />
              </Typography>
              <Typography variant="body2">
                Products: {product.student.products_count}
              </Typography>
              <Typography variant="body2">
                Member since: {formatDate(product.student.joined_date)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Product Variants */}
        {product.variants && product.variants.length > 0 && (
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Available Options
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Option</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell align="right">Price Adjustment</TableCell>
                  <TableCell align="right">Final Price</TableCell>
                  <TableCell align="right">Stock</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {product.variants.map((variant) => (
                  <TableRow key={variant.id}>
                    <TableCell>{variant.name}</TableCell>
                    <TableCell>{variant.sku}</TableCell>
                    <TableCell align="right">
                      {formatPrice(variant.price_adjustment)}
                    </TableCell>
                    <TableCell align="right">
                      {formatPrice(variant.final_price)}
                    </TableCell>
                    <TableCell align="right">
                      {variant.available_stock}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Grid>
        )}

        {/* Statistics */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Product Statistics
          </Typography>
          <Grid container spacing={2}>
            <ProductStatCard 
              title="Total Sales" 
              value={formatNumber(product.statistics.total_sales)} 
            />
            <ProductStatCard 
              title="Revenue" 
              value={formatPrice(product.statistics.total_revenue)} 
            />
            <ProductStatCard 
              title="Views" 
              value={formatNumber(product.statistics.views_count)} 
            />
            <ProductStatCard 
              title="Rating" 
              value={product.statistics.average_rating.toFixed(1)} 
            />
          </Grid>
        </Grid>

        {/* Reviews */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Recent Reviews
          </Typography>
          <Grid container spacing={2}>
            {product.reviews.recent.map((review) => (
              <Grid item xs={12} sm={6} md={4} key={review.id}>
                <ReviewCard {...review} />
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}
