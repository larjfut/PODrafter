<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import Fuse from 'fuse.js'

  export type Item = { title: string; href?: string; action?: () => void; keywords?: string[] }
  export let items: Item[] = []
  export let open = false

  let query = ''
  let results: Item[] = []
  let dialogEl: HTMLDivElement | null = null
  let inputEl: HTMLInputElement | null = null
  let fuse: Fuse<Item>

  function buildFuse() {
    fuse = new Fuse(items, { keys: ['title', 'keywords'], includeScore: true, threshold: 0.4 })
  }

  $: buildFuse()
  $: results = query ? fuse.search(query).map(r => r.item) : items.slice(0, 20)

  function onGlobalKey(e: KeyboardEvent) {
    const isCmdK = (e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')
    if (isCmdK) {
      e.preventDefault()
      open = !open
      if (open) queueMicrotask(() => inputEl?.focus())
    } else if (open && e.key === 'Escape') {
      open = false
    }
  }

  function activate(item: Item) {
    if (item.href) {
      window.location.href = item.href
    } else if (item.action) {
      item.action()
    }
    open = false
  }

  onMount(() => {
    window.addEventListener('keydown', onGlobalKey)
  })
  onDestroy(() => {
    window.removeEventListener('keydown', onGlobalKey)
  })
</script>

{#if open}
  <div class="fixed inset-0 z-50 bg-black/40" aria-hidden="true"></div>
  <div bind:this={dialogEl} role="dialog" aria-modal="true" aria-label="Command Menu" class="fixed inset-x-0 top-24 z-50 mx-auto w-full max-w-2xl glass p-3 shadow-e3">
    <div class="flex items-center gap-2 p-2">
      <input bind:this={inputEl} bind:value={query} placeholder="Search…" class="flex-1 h-11 bg-white/70 rounded-control px-3 outline-none" aria-label="Search" />
      <kbd class="text-xs text-slate-500">Ctrl/⌘ K</kbd>
    </div>
    <div class="max-h-80 overflow-auto">
      {#if results.length === 0}
        <div class="p-4 text-sm text-slate-500">No results</div>
      {:else}
        <ul>
          {#each results as item}
            <li>
              <button class="w-full text-left px-3 py-2 hover:bg-indigo-600/10 rounded-md" on:click={() => activate(item)}>{item.title}</button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
{/if}

<style>
  :global(.reduce-effects) .glass { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }
</style>
