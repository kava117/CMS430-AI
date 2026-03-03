/* render.js — Pure canvas rendering for DOMINION. No fetch, no game logic. */

// Tile type constants (mirror game/constants.py)
const FOREST = 0, PLAINS = 1, TOWER = 2, CAVE = 3, MOUNTAIN = 4,
      WIZARD = 5, BARBARIAN = 6, DOMAIN = 7;
const NONE = 0, PLAYER = 1, AI = 2;

const TILE_BASE_COLOR = {
  [FOREST]:    '#2d4a2d',
  [PLAINS]:    '#4a7a2a',
  [TOWER]:     '#4a4a6a',
  [CAVE]:      '#3a2a1a',
  [MOUNTAIN]:  '#5a5a5a',
  [WIZARD]:    '#3a1a5a',
  [BARBARIAN]: '#6a1a1a',
  [DOMAIN]:    '#5a4a1a',
};

const TILE_ICON = {
  [FOREST]:    '♣',
  [PLAINS]:    '≈',
  [TOWER]:     '▲',
  [CAVE]:      '○',
  [MOUNTAIN]:  '◆',
  [WIZARD]:    '✦',
  [BARBARIAN]: '⚔',
  [DOMAIN]:    '⬡',
};

const TILE_LABEL = {
  [FOREST]:    'Forest',
  [PLAINS]:    'Plains',
  [TOWER]:     'Tower',
  [CAVE]:      'Cave',
  [MOUNTAIN]:  'Mountain',
  [WIZARD]:    'Wizard',
  [BARBARIAN]: 'Barbarian',
  [DOMAIN]:    'Domain',
};

/**
 * Compute the cell size in pixels given the current canvas-wrap dimensions.
 * @param {object} state - current game state with W and H
 * @returns {number} cell size in pixels (40–64)
 */
function computeCellSize(state) {
  const wrap = document.getElementById('canvas-wrap');
  if (!wrap) return 48;
  const availW = wrap.clientWidth - 32;
  const availH = wrap.clientHeight - 32;
  const byW = Math.floor(availW / state.W);
  const byH = Math.floor(availH / state.H);
  return Math.min(64, Math.max(40, byW, byH));
}

/**
 * Blend two hex colors linearly by `amount` toward `tint`.
 * @param {string} base - hex color string e.g. '#2d4a2d'
 * @param {string} tint - hex color string
 * @param {number} amount - 0..1
 * @returns {string} 'rgb(r, g, b)'
 */
function blendColor(base, tint, amount) {
  const parse = h => [
    parseInt(h.slice(1, 3), 16),
    parseInt(h.slice(3, 5), 16),
    parseInt(h.slice(5, 7), 16),
  ];
  const [br, bg, bb] = parse(base);
  const [tr, tg, tb] = parse(tint);
  const r = Math.round(br + (tr - br) * amount);
  const g = Math.round(bg + (tg - bg) * amount);
  const b = Math.round(bb + (tb - bb) * amount);
  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Render the full board onto #board-canvas.
 * @param {object} state - game state from the server
 * @param {number} cellSize - pixel size per cell
 */
function render(state, cellSize) {
  const canvas = document.getElementById('board-canvas');
  canvas.width  = state.W * cellSize;
  canvas.height = state.H * cellSize;
  const ctx = canvas.getContext('2d');

  const fogSet   = new Set(state.fog);
  const validSet = new Set(state.valid_moves);
  const fogDisabled = window._fogDisabled || false;

  const PLAYER_TINT = '#4a9eff';
  const AI_TINT     = '#e05555';

  for (let i = 0; i < state.board.length; i++) {
    const cell = state.board[i];
    const x = (i % state.W) * cellSize;
    const y = Math.floor(i / state.W) * cellSize;

    const revealed = fogDisabled || fogSet.has(i);

    if (!revealed) {
      // Fogged cell
      ctx.fillStyle = '#0a0c0a';
      ctx.fillRect(x, y, cellSize, cellSize);
      ctx.fillStyle = '#1a2018';
      ctx.fillRect(x + cellSize / 2 - 1, y + cellSize / 2 - 1, 2, 2);
    } else {
      // Revealed cell — base color blended toward owner tint
      let baseColor = TILE_BASE_COLOR[cell.type] || '#333';
      let fillColor = baseColor;
      if (cell.owner === PLAYER) {
        fillColor = blendColor(baseColor, PLAYER_TINT, 0.35);
      } else if (cell.owner === AI) {
        fillColor = blendColor(baseColor, AI_TINT, 0.35);
      }

      ctx.fillStyle = fillColor;
      ctx.fillRect(x, y, cellSize, cellSize);

      // Owner border
      if (cell.owner !== NONE) {
        ctx.strokeStyle = cell.owner === PLAYER ? PLAYER_TINT : AI_TINT;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x + 0.75, y + 0.75, cellSize - 1.5, cellSize - 1.5);
      }

      // Tile icon
      const icon = TILE_ICON[cell.type] || '?';
      const fontSize = Math.max(10, Math.floor(cellSize * 0.38));
      ctx.font = `${fontSize}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      if (cell.type === WIZARD && cell.used) {
        ctx.globalAlpha = 0.4;
      }
      ctx.fillStyle = '#d4c9a8';
      ctx.fillText(icon, x + cellSize / 2, y + cellSize / 2);
      ctx.globalAlpha = 1.0;
    }

    // Valid move highlight
    if (validSet.has(i) && revealed) {
      const isWizardTeleport = state.phase === 'wizard-teleport';
      ctx.fillStyle = isWizardTeleport
        ? 'rgba(180, 80, 240, 0.35)'
        : 'rgba(200, 220, 60, 0.35)';
      ctx.fillRect(x, y, cellSize, cellSize);
      ctx.strokeStyle = isWizardTeleport
        ? 'rgba(180, 80, 240, 0.8)'
        : 'rgba(200, 220, 60, 0.8)';
      ctx.lineWidth = 2;
      ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
    }
  }
}
