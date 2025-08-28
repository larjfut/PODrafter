<script lang="ts">
  export let id = crypto.randomUUID()
  export let label = ''
  export let type = 'text'
  export let value: string | number | undefined
  export let placeholder = ''
  export let help = ''
  export let error = ''
  export let required = false
</script>
<div class="space-y-1.5">
  {#if label}<label class="block text-sm font-medium text-gray-700" for={id}>
    {label}{#if required}<span class="text-red-500"> *</span>{/if}
  </label>{/if}
  <input class={`input ${error ? 'input-error' : ''}`} {id} {type} {placeholder} {required} bind:value />
  {#if error}<p class="text-xs text-red-600">{error}</p>
  {:else if help}<p class="text-xs text-gray-500">{help}</p>{/if}
</div>
