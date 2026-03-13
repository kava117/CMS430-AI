import { useRef, useEffect, useState } from 'react'
import './ChatInterface.css'

export const TYPEWRITER_SPEED = 18
export const BOOT_ANIM_MS = 1800

function TypewriterText({ text, speed = TYPEWRITER_SPEED }) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    setDisplayed('')
    setDone(false)
    let i = 0
    const interval = setInterval(() => {
      i++
      setDisplayed(text.slice(0, i))
      if (i >= text.length) {
        clearInterval(interval)
        setDone(true)
      }
    }, speed)
    return () => clearInterval(interval)
  }, [text, speed])

  return (
    <pre className="system-blurb">
      {displayed}
      {!done && <span className="typewriter-cursor">▋</span>}
    </pre>
  )
}

export default function ChatInterface({ messages, onSubmit, isLoading, tone }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea to fit content
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
  }, [input])

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
            {msg.role === 'system' ? (
              <TypewriterText text={msg.content} />
            ) : msg.role === 'sunzi' ? (
              <><span className="prefix sunzi-prefix">&gt; SUNZI: </span>{msg.content}</>
            ) : (
              <><span className="prefix user-prefix">&gt; YOU: </span>{msg.content}</>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-row">
        {isLoading ? (
          <span className="loading-text">PROCESSING INPUT...</span>
        ) : (
          <>
            <textarea
              ref={textareaRef}
              className="chat-input"
              rows={1}
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
