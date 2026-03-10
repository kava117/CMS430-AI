import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import ChatInterface from '../ChatInterface'

const noop = () => {}

describe('ChatInterface', () => {
  it('renders with empty messages — no message elements', () => {
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={false} tone="neutral" />)
    expect(screen.queryByText(/> SUNZI:/)).toBeNull()
    expect(screen.queryByText(/> YOU:/)).toBeNull()
  })

  it('renders SUNZI messages with correct prefix', () => {
    const messages = [{ role: 'sunzi', content: 'Assessment begins.' }]
    render(<ChatInterface messages={messages} onSubmit={noop} isLoading={false} tone="neutral" />)
    expect(screen.getByText(/> SUNZI:/)).toBeTruthy()
    expect(screen.getByText(/Assessment begins/)).toBeTruthy()
  })

  it('renders user messages with correct prefix', () => {
    const messages = [{ role: 'user', content: 'My answer here.' }]
    render(<ChatInterface messages={messages} onSubmit={noop} isLoading={false} tone="neutral" />)
    expect(screen.getByText(/> YOU:/)).toBeTruthy()
  })

  it('input field is present', () => {
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={false} tone="neutral" />)
    expect(screen.getByRole('textbox')).toBeTruthy()
  })

  it('clicking submit calls onSubmit with input value', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(<ChatInterface messages={[]} onSubmit={onSubmit} isLoading={false} tone="neutral" />)
    await user.type(screen.getByRole('textbox'), 'test answer')
    await user.click(screen.getByRole('button'))
    expect(onSubmit).toHaveBeenCalledWith('test answer')
  })

  it('pressing Enter calls onSubmit', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(<ChatInterface messages={[]} onSubmit={onSubmit} isLoading={false} tone="neutral" />)
    await user.type(screen.getByRole('textbox'), 'press enter{Enter}')
    expect(onSubmit).toHaveBeenCalledWith('press enter')
  })

  it('after submit, input field is cleared', async () => {
    const user = userEvent.setup()
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={false} tone="neutral" />)
    const input = screen.getByRole('textbox')
    await user.type(input, 'something')
    await user.keyboard('{Enter}')
    expect(input.value).toBe('')
  })

  it('isLoading=true disables input and button', () => {
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={true} tone="neutral" />)
    expect(screen.queryByRole('textbox')).toBeNull()
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('isLoading=true displays PROCESSING INPUT text', () => {
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={true} tone="neutral" />)
    expect(screen.getByText(/PROCESSING INPUT/)).toBeTruthy()
  })

  it('isLoading=false removes loading text', () => {
    render(<ChatInterface messages={[]} onSubmit={noop} isLoading={false} tone="neutral" />)
    expect(screen.queryByText(/PROCESSING INPUT/)).toBeNull()
  })

  it('multiple messages render in correct order', () => {
    const messages = [
      { role: 'sunzi', content: 'First.' },
      { role: 'user', content: 'Second.' },
      { role: 'sunzi', content: 'Third.' },
    ]
    render(<ChatInterface messages={messages} onSubmit={noop} isLoading={false} tone="neutral" />)
    const allText = document.body.textContent
    expect(allText.indexOf('First.')).toBeLessThan(allText.indexOf('Second.'))
    expect(allText.indexOf('Second.')).toBeLessThan(allText.indexOf('Third.'))
  })

  it('onSubmit is not called when input is empty', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(<ChatInterface messages={[]} onSubmit={onSubmit} isLoading={false} tone="neutral" />)
    await user.keyboard('{Enter}')
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
