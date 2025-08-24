import { defineConfig } from '@playwright/test'

const frontendPort = Number(process.env.FRONTEND_PORT) || 5173

export default defineConfig({
  webServer: {
    command: 'npm run dev',
    port: frontendPort,
    timeout: 120 * 1000,
    reuseExistingServer: true,
    env: { FRONTEND_PORT: String(frontendPort) },
  },
  testDir: 'tests',
  use: {
    baseURL: `http://localhost:${frontendPort}`,
  },
})
