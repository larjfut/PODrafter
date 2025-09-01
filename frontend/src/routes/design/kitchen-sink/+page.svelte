<script lang="ts">
  import Button from '$src/components/Button.svelte'
  import Card from '$src/components/Card.svelte'
  import Input from '$src/components/Input.svelte'
  import Skeleton from '$src/components/Skeleton.svelte'
  import CommandMenu from '$src/components/CommandMenu.svelte'
  import { tilt } from '$src/lib/tilt'

  let cmdOpen = false
  const items = [
    { title: 'Home', href: '/' },
    { title: 'Welcome', href: '/welcome' },
    { title: 'Kitchen Sink', href: '/design/kitchen-sink' },
  ]

  function toggleReduceEffects() {
    document.documentElement.classList.toggle('reduce-effects')
  }
</script>

<svelte:head>
  <title>Design System Kitchen Sink</title>
</svelte:head>

<section class="container mx-auto p-6 space-y-8">
  <h1>Design System Kitchen Sink</h1>

  <div class="flex items-center gap-3">
    <Button variant="primary">Primary CTA</Button>
    <Button variant="secondary">Secondary</Button>
    <Button variant="danger">Destructive</Button>
    <Button variant="primary" loading>Loading</Button>
    <button class="ml-auto text-sm underline" on:click={toggleReduceEffects}>Toggle Reduce Effects</button>
  </div>

  <div class="grid md:grid-cols-2 gap-6">
    <Card className="min-h-[160px]" use:tilt>
      <h2 class="mb-2">Card (e3 glass)</h2>
      <p class="muted">With specular highlight and grain.</p>
    </Card>
    <Card className="min-h-[160px]">
      <h2 class="mb-2">Form Controls</h2>
      <div class="grid gap-3">
        <Input label="Full name" placeholder="Jane Doe" />
        <Input label="Email" type="email" placeholder="jane@example.com" />
      </div>
    </Card>
  </div>

  <div>
    <h2 class="mb-2">Skeleton</h2>
    <div class="grid grid-cols-3 gap-3">
      <Skeleton className="h-20" />
      <Skeleton className="h-20" />
      <Skeleton className="h-20" />
    </div>
  </div>

  <div>
    <h2 class="mb-2">Data Viz Demo</h2>
    <div class="grid gap-4 md:grid-cols-2">
      <Card>
        <h3 class="mb-2">Series</h3>
        <div class="space-y-2">
          <div class="h-3 w-3/4 dv-pos pattern-diag rounded-pill" aria-label="Positive series"></div>
          <div class="h-3 w-2/5 dv-neg pattern-cross rounded-pill" aria-label="Negative series"></div>
          <div class="h-3 w-1/2 dv-neutral pattern-dots rounded-pill" aria-label="Neutral series"></div>
        </div>
        <div class="mt-3 text-xs dv-callout">Deep Purple callout label</div>
      </Card>
      <Card>
        <h3 class="mb-2">Axis & Callout</h3>
        <div class="flex items-center gap-4 text-sm">
          <span class="dv-axis-tick">0</span>
          <span class="dv-axis-tick">10</span>
          <span class="dv-axis-tick">20</span>
          <span class="dv-axis-tick">30</span>
        </div>
        <div class="mt-3 dv-plate inline-block">Over-image text on blur plate</div>
      </Card>
    </div>
  </div>

  <div>
    <h2 class="mb-2">Command Menu</h2>
    <p class="muted mb-2">Press ⌘/Ctrl+K</p>
    <Button variant="secondary" on:click={() => (cmdOpen = true)}>Open Command Menu</Button>
    <CommandMenu {items} bind:open={cmdOpen} />
  </div>
</section>
