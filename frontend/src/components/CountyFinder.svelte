<script lang="ts">
  /* Lightweight ZIP -> county suggester for Texas. Uses common ZIP prefixes. */
  export let zip = ''
  let county: string | null = null

  let prefixMap: Record<string, string> = {}
  let zipMap: Record<string, string> = {}
  let loaded = false
  async function ensureMap() {
    if (loaded) return
    try {
      const [pref, full] = await Promise.all([
        import('$src/lib/tx-zip-prefix-counties.json'),
        import('$src/lib/tx-zip-counties.json'),
      ])
      prefixMap = pref.default as Record<string, string>
      zipMap = full.default as Record<string, string>
    } catch {
      prefixMap = {}
    } finally {
      loaded = true
    }
  }

  $: county = suggest(zip)

  function suggest(z: string): string | null {
    const digits = (z || '').trim()
    if (!loaded) ensureMap()
    if (digits.length >= 5 && zipMap[digits]) return zipMap[digits]
    if (digits.length >= 3) {
      const pref = digits.slice(0, 3)
      return prefixMap[pref] || null
    }
    return null
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
