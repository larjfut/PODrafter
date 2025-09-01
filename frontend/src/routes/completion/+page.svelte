<script lang="ts">
  import { clearDraft } from '$lib/draft'
  function wipe() {
    try { clearDraft(); localStorage.clear() } catch {}
  }
  function printPage() { if (typeof window !== 'undefined') window.print() }
</script>

<main class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-2">Next Steps & Safety</h1>
  <p class="text-sm text-gray-700 mb-4">Here’s what to expect after you file and how to stay safe.</p>

  <section class="prose max-w-none">
    <h2>What to Expect</h2>
    <ul>
      <li>You may receive a court date; bring your documents and any evidence.</li>
      <li>The respondent must be served before a hearing can proceed.</li>
      <li>Keep a copy of your filings for your records.</li>
    </ul>

    <h2>Support</h2>
    <p>For help with safety planning or questions, call 800-799-SAFE (7233).</p>

    <h2>Privacy</h2>
    <p>For shared devices, consider clearing your data when finished.</p>
  </section>

  <div class="mt-4 flex gap-3">
    <button class="no-print bg-gray-100 text-gray-800 px-3 py-1 rounded" on:click|preventDefault={printPage}>Print this page</button>
    <button class="no-print bg-red-600 text-white px-3 py-1 rounded" on:click|preventDefault={wipe}>Clear my information</button>
    <a class="text-blue-600 underline" href="/">Back to Chat</a>
  </div>
</main>
<script lang="ts">
  import IcsExport from '$src/components/IcsExport.svelte'
</script>

<section class="container mx-auto p-6 space-y-6">
  <h1>Completion</h1>
  <p class="muted">You can download a calendar reminder for your court date.</p>
  <div class="glass p-4">
    <h2 class="mb-2">Add a calendar reminder (.ics)</h2>
    <IcsExport />
  </div>
</section>
