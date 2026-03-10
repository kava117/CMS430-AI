SPEC_FRONTEND.md — React Frontend

Overview
The frontend is a single-page React application that presents SUNZI as a visual terminal interface. The UI reflects the current state of the assessment in real time — tone, stage progress, topic position, and evaluation score all update with each conversational turn.
The aesthetic is cyberpunk terminal: dark background, monospace fonts, glowing geometric elements, minimal color used deliberately to signal state.

Component Structure
App.jsx
├── SunziDisplay.jsx        # Central visual — sigil + tone state
├── ChatInterface.jsx       # Message history + input
├── TopicGraph.jsx          # Four-node linear graph
├── StageProgress.jsx       # Stage indicator within current topic
└── ScoreReadout.jsx        # Evaluation score display

App.jsx
Root component. Manages:

Session ID (generate UUID on first load, store in component state)
Full application state (mirrored from backend response)
Conversation history array for display
API call orchestration

State shape:
javascriptconst [gameState, setGameState] = useState({
  topic: "deception",
  stage: "introduction",
  tone: "neutral",
  score: 50,
  stage_turn_count: 0,
  tone_signal_count: 0,
  topic_index: 0,
  conversation_complete: false
});

const [messages, setMessages] = useState([]);
const [isLoading, setIsLoading] = useState(false);
API call on submit:
javascriptconst handleSubmit = async (userInput) => {
  setIsLoading(true);
  const response = await fetch('/api/turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput, session_id: sessionId })
  });
  const data = await response.json();
  setGameState(data.state);
  setMessages(prev => [
    ...prev,
    { role: 'user', content: userInput },
    { role: 'sunzi', content: data.response_text }
  ]);
  setIsLoading(false);
};

SunziDisplay.jsx
The central visual element. Renders a geometric sigil that responds to the current tone state. This is the primary visual representation of SUNZI's character state.
Props: tone: string
Sigil Design
The sigil is an SVG-based geometric shape — a central hexagon with radiating lines, rendered with CSS animations. Each tone state changes color, animation speed, and geometry behavior.
Tone Visual Specifications
ToneColorAnimationGeometry Behaviorneutral#4A9EFF (cool blue)Slow, steady pulse (3s cycle)Clean lines, stableprobing#FFB347 (amber)Faster pulse (1.5s cycle), slight rotationLines tighten inwardcontemptuous#CC2233 (deep red)No animation — completely stillGeometry compresses, sharp anglesilluminated#FFFFFF (white)Single bright flare, then fade (0.8s)Geometry briefly expands then snaps backrecalibrating#888888 (grey)Glitch/flicker effect, irregular timingSigil fragments then reassembles
Implementation notes:

Use CSS keyframe animations keyed to tone class
The illuminated animation should play once (not loop) and trigger on tone entry
The recalibrating effect can be approximated with CSS clip-path animation or opacity flicker
SVG viewBox: 0 0 200 200, centered at 100 100

Example structure:
jsxconst toneConfig = {
  neutral: { color: '#4A9EFF', animationClass: 'pulse-slow' },
  probing: { color: '#FFB347', animationClass: 'pulse-fast' },
  contemptuous: { color: '#CC2233', animationClass: 'still' },
  illuminated: { color: '#FFFFFF', animationClass: 'flare' },
  recalibrating: { color: '#888888', animationClass: 'glitch' }
};
Below the sigil, display the tone label in monospace text:
TONE STATE: EVALUATING

ChatInterface.jsx
Displays the conversation history and the user input field.
Props: messages: array, onSubmit: function, isLoading: boolean
Message Display

SUNZI messages: left-aligned, prefixed with > SUNZI:, colored to match current tone
User messages: right-aligned, prefixed with > YOU:, grey
Monospace font throughout
Auto-scroll to bottom on new message

Input Field

Single text input + submit button
Disabled while isLoading is true
During loading, display: PROCESSING INPUT... in the input area
On submit: clear input field, call onSubmit
Support Enter key to submit

Visual Style

Dark background (#0A0A0F)
Thin border in current tone color
Scrollable message area with fixed height
Terminal-style cursor blink on input


TopicGraph.jsx
Visualizes the four-topic linear graph. Shows the student's position and progress.
Props: topicIndex: number, topics: array
Layout
Four nodes arranged horizontally with connecting lines between them:
[DECEPTION] ——— [SELF-KNOWLEDGE] ——— [ADAPTABILITY] ——— [VICTORY]
Node States
StateVisualCompletedFilled circle, bright color, checkmark or solid fillCurrentPulsing outline, tone colorUpcomingDim outline only, grey
Labels
Below each node, display the topic name in small monospace caps. Below the current node, display the current stage:
[●]————[◉]————[○]————[○]
 DECEPTION   SELF-KNOWLEDGE   ADAPTABILITY   VICTORY
             EXAMINATION

StageProgress.jsx
Shows progress through the four stages within the current topic.
Props: stage: string
Layout
Four stage indicators in a row, styled as segmented progress:
[■ INTRO] [■ EXAM] [□ CHALLENGE] [□ RESOLUTION]
Completed stages are filled. Current stage is highlighted in tone color. Upcoming stages are dim.
Stage order: introduction → examination → challenge → resolution

ScoreReadout.jsx
Displays the running evaluation score.
Props: score: number
Layout
HUMAN INTELLIGENCE ASSESSMENT
[████████░░░░░░░░░░░░] 42%
A progress bar with the score as a percentage. Bar fill color matches current tone color. Label above is fixed monospace text.
Animate score changes smoothly (CSS transition on width).

Overall Layout
┌─────────────────────────────────────────────────────┐
│  STRATEGIC INTELLIGENCE ASSESSMENT MODULE v.7.3      │
│                                                       │
│  ┌─────────────┐  ┌─────────────────────────────┐   │
│  │             │  │                             │   │
│  │   SIGIL     │  │   TOPIC GRAPH               │   │
│  │  (SunziDisplay) │  │   (TopicGraph)              │   │
│  │             │  │                             │   │
│  └─────────────┘  └─────────────────────────────┘   │
│                                                       │
│  ┌─────────────────────────────────────────────┐     │
│  │  STAGE PROGRESS    (StageProgress)           │     │
│  └─────────────────────────────────────────────┘     │
│                                                       │
│  ┌─────────────────────────────────────────────┐     │
│  │  SCORE READOUT     (ScoreReadout)            │     │
│  └─────────────────────────────────────────────┘     │
│                                                       │
│  ┌─────────────────────────────────────────────┐     │
│  │                                             │     │
│  │  CHAT INTERFACE    (ChatInterface)           │     │
│  │                                             │     │
│  │  > INPUT                          [SUBMIT]  │     │
│  └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘

Styling

Font: Monospace throughout — 'Courier New' or 'JetBrains Mono' (Google Fonts)
Background: #0A0A0F (near black)
Primary text: #C8C8D0 (cool grey)
Accent colors: Per tone state (see SunziDisplay spec)
No rounded corners — sharp geometry only, consistent with SUNZI's character
Thin 1px borders in tone color on panel elements


Flask Proxy Setup
In development, configure React's dev server to proxy API requests to Flask:
In package.json:
json{
  "proxy": "http://localhost:5000"
}
This allows React to call /api/turn without CORS issues during local development.

Dependencies
react
react-dom
No additional UI libraries required. All styling in plain CSS or inline styles.