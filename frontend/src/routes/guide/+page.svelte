<script lang="ts">
  function printPage() { if (typeof window !== 'undefined') window.print() }
</script>

<main class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-2">Filing Guide</h1>
  <p class="mb-4 text-sm text-gray-600">Texas General form — accepted in all Texas counties.</p>

  <button class="no-print bg-gray-100 text-gray-800 px-3 py-1 rounded mb-3" on:click|preventDefault={printPage}>Print this page</button>
  <section class="prose max-w-none">
    <h2>Step-by-Step Instructions</h2>
    <ol>
      <li>Print all documents: petition, (optional) firearm-surrender addendum, and this guide.</li>
      <li>Sign the petition in blue ink where indicated.</li>
      <li>Review the checklist below to ensure completion.</li>
      <li>Place documents in a manila envelope.</li>
      <li>Submit to the Clerk's office. If you have the clerk's mailing address, include it on your cover letter.</li>
      <li>Request fee waiver and ask for file-stamping.</li>
      <li>Obtain a file-stamped copy and retain it for your records.</li>
      <li>If mailing is needed, mail the stamped copy back to your address.</li>
    </ol>

    <h2>Checklist</h2>
    <ul>
      <li>Signed Protective Order Petition</li>
      <li>Completed Firearm-Surrender Addendum (if applicable)</li>
      <li>Self-Addressed Stamped Envelope</li>
      <li>Fee Waiver Request Included</li>
      <li>Copy for Your Records</li>
    </ul>

    <h2>Safety & Support</h2>
    <p>
      For assistance or emergency, call 911. For support services, dial 800-799-SAFE (7233) or visit
      <a href="https://www.texasadvocacy.org">www.texasadvocacy.org</a>.
    </p>
  </section>

  <div class="mt-6">
    <a class="text-blue-600 underline" href="/">Back to Chat</a>
    <a class="ml-3 text-blue-600 underline" href="/review">Review & Generate</a>
  </div>
</main>
<script lang="ts">
  import CountyFinder from '$src/components/CountyFinder.svelte'
</script>

<section class="container mx-auto p-6 space-y-6">
  <h1>Filing Guide</h1>
  <p class="muted">This guide helps you prepare to file your petition. You’re in control—take breaks anytime.</p>

  <div class="grid md:grid-cols-2 gap-6">
    <div class="glass p-4">
      <h2 class="mb-2">Find Your County</h2>
      <CountyFinder />
    </div>
    <div class="glass p-4">
      <h2 class="mb-2">What to Bring</h2>
      <ul class="list-disc pl-5 text-sm">
        <li>Photo ID (if you have one)</li>
        <li>Any incident notes or dates (if available)</li>
        <li>Addresses and contact info (as you’re comfortable)</li>
      </ul>
    </div>
  </div>
</section>
