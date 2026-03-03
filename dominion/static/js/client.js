/* client.js — UI logic, API calls, HUD, and event wiring for DOMINION. */

window._state = null;
window._cellSize = 48;
window._fogDisabled = false;
let legendBuilt = false;

// ========== Screen Management ==========

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
}

// ========== Apply State ==========

function applyState(state) {
  window._state = state;
  window._cellSize = computeCellSize(state);

  if (state.phase === 'gameover') {
    showScreen('screen-end');
    updateEndScreen(state);
    return;
  }

  showScreen('screen-game');

  if (state.phase === 'wizard-prompt') {
    document.getElementById('wizard-modal').classList.remove('hidden');
  } else {
    document.getElementById('wizard-modal').classList.add('hidden');
  }

  updateHUD(state);
  updateEventLog(state);
  if (!legendBuilt) {
    buildLegend();
    legendBuilt = false; // rebuild on new game
  }
  render(state, window._cellSize);
}

// ========== HUD ==========

function updateHUD(state) {
  const board = state.board;
  const playerCount = board.filter(c => c.owner === 1).length;
  const aiCount     = board.filter(c => c.owner === 2).length;

  document.getElementById('hud-player-count').textContent = playerCount;
  document.getElementById('hud-ai-count').textContent     = aiCount;

  const turnEl = document.getElementById('hud-turn');
  if (state.phase === 'wizard-prompt') {
    turnEl.textContent = 'Wizard awakens…';
  } else if (state.phase === 'wizard-teleport') {
    turnEl.textContent = 'Choose teleport destination';
  } else {
    turnEl.textContent = 'Your turn';
  }
}

// ========== Event Log ==========

function updateEventLog(state) {
  const logEl = document.getElementById('event-log');
  if (!logEl || !state.log) return;
  logEl.innerHTML = '';
  const entries = [...state.log].reverse();
  for (const msg of entries) {
    const div = document.createElement('div');
    div.textContent = msg;
    if (msg.toLowerCase().includes('barbarian')) div.classList.add('log-barbarian');
    else if (msg.toLowerCase().includes('player')) div.classList.add('log-player');
    else if (msg.toLowerCase().includes('ai'))     div.classList.add('log-ai');
    logEl.appendChild(div);
  }
}

// ========== End Screen ==========

function updateEndScreen(state) {
  const board = state.board;
  const playerCount = board.filter(c => c.owner === 1).length;
  const aiCount     = board.filter(c => c.owner === 2).length;

  const titleEl = document.getElementById('result-title');
  const scoreEl = document.getElementById('result-score');

  titleEl.className = '';
  if (playerCount > aiCount) {
    titleEl.textContent = 'Victory!';
    titleEl.classList.add('victory');
  } else if (aiCount > playerCount) {
    titleEl.textContent = 'Defeat';
    titleEl.classList.add('defeat');
  } else {
    titleEl.textContent = 'Draw';
    titleEl.classList.add('draw');
  }
  scoreEl.textContent = `You: ${playerCount} tiles  |  AI: ${aiCount} tiles`;
}

// ========== Tile Legend ==========

function buildLegend() {
  const TILE_NAMES  = ['Forest','Plains','Tower','Cave','Mountain','Wizard','Barbarian','Domain'];
  const TILE_COLORS = ['#2d4a2d','#4a7a2a','#4a4a6a','#3a2a1a','#5a5a5a','#3a1a5a','#6a1a1a','#5a4a1a'];
  const TILE_ICONS  = ['♣','≈','▲','○','◆','✦','⚔','⬡'];

  const legendEl = document.getElementById('tile-legend');
  legendEl.innerHTML = '';
  for (let t = 0; t < 8; t++) {
    const item = document.createElement('div');
    item.className = 'legend-item';
    const swatch = document.createElement('div');
    swatch.className = 'legend-swatch';
    swatch.style.background = TILE_COLORS[t];
    const icon = document.createElement('span');
    icon.textContent = TILE_ICONS[t];
    const name = document.createElement('span');
    name.textContent = TILE_NAMES[t];
    item.append(swatch, icon, name);
    legendEl.appendChild(item);
  }
  legendBuilt = true;
}

// ========== API Helpers ==========

async function apiPost(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body),
  });
  return r.json();
}

// ========== Event Wiring ==========

document.addEventListener('DOMContentLoaded', () => {

  // Start game
  document.getElementById('btn-start').addEventListener('click', async () => {
    let W = parseInt(document.getElementById('input-width').value, 10);
    let H = parseInt(document.getElementById('input-height').value, 10);
    W = Math.max(8, Math.min(24, isNaN(W) ? 14 : W));
    H = Math.max(6, Math.min(18, isNaN(H) ? 10 : H));
    const seed  = document.getElementById('input-seed').value.trim();
    const depth = parseInt(document.getElementById('input-depth').value, 10);

    legendBuilt = false;
    const state = await apiPost('/api/start', {W, H, seed, depth});
    applyState(state);
  });

  // Board canvas click
  document.getElementById('board-canvas').addEventListener('click', async (e) => {
    const state = window._state;
    if (!state) return;
    if (state.phase !== 'normal' && state.phase !== 'wizard-teleport') return;

    const canvas = e.currentTarget;
    const rect   = canvas.getBoundingClientRect();
    const cx     = Math.floor((e.clientX - rect.left) / window._cellSize);
    const cy     = Math.floor((e.clientY - rect.top)  / window._cellSize);
    const index  = cy * state.W + cx;

    if (!state.valid_moves.includes(index)) return;

    // Show thinking indicator
    document.getElementById('hud-turn').textContent = 'AI is thinking…';

    const newState = await apiPost('/api/move', {index});
    applyState(newState);
  });

  // Toggle fog
  document.getElementById('btn-toggle-fog').addEventListener('click', () => {
    window._fogDisabled = !window._fogDisabled;
    if (window._state) render(window._state, window._cellSize);
  });

  // New game
  document.getElementById('btn-new-game').addEventListener('click', () => {
    showScreen('screen-title');
  });

  // Play again
  document.getElementById('btn-play-again').addEventListener('click', () => {
    showScreen('screen-title');
  });

  // Wizard invoke
  document.getElementById('wizard-invoke').addEventListener('click', async () => {
    document.getElementById('wizard-modal').classList.add('hidden');
    const state = await apiPost('/api/wizard', {action: 'invoke'});
    applyState(state);
  });

  // Wizard decline
  document.getElementById('wizard-decline').addEventListener('click', async () => {
    document.getElementById('wizard-modal').classList.add('hidden');
    const state = await apiPost('/api/wizard', {action: 'decline'});
    applyState(state);
  });

  // Responsive canvas resize
  window.addEventListener('resize', () => {
    if (window._state) {
      window._cellSize = computeCellSize(window._state);
      render(window._state, window._cellSize);
    }
  });

});
