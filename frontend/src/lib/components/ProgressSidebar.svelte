<script lang="ts">
  import { progress } from '$lib/stores/progressStore'
  import { FIELD_DESCRIPTIONS } from '$lib/constants'
  import type { PetitionData } from '$lib/types'
</script>

<aside class="mt-4 md:mt-0 md:w-64 border p-2 rounded text-sm">
  <p class="font-semibold mb-2">Progress</p>
  <div class="w-full bg-gray-200 h-2 rounded">
    <div
      class="bg-blue-500 h-2 rounded"
      style={`width: ${$progress.completionPercentage}%`}
    ></div>
  </div>
  <p class="mt-1">{$progress.completionPercentage}% complete</p>
  <ul class="mt-4 space-y-1">
    {#each Object.entries(FIELD_DESCRIPTIONS) as [field, desc]}
      <li class="flex items-center gap-2">
        {#if $progress.fieldStatus.collected.includes(field as keyof PetitionData)}
          <span class="text-green-600">✔</span>
        {:else}
          <span class="text-gray-400">✖</span>
        {/if}
        <span>{desc}</span>
      </li>
    {/each}
  </ul>
  {#if $progress.nextField}
    <p class="mt-4">Next: {FIELD_DESCRIPTIONS[$progress.nextField]}</p>
  {/if}
</aside>

