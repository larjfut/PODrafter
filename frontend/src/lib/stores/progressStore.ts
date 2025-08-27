import { writable, derived } from 'svelte/store'
import type { AppState, WizardStep } from '$lib/types'
import { WIZARD_STEP_KEYS } from '$lib/constants'
import { petitionData } from './petitionStore'
import { validation } from './validationStore'
import { getCollectedFields, getNextSuggestedField } from '$lib/utils'

export const appState = writable<AppState>({ currentStep: 'chat', isLoading: false })

export const progress = derived([
  petitionData,
  validation
], ([$petitionData, $validation]) => {
  const fieldStatus = getCollectedFields($petitionData)
  const nextField = getNextSuggestedField($petitionData)
  return {
    completionPercentage: $validation.completionPercentage,
    fieldStatus,
    nextField,
    canReview: $validation.isValid
  }
})

export function goToStep(step: WizardStep) {
  appState.update(state => ({ ...state, currentStep: step }))
}

export function nextStep() {
  appState.update(state => {
    const idx = WIZARD_STEP_KEYS.indexOf(state.currentStep)
    const next = WIZARD_STEP_KEYS[idx + 1] ?? state.currentStep
    return { ...state, currentStep: next }
  })
}

export function prevStep() {
  appState.update(state => {
    const idx = WIZARD_STEP_KEYS.indexOf(state.currentStep)
    const prev = WIZARD_STEP_KEYS[idx - 1] ?? state.currentStep
    return { ...state, currentStep: prev }
  })
}
