import { derived } from 'svelte/store'
import { petitionData } from './petitionStore'
import { validatePetition } from '$lib/utils'
import type { ValidationResult } from '$lib/types'

export const validation = derived<typeof petitionData, ValidationResult>(petitionData, $petitionData =>
  validatePetition($petitionData)
)
