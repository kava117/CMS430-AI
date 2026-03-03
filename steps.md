# DOMINION — Implementation Steps

**Target deliverable:** A single self-contained `dominion.html` file.
**Stack:** Vanilla JS (ES2020+), HTML5 Canvas, inline CSS. No build tools or external dependencies (Google Fonts CDN only).

Each step builds on the last. Complete and verify all tests before moving to the next step.

---

## Step 1 — HTML Skeleton & CSS Foundation

**Goal:** Create `dominion.html` with the full page structure, CSS custom properties, and Google Fonts loaded. No game logic yet.

### Tasks
1. Create `dominion.html` with `<!DOCTYPE html>` and `<meta charset="UTF-8">`.
2. Link Google Fonts: `Cinzel` (headers) and `Crimson Text` (body/log).
3. Define CSS custom properties (`:root`):
   - `--bg: #0d0f0e`
   - `--player-color: #4a9eff`
   - `--ai-color: #e05555`
   - `--accent: #c9a84c`
   - `--text: #d4c9a8`
   - `--fog: #080a08`
4. Apply `box-sizing: border-box`, `margin: 0`, dark background to `body`.
5. Create three `<div>` sections (hidden by default, shown via JS class toggling):
   - `#screen-title` — title/setup screen
   - `#screen-game` — game screen
   - `#screen-end` — end/result screen
6. Place a `<canvas id="board-canvas">` inside `#screen-game`.
7. Add a single `<script>` tag at the bottom of `<body>` (all game code lives here).
8. On `DOMContentLoaded`, show `#screen-title` and hide the others.

### Tests
```
// Paste into browser console after opening dominion.html
console.assert(document.getElementById('screen-title').style.display !== 'none' ||
  document.getElementById('screen-title').classList.contains('active'),
  'FAIL: title screen should be visible on load');
console.assert(document.getElementById('board-canvas') !== null,
  'FAIL: canvas element must exist');
console.assert(getComputedStyle(document.body).fontFamily.includes('Crimson') ||
  getComputedStyle(document.body).backgroundColor !== 'rgba(0, 0, 0, 0)',
  'FAIL: custom fonts/background not applied');
console.log('Step 1 tests passed');
```
**Visual check:** Opening the file shows a dark page; no browser-default white background visible.

---

## Step 2 — Title / Setup Screen UI

**Goal:** Render a styled setup card on `#screen-title` with all configuration inputs and a working "Begin Conquest" button.

### Tasks
1. Inside `#screen-title`, add:
   - Game title `<h1>DOMINION</h1>` in `Cinzel` font with a CSS glow/text-shadow animation.
   - Tagline `<p>` in italic `Crimson Text`.
   - A setup card `<div class="setup-card">` containing:
     - Number input **Board Width** (min=8, max=24, value=14)
     - Number input **Board Height** (min=6, max=18, value=10)
     - Text input **Seed** (placeholder: "leave blank for random")
     - Select **AI Difficulty**: Scout (depth=2), Knight (depth=3, selected), Warlord (depth=4)
   - `<button id="btn-start">Begin Conquest</button>`
2. Style the card with a parchment-border look using CSS (no images required — use `border`, `box-shadow`, `background`).
3. Wire `#btn-start` click: read all input values, validate ranges (clamp if out of bounds), then call `startGame(config)` (stubbed for now — just `console.log(config)`).

### Tests
```
// In console:
const w = document.querySelector('input[name="width"]') ||
          document.querySelector('#input-width');
const h = document.querySelector('input[name="height"]') ||
          document.querySelector('#input-height');
console.assert(w !== null, 'FAIL: width input missing');
console.assert(h !== null, 'FAIL: height input missing');
console.assert(document.querySelector('#btn-start') !== null, 'FAIL: start button missing');

// Simulate out-of-range input clamping:
w.value = 99;
document.querySelector('#btn-start').click();
// Check console — logged config.W should be 24, not 99
console.log('Step 2 tests: verify logged config.W === 24 for input 99');
```
**Visual check:** Setup card is centered, dark-themed, styled fonts visible, glow animation on title.

---

## Step 3 — PRNG, Board Data Model & Generation

**Goal:** Implement the seeded PRNG (mulberry32 + FNV-1a hash), the board data model, and `generateBoard()`.

### Tasks
1. Implement `hashStr(s)` using FNV-1a:
   ```js
   function hashStr(s) {
     let h = 0x811c9dc5;
     for (let i = 0; i < s.length; i++) {
       h ^= s.charCodeAt(i);
       h = (h * 0x01000193) >>> 0;
     }
     return h;
   }
   ```
2. Implement `mulberry32(seed)` returning a `() => float[0,1)` function.
3. If the seed input is blank, use `String(Date.now())` as the seed.
4. Define tile type constants:
   ```js
   const T = { FOREST:0, PLAINS:1, TOWER:2, CAVE:3, MOUNTAIN:4, WIZARD:5, BARBARIAN:6, DOMAIN:7 };
   ```
