/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: '/AGenNext-Kernel',
  assetPrefix: '/AGenNext-Kernel/',
}

module.exports = nextConfig