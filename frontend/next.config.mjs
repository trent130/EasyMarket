/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add webpack configuration
  webpack: (config, { dev }) => {
    // Disable caching in development to prevent corruption issues
    if (dev) {
      config.cache = false;
    }

    // Replace punycode with a modern alternative
    config.resolve.fallback = {
      ...config.resolve.fallback,
      punycode: false,
    };

    return config;
  },
  // Suppress deprecation warnings in production
  reactStrictMode: true,
  // Recommended for performance
  swcMinify: true,
  // Configure image domains
  images: {
    domains: process.env.IMAGE_DOMAINS?.split(',') || ['localhost']
  },

    // Configure on-demand entries
    onDemandEntries: {
      // Adjust to increase time before entries are disposed
      maxInactiveAge: 60 * 1000, // 60 seconds
    },
};

export default nextConfig;