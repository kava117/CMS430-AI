import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('../ChatInterface', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, TYPEWRITER_SPEED: 0, BOOT_ANIM_MS: 0 }
})

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

/** Wait for the initial /api/start call to resolve (input becomes available). */
async function renderAndWaitForStart(state, response_text) {
  mockFetch(state, response_text)
  render(<App />)
  await waitFor(() => screen.getAllByText(/> SUNZI:/))
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
    expect(screen.getAllByText(/STRATEGIC INTELLIGENCE ASSESSMENT MODULE/i).length).toBeGreaterThan(0)
  })

  it('after start resolves, input is enabled', async () => {
    await renderAndWaitForStart()
    const input = screen.getByRole('textbox')
    expect(input).not.toBeDisabled()
  })

  it('after start resolves, opening SUNZI message is shown', async () => {
    await renderAndWaitForStart()
    expect(screen.getByText(/> SUNZI:/)).toBeTruthy()
  })

  it('sets isLoading true during fetch (input disabled)', async () => {
    // First resolve the start call
    mockFetch()
    render(<App />)
    await waitFor(() => screen.getByRole('textbox'))

    // Now set up a pending fetch for the turn call
    let resolveFetch
    global.fetch = vi.fn(() =>
      new Promise((resolve) => { resolveFetch = resolve })
    )
    const user = userEvent.setup()
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
    await renderAndWaitForStart()
    const user = userEvent.setup()
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByText(/> YOU:/)).toBeTruthy()
    })
    expect(screen.getAllByText(/> SUNZI:/).length).toBeGreaterThan(0)
  })

  it('after fetch, gameState is updated from response', async () => {
    await renderAndWaitForStart({ ...INITIAL_STATE, tone: 'probing', score: 45 })
    const user = userEvent.setup()
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByText(/PROBING/i)).toBeTruthy()
    })
  })

  it('after fetch, isLoading is false and input re-enabled', async () => {
    await renderAndWaitForStart()
    const user = userEvent.setup()
    const input = screen.getByRole('textbox')
    await user.type(input, 'my answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      expect(screen.getByRole('textbox')).not.toBeDisabled()
    })
  })

  it('fetch called with correct URL and body for turn', async () => {
    await renderAndWaitForStart()
    const user = userEvent.setup()
    const input = screen.getByRole('textbox')
    await user.type(input, 'test input')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      // /api/start is call 0; /api/turn is call 1
      expect(global.fetch).toHaveBeenCalledWith('/api/turn', expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('test input'),
      }))
    })
  })

  it('fetch body contains session_id', async () => {
    await renderAndWaitForStart()
    const user = userEvent.setup()
    const input = screen.getByRole('textbox')
    await user.type(input, 'answer')
    await user.keyboard('{Enter}')
    await waitFor(() => {
      // find the /api/turn call (second call, index 1)
      const turnCall = global.fetch.mock.calls.find(([url]) => url === '/api/turn')
      expect(turnCall).toBeTruthy()
      const body = JSON.parse(turnCall[1].body)
      expect(body.session_id).toBeTruthy()
      expect(typeof body.session_id).toBe('string')
    })
  })
})
