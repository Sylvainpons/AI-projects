import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*", // Si le front appelle /api/chat...
        destination: "http://127.0.0.1:8000/api/:path*", // ...Next.js transfère vers FastAPI
      },
    ];
  },
};

export default nextConfig;