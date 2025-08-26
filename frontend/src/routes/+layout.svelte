<script lang="ts">
  import '../app.css'
  import ErrorBoundary from '$lib/components/ErrorBoundary.svelte'
  import { onMount } from 'svelte'

  onMount(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
    }
  })
</script>

<ErrorBoundary>
  <slot />
</ErrorBoundary>

