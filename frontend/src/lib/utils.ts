import type {
  ChatMessage,
  ChatResponse,
  PetitionData,
  PDFResponse,
  ValidationError,
  ValidationResult
} from './types'
import { API_BASE_URL, REQUIRED_FIELDS, SYSTEM_PROMPT } from './constants'

export async function sendChat(
  messages: ChatMessage[]
): Promise<ChatResponse> {
  const payload = {
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      ...messages.map(m => ({ role: m.role, content: m.content }))
    ]
  }
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`)
  return res.json()
}

export async function generatePDF(
  data: PetitionData
): Promise<PDFResponse> {
  const res = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) return { success: false, error: `Status ${res.status}` }
  return res.json()
}

export function validatePetition(
  data: PetitionData
): ValidationResult {
  const errors: ValidationError[] = []
  for (const field of REQUIRED_FIELDS) {
    if (!data[field]) {
      errors.push({ field, message: `${field} is required` })
    }
  }
  const filled = Object.values(data).filter(v => v !== undefined && v !== '').length
  const completion = Math.round((filled / Object.keys(data).length) * 100)
  return {
    isValid: errors.length === 0,
    errors,
    completionPercentage: completion
  }
}
