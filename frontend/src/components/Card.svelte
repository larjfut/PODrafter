<script lang="ts">
  export let className = ''
</script>

<div class={`glass p-6 shadow-e3 ${className}`}>
  <slot />
</div>
