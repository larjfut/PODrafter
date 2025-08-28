<script lang="ts">
  export let hover = false
  export let padded = true
</script>
<section class={`card ${hover ? 'hover' : ''}`}>
  <header class="px-4 pt-4 pb-2"><slot name="header"/></header>
  <div class={`${padded ? 'p-4' : ''}`}><slot/></div>
  {#if $$slots.footer}<footer class="px-4 pt-2 pb-4"><slot name="footer"/></footer>{/if}
</section>
