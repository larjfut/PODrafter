import type { WizardStep, PetitionData } from './types'

export const COUNTIES = ['Harris', 'Dallas', 'Travis', 'General'] as const

export const WIZARD_STEPS: {
  step: WizardStep
  title: string
  description: string
}[] = [
  {
    step: 'chat',
    title: 'Information Gathering',
    description: 'Tell us about your situation',
  },
  {
    step: 'review',
    title: 'Review Details',
    description: 'Check and edit your information',
  },
  {
    step: 'generate',
    title: 'Generate Documents',
    description: 'Create your legal documents',
  },
  {
    step: 'download',
    title: 'Download & File',
    description: 'Get your completed packet',
  },
]

export const FIELD_LABELS: Record<keyof PetitionData, string> = {
  county: 'County',
  case_no: 'Case Number',
  hearing_date: 'Hearing Date',
  petitioner_full_name: 'Your Full Name',
  petitioner_address: 'Your Address',
  petitioner_phone: 'Your Phone Number',
  petitioner_email: 'Your Email Address',
  respondent_full_name: 'Respondent Full Name',
  firearm_surrender: 'Firearm Surrender Required',
}

export const API_ENDPOINTS = {
  CHAT: '/api/chat',
  PDF: '/pdf',
} as const
