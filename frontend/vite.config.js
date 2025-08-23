// Vite configuration for the SvelteKit frontend
// - sets dev server port and API proxy
// - documents build and alias settings

import { sveltekit } from '@sveltejs/kit/vite'

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit()],
  server: {
    port: 5173,
    proxy: {
      // proxy API requests to the backend server
      '/api': 'http://localhost:3000',
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

