<script lang="ts">
  export let title = ''
  let open = false
</script>
<nav class="navbar">
  <div class="mx-auto max-w-7xl px-4">
    <div class="flex h-14 items-center justify-between">
      <div class="flex items-center gap-3"><slot name="logo"/>{#if title}<h1 class="text-sm font-semibold">{title}</h1>{/if}</div>
      <div class="hidden md:flex items-center gap-2"><slot name="actions"/></div>
      <button class="md:hidden btn btn-ghost btn-sm" on:click={() => open = !open} aria-expanded={open}>Menu</button>
    </div>
    {#if open}<div class="md:hidden py-2 border-t" style="border-color:var(--color-border)"><slot name="actions"/></div>{/if}
  </div>
</nav>
