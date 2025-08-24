export function sanitizeBaseUrl(url: string): string {
  // Handle relative paths (like '/api')
  if (url.startsWith('/')) {
    return url.replace(/\/+$/, '')
  }

  // Handle absolute URLs
  try {
    const parsed = new URL(url)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      throw new Error(`unsupported protocol: ${parsed.protocol}`)
    }
    return url.replace(/\/+$/, '')
  } catch (error) {
    throw new Error(`Invalid URL: ${url}`)
  }
}
