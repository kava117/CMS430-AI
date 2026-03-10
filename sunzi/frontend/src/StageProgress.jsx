import './StageProgress.css'

const STAGES = [
  { key: 'introduction', label: 'INTRO' },
  { key: 'examination',  label: 'EXAM' },
  { key: 'challenge',    label: 'CHALLENGE' },
  { key: 'resolution',   label: 'RESOLUTION' },
]

export default function StageProgress({ stage }) {
  const currentIndex = STAGES.findIndex((s) => s.key === stage)

  return (
    <div className="stage-progress panel">
      <div className="stage-segments">
        {STAGES.map((s, i) => {
          const state = i < currentIndex ? 'completed' : i === currentIndex ? 'current' : 'upcoming'
          return (
            <div key={s.key} className={`stage-segment stage-segment--${state}`} data-state={state}>
              {s.label}
            </div>
          )
        })}
      </div>
    </div>
  )
}
