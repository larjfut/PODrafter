<script lang="ts">
  import { petitionData } from '$lib/stores'
  import { FIELD_DESCRIPTIONS, FIELD_LABELS } from '$lib/constants'
  import type { PetitionData } from '$lib/types'
  import {
    validatePetition,
    getCollectedFields,
    getNextSuggestedField
  } from '$lib/utils'
  import Tooltip from './ui/Tooltip.svelte'

  $: validation = validatePetition($petitionData)
  $: fieldStatus = getCollectedFields($petitionData)
  $: nextField = getNextSuggestedField($petitionData)
</script>

<aside class="mt-4 md:mt-0 md:w-64 border p-2 rounded text-sm">
  <p class="font-semibold mb-2">Progress</p>
  <div class="w-full bg-gray-200 h-2 rounded">
    <div
      class="bg-blue-500 h-2 rounded"
      style={`width: ${validation.completionPercentage}%`}
    ></div>
  </div>
  <p class="mt-1">{validation.completionPercentage}% complete</p>
  <ul class="mt-4 space-y-1">
    {#each Object.keys(FIELD_LABELS) as field}
      <li class="flex items-center gap-2">
        {#if fieldStatus.collected.includes(field as keyof PetitionData)}
          <span class="text-green-600">✔</span>
        {:else}
          <span class="text-gray-400">✖</span>
        {/if}
        <span class="flex items-center gap-1">
          {FIELD_LABELS[field as keyof PetitionData]}
          <Tooltip content={FIELD_DESCRIPTIONS[field as keyof PetitionData]}>
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
              <span class="sr-only">Info about {FIELD_LABELS[field as keyof PetitionData]}</span>
            </button>
          </Tooltip>
        </span>
      </li>
    {/each}
  </ul>
  {#if nextField}
    <p class="mt-4">Next: {FIELD_DESCRIPTIONS[nextField]}</p>
  {/if}
</aside>

