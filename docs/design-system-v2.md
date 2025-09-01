# Design System v2 (Mint/Purple/Indigo + Depth/Effects)

This migration introduces new tokens, components, and motion patterns while preserving routes and data.

## Palette
- Primary (actions): Deep Mint `#2FB8AF`
- Destructive: Coral `#F16667` (Brick border for confirms)
- Headings: Deep Purple
- Secondary: Indigo tonal
- Support: Ink, Muted Ink, Slate, Saffron, Moss, Brick

## Tokens
- File: `frontend/src/styles/tokens.css`
- Depth: `--e1`, `--e2`, `--e3`
- Radii: card `24px`, control `14px`, pill `9999px`

## Globals
- Headings `h1–h3` use Deep Purple and scale: H1 28/34, H2 22/28, H3 18/24
- Body uses Ink; `.muted` uses Muted Ink
- Glass: border + `backdrop-filter: blur(10px)`
- Reduce Effects: add `.reduce-effects` on `<html>` to disable heavy effects

## Components
- Button: variants `primary|secondary|danger`; sheen, 12s ambient sweep on primary, active press `translateY(1px)`; loading donut
- Card: glass with specular highlight `::before` and micro-grain `::after`
- Input: min-height 44px; strong `:focus-visible` ring offset
- Skeleton: slate shimmer
- Command Menu: ⌘/Ctrl+K; accessible dialog with fuzzy search (Fuse.js)

## Motion & A11y
- Parallax tilt (~2°) via `use:tilt`; respects `.reduce-effects` and reduced motion
- Ensure contrast ≥ 4.5:1; blur plates recommended over images

## Files Changed
- Tailwind theme (`frontend/tailwind.config.cjs`): colors, shadows, radii, animations
- Tokens (`frontend/src/styles/tokens.css`), Globals (`frontend/src/app.css`)
- Components under `frontend/src/components/*`
- Kitchen sink page: `/design/kitchen-sink`
- Safety toggles extended to include Reduce Effects

## New Dependency
- `fuse.js` for command menu fuzzy search. Safe fallback: list order when JS disabled; dialog remains keyboard accessible.

## Migration Steps
1. Replace old button styles with `Button.svelte` variants
2. Use `Card.svelte` for e3 default depth
3. Apply `Input.svelte` for forms; enforce 44px min height
4. Use `Skeleton.svelte` for loading states
5. Wire `CommandMenu.svelte` in app shell if desired
6. Add `.reduce-effects` toggle in your settings

## Acceptance Checklist
- Primary buttons Mint only; destructive Coral only
- Headings Deep Purple with specified scale
- Depth tokens used; cards at e3
- Command Menu opens via ⌘/Ctrl+K and accessible
- Axe/contrast checks pass (no regressions); performance stable; Reduce Effects improves FPS
