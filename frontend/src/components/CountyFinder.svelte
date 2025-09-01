<script lang="ts">
  /* Lightweight ZIP -> county suggester for Texas. Uses common ZIP prefixes. */
  export let zip = ''
  let county: string | null = null

  const prefixMap: Record<string, string> = {
    '752': 'Dallas County',
    '750': 'Dallas County',
    '751': 'Dallas County',
    '770': 'Harris County',
    '773': 'Harris County',
    '774': 'Harris County',
    '787': 'Travis County',
    '786': 'Travis County',
    '782': 'Bexar County',
    '781': 'Bexar County',
    '761': 'Tarrant County',
    '760': 'Tarrant County',
  }

  $: county = suggest(zip)

  function suggest(z: string): string | null {
    const digits = (z || '').trim()
    if (digits.length < 3) return null
    const pref = digits.slice(0, 3)
    return prefixMap[pref] || null
  }
</script>

<div class="space-y-2">
  <label for="zip" class="text-sm font-medium text-[color:var(--muted-ink)]">ZIP code (Texas)</label>
  <input id="zip" bind:value={zip} inputmode="numeric" pattern="\\d*" class="h-11 px-3 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" placeholder="e.g., 77002" />
  {#if county}
    <div class="text-sm">
      Suggested county: <strong>{county}</strong>
      <div class="text-xs muted mt-1">Verify with your address. If this seems wrong, select your county manually in the next step.</div>
    </div>
  {:else if zip && zip.length >= 3}
    <div class="text-sm muted">We couldn’t suggest a county. You can still choose it manually next.</div>
  {/if}
  <div class="text-xs mt-2">
    Need help? See filing guidance on the <a class="underline text-indigo-600" href="/guide">guide</a> page.
  </div>
</div>
