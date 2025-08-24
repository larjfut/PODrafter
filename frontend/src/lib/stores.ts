import { writable, derived } from 'svelte/store'
import type {
  PetitionData,
  AppState,
  ChatMessage,
  ValidationResult,
} from './types'

export const petitionData = writable<Partial<PetitionData>>({})

export const appState = writable<AppState>({
  currentStep: 'chat',
  isLoading: false,
  error: undefined,
})

export const chatHistory = writable<ChatMessage[]>([])

export const validationStatus = derived(
  petitionData,
  ($petitionData): ValidationResult => {
    const errors: ValidationResult['errors'] = []

    if (!$petitionData.petitioner_full_name) {
      errors.push({
        field: 'petitioner_full_name',
        message: 'Your full name is required',
      })
    }

    if (!$petitionData.respondent_full_name) {
      errors.push({
        field: 'respondent_full_name',
        message: 'Respondent full name is required',
      })
    }

    const totalFields = 9 // Total number of petition fields
    const completedFields = Object.keys($petitionData).length
    const completionPercentage = Math.round(
      (completedFields / totalFields) * 100,
    )

    return {
      isValid:
        errors.length === 0 &&
        !!$petitionData.petitioner_full_name &&
        !!$petitionData.respondent_full_name,
      errors,
      completionPercentage,
    }
  },
)

export function quickEscape() {
  petitionData.set({})
  chatHistory.set([])
  appState.set({ currentStep: 'chat', isLoading: false })

  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem('po-drafter-data')
    localStorage.removeItem('po-drafter-chat')
  }

  window.location.href = 'https://weather.com'
}
