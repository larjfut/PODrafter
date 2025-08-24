import { describe, it, expect } from 'vitest'
import { sanitizeBaseUrl } from '../src/lib/sanitizeBaseUrl'

describe('sanitizeBaseUrl', () => {
  it('baseUrl values with or without trailing slash match', () => {
    const noSlash = sanitizeBaseUrl('https://api.example.com')
    const withSlash = sanitizeBaseUrl('https://api.example.com/')
    expect(withSlash).toBe(noSlash)
  })

  it('allows http and https protocols', () => {
    expect(sanitizeBaseUrl('http://api.example.com/')).toBe('http://api.example.com')
    expect(sanitizeBaseUrl('https://api.example.com/')).toBe('https://api.example.com')
  })

  it('handles relative paths', () => {
    expect(sanitizeBaseUrl('/api')).toBe('/api')
    expect(sanitizeBaseUrl('/api/')).toBe('/api')
    expect(sanitizeBaseUrl('/api/v1/')).toBe('/api/v1')
  })

  it('throws on unsupported protocol', () => {
    expect(() => sanitizeBaseUrl('ftp://api.example.com')).toThrow()
  })

  it('throws on invalid URL format', () => {
    expect(() => sanitizeBaseUrl('not-a-url')).toThrow()
  })
})
