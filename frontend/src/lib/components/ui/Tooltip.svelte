<script lang="ts">
  export let content = ''
</script>

<span class="relative inline-block group">
  <slot />
  <span
    role="tooltip"
    class="pointer-events-none absolute left-1/2 top-full mt-1 -translate-x-1/2 rounded bg-gray-700 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
  >
    {content}
  </span>
</span>

