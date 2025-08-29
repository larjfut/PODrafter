<script lang="ts">
  import { chatMessages, petitionData, appState } from '$lib/stores'
  import { sendChat } from '$lib/utils'
  import type { ChatMessage } from '$lib/types'
  import { get } from 'svelte/store'
  import { onMount } from 'svelte'

  let userInput = ''
  let chatContainer: HTMLDivElement

  $: if ($chatMessages.length && chatContainer) {
    setTimeout(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }, 100)
  }

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

      if (response.upserts.length > 0) {
        petitionData.update(current => {
          const updated = { ...current }
          for (const upsert of response.upserts) {
            for (const [key, value] of Object.entries(upsert)) {
              if (key === 'source_msg_id' || key === 'confidence') continue
              if (value !== undefined && value !== null && value !== '') {
                ;(updated as any)[key] = value
              }
            }
          }
          return updated
        })
      }

      const last = response.messages[response.messages.length - 1]
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: last?.content || '',
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
</script>

<p class="mb-2 p-2 text-xs text-gray-600 bg-gray-50 rounded">
  For your privacy, avoid sharing personal details. Try prompts like "I need
  help filing in Travis County" or "What goes in the petition?"
</p>
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
  <div class="relative flex-grow">
    <input
      class="w-full border p-2 rounded-l pr-8"
      bind:value={userInput}
      placeholder="Type your message..."
      disabled={$appState.isLoading}
    />
    <span
      class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 cursor-help"
      title="Avoid sharing personal or sensitive information"
      aria-label="Privacy reminder"
      >&#9432;</span
    >
  </div>
  <button
    type="submit"
    class="bg-blue-500 text-white px-4 rounded-r disabled:opacity-50"
    disabled={$appState.isLoading}
  >
    {$appState.isLoading ? 'Thinking...' : 'Send'}
  </button>
</form>

