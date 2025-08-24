export function sanitizeBaseUrl(url: string): string {
  const protocol = new URL(url).protocol
  if (protocol !== 'http:' && protocol !== 'https:') {
    throw new Error(`unsupported protocol: ${protocol}`)
  }
  return url.replace(/\/+$/, '')
}
