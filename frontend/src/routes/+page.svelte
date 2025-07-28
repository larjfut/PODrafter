<script lang="ts">
  import { onMount } from 'svelte';

  interface Message {
    role: 'user' | 'bot';
    content: string;
  }

  let messages: Message[] = [];
  let input = '';

  function send() {
    if (input.trim().length === 0) return;
    // append user message
    messages = [...messages, { role: 'user', content: input }];
    // reset input
    input = '';
    // TODO: call backend API for assistant response
    messages = [...messages, { role: 'bot', content: 'This is a placeholder response.' }];
  }
</script>

<main class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">PO Drafter Chat Wizard</h1>
  <div class="chat-area mb-4 h-96 overflow-y-auto border p-2 rounded">
    {#each messages as msg}
      <div class="my-2" class:text-right={msg.role === 'user'} class:text-left={msg.role === 'bot'}>
        <span class="p-2 rounded inline-block" class:bg-blue-200={msg.role === 'user'} class:bg-gray-200={msg.role === 'bot'}>{msg.content}</span>
      </div>
    {/each}
  </div>
  <form on:submit|preventDefault={send} class="flex">
    <input class="flex-grow border p-2 rounded-l" bind:value={input} placeholder="Type your message..." />
    <button type="submit" class="bg-blue-500 text-white px-4 rounded-r">Send</button>
  </form>
</main>