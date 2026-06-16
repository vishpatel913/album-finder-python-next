var _a;
import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
// The dev server proxies /api -> the FastAPI backend, so the browser only ever
// talks to the Vite origin. No CORS to configure, and it mirrors how you'd
// reverse-proxy in a real deploy.
//   - Running Vite on the host  -> backend is on localhost:8004 (compose port map)
//   - Running Vite in compose   -> backend is the `api` service on :8000
// Override with VITE_PROXY_TARGET (the compose `web` service sets it).
var proxyTarget = (_a = process.env.VITE_PROXY_TARGET) !== null && _a !== void 0 ? _a : 'http://localhost:8004';
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: { '@': path.resolve(__dirname, './src') },
    },
    server: {
        host: true,
        port: 5173,
        // usePolling keeps HMR reliable when the source is bind-mounted into Docker.
        watch: { usePolling: true },
        proxy: {
            '/api': {
                target: proxyTarget,
                changeOrigin: true,
                rewrite: function (p) { return p.replace(/^\/api/, ''); },
            },
        },
    },
});
