import { useState } from 'react'
import SunziDisplay from './SunziDisplay'
import ChatInterface from './ChatInterface'
import TopicGraph from './TopicGraph'
import StageProgress from './StageProgress'
import ScoreReadout from './ScoreReadout'
import './App.css'

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
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

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
    <div className="app" data-tone={gameState.tone}>
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
