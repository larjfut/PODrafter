import { describe, it, expect, beforeEach } from 'vitest'
import { get } from 'svelte/store'
import { appState, nextStep, prevStep, goToStep } from '../src/lib/stores'

describe('wizard navigation', () => {
  beforeEach(() => {
    appState.set({ currentStep: 'chat', isLoading: false })
  })

  it('moves forward through steps and stops at last', () => {
    expect(get(appState).currentStep).toBe('chat')
    nextStep()
    expect(get(appState).currentStep).toBe('review')
    nextStep()
    expect(get(appState).currentStep).toBe('generate')
    nextStep()
    expect(get(appState).currentStep).toBe('download')
    nextStep()
    expect(get(appState).currentStep).toBe('download')
  })

  it('moves backward through steps and stops at first', () => {
    goToStep('download')
    expect(get(appState).currentStep).toBe('download')
    prevStep()
    expect(get(appState).currentStep).toBe('generate')
    prevStep()
    expect(get(appState).currentStep).toBe('review')
    prevStep()
    expect(get(appState).currentStep).toBe('chat')
    prevStep()
    expect(get(appState).currentStep).toBe('chat')
  })

  it('goToStep sets specified step', () => {
    goToStep('generate')
    expect(get(appState).currentStep).toBe('generate')
  })
})

