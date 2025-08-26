<script lang="ts">
  import { onMount } from 'svelte'

  let AppLayout: typeof import('$lib/components/AppLayout.svelte').default | null = null

  onMount(async () => {
    const mod = await import('$lib/components/AppLayout.svelte')
    AppLayout = mod.default
  })
</script>

{#if AppLayout}
  <svelte:component this={AppLayout} />
{/if}
