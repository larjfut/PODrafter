import { describe, it, expect, vi } from 'vitest'
import type { ChatMessage } from '../src/lib/types'
import { sendChat } from '../src/lib/utils'

const originalFetch = global.fetch

describe('sendChat', () => {
  it('aborts the request after timeout', async () => {
    vi.useFakeTimers()
    const fetchMock = vi.fn(
      (_url, options: any) =>
        new Promise((_resolve, reject) => {
          options.signal.addEventListener('abort', () =>
            reject(new Error('aborted')),
          )
        }),
    )
    global.fetch = fetchMock as any

    const messages: ChatMessage[] = [{ role: 'user', content: 'hi' }]
    const promise = sendChat(messages, 10)
    vi.runAllTimers()
    await expect(promise).rejects.toThrow(/aborted/)
    expect(fetchMock).toHaveBeenCalled()

    global.fetch = originalFetch
    vi.useRealTimers()
  })
})
