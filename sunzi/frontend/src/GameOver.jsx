import './GameOver.css'

const VERDICTS = [
  { min: 85, label: 'EXCEPTIONAL',  color: '#FFFFFF' },
  { min: 70, label: 'COMMENDABLE',  color: '#4A9EFF' },
  { min: 50, label: 'ADEQUATE',     color: '#4A9EFF' },
  { min: 30, label: 'MARGINAL',     color: '#FFB347' },
  { min: 0,  label: 'INSUFFICIENT', color: '#CC2233' },
]

function getVerdict(score) {
  return VERDICTS.find((v) => score >= v.min)
}

export default function GameOver({ score, epitaph, onRestart }) {
  const verdict = getVerdict(Math.max(0, Math.min(100, score)))

  return (
    <div className="game-over-overlay">
      <div className="game-over-panel panel">
        <div className="go-header">ASSESSMENT ARCHIVED</div>
        <div className="go-divider" />
        <div className="go-verdict-label">FINAL CLASSIFICATION</div>
        <div className="go-verdict" style={{ color: verdict.color }}>
          {verdict.label}
        </div>
        <div className="go-score-line">
          INTELLIGENCE INDEX: <span style={{ color: verdict.color }}>{score}</span>/100
        </div>
        <div className="go-subtext">
          {epitaph ?? 'COMPILING RECORD...'}
        </div>
        <div className="go-divider" />
        <button className="go-restart" onClick={onRestart}>
          REINITIALIZE ASSESSMENT
        </button>
      </div>
    </div>
  )
}
