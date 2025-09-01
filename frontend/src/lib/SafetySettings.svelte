<script lang="ts">
  import type { Safety } from '$src/lib/safety'
  export let safety: Safety
  import { createEventDispatcher } from 'svelte'
  const dispatch = createEventDispatcher()

  function toggle(key: keyof Safety) {
    const next = { ...safety, [key]: !safety[key] }
    dispatch('change', next)
  }
</script>

<div class="safety-settings">
  <label class="inline-flex items-center gap-2 text-sm">
    <input type="checkbox" checked={safety.stealth} on:change={() => toggle('stealth')} />
    Stealth mode
  </label>
  <label class="inline-flex items-center gap-2 text-sm ml-3">
    <input type="checkbox" checked={safety.reducedMotion} on:change={() => toggle('reducedMotion')} />
    Reduced motion
  </label>
  <label class="inline-flex items-center gap-2 text-sm ml-3">
    <input type="checkbox" checked={safety.reduceEffects} on:change={() => toggle('reduceEffects')} />
    Reduce effects
  </label>
</div>

<style>
  .safety-settings :global(input[type='checkbox']) {
    transform: scale(1.1);
  }
</style>
