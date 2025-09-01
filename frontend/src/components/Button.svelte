<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'danger' = 'primary'
  export let loading: boolean = false
  export let type: 'button' | 'submit' | 'reset' = 'button'
  export let disabled: boolean = false
  export let className = ''
  export let confirm: boolean = false

  $: base = 'relative inline-flex items-center justify-center gap-2 px-4 h-11 rounded-control font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-400 active:translate-y-[1px] disabled:opacity-50 disabled:pointer-events-none'
  $: color = variant === 'primary'
    ? 'bg-[color:var(--mint-deep)] text-white '
    : variant === 'secondary'
    ? 'bg-indigo-600/10 text-indigo-700 hover:bg-indigo-600/15 dark:text-indigo-200 '
    : 'bg-[color:var(--coral)] text-white'
  $: confirmRing = variant === 'danger' && confirm ? 'ring-2 ring-[color:var(--brick)] ring-offset-2 ring-offset-white border border-[color:var(--brick)]' : ''

  $: sheen = 'before:content-[\'\'] before:absolute before:inset-y-0 before:-left-1/2 before:w-1/3 before:bg-white/40 before:rounded-inherit before:opacity-0 hover:before:opacity-100 before:pointer-events-none before:animate-[sheen_1.1s_ease-in-out]'
  $: ambient = variant === 'primary' ? 'ambient-sweep' : ''
</script>

<button {type} class={`${base} ${color} ${confirmRing} ${sheen} ${ambient} ${className}`} {disabled}>
  {#if loading}
    <span class="inline-block h-4 w-4 rounded-full border-2 border-white/60 border-t-transparent animate-spin"></span>
  {/if}
  <slot />
</button>

<style>
  :global(.reduce-effects) .ambient-sweep { animation: none !important; }
  :global(.reduce-effects) button::before { display: none !important; }
</style>
