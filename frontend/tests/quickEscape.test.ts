import { render, fireEvent } from '@testing-library/svelte'
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { get } from 'svelte/store'
import AppLayout from '../src/lib/components/AppLayout.svelte'
import { chatMessages, petitionData, pdfUrl, appState } from '../src/lib/stores'

const defaultPetition = {
  county: 'General',
  petitioner_full_name: '',
  respondent_full_name: ''
}

const originalLocation = window.location

describe('quickEscape', () => {
  beforeEach(() => {
    chatMessages.set([{ role: 'user', content: 'hi' }])
    petitionData.set({
      county: 'Test',
      petitioner_full_name: 'A',
      respondent_full_name: 'B'
    })
    pdfUrl.set('http://example.com')
    appState.set({ currentStep: 'download', isLoading: true })
    localStorage.setItem('foo', 'bar')
    sessionStorage.setItem('baz', 'qux')
    Object.defineProperty(window, 'location', { writable: true, value: { href: '' } })
  })

  afterEach(() => {
    Object.defineProperty(window, 'location', { writable: true, value: originalLocation })
    localStorage.clear()
    sessionStorage.clear()
  })

  it('clears all client-side data', async () => {
    const { getByText } = render(AppLayout)
    await fireEvent.click(getByText('Quick Escape'))

    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)
    expect(get(chatMessages)).toEqual([])
    expect(get(petitionData)).toEqual(defaultPetition)
    expect(get(pdfUrl)).toBeNull()
    expect(get(appState)).toEqual({ currentStep: 'chat', isLoading: false })
  })
})