5. Define owner constants: `const OWNER = { NONE:0, PLAYER:1, AI:2 };`
6. Implement `makeCell(type)` returning `{ type, owner: OWNER.NONE, used: false }`.
7. Implement `idx(x, y)` → `y * G.W + x` and `xy(i)` → `{ x: i % G.W, y: Math.floor(i / G.W) }`.
8. Implement `generateBoard(rng, W, H)`:
   - Tile weights: Forest=35, Plains=20, Tower=8, Cave=8, Mountain=15, Wizard=5, Barbarian=9 (total=100).
   - Use a weighted-random pick: for each cell, draw `rng()` and map to a tile type using cumulative weights.
   - After placing all tiles, **guarantee ≥ 2 Cave tiles**: count Caves; if fewer than 2, overwrite random non-Mountain cells (using `rng`) until count reaches 2.
   - Place Domain tiles for each player (Section 3.4 of spec):
     - Player: start at `(1,1)`, walk right (x++) until a non-Mountain cell is found; set `type = T.DOMAIN`, `owner = OWNER.PLAYER`.
     - AI: start at `(W-2, H-2)`, walk left (x--) until an unclaimed non-Mountain cell is found; set `type = T.DOMAIN`, `owner = OWNER.AI`.
9. Store board as `G.board = generateBoard(G.rng, G.W, G.H)` on game start.

### Tests
```js
// In console after stubbing startGame to expose G globally:
// Call startGame with fixed seed and check board properties

startGame({ W:14, H:10, seed:'test123', depth:3 });

// 1. Board length
console.assert(G.board.length === 14*10, 'FAIL: board length');

// 2. All cells have valid types
const validTypes = new Set([0,1,2,3,4,5,6,7]);
console.assert(G.board.every(c => validTypes.has(c.type)), 'FAIL: invalid tile type');

// 3. Cave guarantee
const caves = G.board.filter(c => c.type === T.CAVE);
console.assert(caves.length >= 2, 'FAIL: fewer than 2 caves');

// 4. Domain tiles placed
const playerDomain = G.board.find(c => c.type === T.DOMAIN && c.owner === OWNER.PLAYER);
const aiDomain = G.board.find(c => c.type === T.DOMAIN && c.owner === OWNER.AI);
console.assert(playerDomain !== undefined, 'FAIL: player domain missing');
console.assert(aiDomain !== undefined, 'FAIL: AI domain missing');

// 5. Mountains never owned
console.assert(G.board.filter(c => c.type === T.MOUNTAIN).every(c => c.owner === OWNER.NONE),
  'FAIL: mountain is owned');

// 6. Determinism — same seed gives same board
startGame({ W:14, H:10, seed:'test123', depth:3 });
const board1types = G.board.map(c => c.type).join(',');
startGame({ W:14, H:10, seed:'test123', depth:3 });
const board2types = G.board.map(c => c.type).join(',');
console.assert(board1types === board2types, 'FAIL: same seed produces different boards');

console.log('Step 3 tests passed');
```

---

## Step 4 — Fog of War

**Goal:** Implement the shared fog system: initial fog computation and `computeFog()`.

### Tasks
1. Add `G.fog = new Set()` — indices of revealed tiles.
2. Implement `computeFog()`:
   - Clear and rebuild `G.fog` from scratch.
   - For each tile in `G.board` that has `owner !== OWNER.NONE`:
     - Determine vision range by tile type (Forest/Domain/Wizard/Barbarian=1, Plains=2, Tower=3, Cave=1, Mountain=0).
     - BFS flood in cardinal directions up to the vision range from that tile's position.
     - Mountains do **not** block propagation — the BFS continues through them.
     - Add all visited indices to `G.fog`.
   - **Cave special:** if any player owns ≥ 1 Cave tile, add all Cave tile indices to `G.fog`.
3. Call `computeFog()` immediately after `generateBoard()` to establish initial visibility.
4. Implement `isFogged(i)` → `!G.fog.has(i)`.

### Tests
```js
startGame({ W:14, H:10, seed:'test123', depth:3 });

// 1. Starting tiles are revealed
const playerIdx = G.board.findIndex(c => c.owner === OWNER.PLAYER);
const aiIdx = G.board.findIndex(c => c.owner === OWNER.AI);
console.assert(G.fog.has(playerIdx), 'FAIL: player domain not revealed');
console.assert(G.fog.has(aiIdx), 'FAIL: AI domain not revealed');

// 2. Cardinal neighbors of player domain are revealed
const {x:px, y:py} = xy(playerIdx);
const neighbors = [
  [px+1,py],[px-1,py],[px,py+1],[px,py-1]
].filter(([x,y]) => x>=0&&x<G.W&&y>=0&&y<G.H);
console.assert(neighbors.every(([x,y]) => G.fog.has(idx(x,y))),
  'FAIL: adjacent tiles of player domain not revealed');

// 3. Fog is shared — re-compute and check size is > 0
console.assert(G.fog.size > 0, 'FAIL: fog set is empty');

// 4. Tiles far from both starting positions are fogged
// (Pick a tile near center of a large board — likely fogged on default 14x10)
const centerIdx = idx(7, 5);
// Note: this assertion might not hold for all seeds — just log rather than assert
console.log('Center tile fogged?', isFogged(centerIdx));

console.log('Step 4 tests passed');
```

---

## Step 5 — Valid Moves Computation

**Goal:** Implement `computeValidMoves(owner)` returning a `Set` of valid move indices.

### Tasks
1. Implement `computeValidMoves(owner)`:
   - Initialize empty `Set candidates`.
   - For each tile `c` at index `i` where `c.owner === owner`:
     - **Forest / Domain:** BFS/enumerate cardinal neighbors at distance exactly 1.
     - **Plains:** all tiles at cardinal Manhattan distance ≤ 2 (include distance-1 and distance-2). Use a double-loop over directions, not a full BFS, to enumerate (up to 8 tiles in cardinal cross pattern at distances 1 and 2).
     - **Tower:** all tiles at cardinal Manhattan distance ≤ 3 (teleport-style — Mountains do not block). Enumerate all positions at dist 1, 2, 3 in each cardinal direction.
     - **Cave:** if this owner owns ≥ 1 cave, add all Cave tile indices (regardless of position).
     - **Wizard (not used):** treat as domain (dist ≤ 1) for expansion — the Wizard tile's expansion is normal; the *power* is separate.
     - **Barbarian, Mountain:** no expansion contribution.
   - Filter candidates: keep only those where `G.board[i].owner === OWNER.NONE` AND `G.board[i].type !== T.MOUNTAIN` AND `G.fog.has(i)` (tile is revealed).
   - **Wizard teleport phase exception:** if `G.wizardActiveFor === owner`, skip the normal move set and instead return all revealed unclaimed non-Mountain tiles.
