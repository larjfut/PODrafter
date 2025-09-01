<script lang="ts">
  import { onMount } from 'svelte'
  import { setPassphrase, addEntry, listEntries, clearAll, type Entry } from '$src/lib/locker'

  let pass = ''
  let confirmed = false
  let entries: Entry[] = []
  let title = ''
  let date = ''
  let details = ''
  let error: string | null = null

  async function enter() {
    error = null
    if (!pass || pass.length < 8) { error = 'Use at least 8 characters.'; return }
    await setPassphrase(pass)
    confirmed = true
    entries = await listEntries()
  }

  async function save() {
    error = null
    if (!title || !details) { error = 'Add a title and some details.'; return }
    await addEntry({ title, details, date })
    title = ''; date=''; details=''
    entries = await listEntries()
  }

  async function wipe() {
    if (!confirm('Delete all locker entries on this device?')) return
    await clearAll()
    entries = []
  }

  onMount(() => { /* client only */ })
</script>

<section class="container mx-auto p-6 space-y-6">
  <h1>Private Evidence Locker</h1>
  <p class="muted">Optional, private notes stored only on this device. Set a passphrase you can remember. This data is not uploaded or shared.</p>

  {#if !confirmed}
    <div class="glass p-4 max-w-xl">
      <label class="text-sm font-medium text-[color:var(--muted-ink)]">Set a passphrase</label>
      <input type="password" bind:value={pass} class="mt-1 h-11 px-3 w-full rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" placeholder="At least 8 characters" />
      <button class="mt-3 bg-[color:var(--mint-deep)] text-white h-11 px-4 rounded-control active:translate-y-[1px]" on:click|preventDefault={enter}>Continue</button>
      {#if error}<div class="text-[color:var(--coral)] text-sm mt-2">{error}</div>{/if}
      <p class="text-xs muted mt-3">Warning: If someone else has access to this device, they may see that this page exists. Use Stealth/Quick Escape as needed.</p>
    </div>
  {:else}
    <div class="grid md:grid-cols-2 gap-6">
      <div class="glass p-4">
        <h2 class="mb-2">Add a note</h2>
        <label class="text-sm font-medium text-[color:var(--muted-ink)]">Title</label>
        <input bind:value={title} class="h-11 px-3 w-full rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" placeholder="e.g., Incident on May 3" />
        <div class="grid grid-cols-2 gap-2 mt-2">
          <div>
            <label class="text-sm font-medium text-[color:var(--muted-ink)]">Date (optional)</label>
            <input type="date" bind:value={date} class="h-11 px-3 w-full rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" />
          </div>
        </div>
        <label class="text-sm font-medium text-[color:var(--muted-ink)] mt-2">Details</label>
        <textarea rows="6" bind:value={details} class="px-3 py-2 w-full rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" placeholder="What happened, where, who was present..." />
        <div class="mt-3 flex items-center gap-2">
          <button class="bg-[color:var(--mint-deep)] text-white h-11 px-4 rounded-control active:translate-y-[1px]" on:click|preventDefault={save}>Save note</button>
          <button class="bg-[color:var(--coral)] text-white h-11 px-4 rounded-control active:translate-y-[1px]" on:click|preventDefault={wipe}>Delete all</button>
        </div>
        {#if error}<div class="text-[color:var(--coral)] text-sm mt-2">{error}</div>{/if}
      </div>
      <div class="glass p-4">
        <h2 class="mb-2">Your notes</h2>
        {#if entries.length === 0}
          <div class="muted text-sm">No notes yet.</div>
        {:else}
          <ul class="space-y-3">
            {#each entries as e}
              <li class="p-3 rounded-card bg-white/70 shadow-e1">
                <div class="text-sm muted">{new Date(e.createdAt).toLocaleString()} {#if e.date}· {e.date}{/if}</div>
                <div class="font-medium">{e.title}</div>
                <div class="text-sm whitespace-pre-wrap">{e.details}</div>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  {/if}
</section>
