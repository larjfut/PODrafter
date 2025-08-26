import { writable } from 'svelte/store'
import type { PetitionData, ChatMessage } from '$lib/types'

export const petitionData = writable<PetitionData>({
  county: 'General',
  petitioner_full_name: '',
  respondent_full_name: ''
})

export const chatMessages = writable<ChatMessage[]>([])

export const pdfUrl = writable<string | null>(null)
