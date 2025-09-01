<script lang="ts">
  import '../app.css'
  import { onMount } from 'svelte'
  import { sanitizeBaseUrl } from '$lib/sanitizeBaseUrl'
  import { clearDraft } from '$lib/draft'
  import SafetySettings from '$src/lib/SafetySettings.svelte'
  import { loadSafety, saveSafety, type Safety } from '$src/lib/safety'
  import CommandMenu from '$src/components/CommandMenu.svelte'

  let safety: Safety = loadSafety()
  let cmdOpen = false
  const cmdItems = [
    { title: 'Home', href: '/' },
    { title: 'Welcome', href: '/welcome' },
    { title: 'Design — Kitchen Sink', href: '/design/kitchen-sink', keywords: ['design','kitchen','components'] },
    { title: 'Consent', href: '/consent' },
    { title: 'Guide', href: '/guide' },
    { title: 'Review', href: '/review' },
    { title: 'Completion', href: '/completion' },
    { title: 'Toggle Stealth', action: () => onSafetyChange(new CustomEvent('change', { detail: { ...safety, stealth: !safety.stealth } })) },
    { title: 'Toggle Reduced Motion', action: () => onSafetyChange(new CustomEvent('change', { detail: { ...safety, reducedMotion: !safety.reducedMotion } })) },
    { title: 'Toggle Reduce Effects', action: () => onSafetyChange(new CustomEvent('change', { detail: { ...safety, reduceEffects: !safety.reduceEffects } })) },
  ]

  function applyStealth() {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('stealth', !!safety.stealth)
      document.documentElement.classList.toggle('reduced-motion', !!safety.reducedMotion)
      document.documentElement.classList.toggle('reduce-effects', !!safety.reduceEffects)
    }
  }

  function updateSafety(s: Safety) {
    safety = s
    saveSafety(safety)
    applyStealth()
  }

  function onSafetyChange(e: CustomEvent) {
    updateSafety((e as any).detail)
  }

  function quickEscape() {
    try {
      clearDraft()
      localStorage.clear()
    } catch {}
    // Redirect to neutral site
    if (typeof window !== 'undefined') {
      window.location.assign('https://www.weather.com')
    }
  }

  onMount(async () => {
    applyStealth()
    try {
      const baseUrl = sanitizeBaseUrl(import.meta.env.VITE_API_BASE_URL || '/api')
      await fetch(`${baseUrl}/auth/issue`, { method: 'GET', credentials: 'include' })
    } catch (e) {
      console.warn('Failed to issue session', e)
    }
  })
</script>

<header class="app-header">
  <nav class="container mx-auto p-3 flex items-center justify-between gap-3">
    <a href="/" class="font-semibold text-lg">PO Drafter</a>
    <div class="flex items-center gap-3">
      <a href="/welcome" class="text-blue-600 underline">Safety</a>
      <button class="quick-escape" on:click|preventDefault={quickEscape} aria-label="Quick Escape">Quick Escape</button>
      <SafetySettings {safety} on:change={onSafetyChange} />
    </div>
  </nav>
  {#if safety?.stealth}
    <div class="stealth-banner" role="status">Stealth mode is ON</div>
  {/if}
  <hr />
</header>

<main>
  <slot />
  <div class="sr-only" aria-live="polite" aria-atomic="true"></div>
</main>

<CommandMenu items={cmdItems} bind:open={cmdOpen} />
