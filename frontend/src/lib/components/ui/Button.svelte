<script lang="ts">
  export let variant: 'primary' | 'ghost' | 'danger' = 'primary'
  export let size: 'sm' | 'md' | 'lg' = 'md'
  export let loading = false
  export let type: 'button' | 'submit' | 'reset' = 'button'
  export let disabled = false
</script>
<button class={`btn btn-${variant} ${size !== 'md' ? 'btn-'+size : ''} ${loading ? 'opacity-80 cursor-wait' : ''}`}
  {type} disabled={disabled || loading} aria-busy={loading}>
  <slot />
</button>
