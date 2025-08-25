import { writable } from 'svelte/store'
import type {
  PetitionData,
  AppState,
  ChatMessage,
  WizardStep
} from './types'
import { WIZARD_STEP_KEYS } from './constants'

export const petitionData = writable<PetitionData>({
  county: 'General',
  petitioner_full_name: '',
  respondent_full_name: ''
})

export const chatMessages = writable<ChatMessage[]>([])

export const appState = writable<AppState>({
  currentStep: 'chat',
  isLoading: false
})

export const pdfUrl = writable<string | null>(null)

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
