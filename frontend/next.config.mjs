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
};

export default nextConfig;
