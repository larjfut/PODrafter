<script lang="ts">

  interface Message {
    role: 'user' | 'bot';
    content: string;
  }

  let messages: Message[] = [];
  let input = '';

  async function send() {
    if (input.trim().length === 0) return;

    // 1️⃣ Append user message
    messages = [...messages, { role: 'user', content: input }];

    // 2️⃣ Capture and clear input
    input = '';

    // 3️⃣ Call your backend
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://podrafter.fly.dev'
    try {
      const res = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // transform to OpenAI roles
          messages: messages.map(msg => ({
            role: msg.role === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        })
      });

      if (!res.ok) {
        throw new Error(`Error ${res.status}: ${await res.text()}`);
      }

      const assistantMsg = await res.json();
      // 4️⃣ Append the assistant’s reply
      messages = [
        ...messages,
        { role: 'bot', content: assistantMsg.content }
      ];

    } catch (err) {
      console.error(err);
      messages = [
        ...messages,
        { role: 'bot', content: '🚨 Sorry, something went wrong.' }
      ];
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
        class:text-left={msg.role === 'bot'}
      >
        <span
          class="p-2 rounded inline-block"
          class:bg-blue-200={msg.role === 'user'}
          class:bg-gray-200={msg.role === 'bot'}
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
