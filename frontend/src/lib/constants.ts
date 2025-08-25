import { sanitizeBaseUrl } from './sanitizeBaseUrl'
import type { PetitionData, WizardStep } from './types'

export const API_BASE_URL = sanitizeBaseUrl(
  import.meta.env.PUBLIC_API_BASE_URL ?? '/api'
)

export const CHAT_API_KEY = import.meta.env.PUBLIC_CHAT_API_KEY

export const WIZARD_STEPS: { step: WizardStep, title: string }[] = [
  { step: 'chat', title: 'Tell Your Story' },
  { step: 'review', title: 'Review Details' },
  { step: 'generate', title: 'Create Document' },
  { step: 'download', title: 'Download' }
]

export const WIZARD_STEP_KEYS: WizardStep[] = WIZARD_STEPS.map(({ step }) => step)

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

export const FIELD_DESCRIPTIONS: Record<keyof PetitionData, string> = {
  county: 'Which Texas county will you file in?',
  case_no: 'Leave blank - court will assign',
  hearing_date: 'Court will schedule this',
  petitioner_full_name: 'Your legal name as it appears on ID',
  petitioner_address: 'Where you can receive mail safely',
  petitioner_phone: 'Best number to reach you',
  petitioner_email: 'Email for court notifications',
  respondent_full_name:
    'Full legal name of the person you need protection from',
  firearm_surrender: 'Should they surrender any firearms?'
}

export const REQUIRED_FIELDS: (keyof PetitionData)[] = [
  'county',
  'petitioner_full_name',
  'respondent_full_name'
]

export const SYSTEM_PROMPT = `You are a compassionate legal assistant helping someone draft a protective order petition. Ask trauma-informed questions one at a time in a respectful, logical order. Collect required fields such as petitioner_full_name, respondent_full_name, and county. When you learn any petition information, call the set_petition_data function with the fields. Explain briefly why each detail is needed and respond with empathy.`
