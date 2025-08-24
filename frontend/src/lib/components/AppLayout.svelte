<script lang="ts">
  import {
    appState,
    chatMessages,
    petitionData,
    pdfUrl,
    nextStep,
    prevStep
  } from '$lib/stores'
  import { FIELD_LABELS, WIZARD_STEPS } from '$lib/constants'
  import { sendChat, validatePetition, generatePDF } from '$lib/utils'
  import type { ChatMessage, PetitionData } from '$lib/types'
  import { get } from 'svelte/store'

  let userInput = ''
  const fieldEntries: [keyof PetitionData, string][] = Object.entries(
    FIELD_LABELS
  ) as [keyof PetitionData, string][]

  $: validation = validatePetition($petitionData)

  async function handleSend() {
    if (userInput.trim().length === 0) return
    const userMsg: ChatMessage = {
      role: 'user',
      content: userInput,
      timestamp: new Date(),
      id: crypto.randomUUID()
    }
    chatMessages.update(m => [...m, userMsg])
    userInput = ''
    appState.update(s => ({ ...s, isLoading: true }))
    try {
      const res = await sendChat(get(chatMessages))
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.content,
        timestamp: new Date(),
        id: crypto.randomUUID()
      }
      chatMessages.update(m => [...m, assistantMsg])
      if (res.data) {
        petitionData.update(d => ({ ...d, ...res.data }))
      }

    } catch (err) {
      console.error(err)
      appState.update(s => ({ ...s, error: 'Chat request failed' }))
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
    const res = await generatePDF(get(petitionData))
    if (res.success && res.fileUrl) {
      pdfUrl.set(res.fileUrl)
      nextStep()
    } else {
      appState.update(s => ({ ...s, error: res.error ?? 'PDF generation failed' }))
    }
    appState.update(s => ({ ...s, isLoading: false }))
  }
</script>

<div class="mx-auto p-4 max-w-2xl">
  {#if $appState.error}
    <p class="text-red-600 mb-2">{$appState.error}</p>
  {/if}
<nav class="mb-4 flex justify-between">
  {#each WIZARD_STEPS as { step, title }}
    <span class:text-blue-600={step === $appState.currentStep}>
      {title}
    </span>
  {/each}
</nav>

  {#if $appState.currentStep === 'chat'}
    <div class="chat-area mb-4 h-64 overflow-y-auto border p-2 rounded">
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
      />
      <button type="submit" class="bg-blue-500 text-white px-4 rounded-r">
        Send
      </button>
    </form>
    <div class="mt-4">
      <p class="mb-2">Progress: {validation.completionPercentage}%</p>
      {#if validation.errors.length > 0}
        <ul class="text-sm text-red-600 mb-2">
          {#each validation.errors as err}
            <li>{FIELD_LABELS[err.field]} is required</li>
          {/each}
        </ul>
      {/if}
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
    <button
      class="mt-4 bg-gray-200 px-3 py-1 rounded"
      on:click={nextStep}
      disabled={!validation.isValid}
    >

    <button class="mt-4 bg-gray-200 px-3 py-1 rounded" on:click={nextStep}>
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
