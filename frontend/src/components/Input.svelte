<script lang="ts">
  export let label = ''
  export let id = ''
  export let type: 'text' | 'email' | 'tel' | 'password' = 'text'
  export let value: string = ''
  export let placeholder = ''
  export let className = ''
  export let required: boolean = false
  export let disabled: boolean = false
  export let name = ''
  export let autocomplete = ''
  export let describedby = ''
  const inputId = id || `in-${Math.random().toString(36).slice(2)}`
  $: aria = describedby ? { 'aria-describedby': describedby } : {}
</script>

<label class="block text-sm font-medium text-[color:var(--muted-ink)]" for={inputId}>
  {label}{#if required}<span aria-hidden="true" class="text-[color:var(--coral)]">*</span>{/if}
</label>
<input
  {name}
  {autocomplete}
  class={`mt-1 w-full h-11 px-3 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1 backdrop-blur-glass ${className}`}
  {id}
  bind:value
  {type}
  {placeholder}
  {required}
  {disabled}
  {...aria}
/>
