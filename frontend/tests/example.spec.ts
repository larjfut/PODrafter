import { test, expect } from '@playwright/test'

test('home page has title', async ({ page }) => {
  await page.goto('http://localhost:5173/')
  await expect(page.locator('h1')).toHaveText('PO Drafter Chat Wizard')
})
