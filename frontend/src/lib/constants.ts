import { sanitizeBaseUrl } from './sanitizeBaseUrl'
import type { PetitionData, WizardStep } from './types'

export const API_BASE_URL = sanitizeBaseUrl(
  import.meta.env.PUBLIC_API_BASE_URL ?? '/api'
)

export const WIZARD_STEPS: WizardStep[] = [
  'chat',
  'review',
  'generate',
  'download'
]

export const FIELD_LABELS: Record<keyof PetitionData, string> = {
  county: 'County',
  case_no: 'Case Number',
  hearing_date: 'Hearing Date',
  petitioner_full_name: 'Petitioner Full Name',
  petitioner_address: 'Petitioner Address',
  petitioner_phone: 'Petitioner Phone',
  petitioner_email: 'Petitioner Email',
  respondent_full_name: 'Respondent Full Name',
  firearm_surrender: 'Firearm Surrender'
}

export const REQUIRED_FIELDS: (keyof PetitionData)[] = [
  'county',
  'petitioner_full_name',
  'respondent_full_name'
]

export const SYSTEM_PROMPT = `You are a compassionate legal assistant helping someone draft a protective order petition. Ask trauma-informed questions in a respectful, logical order. Collect required fields such as petitioner_full_name, respondent_full_name, and county. When you learn any petition information, call the set_petition_data function with the fields. Offer brief legal context and respond with empathy.`
