/** @type {import('next').NextConfig} */
const nextConfig = {
  // Self-contained production server (.next/standalone) — small image, runs
  // with `node server.js`, no source bind-mounts or dev compile in Docker.
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "i.scdn.co" },
      { protocol: "https", hostname: "mosaic.scdn.co" },
    ],
  },
};

export default nextConfig;
