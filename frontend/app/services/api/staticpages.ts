import apiClient from '../api-client';

export interface StaticPage {
  id: number;
  title: string;
  slug: string;
  content: string;
  meta_description: string;
  is_published: boolean;
  updated_at: string;
}

export interface FAQ {
  id: number;
  question: string;
  answer: string;
  category: string;
  order: number;
  is_published: boolean;
}

export interface FAQCategory {
  category: string;
  faqs: FAQ[];
}

export interface ContactMessage {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface Testimonial {
  id: number;
  student: {
    id: number;
    name: string;
    avatar?: string;
  };
  content: string;
  rating: number;
  is_featured: boolean;
  created_at: string;
}

export interface SiteSettings {
  site_name: string;
  site_description: string;
  contact_email: string;
  contact_phone: string;
  social_links?: Record<string, string>;
  maintenance_mode: boolean;
}

export interface MetaTags {
  title: string;
  description: string;
  keywords?: string[];
  og_title?: string;
  og_description?: string;
  og_image?: string;
  twitter_card?: 'summary' | 'summary_large_image';
}

export const staticPagesApi = {
  // Static Pages
  getPage: async (slug: string) => {
    const response = await apiClient.get<StaticPage>(`/api/pages/${slug}/`);
    return response.data;
  },

  getHomePage: async () => {
    const response = await apiClient.get<StaticPage>('/api/pages/home/');
    return response.data;
  },

  getPageMeta: async (slug: string) => {
    const response = await apiClient.get<MetaTags>(`/api/pages/${slug}/meta/`);
    return response.data;
  },

  // FAQs
  getAllFAQs: async () => {
    const response = await apiClient.get<FAQ[]>('/api/faqs/');
    return response.data;
  },

  getFAQsByCategory: async () => {
    const response = await apiClient.get<FAQCategory[]>('/api/faqs/categories/');
    return response.data;
  },

  searchFAQs: async (query: string) => {
    const response = await apiClient.get<FAQ[]>('/api/faqs/search/', {
      params: { q: query }
    });
    return response.data;
  },

  // Contact
  sendContactMessage: async (data: ContactMessage) => {
    const response = await apiClient.post('/api/contact/', data);
    return response.data;
  },

  // Testimonials
  getTestimonials: async () => {
    const response = await apiClient.get<Testimonial[]>('/api/testimonials/');
    return response.data;
  },

  getFeaturedTestimonials: async () => {
    const response = await apiClient.get<Testimonial[]>('/api/testimonials/featured/');
    return response.data;
  },

  addTestimonial: async (data: Omit<Testimonial, 'id' | 'student' | 'created_at' | 'is_featured'>) => {
    const response = await apiClient.post<Testimonial>('/api/testimonials/', data);
    return response.data;
  },

  // Site Settings
  getSiteSettings: async () => {
    const response = await apiClient.get<SiteSettings>('/api/settings/');
    return response.data;
  },

  // Newsletter
  subscribeNewsletter: async (email: string, name?: string) => {
    const response = await apiClient.post('/api/newsletter/subscribe/', {
      email,
      name
    });
    return response.data;
  },

  // Feedback
  submitFeedback: async (data: {
    type: 'bug' | 'feature' | 'content' | 'other';
    subject: string;
    description: string;
    screenshot?: File;
  }) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await apiClient.post('/api/feedback/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // SEO
  getSitemap: async () => {
    const response = await apiClient.get('/api/seo/sitemap/');
    return response.data;
  },

  getRobots: async () => {
    const response = await apiClient.get('/api/seo/robots/');
    return response.data;
  },

  getMetaTags: async () => {
    const response = await apiClient.get<MetaTags>('/api/seo/meta-tags/');
    return response.data;
  },

  // Analytics
  getPageViews: async (slug: string) => {
    const response = await apiClient.get(`/api/analytics/page-views/`, {
      params: { slug }
    });
    return response.data;
  },

  getPopularPages: async () => {
    const response = await apiClient.get('/api/analytics/popular-pages/');
    return response.data;
  }
};
