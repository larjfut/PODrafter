<script lang="ts">
  import { petitionData, appState, prevStep, nextStep } from '$lib/stores'
  import {
    FIELD_LABELS,
    FIELD_DESCRIPTIONS,
    REQUIRED_FIELDS
  } from '$lib/constants'
  import { validatePetition } from '$lib/utils'
  import { get } from 'svelte/store'
  import type { PetitionData } from '$lib/types'
  import Tooltip from './ui/Tooltip.svelte'

  const fieldEntries: [keyof PetitionData, string][] = Object.entries(
    FIELD_LABELS
  ) as [keyof PetitionData, string][]

  function handleReviewNext() {
    const validation = validatePetition(get(petitionData))
    if (validation.isValid) {
      appState.update(s => ({ ...s, error: undefined }))
      nextStep()
    } else {
      appState.update(s => ({ ...s, error: 'Please complete required fields' }))
    }
  }
</script>

<div class="mb-4">
  <h2 class="text-xl font-semibold mb-2">Review Details</h2>
  <p class="mb-4">
    Confirm the information below. Required fields are marked with an asterisk
    (*)
  </p>
  {#each fieldEntries as [field, label]}
    <div class="mb-2">
      <label
        class="font-bold flex items-center gap-1"
        for={`${field}-input`}
      >
        {label}
        {#if REQUIRED_FIELDS.includes(field)}
          <Tooltip content="Required field">
            <span class="text-red-500" aria-hidden="true">*</span>
          </Tooltip>
        {/if}
        <Tooltip content={FIELD_DESCRIPTIONS[field]}>
          <button type="button" class="text-gray-500 focus:outline-none">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              class="w-4 h-4"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm1 8a1 1 0 100-2h-1V9a1 1 0 00-1-1H9a1 1 0 100 2h1v3H9a1 1 0 100 2h3z"
                clip-rule="evenodd"
              />
            </svg>
            <span class="sr-only">Info about {label}</span>
          </button>
        </Tooltip>
      </label>
      <input
        id={`${field}-input`}
        class="w-full border p-2 rounded"
        value={$petitionData[field] ?? ''}
        on:input={(e) =>
          petitionData.update(d => ({
            ...d,
            [field]: (e.target as HTMLInputElement).value
          }))
        }
      />
    </div>
  {/each}
</div>
<div class="flex gap-2">
  <button class="bg-gray-200 px-3 py-1 rounded" on:click={prevStep}>
    Back
  </button>
  <button
    class="bg-blue-500 text-white px-3 py-1 rounded"
    on:click={handleReviewNext}
  >
    Generate
  </button>
</div>

