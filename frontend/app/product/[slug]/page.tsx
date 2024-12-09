'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { 
  Box, 
  Container, 
  Grid, 
  Typography, 
  Rating, 
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
// import { fetchProductBySlug } from '../../../lib/api-client';
import type { Product } from '../../types/product';
import { productsApi } from '../../services/api/productsApi';
import { isValidSlug } from '../../utils/validation';

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

/**
 * A single review card component.
 * 
 * @prop {string} reviewer_name The name of the reviewer.
 * @prop {string} created_at The date the review was left.
 * @prop {number} rating The rating given by the reviewer (on a scale of 1-5).
 * @prop {string} comment The comment left by the reviewer.
 * @returns A single review card component.
 */
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

/**
 * Renders the product detail page for a specific product.
 *
 * This component fetches and displays detailed information about a product
 * based on the slug obtained from the URL parameters. It includes product
 * image, title, price, description, condition, stock status, seller
 * information, available variants, and statistics such as total sales,
 * revenue, views, and rating. It also shows recent reviews for the product.
 * If the product details are loading or if there is an error in fetching the
 * product, appropriate messages are displayed.
 *
 * @return {React.ReactElement} The JSX element for the product detail page.
 */
export default function ProductDetail() {
  const params = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
/**
 * Fetches detailed information about a product using the product slug 
 * from URL parameters. Updates the product state with the fetched data. 
 * If the operation fails, sets an error message. 
 * Updates the loading state accordingly.
 */
  const loadProduct = async () => {
    const slug = params.slug;
    try {
      if (typeof params.slug === 'string' && isValidSlug(slug)) {
        try {
          const data = await productsApi.getProductDetails(params.slug);
          setProduct(data);
        } catch (error) {
          // More specific error handling
          if (error.response?.status === 404) {
            setError('Product not found');
          } else {
            setError('Failed to load product details');
          }
        }
      }
    } catch (error) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  loadProduct();
  }, [params.slug]);

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
