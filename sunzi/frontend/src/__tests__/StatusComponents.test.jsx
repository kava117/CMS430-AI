import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import TopicGraph from '../TopicGraph'
import StageProgress from '../StageProgress'
import ScoreReadout from '../ScoreReadout'

const TOPICS = [
  { key: 'deception', label: 'DECEPTION' },
  { key: 'self_knowledge', label: 'SELF-KNOWLEDGE' },
  { key: 'adaptability', label: 'ADAPTABILITY' },
  { key: 'victory', label: 'VICTORY' },
]

// --- TopicGraph ---
describe('TopicGraph', () => {
  it('renders 4 topic nodes', () => {
    const { container } = render(<TopicGraph topicIndex={0} topics={TOPICS} stage="introduction" />)
    expect(container.querySelectorAll('.topic-node-wrapper').length).toBe(4)
  })

  it('all 4 topic labels appear in DOM', () => {
    render(<TopicGraph topicIndex={0} topics={TOPICS} stage="introduction" />)
    expect(screen.getByText('DECEPTION')).toBeTruthy()
    expect(screen.getByText('SELF-KNOWLEDGE')).toBeTruthy()
    expect(screen.getByText('ADAPTABILITY')).toBeTruthy()
    expect(screen.getByText('VICTORY')).toBeTruthy()
  })

  it('topicIndex=0 — first node is current, rest upcoming', () => {
    const { container } = render(<TopicGraph topicIndex={0} topics={TOPICS} stage="introduction" />)
    const nodes = container.querySelectorAll('.topic-node')
    expect(nodes[0].classList.contains('topic-node--current')).toBe(true)
    expect(nodes[1].classList.contains('topic-node--upcoming')).toBe(true)
    expect(nodes[2].classList.contains('topic-node--upcoming')).toBe(true)
    expect(nodes[3].classList.contains('topic-node--upcoming')).toBe(true)
  })

  it('topicIndex=2 — first two completed, third current, fourth upcoming', () => {
    const { container } = render(<TopicGraph topicIndex={2} topics={TOPICS} stage="challenge" />)
    const nodes = container.querySelectorAll('.topic-node')
    expect(nodes[0].classList.contains('topic-node--completed')).toBe(true)
    expect(nodes[1].classList.contains('topic-node--completed')).toBe(true)
    expect(nodes[2].classList.contains('topic-node--current')).toBe(true)
    expect(nodes[3].classList.contains('topic-node--upcoming')).toBe(true)
  })

  it('current stage label appears below current node', () => {
    render(<TopicGraph topicIndex={1} topics={TOPICS} stage="examination" />)
    expect(screen.getByText('EXAMINATION')).toBeTruthy()
  })

  it('topicIndex=3 with resolution — last node is current', () => {
    const { container } = render(<TopicGraph topicIndex={3} topics={TOPICS} stage="resolution" />)
    const nodes = container.querySelectorAll('.topic-node')
    expect(nodes[3].classList.contains('topic-node--current')).toBe(true)
  })
})

// --- StageProgress ---
describe('StageProgress', () => {
  it('renders 4 stage segments', () => {
    const { container } = render(<StageProgress stage="introduction" />)
    expect(container.querySelectorAll('.stage-segment').length).toBe(4)
  })

  it('all 4 stage names appear in DOM', () => {
    render(<StageProgress stage="introduction" />)
    expect(screen.getByText('INTRO')).toBeTruthy()
    expect(screen.getByText('EXAM')).toBeTruthy()
    expect(screen.getByText('CHALLENGE')).toBeTruthy()
    expect(screen.getByText('RESOLUTION')).toBeTruthy()
  })

  it('introduction — first segment is current, rest upcoming', () => {
    const { container } = render(<StageProgress stage="introduction" />)
    const segs = container.querySelectorAll('.stage-segment')
    expect(segs[0].classList.contains('stage-segment--current')).toBe(true)
    expect(segs[1].classList.contains('stage-segment--upcoming')).toBe(true)
  })

  it('examination — first completed, second current', () => {
    const { container } = render(<StageProgress stage="examination" />)
    const segs = container.querySelectorAll('.stage-segment')
    expect(segs[0].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[1].classList.contains('stage-segment--current')).toBe(true)
  })

  it('challenge — first two completed, third current', () => {
    const { container } = render(<StageProgress stage="challenge" />)
    const segs = container.querySelectorAll('.stage-segment')
    expect(segs[0].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[1].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[2].classList.contains('stage-segment--current')).toBe(true)
  })

  it('resolution — first three completed, fourth current', () => {
    const { container } = render(<StageProgress stage="resolution" />)
    const segs = container.querySelectorAll('.stage-segment')
    expect(segs[0].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[1].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[2].classList.contains('stage-segment--completed')).toBe(true)
    expect(segs[3].classList.contains('stage-segment--current')).toBe(true)
  })
})

// --- ScoreReadout ---
describe('ScoreReadout', () => {
  it('renders HUMAN INTELLIGENCE ASSESSMENT label', () => {
    render(<ScoreReadout score={50} tone="neutral" />)
    expect(screen.getByText(/HUMAN INTELLIGENCE ASSESSMENT/)).toBeTruthy()
  })

  it('score=50 — progress bar width is 50%', () => {
    const { container } = render(<ScoreReadout score={50} tone="neutral" />)
    const bar = container.querySelector('.score-bar-fill')
    expect(bar.style.width).toBe('50%')
  })

  it('score=0 — bar width is 0%', () => {
    const { container } = render(<ScoreReadout score={0} tone="neutral" />)
    const bar = container.querySelector('.score-bar-fill')
    expect(bar.style.width).toBe('0%')
  })

  it('score=100 — bar width is 100%', () => {
    const { container } = render(<ScoreReadout score={100} tone="neutral" />)
    const bar = container.querySelector('.score-bar-fill')
    expect(bar.style.width).toBe('100%')
  })

  it('score=75 — bar width is 75%', () => {
    const { container } = render(<ScoreReadout score={75} tone="neutral" />)
    const bar = container.querySelector('.score-bar-fill')
    expect(bar.style.width).toBe('75%')
  })

  it('score value is displayed as text', () => {
    render(<ScoreReadout score={42} tone="neutral" />)
    expect(screen.getByText('42%')).toBeTruthy()
  })
})
