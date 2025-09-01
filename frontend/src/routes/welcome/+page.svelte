<script lang="ts">
  import { goto } from '$app/navigation'
  import { loadSafety, saveSafety, type Safety } from '$src/lib/safety'
  let safety: Safety = loadSafety()
  function start() { goto('/consent') }
  function toggle(key: keyof Safety) {
    safety = { ...safety, [key]: !safety[key] }
    saveSafety(safety)
  }
</script>

<main class="container mx-auto p-4">
  <h1 class="mb-2">Welcome — Your Safety Matters</h1>
  <p class="muted mb-4">If you are in immediate danger, call 911. For support, call <a class="underline text-indigo-600" href="https://www.thehotline.org/" target="_blank" rel="noreferrer noopener">800‑799‑SAFE (7233)</a>.</p>

  <section class="mb-4 glass p-4">
    <h2 class="mb-2">Privacy & Safety</h2>
    <ul class="list-disc pl-5 text-sm muted">
      <li>Your answers stay on this device until you generate documents.</li>
      <li>You can clear all data anytime with Quick Escape.</li>
      <li>We use the Texas General form accepted in all counties.</li>
    </ul>
  </section>

  <section class="mb-4 glass p-4">
    <h2 class="mb-2">Safety Settings</h2>
    <label class="block text-sm mb-2"><input type="checkbox" checked={safety.stealth} on:change={() => toggle('stealth')} /> Stealth mode</label>
    <label class="block text-sm"><input type="checkbox" checked={safety.reducedMotion} on:change={() => toggle('reducedMotion')} /> Reduced motion</label>
  </section>

  <section id="resources" class="mb-4 glass p-4">
    <h2 class="mb-2">Resources</h2>
    <ul class="list-disc pl-5 text-sm">
      <li><a class="underline text-indigo-600" href="https://www.thehotline.org/" target="_blank" rel="noreferrer noopener">National Domestic Violence Hotline</a> (24/7 chat/call)</li>
      <li><a class="underline text-indigo-600" href="https://www.tcfv.org/" target="_blank" rel="noreferrer noopener">Texas Council on Family Violence</a> (shelters and programs)</li>
      <li><a class="underline text-indigo-600" href="https://texaslawhelp.org/" target="_blank" rel="noreferrer noopener">TexasLawHelp.org</a> (legal info and forms)</li>
      <li><a class="underline text-indigo-600" href="https://211texas.org/" target="_blank" rel="noreferrer noopener">2‑1‑1 Texas</a> (local services)</li>
    </ul>
    <p class="text-xs muted mt-2">Links open in a new tab. No tracking is added.</p>
  </section>

  <div class="mt-4 flex gap-3">
    <button class="bg-[color:var(--mint-deep)] text-white h-11 px-4 rounded-control active:translate-y-[1px]" on:click|preventDefault={start}>Continue</button>
    <a class="text-indigo-600 underline" href="/review">Skip to Review</a>
  </div>
</main>
