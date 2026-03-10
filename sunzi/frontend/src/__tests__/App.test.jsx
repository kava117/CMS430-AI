import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import App from '../App'

const INITIAL_STATE = {
  topic: 'deception', stage: 'introduction', tone: 'neutral', score: 50,
  stage_turn_count: 0, tone_signal_count: 0, topic_index: 0, conversation_complete: false,
}

function mockFetch(state = INITIAL_STATE, response_text = 'SUNZI speaks.') {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ state, response_text, classification: 'understanding' }),
    })
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('App', () => {
  it('renders without crashing', () => {
    mockFetch()
    render(<App />)
    expect(document.body).toBeTruthy()
  })

  it('renders the header text', () => {
    mockFetch()
    render(<App />)
    expect(screen.getByText(/STRATEGIC INTELLIGENCE ASSESSMENT MODULE/i)).toBeTruthy()
  })

  it('initial isLoading is false — input is enabled', () => {
    mockFetch()
    render(<App />)
    const input = screen.getByRole('textbox')
    expect(input).not.toBeDisabled()
  })

  it('initial messages array is empty — no messages rendered', () => {
    mockFetch()
    render(<App />)
    expect(screen.queryByText(/> SUNZI:/)).toBeNull()
    expect(screen.queryByText(/> YOU:/)).toBeNull()
  })

  it('sets isLoading true during fetch (input disabled)', async () => {
    let resolveFetch
    global.fetch = vi.fn(() =>
      new Promise((resolve) => { resolveFetch = resolve })
    )
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    // isLoading should be true now — input area replaced by loading text
    expect(screen.getByText(/PROCESSING INPUT/)).toBeTruthy()
    // Resolve
    resolveFetch({
      json: () => Promise.resolve({ state: INITIAL_STATE, response_text: 'hi', classification: 'understanding' })
    })
  })

  it('after fetch, messages contain user and sunzi entries', async () => {
    mockFetch()
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByText(/> YOU:/)).toBeTruthy()
      expect(screen.getByText(/> SUNZI:/)).toBeTruthy()
    })
  })

  it('after fetch, gameState is updated from response', async () => {
    mockFetch({ ...INITIAL_STATE, tone: 'probing', score: 45 })
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByText(/PROBING/i)).toBeTruthy()
    })
  })

  it('after fetch, isLoading is false and input re-enabled', async () => {
    mockFetch()
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByRole('textbox')).not.toBeDisabled()
    })
  })

  it('fetch called with correct URL and body', async () => {
    mockFetch()
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'test input')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/turn', expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('test input'),
      }))
    })
  })

  it('fetch body contains session_id', async () => {
    mockFetch()
    const user = userEvent.setup()
    render(<App />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      const body = JSON.parse(global.fetch.mock.calls[0][1].body)
      expect(body.session_id).toBeTruthy()
      expect(typeof body.session_id).toBe('string')
    })
  })
})
