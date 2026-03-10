import { useRef, useEffect, useState } from 'react'
import './ChatInterface.css'

export default function ChatInterface({ messages, onSubmit, isLoading, tone }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    const trimmed = input.trim()
    if (!trimmed) return
    setInput('')
    onSubmit(trimmed)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="chat-interface panel" style={{ '--tone-color': toneColor(tone) }}>
      <div className="message-list" role="log" aria-live="polite">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message message--${msg.role}`}
          >
            {msg.role === 'sunzi'
              ? <span className="prefix sunzi-prefix">&gt; SUNZI: </span>
              : <span className="prefix user-prefix">&gt; YOU: </span>
            }
            {msg.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-row">
        {isLoading ? (
          <span className="loading-text">PROCESSING INPUT...</span>
        ) : (
          <>
            <input
              className="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder=">"
              aria-label="Your response"
            />
            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={isLoading}
            >
              SUBMIT
            </button>
          </>
        )}
      </div>
    </div>
  )
}

function toneColor(tone) {
  const map = {
    neutral: '#4A9EFF',
    probing: '#FFB347',
    contemptuous: '#CC2233',
    illuminated: '#FFFFFF',
    recalibrating: '#888888',
  }
  return map[tone] || map.neutral
}
