<script lang="ts">
  import { onMount } from 'svelte'
  import { writable } from 'svelte/store'

  const error = writable<Error | null>(null)

  function reload() {
    location.reload()
  }

  onMount(() => {
    const handleError = (event: ErrorEvent) => {
      console.error(event.error || event.message)
      error.set(event.error || new Error(event.message))
    }
    const handleRejection = (event: PromiseRejectionEvent) => {
      console.error(event.reason)
      const err =
        event.reason instanceof Error
          ? event.reason
          : new Error(String(event.reason))
      error.set(err)
    }
    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleRejection)
    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleRejection)
    }
  })
</script>

{#if $error}
  <div class="p-4 text-center">
    <p class="mb-2">Something went wrong.</p>
    <button class="bg-blue-500 text-white px-3 py-1 rounded" on:click={reload}>
      Reload
    </button>
  </div>
{:else}
  <slot />
{/if}

