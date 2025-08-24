import { test, expect } from '@playwright/test'
import { sanitizeBaseUrl } from '../src/lib/sanitizeBaseUrl'

test('baseUrl values with or without trailing slash match', () => {
  const noSlash = sanitizeBaseUrl('https://api.example.com')
  const withSlash = sanitizeBaseUrl('https://api.example.com/')
  expect(withSlash).toBe(noSlash)
})

test('allows http and https protocols', () => {
  expect(sanitizeBaseUrl('http://api.example.com/')).toBe('http://api.example.com')
  expect(sanitizeBaseUrl('https://api.example.com/')).toBe('https://api.example.com')
})

test('throws on unsupported protocol', () => {
  expect(() => sanitizeBaseUrl('ftp://api.example.com')).toThrow()
})
