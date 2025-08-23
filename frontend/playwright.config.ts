import { defineConfig } from '@playwright/test'

export default defineConfig({
  webServer: {
    command: 'npm run dev',
    port: 5173,
    timeout: 120 * 1000,
    reuseExistingServer: true,
  },
  testDir: 'tests',
  use: {
    baseURL: 'http://localhost:5173',
  },
})
