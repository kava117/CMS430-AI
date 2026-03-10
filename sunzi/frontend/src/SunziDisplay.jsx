import './SunziDisplay.css'

const TONE_CONFIG = {
  neutral:       { color: '#4A9EFF', animationClass: 'pulse-slow',  label: 'EVALUATING' },
  probing:       { color: '#FFB347', animationClass: 'pulse-fast',  label: 'PROBING' },
  contemptuous:  { color: '#CC2233', animationClass: 'still',       label: 'CONTEMPTUOUS' },
  illuminated:   { color: '#FFFFFF', animationClass: 'flare',       label: 'ILLUMINATED' },
  recalibrating: { color: '#888888', animationClass: 'glitch',      label: 'RECALIBRATING' },
}

export default function SunziDisplay({ tone }) {
  const config = TONE_CONFIG[tone] || TONE_CONFIG.neutral
  const { color, animationClass, label } = config

  return (
    <div className="sunzi-display panel">
      <svg
        viewBox="0 0 200 200"
        className={`sigil ${animationClass}`}
        aria-label="SUNZI sigil"
        style={{ '--sigil-color': color }}
      >
        {/* Central hexagon */}
        <polygon
          points="100,60 134,80 134,120 100,140 66,120 66,80"
          fill="none"
          stroke={color}
          strokeWidth="1.5"
        />
        {/* Radiating lines */}
        <line x1="100" y1="10"  x2="100" y2="60"  stroke={color} strokeWidth="1" />
        <line x1="160" y1="45" x2="134" y2="80"  stroke={color} strokeWidth="1" />
        <line x1="160" y1="155" x2="134" y2="120" stroke={color} strokeWidth="1" />
        <line x1="100" y1="190" x2="100" y2="140" stroke={color} strokeWidth="1" />
        <line x1="40"  y1="155" x2="66"  y2="120" stroke={color} strokeWidth="1" />
        <line x1="40"  y1="45"  x2="66"  y2="80"  stroke={color} strokeWidth="1" />
        {/* Center point */}
        <circle cx="100" cy="100" r="3" fill={color} />
        {/* Inner lines to center */}
        <line x1="100" y1="100" x2="100" y2="60"  stroke={color} strokeWidth="0.5" opacity="0.4" />
        <line x1="100" y1="100" x2="134" y2="80"  stroke={color} strokeWidth="0.5" opacity="0.4" />
        <line x1="100" y1="100" x2="134" y2="120" stroke={color} strokeWidth="0.5" opacity="0.4" />
        <line x1="100" y1="100" x2="100" y2="140" stroke={color} strokeWidth="0.5" opacity="0.4" />
        <line x1="100" y1="100" x2="66"  y2="120" stroke={color} strokeWidth="0.5" opacity="0.4" />
        <line x1="100" y1="100" x2="66"  y2="80"  stroke={color} strokeWidth="0.5" opacity="0.4" />
      </svg>
      <div className="tone-label" style={{ color }}>
        TONE STATE: {label}
      </div>
    </div>
  )
}
