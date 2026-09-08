import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Synchronous Docker operations can exceed Next.js's default proxy timeout.
  experimental: { proxyTimeout: 300_000 },
  async rewrites() {
    const backend = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
    return [{ source: "/api/v1/:path*", destination: `${backend}/api/v1/:path*` }];
  },
};

export default nextConfig;
