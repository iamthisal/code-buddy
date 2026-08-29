import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const project = {
  id: 1, name: 'Crumb', prompt: 'A bakery called Crumb', current_version: 1,
  spec: { name: 'Crumb', kind: 'menu', description: 'A bakery called Crumb', tagline: 'Welcome to Crumb', sections: ['features', 'contact'], items: [], theme: { primary: '#256f68', background: '#ffffff', text: '#17252b', font: 'sans' } },
  validation: { valid: true, issues: [] }, preview_url: '/api/v1/projects/1/preview/index.html?v=1',
}

describe('project editor', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async (url: string, options?: RequestInit) => ({
      ok: true,
      json: async () => options?.method === 'POST' ? project : url.endsWith('/projects') ? [] : project,
    })))
  })
  afterEach(() => vi.unstubAllGlobals())

  it('creates a project and opens its preview', async () => {
    render(<App />)
    fireEvent.change(screen.getByLabelText('Describe your business'), { target: { value: 'A bakery called Crumb' } })
    fireEvent.click(screen.getByRole('button', { name: 'Generate site' }))
    await waitFor(() => expect(screen.getByTitle('Crumb preview')).toBeTruthy())
    expect(screen.getByText('Live preview')).toBeTruthy()
  })

  it('shows changed fields in version history', async () => {
    vi.stubGlobal('fetch', vi.fn(async (url: string, options?: RequestInit) => ({
      ok: true,
      json: async () => url.endsWith('/diff')
        ? { version: 2, changes: { 'theme.primary': { before: '#256f68', after: '#c34878' } } }
        : url.endsWith('/versions')
          ? [{ number: 2, instruction: 'change color to pink', created_at: '2026-01-01T00:00:00Z', spec: project.spec }]
          : options?.method === 'POST' ? project : [],
    })))
    render(<App />)
    fireEvent.change(screen.getByLabelText('Describe your business'), { target: { value: 'A bakery called Crumb' } })
    fireEvent.click(screen.getByRole('button', { name: 'Generate site' }))
    await screen.findByTitle('Crumb preview')
    fireEvent.click(screen.getByRole('tab', { name: 'History' }))
    await waitFor(() => expect(screen.getByText('Changed: primary')).toBeTruthy())
  })
})