2. Store result as `G.validMoves` each turn.

### Tests
```js
startGame({ W:14, H:10, seed:'test123', depth:3 });

// 1. Valid moves are non-empty at start for both players
const playerMoves = computeValidMoves(OWNER.PLAYER);
const aiMoves = computeValidMoves(OWNER.AI);
console.assert(playerMoves.size > 0, 'FAIL: player has no valid moves at start');
console.assert(aiMoves.size > 0, 'FAIL: AI has no valid moves at start');

// 2. No Mountain in valid moves
console.assert([...playerMoves].every(i => G.board[i].type !== T.MOUNTAIN),
  'FAIL: Mountain in player valid moves');

// 3. No already-owned tile in valid moves
console.assert([...playerMoves].every(i => G.board[i].owner === OWNER.NONE),
  'FAIL: owned tile in player valid moves');

// 4. No fogged tile in valid moves
console.assert([...playerMoves].every(i => G.fog.has(i)),
  'FAIL: fogged tile in player valid moves');

// 5. Plains expansion — claim a Plains tile and check 2-step moves appear
const plainsTile = G.board.findIndex(c => c.type === T.PLAINS && c.owner === OWNER.NONE);
if (plainsTile !== -1) {
  G.board[plainsTile].owner = OWNER.PLAYER;
  computeFog();
  const movesAfter = computeValidMoves(OWNER.PLAYER);
  // Should have more moves than before if Plains was accessible
  console.log('Moves after claiming Plains:', movesAfter.size, '(was', playerMoves.size, ')');
  G.board[plainsTile].owner = OWNER.NONE; // restore
  computeFog();
}

// 6. Wizard teleport phase — all unclaimed non-Mountain revealed tiles valid
G.wizardActiveFor = OWNER.PLAYER;
const wizardMoves = computeValidMoves(OWNER.PLAYER);
const allUnclaimed = G.board.filter((c,i) => c.owner===OWNER.NONE && c.type!==T.MOUNTAIN && G.fog.has(i));
console.assert(wizardMoves.size === allUnclaimed.length,
  'FAIL: wizard teleport move count mismatch');
G.wizardActiveFor = OWNER.NONE; // restore

console.log('Step 5 tests passed');
```

---

## Step 6 — Tile Claiming, Barbarian Triggers & Win Condition

**Goal:** Implement `claimTile(index, owner)`, `triggerBarbarians()`, and `checkWinCondition()`.

