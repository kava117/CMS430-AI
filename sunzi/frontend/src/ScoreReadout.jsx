import './ScoreReadout.css'

export default function ScoreReadout({ score, tone }) {
  const clamped = Math.max(0, Math.min(100, score))

  return (
    <div className="score-readout panel">
      <div className="score-label">HUMAN INTELLIGENCE ASSESSMENT</div>
      <div className="score-bar-wrapper">
        <div
          className="score-bar-fill"
          style={{ width: `${clamped}%` }}
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
          role="progressbar"
        />
      </div>
      <div className="score-value">{clamped}%</div>
    </div>
  )
}
