<script>
  import '../app.css'
  import ErrorBoundary from '$lib/components/ErrorBoundary.svelte'
</script>

<ErrorBoundary>
  <slot />
</ErrorBoundary>

