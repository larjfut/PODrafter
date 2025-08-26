import { describe, it, expect, vi } from 'vitest'
import type { PetitionData } from '../src/lib/types'

const originalFetch = global.fetch

describe('generatePDF', () => {
  it('returns success when X-API-Key header present', async () => {
    vi.stubEnv('PUBLIC_CHAT_API_KEY', 'test-key')
    const { generatePDF } = await import('../src/lib/utils')

    const fetchMock = vi.fn().mockImplementation((_url, options: any) => {
      if (options.headers['X-API-Key'] === 'test-key') {
        return Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(new Blob(['pdf'])),
        })
      }
      return Promise.resolve({ ok: false, status: 401 })
    })
    global.fetch = fetchMock as any

    const resp = await generatePDF({} as PetitionData)
    expect(resp.success).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({ 'X-API-Key': 'test-key' }),
      }),
    )

    global.fetch = originalFetch
    vi.unstubAllEnvs()
  })
})
