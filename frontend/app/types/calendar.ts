export interface CalendarEvent {
    id: string;
    title: string;
    description: string;
    date: Date;
    type: string; // e.g., "product_launch", "sale", etc.
    productId?: string; // Optional field for product-specific events
  }
  