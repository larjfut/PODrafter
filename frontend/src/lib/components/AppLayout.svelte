<script lang="ts">
  import {
    appState,
    chatMessages,
    petitionData,
    pdfUrl,
    nextStep,
    prevStep
  } from '$lib/stores'
  import { WIZARD_STEPS } from '$lib/constants'
  import { generatePDF, canProceedToReview } from '$lib/utils'
  import { get } from 'svelte/store'
  import type { WizardStep } from '$lib/types'
  import Tooltip from './ui/Tooltip.svelte'
  import { InformationCircleIcon } from '@heroicons/svelte/24/outline'

  let ChatArea: typeof import('./ChatArea.svelte').default | null = null
  let ProgressSidebar: typeof import('./ProgressSidebar.svelte').default | null = null
  let ReviewForm: typeof import('./ReviewForm.svelte').default | null = null

  let revokePdf: (() => void) | null = null

  const STEP_INSTRUCTIONS: Record<WizardStep, string> = {
    chat: 'Share your story to get started.',
    review: 'Review the details and make any edits.',
    generate: 'Generate your petition document.',
    download: 'Download your completed petition.'
  }

  $: canReview = canProceedToReview($petitionData)
  $: activeStep = WIZARD_STEPS.find(({ step }) => step === $appState.currentStep)

  $: if ($appState.currentStep === 'chat' && (!ChatArea || !ProgressSidebar)) {
    Promise.all([
      import('./ChatArea.svelte').then(m => (ChatArea = m.default)),
      import('./ProgressSidebar.svelte').then(m => (ProgressSidebar = m.default))
    ])
  }

  $: if ($appState.currentStep === 'review' && !ReviewForm) {
    import('./ReviewForm.svelte').then(m => (ReviewForm = m.default))
  }

  async function handleGenerate() {
    appState.update(s => ({ ...s, isLoading: true, error: undefined }))
    try {
      revokePdf?.()
      const res = await generatePDF(get(petitionData))
      if (res.success && res.fileUrl) {
        revokePdf = res.revoke ?? null
        pdfUrl.set(res.fileUrl)
        nextStep()
      } else {
        appState.update(s => ({
          ...s,
          error: res.error ?? 'PDF generation failed'
        }))
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'PDF generation failed'
      appState.update(s => ({ ...s, error: errorMsg }))
    } finally {
      appState.update(s => ({ ...s, isLoading: false }))
    }
  }

  function handleDownloadBack() {
    revokePdf?.()
    pdfUrl.set(null)
    prevStep()
  }

  function quickEscape() {
    chatMessages.set([])
    petitionData.set({
      county: 'General',
      petitioner_full_name: '',
      respondent_full_name: ''
    })
    pdfUrl.set(null)
    appState.set({ currentStep: 'chat', isLoading: false })
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(regs =>
        regs.forEach(r => r.unregister())
      )
    }
    if ('caches' in window) {
      caches.keys().then(keys => keys.forEach(k => caches.delete(k)))
    }
    // Clear browser storage to remove any persisted data
    if ('localStorage' in window) {
      localStorage.clear()
    }
    if ('sessionStorage' in window) {
      sessionStorage.clear()
    }
    window.location.href = 'https://www.google.com'
  }
</script>

<button
  on:click={quickEscape}
  class="fixed top-2 right-2 z-50 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded shadow-lg focus:outline-none focus:ring-2 focus:ring-red-800"
>
  Quick Escape
</button>

<Tooltip content="Immediately clears data and redirects to a safe site.">
  <InformationCircleIcon
    aria-label="Information about quick escape"
    class="fixed top-2 right-28 z-50 h-6 w-6 text-gray-500"
  />
</Tooltip>

<div class="mx-auto p-4 max-w-4xl">
  {#if $appState.error}
    <p class="text-red-600 mb-2">{$appState.error}</p>
  {/if}
  <h1 class="text-xl font-bold mb-4">
    PO Drafter Chat Wizard
  </h1>
  <nav class="mb-4 flex justify-between">
  {#each WIZARD_STEPS as { step, title }}
    <span class:text-blue-600={step === $appState.currentStep}>
      {title}
    </span>
  {/each}
</nav>

  <h2 class="text-lg font-semibold mb-1">
    {activeStep?.title}
  </h2>
  <p class="mb-4 text-gray-600">
    {STEP_INSTRUCTIONS[$appState.currentStep]}
  </p>

  {#if $appState.currentStep === 'chat'}
    <div class="md:flex gap-4">
      <div class="flex-1 flex flex-col">
        {#if ChatArea}
          <svelte:component this={ChatArea} />
        {/if}
      </div>
      {#if ProgressSidebar}
        <svelte:component this={ProgressSidebar} />
      {/if}
    </div>
    <button
      class="mt-4 bg-gray-200 px-3 py-1 rounded disabled:opacity-50"
      on:click={nextStep}
      disabled={!canReview}
    >
      Review
    </button>
  {:else if $appState.currentStep === 'review'}
    {#if ReviewForm}
      <svelte:component this={ReviewForm} />
    {/if}
  {:else if $appState.currentStep === 'generate'}
    <p class="mb-4">Ready to generate your petition PDF.</p>
    <div class="flex gap-2">
      <button class="bg-gray-200 px-3 py-1 rounded" on:click={prevStep}>
        Back
      </button>
      <button
        class="bg-blue-500 text-white px-3 py-1 rounded"
        on:click={handleGenerate}
        disabled={$appState.isLoading}
      >
        {$appState.isLoading ? 'Generating...' : 'Generate PDF'}
      </button>
    </div>
  {:else if $appState.currentStep === 'download'}
    {#if $pdfUrl}
      <a class="text-blue-600 underline" href={$pdfUrl} download>
        Download PDF
      </a>
    {/if}
    <div class="mt-4">
      <button class="bg-gray-200 px-3 py-1 rounded" on:click={handleDownloadBack}>
        Back
      </button>
    </div>
  {/if}
</div>
