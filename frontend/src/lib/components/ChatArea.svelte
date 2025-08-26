<script lang="ts">
  import { chatMessages, petitionData } from '$lib/stores/petitionStore'
  import { appState } from '$lib/stores/progressStore'
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

