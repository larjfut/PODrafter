import type {
  ChatMessage,
  ChatResponse,
  PetitionData,
  PDFResponse,
  ValidationError,
  ValidationResult,
} from './types'
import { API_BASE_URL, REQUIRED_FIELDS, CHAT_API_KEY } from './constants'

export async function sendChat(
  messages: ChatMessage[],
  timeoutMs = 10000,
): Promise<ChatResponse> {
  const payload = {
    messages: messages.map((m) => ({ role: m.role, content: m.content })),
  }
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(CHAT_API_KEY ? { 'X-API-Key': CHAT_API_KEY } : {}),
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(`Chat request failed: ${res.status} ${text}`)
    }
    const json = (await res.json()) as ChatResponse
    return json
  } catch (err) {
    throw err
  } finally {
    clearTimeout(timer)
  }
}

export async function generatePDF(data: PetitionData): Promise<PDFResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) return { success: false, error: `Status ${res.status}` }
    const blob = await res.blob()
    const fileUrl = URL.createObjectURL(blob)
    const revoke = () => URL.revokeObjectURL(fileUrl)
    return { success: true, fileUrl, revoke }
  } catch (err) {
    return { success: false, error: (err as Error).message }
  }
}

export function getCollectedFields(data: PetitionData): {
  collected: (keyof PetitionData)[]
  missing: (keyof PetitionData)[]
  requiredMissing: (keyof PetitionData)[]
} {
  const allFields = Object.keys(data) as (keyof PetitionData)[]
  const collected = allFields.filter((field) => {
    const value = data[field]
    return value !== undefined && value !== null && value !== ''
  })
  const missing = allFields.filter((field) => !collected.includes(field))
  const requiredMissing = REQUIRED_FIELDS.filter(
    (field) => !collected.includes(field),
  )
  return { collected, missing, requiredMissing }
}

export function getNextSuggestedField(
  data: PetitionData,
): keyof PetitionData | null {
  const { collected } = getCollectedFields(data)
  const priorityOrder: (keyof PetitionData)[] = [
    'county',
    'petitioner_full_name',
    'respondent_full_name',
    'petitioner_address',
    'petitioner_phone',
    'petitioner_email',
  ]
  for (const field of priorityOrder) {
    if (!collected.includes(field)) return field
  }
  return null
}

export function canProceedToReview(data: PetitionData): boolean {
  const validation = validatePetition(data)
  return validation.isValid
}

export function validatePetition(data: PetitionData): ValidationResult {
  const { collected, requiredMissing } = getCollectedFields(data)
  const errors: ValidationError[] = requiredMissing.map((field) => ({
    field,
    message: `${field} is required`,
  }))
  const completionPercentage = Math.round(
    (collected.length / Object.keys(data).length) * 100,
  )
  return {
    isValid: errors.length === 0,
    errors,
    completionPercentage,
  }
}
