export function sanitizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, '')
}
