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

    const messages: ChatMessage[] = [
      { role: 'user', content: 'hi', timestamp: new Date(), id: 'm1' },
    ]
    const promise = sendChat(messages, 10)
    vi.runAllTimers()
    await expect(promise).rejects.toThrow(/aborted/)
    expect(fetchMock).toHaveBeenCalled()

    global.fetch = originalFetch
    vi.useRealTimers()
  })

  it('returns ChatResponse with messages and upserts', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [
            { role: 'user', content: 'hi' },
            { role: 'assistant', content: 'hello' },
          ],
          upserts: [{ county: 'Harris', source_msg_id: 'm1', confidence: 0.9 }],
        }),
    })
    global.fetch = fetchMock as any
    const messages: ChatMessage[] = [
      { role: 'user', content: 'hi', timestamp: new Date(), id: 'm1' },
    ]
    const resp = await sendChat(messages)
    expect(resp.messages[1].content).toBe('hello')
    expect(resp.upserts[0].county).toBe('Harris')
    global.fetch = originalFetch
  })
})
