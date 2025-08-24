import { render, screen } from '@testing-library/svelte'
import { describe, it, expect } from 'vitest'
import Page from '../src/routes/+page.svelte'

describe('Page', () => {
  it('renders heading', () => {
    render(Page)
    expect(screen.getByText('PO Drafter Chat Wizard')).toBeInTheDocument()
  })
})
