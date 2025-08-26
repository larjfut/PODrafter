import { render, screen } from '@testing-library/svelte'
import { describe, it, expect } from 'vitest'
import Page from '../src/routes/+page.svelte'

describe('Page', () => {
  it('renders PO Drafter heading', () => {
    render(Page)
    const heading = screen.getByRole('heading', {
      level: 1,
      name: /PO Drafter Chat Wizard/
    })
    expect(heading).toBeInTheDocument()
  })
})
