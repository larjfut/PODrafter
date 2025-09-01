import { test, expect } from '@playwright/test'

test('kitchen sink renders and command menu toggles', async ({ page }) => {
  await page.goto('/design/kitchen-sink')
  await expect(page.getByRole('heading', { level: 1, name: /design system/i })).toBeVisible()
  const primary = page.getByRole('button', { name: /primary cta/i })
  await expect(primary).toBeVisible()
  // Command menu opens with keyboard
  await page.keyboard.down(process.platform === 'darwin' ? 'Meta' : 'Control')
  await page.keyboard.press('KeyK')
  await page.keyboard.up(process.platform === 'darwin' ? 'Meta' : 'Control')
  await expect(page.getByRole('dialog', { name: /command menu/i })).toBeVisible()
})
