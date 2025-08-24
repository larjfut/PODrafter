import type { PetitionData, ValidationResult } from './types'
import { sanitizeBaseUrl } from './sanitizeBaseUrl'

export async function callChatAPI(messages: any[]): Promise<any> {
  const baseUrl = sanitizeBaseUrl(
    (import.meta as any).env.PUBLIC_API_BASE_URL ?? '/api',
  )
  const url = `${baseUrl}/chat`

  const apiKey = (import.meta as any).env.PUBLIC_CHAT_API_KEY
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(apiKey ? { 'X-API-Key': apiKey } : {}),
    },
    body: JSON.stringify({ messages }),
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}

export function validatePetitionData(
  data: Partial<PetitionData>,
): ValidationResult {
  const errors: ValidationResult['errors'] = []

  if (!data.petitioner_full_name) {
    errors.push({
      field: 'petitioner_full_name',
      message: 'Your full name is required',
    })
  }

  if (!data.respondent_full_name) {
    errors.push({
      field: 'respondent_full_name',
      message: 'Respondent full name is required',
    })
  }

  if (data.petitioner_email && !isValidEmail(data.petitioner_email)) {
    errors.push({
      field: 'petitioner_email',
      message: 'Please enter a valid email address',
    })
  }

  const totalRequiredFields = 2 // petitioner_full_name, respondent_full_name
  const completedRequiredFields = [
    data.petitioner_full_name,
    data.respondent_full_name,
  ].filter(Boolean).length

  const completionPercentage = Math.round(
    (completedRequiredFields / totalRequiredFields) * 100,
  )

  return {
    isValid: errors.length === 0,
    errors,
    completionPercentage,
  }
}

function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function saveToLocalStorage(key: string, data: any): void {
  if (typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (error) {
      console.warn('Failed to save to localStorage:', error)
    }
  }
}

export function loadFromLocalStorage<T>(key: string, fallback: T): T {
  if (typeof localStorage !== 'undefined') {
    try {
      const stored = localStorage.getItem(key)
      return stored ? JSON.parse(stored) : fallback
    } catch (error) {
      console.warn('Failed to load from localStorage:', error)
    }
  }
  return fallback
}
