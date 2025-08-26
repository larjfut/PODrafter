// Core petition data matching JSON schema exactly
export interface PetitionData {
  county: 'Harris' | 'Dallas' | 'Travis' | 'General'
  case_no?: string
  hearing_date?: string // YYYY-MM-DD format
  petitioner_full_name: string
  petitioner_address?: string
  petitioner_phone?: string
  petitioner_email?: string
  respondent_full_name: string
  firearm_surrender?: boolean
}

// Chat system interfaces
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  id: string
}

// App state management
export type WizardStep = 'chat' | 'review' | 'generate' | 'download'

export interface AppState {
  currentStep: WizardStep
  isLoading: boolean
  error?: string
}

// API response types
export interface ChatResponseMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface PetitionUpsert extends Partial<PetitionData> {
  source_msg_id: string
  confidence: number
}

export interface ChatResponse {
  messages: ChatResponseMessage[]
  upserts: PetitionUpsert[]
}

export interface PDFResponse {
  success: boolean
  fileUrl?: string
  revoke?: () => void
  error?: string
}

// Form validation
export interface ValidationError {
  field: keyof PetitionData
  message: string
}

export interface ValidationResult {
  isValid: boolean
  errors: ValidationError[]
  completionPercentage: number
}
