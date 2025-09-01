<script lang="ts">
  export let className = ''
  export let rounded = 'rounded-md'
</script>

<div class={`relative overflow-hidden bg-slate-200 ${rounded} ${className}`} aria-hidden="true">
  <div class="absolute inset-0 bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] animate-shimmer"></div>
</div>
