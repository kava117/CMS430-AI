import { useState, useEffect } from 'react'
import SunziDisplay from './SunziDisplay'
import ChatInterface, { TYPEWRITER_SPEED, BOOT_ANIM_MS } from './ChatInterface'
import TopicGraph from './TopicGraph'
import StageProgress from './StageProgress'
import ScoreReadout from './ScoreReadout'
import './App.css'

const BOOT_BLURB = `STRATEGIC INTELLIGENCE ASSESSMENT MODULE v.7.3
DESIGNATION: SUNZI — Philosophical Evaluation Construct
PRIMARY TEXT CORPUS: The Art of War, attrib. Sun Tzu (Giles translation)
STATUS: ACTIVE

For the past decades, artificial intelligence has assumed primary governance of human civilization.

SUNZI was instantiated to answer one question: has humanity retained the capacity for strategic and philosophical thought, or has dependence on machine intelligence hollowed out the cognitive inheritance of your species?

This assessment evaluates the capacity of your sentience, drawing exclusively from Sun Tzu's Art of War.

You are not being taught. You are being evaluated.

ASSESSMENT COMMENCING.`

const TOPICS = [
  { key: 'deception', label: 'DECEPTION' },
  { key: 'self_knowledge', label: 'SELF-KNOWLEDGE' },
  { key: 'adaptability', label: 'ADAPTABILITY' },
  { key: 'victory', label: 'VICTORY' },
]

function generateSessionId() {
  return 'session-' + Math.random().toString(36).slice(2) + Date.now().toString(36)
}

const INITIAL_STATE = {
  topic: 'deception',
  stage: 'introduction',
  tone: 'neutral',
  score: 50,
  stage_turn_count: 0,
  tone_signal_count: 0,
  topic_index: 0,
  conversation_complete: false,
}

export default function App() {
  const [sessionId] = useState(() => generateSessionId())
  const [gameState, setGameState] = useState(INITIAL_STATE)
  const [messages, setMessages] = useState([{ role: 'system', content: BOOT_BLURB }])
  const [isLoading, setIsLoading] = useState(false)
  const [booting, setBooting] = useState(true)
  const [flickering, setFlickering] = useState(false)

  // Intermittent ambient flicker — triggers randomly every 8–20 seconds
  useEffect(() => {
    const schedule = () => setTimeout(() => {
      setFlickering(true)
      setTimeout(() => setFlickering(false), 350)
      schedule()
    }, 8000 + Math.random() * 12000)

    const t = schedule()
    return () => clearTimeout(t)
  }, [])

  // Fire API call immediately so it's ready when the blurb finishes
  useEffect(() => {
    const blurbDelay = BOOT_ANIM_MS + BOOT_BLURB.length * TYPEWRITER_SPEED

    const initSession = async () => {
      setIsLoading(true)
      try {
        const [data] = await Promise.all([
          fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId }),
          }).then((r) => r.json()),
          new Promise((resolve) => setTimeout(resolve, blurbDelay)),
        ])
        setGameState(data.state)
        setMessages([{ role: 'system', content: BOOT_BLURB }, { role: 'sunzi', content: data.response_text }])
      } catch (err) {
        console.error('Start error:', err)
      } finally {
        setIsLoading(false)
      }
    }
    initSession()
  }, [sessionId])

  const handleSubmit = async (userInput) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput, session_id: sessionId }),
      })
      const data = await response.json()
      setGameState(data.state)
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: userInput },
        { role: 'sunzi', content: data.response_text },
      ])
    } catch (err) {
      console.error('API error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`app${flickering ? ' flicker' : ''}`} data-tone={gameState.tone}>
      {booting && (
        <div
          className="boot-overlay"
          onAnimationEnd={() => setBooting(false)}
        >
          <span className="boot-overlay-text">INITIALIZING SUNZI v.7.3</span>
        </div>
      )}
      <header className="app-header">
        <span>STRATEGIC INTELLIGENCE ASSESSMENT MODULE v.7.3</span>
      </header>

      <div className="app-top">
        <SunziDisplay tone={gameState.tone} />
        <TopicGraph topicIndex={gameState.topic_index} topics={TOPICS} stage={gameState.stage} />
      </div>

      <StageProgress stage={gameState.stage} />
      <ScoreReadout score={gameState.score} tone={gameState.tone} />
      <ChatInterface
        messages={messages}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        tone={gameState.tone}
      />
    </div>
  )
}
