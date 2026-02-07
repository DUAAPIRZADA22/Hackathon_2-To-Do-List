/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Enable SWC minification (default in Next.js 15, explicit for clarity)
  swcMinify: true,
  // Enable standalone output for Docker containerization
  output: 'standalone',
  // Reduce memory usage during development
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['recharts', 'sonner'],
  },
  // Optimize webpack caching for development
  webpack: (config, { dev, isServer }) => {
    if (dev) {
      // Reduce memory usage in development mode
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
        ignored: ['**/node_modules', '**/.git', '**/.next'],
      };
    }
    return config;
  },
}

module.exports = nextConfig