### Tasks
1. Implement `claimTile(index, owner)`:
   - Snapshot `G.fog` (copy the Set) before mutating.
   - Set `G.board[index].owner = owner`.
   - If the claimed tile is `T.WIZARD`, set `G.board[index].used = false` and immediately show the wizard prompt (stub as `promptWizard(index, owner)` for now).
   - If the claimed tile is `T.BARBARIAN`, call `triggerBarbarians(index)` immediately.
   - Call `computeFog()`.
   - Detect newly revealed tiles: iterate the new `G.fog` and find indices that were NOT in the snapshot.
   - For each newly revealed tile that is a Barbarian (and wasn't the claimed tile, which already triggered), call `triggerBarbarians(i)` in index order.
2. Implement `triggerBarbarians(index)`:
   - Determine sweep direction:
     - `W > H` → horizontal (row sweep)
     - `H > W` → vertical (column sweep)
     - `W === H` → use `G.rng() < 0.5 ? 'h' : 'v'` (only during gameplay, not minimax — see Step 8)
   - For horizontal sweep: reset `owner = OWNER.NONE` for all non-Mountain tiles in the same **row** as `index`, including the Barbarian tile itself.
   - For vertical sweep: reset `owner = OWNER.NONE` for all non-Mountain tiles in the same **column** as `index`.
   - Log the event to the event log (stub as `logEvent()` for now).
   - Call `computeFog()` after the sweep.
3. Implement `checkWinCondition()`:
   - Count claimable tiles: all tiles where `type !== T.MOUNTAIN`.
   - Count player tiles and AI tiles.
   - Return `OWNER.PLAYER` if player tiles > `floor(claimable / 2)`.
   - Return `OWNER.AI` if AI tiles > `floor(claimable / 2)`.
   - Return `'DRAW'` if player tiles === AI tiles and all tiles are claimed (or no moves for both).
   - Return `null` if game continues.
   - Also check: if all claimable tiles are claimed, compare counts and return winner or draw.

### Tests
```js
startGame({ W:14, H:10, seed:'test123', depth:3 });

// 1. Claiming a tile sets owner
const movesSet = computeValidMoves(OWNER.PLAYER);
const firstMove = [...movesSet][0];
claimTile(firstMove, OWNER.PLAYER);
console.assert(G.board[firstMove].owner === OWNER.PLAYER, 'FAIL: tile not claimed');

// 2. Fog updates after claim
computeFog();
console.assert(G.fog.has(firstMove), 'FAIL: claimed tile not in fog');

// 3. Win condition returns null at start (not over)
console.assert(checkWinCondition() === null, 'FAIL: game should not be over at start');

// 4. Barbarian sweep — manually place a Barbarian and trigger it
// Use a W > H board so sweep is horizontal
startGame({ W:14, H:10, seed:'test123', depth:3 });
const row = 3;
// Place barbarian at (5, row)
const barbIdx = idx(5, row);
G.board[barbIdx].type = T.BARBARIAN;
G.board[barbIdx].owner = OWNER.PLAYER; // pretend player owns tiles in row
// Place some player tiles in the same row
[1,2,3,4].forEach(x => { G.board[idx(x,row)].owner = OWNER.PLAYER; });
triggerBarbarians(barbIdx);
// All non-Mountain tiles in row should now be NONE
const rowTiles = Array.from({length: G.W}, (_,x) => G.board[idx(x,row)]);
console.assert(rowTiles.filter(c => c.type !== T.MOUNTAIN).every(c => c.owner === OWNER.NONE),
  'FAIL: Barbarian sweep did not reset row');

// 5. Win condition — force majority
startGame({ W:8, H:6, seed:'abc', depth:2 });
const claimable = G.board.filter(c => c.type !== T.MOUNTAIN).length;
const majority = Math.floor(claimable / 2) + 1;
// Give player majority
let assigned = 0;
G.board.forEach((c, i) => {
  if (c.type !== T.MOUNTAIN && c.owner === OWNER.NONE && assigned < majority) {
    c.owner = OWNER.PLAYER;
    assigned++;
  }
});
console.assert(checkWinCondition() === OWNER.PLAYER, 'FAIL: majority win not detected');

console.log('Step 6 tests passed');
```

---

## Step 7 — Canvas Rendering

**Goal:** Implement `render()` to draw the full board state to the canvas.

### Tasks
1. Set canvas dimensions based on `G.W`, `G.H`, and cell size (56–64px, reduced to fit viewport — minimum 40px).
2. Define base colors per tile type (from spec §11.3):
   - Forest: `#2d4a2d`, Plains: `#6b7a3a`, Tower: `#3a3a5c`, Cave: `#2a2a38`
   - Mountain: `#3a3a3a`, Wizard: `#4a2a60`, Barbarian: `#5c2e18`, Domain: `#6b5a38`
3. Define icons per tile (Unicode): Forest=`♣`, Plains=`≈`, Tower=`▲`, Cave=`○`, Mountain=`◆`, Wizard=`✦`, Barbarian=`⚔`, Domain=`⬡`.
4. For each cell `i`:
   - If `isFogged(i)`: fill with `#080a08` (fog color), draw subtle grid line, skip to next cell.
   - Otherwise:
     - Fill with base tile color, tinted toward `#4a9eff` (player) or `#e05555` (AI) if owned.
     - Draw a 2px border in owner's color if owned.
     - Render the tile icon centered in the cell (white or light text).
     - If `i` is in `G.validMoves`: draw a semi-transparent yellow-green overlay + colored border.
     - If wizard teleport phase and tile is valid: use purple highlight instead.
5. Add 3px gutter between cells using inset padding.
6. Call `render()` at end of every game-state change.

### Tests
```js
startGame({ W:14, H:10, seed:'test123', depth:3 });

// 1. Canvas has correct pixel dimensions
const canvas = document.getElementById('board-canvas');
const cellSize = 56; // or whatever was computed
console.assert(canvas.width >= 14 * 40, 'FAIL: canvas too narrow');
console.assert(canvas.height >= 10 * 40, 'FAIL: canvas too short');

// 2. Render runs without throwing
try { render(); console.log('render() OK'); }
catch(e) { console.error('FAIL: render() threw:', e); }

// 3. Pixel spot-check: player domain tile should NOT be fog-colored
// (This is a visual check — open browser and inspect)
console.log('Visual check: player start tile should show Domain icon (⬡) in blue tint');
console.log('Visual check: fogged tiles should appear as near-black rectangles');
console.log('Visual check: valid moves should show yellow-green highlight');

console.log('Step 7 tests passed (visual verification required)');
```
**Visual check:** Open `dominion.html`, start a game, verify tiles render with correct colors, icons, and fog.

---

## Step 8 — AI: Minimax with Alpha-Beta Pruning

**Goal:** Implement the full minimax AI: `minimaxRoot()`, `minimaxAlphaBeta()`, and `heuristic()`.

### Tasks
1. Implement `heuristic()`:
   ```
   score = (aiCount - playerCount) * 10
         + (aiFrontier - playerFrontier) * 3
         + aiOwnsCave ? 8 : 0
         - playerOwnsCave ? 8 : 0
         + aiHasActiveWizard ? 5 : 0
         - playerHasActiveWizard ? 5 : 0
         - barbExposure(AI) * 2
         + barbExposure(PLAYER) * 2
   ```
   - `barbExposure(owner)`: count owned tiles that share a row (W>=H) or column (H>W) with a **fogged** Barbarian tile.
   - AI must only score **revealed** tiles — do not include hidden tile data.
2. Implement board snapshot/restore for simulation:
   - `snapshotBoard()` → deep copy of `G.board` as array of `{type, owner, used}`.
   - `restoreBoard(snap)` → restore `G.board` and recompute fog.
3. Implement `minimaxAlphaBeta(depth, alpha, beta, isMaximizing)`:
   - At depth 0 or no valid moves for the active player: return `heuristic()`.
   - Move ordering: sort candidate moves by strategic tile value (Cave=4, Wizard=3, Tower=2.5, Plains=2, Forest/Domain=1.5, Barbarian=0.5, Mountain=0) descending before iterating.
   - For each move: snapshot → `claimTile(move, owner)` (simulate) → recurse → restore.
   - **Barbarian simulation:** during minimax, use deterministic direction: `W >= H ? 'h' : 'v'` (no PRNG).
   - Apply alpha-beta pruning (prune when `beta <= alpha`).
4. Implement `minimaxRoot(depth)`:
   - Iterate all AI valid moves, call `minimaxAlphaBeta` for each, track best.
   - Return the index of the best move.
5. Implement `wizardTeleportDecision()` for AI:
   - Score all revealed unclaimed non-Mountain tiles by strategic value.
   - If best > 2, return that index. Otherwise return `null`.

### Tests
```js
startGame({ W:10, H:8, seed:'aitest', depth:2 }); // small board, shallow depth

// 1. heuristic() returns a number
const h = heuristic();
console.assert(typeof h === 'number' && isFinite(h), 'FAIL: heuristic not a number');

// 2. Snapshot/restore round-trip
const snap = snapshotBoard();
const firstCell = Object.assign({}, G.board[0]);
G.board[0].owner = OWNER.PLAYER;
restoreBoard(snap);
console.assert(G.board[0].owner === firstCell.owner, 'FAIL: restore changed board');

// 3. minimaxRoot returns a valid move index
const aiMoves = computeValidMoves(OWNER.AI);
const bestMove = minimaxRoot(2);
console.assert(aiMoves.has(bestMove), 'FAIL: minimaxRoot returned invalid move');

// 4. AI prefers high-value tiles — place a Cave next to AI domain
startGame({ W:10, H:8, seed:'aitest2', depth:2 });
const aiDomIdx = G.board.findIndex(c => c.owner === OWNER.AI);
const {x:ax, y:ay} = xy(aiDomIdx);
// Place revealed Cave adjacent to AI domain
const caveIdx = idx(Math.max(0, ax-1), ay);
G.board[caveIdx].type = T.CAVE;
G.board[caveIdx].owner = OWNER.NONE;
G.fog.add(caveIdx);
const move = minimaxRoot(2);
// Not guaranteed but likely Cave is preferred
console.log('AI picked index', move, '— type:', G.board[move].type,
  '(Cave=3, expect Cave or adjacent high-value)');

// 5. Heuristic is higher when AI has more tiles
const baseH = heuristic();
G.board.find(c => c.type !== T.MOUNTAIN && c.owner === OWNER.NONE
  && G.fog.has(G.board.indexOf(c))).owner = OWNER.AI;
const afterH = heuristic();
console.assert(afterH > baseH, 'FAIL: heuristic did not increase when AI gained tile');

console.log('Step 8 tests passed');
```

---

## Step 9 — Player Turn & Click Handling

**Goal:** Wire up human player input — click-to-claim on the canvas, turn switching, and Wizard prompt.

### Tasks
1. Add a `click` event listener to the canvas.
2. In `handlePlayerClick(e)`:
   - If `G.phase !== 'normal'` and not `'wizard-teleport'`, ignore.
   - Convert mouse coordinates to cell index using cell size.
   - If the clicked index is not in `G.validMoves`, ignore (no flash, no error).
   - Call `claimTile(index, OWNER.PLAYER)`.
   - If claimed tile is `T.WIZARD`: set `G.phase = 'wizard-prompt'`, show modal (see §11.5).
   - Otherwise: call `endPlayerTurn()`.
3. Implement `endPlayerTurn()`:
   - Check win condition — if game over, call `showEndScreen()`.
   - Otherwise, switch `G.turn = OWNER.AI`, update HUD, call `render()`.
   - After a 400–600ms delay (so "AI is thinking…" renders), call `runAITurn()`.
4. Implement the Wizard prompt modal:
   - On **Invoke**: set `G.wizardActiveFor = OWNER.PLAYER`, set `G.phase = 'normal'`, call `endPlayerTurn()`.
   - On **Decline**: set `G.wizardActiveFor = OWNER.NONE`, set `G.phase = 'normal'`, call `endPlayerTurn()`.
5. Implement `runAITurn()`:
   - Set `G.phase = 'ai-thinking'`, render HUD "AI is thinking…".
   - Use `setTimeout(0)` to yield to the browser so the HUD updates.
   - Compute AI move: if `G.wizardActiveFor === OWNER.AI`, call `wizardTeleportDecision()` for target; otherwise call `minimaxRoot(G.depth)`.
   - `claimTile(chosenIndex, OWNER.AI)`.
   - If claimed tile is `T.WIZARD`: call `wizardTeleportDecision()` — if result > threshold, set `G.wizardActiveFor = OWNER.AI`; otherwise decline.
   - Check win condition. If not over: switch `G.turn = OWNER.PLAYER`, set `G.phase = 'normal'`, recompute `G.validMoves`, `render()`.
6. Handle "no valid moves" (§7.3): if `G.validMoves.size === 0` after computing, skip the player's turn.

### Tests
```js
startGame({ W:10, H:8, seed:'clicktest', depth:2 });
render();

// 1. Clicking a fogged tile does nothing
const foggedIdx = [...Array(G.W*G.H).keys()].find(i => !G.fog.has(i));
if (foggedIdx !== undefined) {
  const {x,y} = xy(foggedIdx);
  const cellSize = Math.floor(Math.min(
    (window.innerWidth * 0.8) / G.W,
    (window.innerHeight * 0.7) / G.H
  ));
  // Dispatch click event at center of fogged cell
  const canvas = document.getElementById('board-canvas');
  const rect = canvas.getBoundingClientRect();
  const ev = new MouseEvent('click', {
    clientX: rect.left + x * cellSize + cellSize/2,
    clientY: rect.top + y * cellSize + cellSize/2
  });
  const prevOwner = G.board[foggedIdx].owner;
  canvas.dispatchEvent(ev);
  console.assert(G.board[foggedIdx].owner === prevOwner,
    'FAIL: clicking fogged tile changed ownership');
}

// 2. Clicking a valid move claims the tile and switches turn
const validMove = [...G.validMoves][0];
const {x:vx, y:vy} = xy(validMove);
const cellSize = 56; // approximate
const canvas = document.getElementById('board-canvas');
const rect = canvas.getBoundingClientRect();
const ev = new MouseEvent('click', {
  clientX: rect.left + vx * cellSize + cellSize/2,
  clientY: rect.top + vy * cellSize + cellSize/2,
  bubbles: true
});
canvas.dispatchEvent(ev);
console.assert(G.board[validMove].owner === OWNER.PLAYER,
  'FAIL: clicking valid move did not claim tile');

// 3. After player turn, turn switches to AI (may have already processed)
setTimeout(() => {
  console.log('Turn after player click:', G.turn === OWNER.AI ? 'AI (correct)' : 'PLAYER (may still be thinking)');
}, 100);

// 4. Phase transitions correctly
console.assert(['normal','ai-thinking','wizard-prompt','wizard-teleport','gameover']
  .includes(G.phase), 'FAIL: unknown game phase');

console.log('Step 9 tests passed');
```

---

## Step 10 — HUD, Event Log & Control Buttons

**Goal:** Implement the game screen HUD, event log panel, and control buttons (New Game, Toggle Fog).

### Tasks
1. In `#screen-game`, add:
   - **Header row** (flex, space-between):
     - Left: Player HUD — tile count `<span id="hud-player-count">`, label "YOUR TERRITORY".
     - Center: game title `DOMINION` + `<span id="hud-turn">` showing whose turn or "AI is thinking…".
     - Right: AI HUD — label "AI TERRITORY" + `<span id="hud-ai-count">`.
   - **Canvas** centered below header.
   - **Bottom bar**:
     - Left: `<div id="event-log">` — scrollable, showing last 8 events, color-coded (blue=player, red=AI, gold=world events).
     - Right: buttons `#btn-new-game` (→ title screen) and `#btn-toggle-fog`.
2. Implement `updateHUD()`:
   - Count player/AI tiles, update `#hud-player-count` and `#hud-ai-count`.
   - Set `#hud-turn` text based on `G.turn` and `G.phase`.
3. Implement `logEvent(msg, color)`:
   - Prepend a `<div>` with styled color to `#event-log`.
   - Limit to 20 entries (remove oldest if exceeded).
4. Wire `#btn-toggle-fog`:
   - Toggle a `G.fogDisabled` boolean.
   - Call `render()` — in render, if `G.fogDisabled`, treat all tiles as revealed.
5. Wire `#btn-new-game`:
   - Reset game state, hide `#screen-game`, show `#screen-title`.
6. Add a tile legend below the canvas: a small row of colored squares with labels for each tile type (from §11.3 visual reference).

### Tests
```js
startGame({ W:14, H:10, seed:'hudtest', depth:3 });

// 1. HUD elements exist
console.assert(document.getElementById('hud-player-count') !== null, 'FAIL: player count HUD missing');
console.assert(document.getElementById('hud-ai-count') !== null, 'FAIL: AI count HUD missing');
console.assert(document.getElementById('hud-turn') !== null, 'FAIL: turn indicator missing');
console.assert(document.getElementById('event-log') !== null, 'FAIL: event log missing');

// 2. HUD counts are correct
updateHUD();
const playerCount = G.board.filter(c => c.owner === OWNER.PLAYER).length;
const displayedCount = parseInt(document.getElementById('hud-player-count').textContent);
console.assert(displayedCount === playerCount, 'FAIL: HUD player count mismatch');

// 3. logEvent adds to event log
const logBefore = document.getElementById('event-log').children.length;
logEvent('Test event', 'gold');
const logAfter = document.getElementById('event-log').children.length;
console.assert(logAfter === logBefore + 1, 'FAIL: logEvent did not add entry');

// 4. Toggle fog reveals all tiles
G.fogDisabled = false;
render();
const foggedBefore = [...Array(G.W*G.H).keys()].filter(i => !G.fog.has(i)).length;
document.getElementById('btn-toggle-fog').click();
console.assert(G.fogDisabled === true, 'FAIL: fog toggle did not set G.fogDisabled');

// 5. New game button returns to title screen
document.getElementById('btn-new-game').click();
console.assert(document.getElementById('screen-title').style.display !== 'none' ||
  document.getElementById('screen-title').classList.contains('active'),
  'FAIL: new game did not return to title screen');

console.log('Step 10 tests passed');
```

---

## Step 11 — End Screen & Win Condition Integration

**Goal:** Wire `checkWinCondition()` into the game loop and show the end screen with final results.

### Tasks
1. After every `claimTile()` call (both player and AI turns), call `checkWinCondition()`.
2. If a winner is detected, call `showEndScreen(winner)`.
3. Implement `showEndScreen(winner)`:
   - Set `G.phase = 'gameover'`, `G.gameOver = true`.
   - Hide `#screen-game`, show `#screen-end`.
   - Set result text: `VICTORY` (player wins), `DEFEAT` (AI wins), or `DRAW`.
   - Display final player tile count vs AI tile count.
   - Confirm `#btn-play-again` returns to title screen.
4. In `#screen-end`, add:
   - Large result header (`#result-title`) styled in `Cinzel`.
   - Score summary `<p id="result-score">`.
   - `<button id="btn-play-again">Play Again</button>`.
5. Wire no-moves handling: if `G.validMoves.size === 0` for the current player, log "No moves — turn skipped", switch turns. If both sides have 0 moves in succession, call `showEndScreen(checkWinCondition())`.

### Tests
```js
// 1. End screen elements exist
console.assert(document.getElementById('result-title') !== null, 'FAIL: result-title missing');
console.assert(document.getElementById('result-score') !== null, 'FAIL: result-score missing');
console.assert(document.getElementById('btn-play-again') !== null, 'FAIL: play-again button missing');

// 2. Force a win condition and check end screen displays
startGame({ W:8, H:6, seed:'endtest', depth:2 });
const claimable = G.board.filter(c => c.type !== T.MOUNTAIN).length;
const majority = Math.floor(claimable / 2) + 1;
let count = 0;
G.board.forEach(c => {
  if (c.type !== T.MOUNTAIN && c.owner === OWNER.NONE && count < majority) {
    c.owner = OWNER.PLAYER;
    count++;
  }
});
const result = checkWinCondition();
console.assert(result === OWNER.PLAYER, 'FAIL: win condition not detected');
showEndScreen(result);
console.assert(document.getElementById('screen-end').style.display !== 'none' ||
  document.getElementById('screen-end').classList.contains('active'),
  'FAIL: end screen not shown');
console.assert(document.getElementById('result-title').textContent.includes('VICTORY'),
  'FAIL: result title should say VICTORY');

// 3. Play Again returns to title
document.getElementById('btn-play-again').click();
console.assert(document.getElementById('screen-title').style.display !== 'none' ||
  document.getElementById('screen-title').classList.contains('active'),
  'FAIL: play again did not return to title');

console.log('Step 11 tests passed');
```

---

## Step 12 — Wizard Full Flow Integration

**Goal:** Complete the Wizard tile interaction — modal prompt for the human player, AI decision, and wizard teleport turn.

### Tasks
1. Build the Wizard prompt modal (`#wizard-modal`):
   - Dark overlay covering the game screen.
   - Text: "A Wizard appears! Invoke their power on your next turn?"
   - Two buttons: `#wizard-invoke` and `#wizard-decline`.
   - Style with `Cinzel` heading and `Crimson Text` body text.
2. Wire `#wizard-invoke`:
   - Set `G.wizardActiveFor = OWNER.PLAYER`.
   - Hide modal, set `G.phase = 'normal'`.
   - Call `endPlayerTurn()`.
3. Wire `#wizard-decline`:
   - Set `G.wizardActiveFor = OWNER.NONE`.
   - Hide modal, set `G.phase = 'normal'`.
   - Call `endPlayerTurn()`.
4. On the player's **next** turn, if `G.wizardActiveFor === OWNER.PLAYER`:
   - Set `G.phase = 'wizard-teleport'`.
   - Recompute `G.validMoves` (all revealed unclaimed non-Mountain tiles).
   - Highlight all valid tiles in purple on the canvas.
   - After the player clicks a tile, claim it, clear `G.wizardActiveFor = OWNER.NONE`, set `G.phase = 'normal'`.
5. Mark the used Wizard tile: `G.board[wizardIdx].used = true` after the power is invoked.
6. Ensure AI Wizard flow in `runAITurn()` uses `wizardTeleportDecision()` correctly (already wired in Step 9).
7. Log all Wizard events to the event log in gold color.

### Tests
```js
startGame({ W:14, H:10, seed:'wiztest', depth:3 });

// 1. Wizard modal elements exist
console.assert(document.getElementById('wizard-modal') !== null, 'FAIL: wizard modal missing');
console.assert(document.getElementById('wizard-invoke') !== null, 'FAIL: invoke button missing');
console.assert(document.getElementById('wizard-decline') !== null, 'FAIL: decline button missing');

// 2. Claiming a wizard tile shows the modal
const wizIdx = G.board.findIndex((c,i) =>
  c.type === T.WIZARD && c.owner === OWNER.NONE && G.fog.has(i));
if (wizIdx !== -1) {
  // Force wizard to be a valid move
  G.validMoves.add(wizIdx);
  claimTile(wizIdx, OWNER.PLAYER);
  console.assert(G.phase === 'wizard-prompt' ||
    document.getElementById('wizard-modal').style.display !== 'none',
    'FAIL: claiming wizard did not show modal');
} else {
  console.log('No revealed wizard found — place one manually to test');
  const freeIdx = G.board.findIndex((c,i) =>
    c.type === T.FOREST && c.owner === OWNER.NONE && G.fog.has(i));
  G.board[freeIdx].type = T.WIZARD;
  G.validMoves.add(freeIdx);
  claimTile(freeIdx, OWNER.PLAYER);
  console.assert(G.phase === 'wizard-prompt', 'FAIL: wizard phase not set');
}

// 3. Invoke button sets wizardActiveFor
document.getElementById('wizard-invoke').click();
console.assert(G.wizardActiveFor === OWNER.PLAYER, 'FAIL: wizardActiveFor not set after invoke');

// 4. On next player turn, phase is wizard-teleport and valid moves are all unclaimed revealed
G.turn = OWNER.PLAYER;
G.phase = 'normal';
// Simulate start of player turn with active wizard
if (G.wizardActiveFor === OWNER.PLAYER) {
  G.phase = 'wizard-teleport';
  G.validMoves = computeValidMoves(OWNER.PLAYER);
}
const allUnclaimed = G.board.filter((c,i) =>
  c.owner === OWNER.NONE && c.type !== T.MOUNTAIN && G.fog.has(i)).length;
console.assert(G.validMoves.size === allUnclaimed,
  'FAIL: wizard teleport move set size mismatch');

console.log('Step 12 tests passed');
```

---

## Step 13 — Polish, Responsiveness & Final Integration

**Goal:** Final pass — responsive canvas sizing, edge cases, visual polish, and full game loop end-to-end verification.

### Tasks
1. **Responsive canvas:** On `startGame()` and on `window.resize`, compute:
   ```js
   const maxCellW = Math.floor(window.innerWidth * 0.80 / G.W);
   const maxCellH = Math.floor(window.innerHeight * 0.65 / G.H);
   G.cellSize = Math.max(40, Math.min(64, maxCellW, maxCellH));
   ```
   Resize canvas and re-render.
2. **Title screen glow animation:** CSS `@keyframes` on `#screen-title h1` — subtle pulsing `text-shadow`.
3. **Turn indicator clarity:** `#hud-turn` shows "Your Turn", "AI is thinking…" (during AI), or "Wizard Power Ready" (if `G.wizardActiveFor === OWNER.PLAYER`).
4. **Tile legend:** A row of small colored squares with labels below the canvas; rendered in HTML/CSS (not on canvas).
5. **Event log polish:** Max height with `overflow-y: auto`; newest events at top; color per type.
6. **Edge cases:**
   - Both players have no moves → trigger `checkWinCondition()` and show end screen.
   - Board with all Mountains (degenerate seed) → at least 2 Caves guaranteed by generation step.
   - Wizard on AI's first revealed tile → AI decision runs correctly.
   - Barbarian sweep wipes everything → validate fog recomputes correctly after.
7. **Inert Wizard tiles:** once `used = true`, they render with a dimmed icon and no special behavior.

### Tests
```js
// Full end-to-end game simulation (automated fast-play)
startGame({ W:8, H:6, seed:'e2e', depth:2 });

let safetyCounter = 0;
function simulateTurn() {
  safetyCounter++;
  if (safetyCounter > 500 || G.gameOver) {
    console.log('Game ended after', safetyCounter, 'simulated turns');
    console.assert(G.gameOver, 'FAIL: game not marked over after all moves');
    console.log('Final state:', G.board.filter(c=>c.owner===OWNER.PLAYER).length,
      'player vs', G.board.filter(c=>c.owner===OWNER.AI).length, 'AI');
    return;
  }

  computeValidMoves(G.turn); // sets G.validMoves internally or returns
  G.validMoves = computeValidMoves(G.turn);

  if (G.validMoves.size === 0) {
    G.turn = G.turn === OWNER.PLAYER ? OWNER.AI : OWNER.PLAYER;
    const otherMoves = computeValidMoves(G.turn);
    if (otherMoves.size === 0) {
      showEndScreen(checkWinCondition());
      return;
    }
  }

  // Pick random valid move for both sides (speed > AI quality for this test)
  const moves = [...G.validMoves];
  const pick = moves[Math.floor(Math.random() * moves.length)];
  claimTile(pick, G.turn);
  const winner = checkWinCondition();
  if (winner !== null) {
    showEndScreen(winner);
  } else {
    G.turn = G.turn === OWNER.PLAYER ? OWNER.AI : OWNER.PLAYER;
    simulateTurn();
  }
}

simulateTurn();

// 2. Responsiveness — resize window and check cellSize updates
window.dispatchEvent(new Event('resize'));
console.assert(G.cellSize >= 40 && G.cellSize <= 64,
  'FAIL: cellSize out of valid range after resize');

// 3. No JS errors in console during full play
console.log('Check browser console for JS errors — none expected');

// 4. Play-again flow from end screen
if (G.gameOver) {
  document.getElementById('btn-play-again').click();
  console.assert(document.getElementById('screen-title').style.display !== 'none' ||
    document.getElementById('screen-title').classList.contains('active'),
    'FAIL: play-again did not go to title');
  document.getElementById('btn-start').click();
  console.assert(document.getElementById('screen-game').style.display !== 'none' ||
    document.getElementById('screen-game').classList.contains('active'),
    'FAIL: start did not go to game screen');
}

console.log('Step 13 final integration tests passed');
```

---

## Implementation Order Summary

| Step | What You Build | Key Test |
|------|---------------|----------|
| 1 | HTML skeleton, CSS vars, font setup | Screen visibility, canvas exists |
| 2 | Title/setup screen UI | Inputs present, clamping works |
| 3 | PRNG + board generation | Cave guarantee, determinism, domain placement |
| 4 | Fog of War system | Starting tiles revealed, BFS propagation |
| 5 | Valid moves computation | No mountains/owned/fogged tiles, wizard exception |
| 6 | Tile claiming, Barbarian sweeps, win condition | Sweep clears row/col, majority win detected |
| 7 | Canvas rendering | Correct colors, icons, fog, highlights |
| 8 | Minimax AI + heuristic | Valid move returned, heuristic scales correctly |
| 9 | Player input handling, turn loop | Click-to-claim, turn switching, AI runs after player |
| 10 | HUD, event log, control buttons | Counts accurate, toggle fog, new game |
| 11 | End screen, win integration | End screen shown, play-again works |
| 12 | Wizard full flow | Modal shows, teleport turn highlights correctly |
| 13 | Polish, responsiveness, edge cases | Full simulated game completes without errors |
