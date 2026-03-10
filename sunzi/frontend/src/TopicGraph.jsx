import './TopicGraph.css'

export default function TopicGraph({ topicIndex, topics, stage }) {
  return (
    <div className="topic-graph panel">
      <div className="topic-nodes">
        {topics.map((topic, i) => {
          const state = i < topicIndex ? 'completed' : i === topicIndex ? 'current' : 'upcoming'
          return (
            <div key={topic.key} className="topic-node-wrapper">
              <div className={`topic-node topic-node--${state}`} data-state={state}>
                {state === 'completed' && <span className="node-dot">●</span>}
                {state === 'current' && <span className="node-dot pulse">◉</span>}
                {state === 'upcoming' && <span className="node-dot dim">○</span>}
              </div>
              <div className="topic-label">{topic.label}</div>
              {state === 'current' && (
                <div className="stage-label">{stage.toUpperCase()}</div>
              )}
              {i < topics.length - 1 && (
                <div className={`connector connector--${i < topicIndex ? 'completed' : 'upcoming'}`} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
