/**
 * Format price with currency symbol and decimal places
 */
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'KSH',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
};

/**
 * Calculate final price including variant adjustments
 */
export const calculateFinalPrice = (basePrice: number, adjustment: number = 0): number => {
  return basePrice + adjustment;
};

/**
 * Format date to local string
 */
export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format rating to display with one decimal place
 */
export const formatRating = (rating: number): string => {
  return rating.toFixed(1);
};

/**
 * Format stock status message
 */
export const getStockStatus = (availableStock: number): { color: string; message: string } => {
  if (availableStock > 10) {
    return { color: 'success', message: 'In Stock' };
  } else if (availableStock > 0) {
    return { color: 'warning', message: `Only ${availableStock} left` };
  }
  return { color: 'error', message: 'Out of Stock' };
};

/**
 * Get condition display text and color
 */
export const getConditionInfo = (condition: string): { label: string; color: string } => {
  const conditionMap: Record<string, { label: string; color: string }> = {
    new: { label: 'New', color: 'success' },
    like_new: { label: 'Like New', color: 'primary' },
    good: { label: 'Good', color: 'info' },
    fair: { label: 'Fair', color: 'warning' },
  };
  return conditionMap[condition] || { label: condition, color: 'default' };
};

/**
 * Format large numbers with K/M suffix
 */
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

/**
 * Calculate discount percentage
 */
export const calculateDiscount = (originalPrice: number, currentPrice: number): number => {
  if (originalPrice <= 0 || currentPrice >= originalPrice) return 0;
  return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Generate product URL
 */
export const getProductUrl = (slug: string): string => {
  return `/products/api/products/${slug}/`;
};

/**
 * Sort products by different criteria
 */
export const sortProducts = <T extends { price: number; created_at: string; average_rating: number }>(
  products: T[],
  sortBy: 'price_asc' | 'price_desc' | 'newest' | 'rating'
): T[] => {
  const sortedProducts = [...products];
  
  switch (sortBy) {
    case 'price_asc':
      return sortedProducts.sort((a, b) => a.price - b.price);
    case 'price_desc':
      return sortedProducts.sort((a, b) => b.price - a.price);
    case 'newest':
      return sortedProducts.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    case 'rating':
      return sortedProducts.sort((a, b) => b.average_rating - a.average_rating);
    default:
      return sortedProducts;
  }
};

/**
 * Conditional class name concatenation
 */
export const cn = (...classes: string[]) => {
  return classes.filter(Boolean).join(' ');
};
