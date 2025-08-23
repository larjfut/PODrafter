import { test, expect } from '@playwright/test'
import { sanitizeBaseUrl } from '../src/lib/sanitizeBaseUrl'

test('baseUrl values with or without trailing slash match', () => {
  const noSlash = sanitizeBaseUrl('https://api.example.com')
  const withSlash = sanitizeBaseUrl('https://api.example.com/')
  expect(withSlash).toBe(noSlash)
})
