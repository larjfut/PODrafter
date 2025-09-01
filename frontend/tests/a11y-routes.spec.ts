import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const routes = ['/welcome', '/guide', '/review', '/completion']

for (const path of routes) {
  test(`axe passes on ${path}`, async ({ page }) => {
    await page.goto(path)
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
    if (results.violations.length) console.error('AXE violations on', path, results.violations)
    expect(results.violations).toEqual([])
  })
}
