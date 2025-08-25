<script lang="ts">
  import {
    appState,
    chatMessages,
    petitionData,
    pdfUrl,
    nextStep,
    prevStep
  } from '$lib/stores'
  import {
    FIELD_LABELS,
    WIZARD_STEPS,
    FIELD_DESCRIPTIONS
  } from '$lib/constants'
  import {
    sendChat,
    validatePetition,
    generatePDF,
    getCollectedFields,
    getNextSuggestedField,
    canProceedToReview
  } from '$lib/utils'
  import type { ChatMessage, PetitionData } from '$lib/types'
  import { get } from 'svelte/store'
  import { onMount } from 'svelte'

  let userInput = ''
  let chatContainer: HTMLDivElement
  const fieldEntries: [keyof PetitionData, string][] = Object.entries(
    FIELD_LABELS
  ) as [keyof PetitionData, string][]

  $: validation = validatePetition($petitionData)
  $: fieldStatus = getCollectedFields($petitionData)
  $: nextField = getNextSuggestedField($petitionData)
  $: canReview = canProceedToReview($petitionData)

  // Auto-scroll chat to bottom when new messages arrive
  $: if ($chatMessages.length && chatContainer) {
    setTimeout(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }, 100)
  }

  // Initial welcome message
  onMount(() => {
    if ($chatMessages.length === 0) {
      setTimeout(() => {
        chatMessages.set([
          {
            role: 'assistant',
            content:
              "Hello, I'm here to help you create a protective order petition. This is an important step toward your safety, and I'll guide you through it carefully.\n\nTo start, could you tell me which Texas county you'd like to file in? We currently support Harris, Dallas, Travis, or General (for other counties).",
            timestamp: new Date(),
            id: crypto.randomUUID()
          }
        ])
      }, 500)
    }
  })

  async function handleSend() {
    if (userInput.trim().length === 0) return

    const userMsg: ChatMessage = {
      role: 'user',
      content: userInput.trim(),
      timestamp: new Date(),
      id: crypto.randomUUID()
    }

    chatMessages.update(m => [...m, userMsg])
    userInput = ''
    appState.update(s => ({ ...s, isLoading: true, error: undefined }))

    try {
      const response = await sendChat(get(chatMessages), 10000)

      // Extract and merge petition data
      if (response.data && Object.keys(response.data).length > 0) {
        petitionData.update(current => {
          const updated = { ...current }
          for (const [key, value] of Object.entries(response.data!)) {
            if (value !== undefined && value !== null && value !== '') {
              ;(updated as any)[key] = value
            }
          }
          return updated
        })
      }

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        id: crypto.randomUUID()
      }

      chatMessages.update(m => [...m, assistantMsg])
    } catch (err) {
      if (import.meta.env.DEV) console.error('Chat error:', err)
      const errorMsg = err instanceof Error ? err.message : 'Chat request failed'
      appState.update(s => ({ ...s, error: errorMsg }))
    } finally {
      appState.update(s => ({ ...s, isLoading: false }))
    }
  }

  function handleReviewNext() {
    const validation = validatePetition(get(petitionData))
    if (validation.isValid) {
      appState.update(s => ({ ...s, error: undefined }))
      nextStep()
    } else {
      appState.update(s => ({ ...s, error: 'Please complete required fields' }))
    }
  }

  async function handleGenerate() {
    appState.update(s => ({ ...s, isLoading: true, error: undefined }))
    try {
      const res = await generatePDF(get(petitionData))
      if (res.success && res.fileUrl) {
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
</script>

<div class="mx-auto p-4 max-w-4xl">
  {#if $appState.error}
    <p class="text-red-600 mb-2">{$appState.error}</p>
  {/if}
  <h1 class="text-xl font-bold mb-4">PO Drafter Chat Wizard</h1>
  <nav class="mb-4 flex justify-between">
  {#each WIZARD_STEPS as { step, title }}
    <span class:text-blue-600={step === $appState.currentStep}>
      {title}
    </span>
  {/each}
</nav>

  {#if $appState.currentStep === 'chat'}
    <div class="md:flex gap-4">
      <div class="flex-1 flex flex-col">
        <div
          class="chat-area mb-4 h-64 overflow-y-auto border p-2 rounded"
          bind:this={chatContainer}
          aria-live="polite"
          role="log"
          aria-atomic="false"
        >
          {#each $chatMessages as msg}
            <div
              class="my-2"
              class:text-right={msg.role === 'user'}
              class:text-left={msg.role === 'assistant'}
            >
              <span
                class="p-2 rounded inline-block"
                class:bg-blue-200={msg.role === 'user'}
                class:bg-gray-200={msg.role === 'assistant'}
              >
                {msg.content}
              </span>
            </div>
          {/each}
        </div>
        <form on:submit|preventDefault={handleSend} class="flex">
          <input
            class="flex-grow border p-2 rounded-l"
            bind:value={userInput}
            placeholder="Type your message..."
            disabled={$appState.isLoading}
          />
          <button
            type="submit"
            class="bg-blue-500 text-white px-4 rounded-r disabled:opacity-50"
            disabled={$appState.isLoading}
          >
            {$appState.isLoading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </div>
      <aside class="mt-4 md:mt-0 md:w-64 border p-2 rounded text-sm">
        <p class="font-semibold mb-2">Progress</p>
        <div class="w-full bg-gray-200 h-2 rounded">
          <div
            class="bg-blue-500 h-2 rounded"
            style={`width: ${validation.completionPercentage}%`}
          ></div>
        </div>
        <p class="mt-1">{validation.completionPercentage}% complete</p>
        <ul class="mt-4 space-y-1">
          {#each Object.entries(FIELD_DESCRIPTIONS) as [field, desc]}
            <li class="flex items-center gap-2">
              {#if fieldStatus.collected.includes(field as keyof PetitionData)}
                <span class="text-green-600">✔</span>
              {:else}
                <span class="text-gray-400">✖</span>
              {/if}
              <span>{desc}</span>
            </li>
          {/each}
        </ul>
        {#if nextField}
          <p class="mt-4">Next: {FIELD_DESCRIPTIONS[nextField]}</p>
        {/if}
      </aside>
    </div>
    <button
      class="mt-4 bg-gray-200 px-3 py-1 rounded disabled:opacity-50"
      on:click={nextStep}
      disabled={!canReview}
    >
      Review
    </button>
  {:else if $appState.currentStep === 'review'}
    <div class="mb-4">
      {#each fieldEntries as [field, label]}
        <div class="mb-2">
          <label class="font-bold">{label}</label>
          <input
            class="w-full border p-2 rounded"
            value={$petitionData[field] ?? ''}
            on:input={(e) =>
              petitionData.update(d => ({
                ...d,
                [field]: (e.target as HTMLInputElement).value
              }))
            }
          />
        </div>
      {/each}
    </div>
    <div class="flex gap-2">
      <button class="bg-gray-200 px-3 py-1 rounded" on:click={prevStep}>
        Back
      </button>
      <button
        class="bg-blue-500 text-white px-3 py-1 rounded"
        on:click={handleReviewNext}
      >
        Generate
      </button>
    </div>
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
      <button class="bg-gray-200 px-3 py-1 rounded" on:click={prevStep}>
        Back
      </button>
    </div>
  {/if}
</div>
