import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('kitchen sink page has no axe violations', async ({ page }) => {
  await page.goto('/design/kitchen-sink')
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze()
  if (results.violations.length) {
    console.error('AXE violations:', results.violations)
  }
  expect(results.violations).toEqual([])
})
