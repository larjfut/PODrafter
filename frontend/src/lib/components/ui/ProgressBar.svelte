<script lang="ts">
  export let value = 0
  export let color: 'primary' | 'success' | 'warning' | 'error' = 'primary'
  const map = {primary:'var(--color-terra)',success:'var(--color-success)',warning:'var(--color-warning)',error:'var(--color-error)'} as const
</script>
<div class="w-full h-2 rounded-full" style="background: color-mix(in srgb, var(--color-border) 60%, transparent);">
  <div class="h-2 rounded-full transition-all" style={`width:${Math.max(0,Math.min(100,value))}%; background:${map[color]};`}/>
</div>
