<script lang="ts">
  import { petitionData } from '$lib/stores/petitionStore'
  import { appState, prevStep, nextStep } from '$lib/stores/progressStore'
  import { validation } from '$lib/stores/validationStore'
  import { FIELD_LABELS } from '$lib/constants'
  import { get } from 'svelte/store'
  import type { PetitionData } from '$lib/types'

  const fieldEntries: [keyof PetitionData, string][] = Object.entries(
    FIELD_LABELS
  ) as [keyof PetitionData, string][]

  function handleReviewNext() {
    const v = get(validation)
    if (v.isValid) {
      appState.update(s => ({ ...s, error: undefined }))
      nextStep()
    } else {
      appState.update(s => ({ ...s, error: 'Please complete required fields' }))
    }
  }
</script>

<div class="mb-4">
  {#each fieldEntries as [field, label]}
    <div class="mb-2">
      <label class="font-bold" for={`${field}-input`}>{label}</label>
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

