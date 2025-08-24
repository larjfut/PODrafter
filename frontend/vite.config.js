// Vite configuration for the SvelteKit frontend
// - sets dev server port and API proxy
// - documents build and alias settings

import { sveltekit } from '@sveltejs/kit/vite'

const backendPort = process.env.BACKEND_PORT ?? 8080
const frontendPort = Number(process.env.FRONTEND_PORT) || 5173

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit()],
  server: {
    port: frontendPort,
    proxy: {
      // proxy API requests to the backend server
      '/api': `http://localhost:${backendPort}`,
    },
  },
  resolve: {
    alias: {
      // allow importing from the project root with $src/
      $src: '/src',
    },
  },
  build: {
    // generate sourcemaps to aid in debugging
    sourcemap: true,
  },
}

export default config
