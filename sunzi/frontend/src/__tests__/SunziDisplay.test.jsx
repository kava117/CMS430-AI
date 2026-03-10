import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SunziDisplay from '../SunziDisplay'

const TONES = ['neutral', 'probing', 'contemptuous', 'illuminated', 'recalibrating']

describe('SunziDisplay', () => {
  TONES.forEach((tone) => {
    it(`renders without crashing for tone: ${tone}`, () => {
      render(<SunziDisplay tone={tone} />)
      expect(document.body).toBeTruthy()
    })
  })

  it('renders an SVG element', () => {
    const { container } = render(<SunziDisplay tone="neutral" />)
    expect(container.querySelector('svg')).toBeTruthy()
  })

  it('neutral tone applies pulse-slow animation class', () => {
    const { container } = render(<SunziDisplay tone="neutral" />)
    expect(container.querySelector('.pulse-slow')).toBeTruthy()
  })

  it('probing tone applies pulse-fast animation class', () => {
    const { container } = render(<SunziDisplay tone="probing" />)
    expect(container.querySelector('.pulse-fast')).toBeTruthy()
  })

  it('contemptuous tone applies still animation class', () => {
    const { container } = render(<SunziDisplay tone="contemptuous" />)
    expect(container.querySelector('.still')).toBeTruthy()
  })

  it('illuminated tone applies flare animation class', () => {
    const { container } = render(<SunziDisplay tone="illuminated" />)
    expect(container.querySelector('.flare')).toBeTruthy()
  })

  it('recalibrating tone applies glitch animation class', () => {
    const { container } = render(<SunziDisplay tone="recalibrating" />)
    expect(container.querySelector('.glitch')).toBeTruthy()
  })

  it('displays tone label text', () => {
    render(<SunziDisplay tone="neutral" />)
    expect(screen.getByText(/TONE STATE:/)).toBeTruthy()
  })

  it('neutral tone label reads EVALUATING', () => {
    render(<SunziDisplay tone="neutral" />)
    expect(screen.getByText(/TONE STATE: EVALUATING/)).toBeTruthy()
  })

  it('illuminated tone label reads ILLUMINATED', () => {
    render(<SunziDisplay tone="illuminated" />)
    expect(screen.getByText(/TONE STATE: ILLUMINATED/)).toBeTruthy()
  })

  it('recalibrating tone label reads RECALIBRATING', () => {
    render(<SunziDisplay tone="recalibrating" />)
    expect(screen.getByText(/TONE STATE: RECALIBRATING/)).toBeTruthy()
  })

  it('unknown tone falls back to neutral without crashing', () => {
    render(<SunziDisplay tone="unknown_value" />)
    expect(document.body).toBeTruthy()
  })
})
