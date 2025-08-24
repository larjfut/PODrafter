<script lang="ts">
  import { sanitizeBaseUrl } from '$lib/sanitizeBaseUrl'

  interface Message {
    role: 'user' | 'assistant'
    content: string
  }

  let messages: Message[] = []
  let input = ''

  async function send() {
    if (input.trim().length === 0) return

    // 1️⃣ Append user message
    messages = [...messages, { role: 'user', content: input }]

    // 2️⃣ Capture and clear input
    input = ''

    // 3️⃣ Call your backend
    const baseUrl = sanitizeBaseUrl(import.meta.env.PUBLIC_API_BASE_URL || '/api')
    const url = `${baseUrl}/chat`
    try {
      const apiKey = import.meta.env.PUBLIC_CHAT_API_KEY
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey ? { 'X-API-Key': apiKey } : {})
        },
        body: JSON.stringify({ messages })
      })

      if (!res.ok) {
        const text = await res.text()
        if (res.status >= 400 && res.status < 500) {
          throw new Error(`Client error ${res.status}: ${text}`)
        } else if (res.status >= 500) {
          throw new Error(`Server error ${res.status}: ${text}`)
        } else {
          throw new Error(`Unexpected status ${res.status}: ${text}`)
        }
      }

      const assistantMsg = await res.json()
      // 4️⃣ Append the assistant’s reply
      messages = [
        ...messages,
        { role: 'assistant', content: assistantMsg.content }
      ]

    } catch (err) {
      console.error('Chat request failed', err)
      let assistantMessage = '🚨 Sorry, something went wrong.'
      if (err instanceof TypeError) {
        assistantMessage =
          '📡 Network issue. Please check your connection and try again.'
      } else if (err.message?.startsWith('Client error')) {
        assistantMessage =
          '🙋 There seems to be a problem with your request. Please adjust it and retry.'
      } else if (err.message?.startsWith('Server error')) {
        assistantMessage =
          '🛠️ The server is having trouble. Please try again later.'
      }
      messages = [...messages, { role: 'assistant', content: assistantMessage }]
    }
  }
</script>

<main class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">PO Drafter Chat Wizard</h1>
  <div class="chat-area mb-4 h-96 overflow-y-auto border p-2 rounded">
    {#each messages as msg}
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
  <form on:submit|preventDefault={send} class="flex">
    <input
      class="flex-grow border p-2 rounded-l"
      bind:value={input}
      placeholder="Type your message..."
    />
    <button type="submit" class="bg-blue-500 text-white px-4 rounded-r">
      Send
    </button>
  </form>
</main>
