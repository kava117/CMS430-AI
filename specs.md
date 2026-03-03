# DOMINION — Game Design Specification
**For use by a coding agent to implement the complete game**

---

## 1. Overview

**Dominion** is a web-based, single-file, two-player turn-based territory strategy game. One player is human; the other is a computer opponent driven by a minimax algorithm with alpha-beta pruning. The goal is to claim more tiles than your opponent by the time the board is fully contested.

**Deliverable:** A single self-contained `.html` file with all game logic, AI, rendering, and styles inline. No build step, no external dependencies beyond Google Fonts and a CDN-hosted font if desired.

---

## 2. Technology Stack

- **Language:** Vanilla JavaScript (ES2020+)
- **Rendering:** HTML5 Canvas (2D context)
- **Styling:** Inline CSS with CSS custom properties
- **No frameworks, no npm packages, no backend**
- A seeded pseudo-random number generator (PRNG) must be implemented in JS (e.g. mulberry32) — do not use `Math.random()` for anything that affects board generation or Barbarian direction on square boards

---

## 3. Game Board

### 3.1 Configuration
The player configures the game before starting via a title/setup screen with these fields:
- **Board Width** — integer, range 8–24, default 14
- **Board Height** — integer, range 6–18, default 10
- **Seed** — string; if blank, use a random seed (e.g. `Date.now()` stringified). The seed must produce an identical board every time the same string is entered.
- **AI Difficulty** — dropdown: Scout (depth 2), Knight (depth 3, default), Warlord (depth 4)

### 3.2 Grid Structure
The board is a flat `W × H` grid of cells. Each cell has:
- `type` — one of the tile types listed in Section 5
- `owner` — `NONE`, `PLAYER`, or `AI`
- `used` — boolean flag (relevant only for Wizard tiles)

Cell indexing: `index = y * W + x`. Helper functions `idx(x,y)` and `xy(i)` should be provided.

### 3.3 Board Generation
Use the seeded PRNG to assign tile types. Suggested probability weights (adjust for balance):

| Tile | Weight |
|------|--------|
| Forest | 35 |
| Plains | 20 |
| Tower | 8 |
| Cave | 8 |
| Mountain | 15 |
| Wizard | 5 |
| Barbarian | 9 |

Domain tiles are **not** randomly placed — see Section 3.4.

**Guarantee at least 2 Cave tiles** on every board. If the PRNG produces fewer, overwrite random non-Mountain cells until the minimum is met.

### 3.4 Starting Positions
Each player starts with exactly **1 Domain tile**, placed deterministically:
- **Player:** placed at or near `(1, 1)` (top-left region), walking right until a non-Mountain cell is found
- **AI:** placed at or near `(W-2, H-2)` (bottom-right region), walking left until an unclaimed non-Mountain cell is found

These starting Domain tiles are assigned `owner = PLAYER` and `owner = AI` respectively at game start.

---

## 4. Fog of War

### 4.1 Shared Fog Model
There is **one shared fog layer** for both players. A tile is either **revealed** or **hidden (fogged)**.

- A tile becomes revealed when it enters the vision range of **either player's** claimed tiles.
- Once revealed, a tile stays revealed for the rest of the game — fog does not re-close.
- Both players (human and AI) see the same revealed set. There is no private fog per player.

### 4.2 Vision Ranges
Each owned tile contributes vision in cardinal directions (BFS flood) up to its range:

| Tile Type | Vision Range |
|-----------|-------------|
| Forest | 1 (cardinally adjacent only) |
| Domain | 1 |
| Wizard | 1 |
| Barbarian | 1 |
| Plains | 2 |
| Tower | 3 |
| Cave | 1 (but also reveals all Cave tiles globally — see §5.5) |
| Mountain | 0 (Mountains don't contribute vision even if owned — mountains cannot be owned) |

Vision is computed as a cardinal BFS flood: from each owned tile of the relevant player, expand outward step-by-step up to the tile's vision range. Mountains do **not** block vision propagation.

### 4.3 Fog Rendering
Fogged tiles are rendered as a dark, obscured cell. The tile type and owner underneath are not shown to the player. Revealed tiles are always drawn with full detail.

Provide a **"Toggle Fog"** button that lets the player reveal the full board for debugging/spectating purposes. This does not affect game logic.

### 4.4 Fog and AI
Because fog is shared, the AI has the same information the player does. The AI must only reason about revealed tiles when computing moves and evaluating the board state. It must not use knowledge of hidden tiles in its heuristic or move generation.

---

## 5. Tile Types

There are 8 tile types. Each has distinct expansion behavior (what moves it adds to the valid move list) and vision range (Section 4.2).

### 5.1 Domain
- **Expansion:** Adds all cardinally adjacent (distance 1) unclaimed non-Mountain tiles to the valid moves list.
- **Notes:** Acts identically to Forest for expansion and vision purposes. Starting tile for each player.

### 5.2 Forest
- **Expansion:** Adds all cardinally adjacent (distance 1) unclaimed non-Mountain tiles to the valid moves list.

### 5.3 Plains
- **Expansion:** Adds all unclaimed non-Mountain tiles reachable within **up to 2** cardinal steps (Manhattan distance ≤ 2, axis-aligned paths). This includes distance-1 and distance-2 tiles. Distance-2 tiles do not require the distance-1 intermediate to be unclaimed or a specific type — all tiles at distance ≤ 2 in cardinal directions are candidates.

### 5.4 Tower
- **Expansion:** Adds all unclaimed non-Mountain tiles reachable within **up to 3** cardinal steps (Manhattan distance ≤ 3). Expansion is teleport-style — Mountains between the Tower and the target do **not** block the move. Any unclaimed non-Mountain tile within cardinal distance ≤ 3 is a valid target.
- **Important correction from prior design:** The Tower allows the player to claim **one tile** of their choice from all valid targets. It does NOT claim all tiles in range at once.

### 5.5 Cave
- **Expansion:** When a player owns at least one Cave tile, **all unclaimed Cave tiles anywhere on the board** are added to the valid moves list (regardless of distance or fog, as long as the cave tiles have been revealed).
- **Vision bonus:** Owning any Cave tile also reveals all other Cave tiles globally (they are added to the shared fog-revealed set immediately).

### 5.6 Mountain
- **Cannot be claimed by either player.** Never a valid move. Never contributes to score. Rendered distinctly.

### 5.7 Wizard
- **Claiming:** A Wizard tile can be claimed like any normal tile if it's within range of an existing owned tile.
- **Activation prompt:** When a player (human or AI) claims a Wizard tile, they are offered a choice:
  - **Invoke the Wizard** — on their *next* turn, instead of a normal move, they may teleport their expansion to any unclaimed non-Mountain tile on the entire board (ignoring fog, ignoring adjacency). The Wizard tile is then marked `used = true` and becomes inert.
  - **Decline** — the turn ends normally; the wizard power is permanently lost.
- **Inert state:** A used Wizard tile is still owned and counts toward score, but provides no special expansion. It still contributes distance-1 vision.
- **AI behavior:** The AI should invoke the Wizard if the best teleport target has a strategic value above a threshold (see Section 8.4).

### 5.8 Barbarian
- **Claiming:** Can be claimed as a valid move if within range.
- **Trigger on reveal:** When a Barbarian tile is newly added to the shared revealed set (i.e., it transitions from fogged to revealed), it **immediately triggers** — before any further moves. The trigger is checked after each fog update.
- **Trigger on claim:** If a player claims a Barbarian tile directly, it also triggers immediately upon being claimed.
- **Sweep direction:**
  - If `W > H`: sweeps horizontally (across the Barbarian's entire row)
  - If `H > W`: sweeps vertically (down the Barbarian's entire column)
  - If `W == H`: choose randomly using the seeded PRNG
- **Effect:** Every non-Mountain tile in the Barbarian's row (horizontal) or column (vertical) has its `owner` reset to `NONE`. The Barbarian tile itself also has `owner = NONE` after the sweep. It does **not** become impassable — it can be reclaimed by either player afterward.
- **Multiple Barbarians:** If revealing one tile causes multiple Barbarians to be newly revealed, process each one in index order.

---

## 6. Valid Moves

On each turn, the active player's valid move set is computed fresh:

1. Start with an empty set.
2. For each tile owned by the active player, apply that tile's expansion rules (Section 5) to generate candidate tiles.
3. A candidate tile is added to the valid move set if and only if:
   - It is not a Mountain
   - Its `owner` is `NONE`
   - It is in the **revealed** (non-fogged) shared fog set
4. Wizard teleport moves (if the player has an active Wizard power) bypass the fog and adjacency requirement — any unclaimed non-Mountain tile qualifies.
5. The valid move set is recomputed at the start of each player's turn and after any Barbarian trigger.

---

## 7. Turn Structure

### 7.1 Player Turn
1. Compute valid moves.
2. Highlight valid move tiles on the canvas.
3. Wait for the player to click a highlighted tile.
4. If the player owns an unused Wizard and previously chose to invoke it, the "wizard teleport" phase is active instead of the normal move — they click any unclaimed non-Mountain tile.
5. On click: claim the tile (`owner = PLAYER`), update shared fog, check for newly revealed Barbarians and trigger them if found.
6. If the claimed tile was a Wizard: show the invoke/decline prompt.
7. Check win condition. If not over, pass to AI.

### 7.2 AI Turn
1. Compute valid moves for AI.
2. If AI has an active Wizard power, evaluate a teleport target (Section 8.4); if worthwhile, execute wizard teleport.
3. Otherwise, run minimax (Section 8) to select the best move.
4. Claim the chosen tile, update shared fog, check for Barbarian triggers.
5. If claimed tile was a Wizard: evaluate and decide (no UI prompt — AI decides instantly).
6. Check win condition. If not over, pass to player.

### 7.3 No Moves
If the active player has no valid moves, their turn is skipped and the turn passes to the opponent. If **both** players have no valid moves, trigger win condition check.

---

## 8. AI — Minimax with Alpha-Beta Pruning

### 8.1 Overview
The AI uses depth-limited minimax search with alpha-beta pruning. The AI is the maximizing player; the human is the minimizing player. Search depth is set by the difficulty selection (2, 3, or 4).

### 8.2 Move Simulation
During minimax, board state must be snapshottable and restorable cheaply. Recommended approach: copy `board` array (array of `{type, owner, used}` objects) before each simulated move, and restore after. Fog must also be recomputed after each simulated move.

Barbarian sweeps must be **simulated** during minimax (using a deterministic direction rule — no randomness during search; use the `W >= H ? 'h' : 'v'` rule for square boards during simulation).

### 8.3 Heuristic Evaluation Function
When the search reaches maximum depth (or a terminal state), evaluate the board using this weighted scoring function:

```
score = 0
score += (aiTileCount - playerTileCount) * 10       // tile differential — primary objective
score += (aiFrontier - playerFrontier) * 3          // mobility advantage
score += aiCaveControl ? +8 : 0                     // bonus for owning any Cave
score += playerCaveControl ? -8 : 0                 // penalty if player owns Cave
score += aiHasActiveWizard ? +5 : 0                 // strategic reserve
score += playerHasActiveWizard ? -5 : 0
score += barbExposurePenalty(AI) * -2               // penalty for tiles in a Barbarian's sweep path
score += barbExposurePenalty(PLAYER) * +2
```

**Frontier** = number of valid moves available (computed with `computeValidMoves`).

**Barbarian exposure penalty** = count of owned tiles that share a row (if W >= H) or column (if H > W) with an unrevealed (fogged) Barbarian tile. This represents risk.

The AI must only use revealed tile information in its heuristic — do not score hidden tiles.

### 8.4 Wizard Teleport Decision (AI)
When the AI has an active Wizard power, evaluate all revealed unclaimed non-Mountain tiles and assign each a strategic value:

| Tile Type | Strategic Value |
|-----------|----------------|
| Cave | 4 |
| Wizard | 3 |
| Tower | 2.5 |
| Plains | 2 |
| Forest / Domain | 1.5 |
| Barbarian | 0.5 |

If the best tile's value > 2, the AI uses the Wizard to claim it. Otherwise it declines.

### 8.5 Alpha-Beta Pruning
Standard alpha-beta pruning must be implemented. At each node:
- Maximizing: track `alpha`, prune when `beta <= alpha`
- Minimizing: track `beta`, prune when `beta <= alpha`

Move ordering: sort candidate moves by immediate tile strategic value (descending) before searching — this improves pruning efficiency significantly.

---

## 9. Win Condition

Check after every move (by either player):

1. **All claimable tiles claimed:** If every non-Mountain tile has an owner, the game ends. Winner has the higher tile count.
2. **Majority secured:** If one player owns more than `floor(total_claimable / 2)` tiles, they win immediately (opponent cannot catch up).
3. **No moves for both:** If both players have zero valid moves, the game ends. Higher tile count wins.
4. **Tie:** If counts are equal at game end, declare a draw.

---

## 10. Scoring & HUD

Display at all times:
- **Player tile count** (live, updates after every move)
- **AI tile count**
- **Turn indicator** — whose turn it is, or "AI is thinking…" during AI computation
- **Event log** — a scrollable panel showing the last several actions: tile claims, Barbarian triggers, Wizard activations, and game-end messages. Color-code entries by player (blue for human, red for AI, gold/amber for world events).

---

## 11. UI & Rendering

### 11.1 Visual Design Direction
The game should have a **dark medieval / cartographic** aesthetic. Suggested palette:

- Background: very dark near-black green (`#0d0f0e`)
- Player color: muted steel blue (`#4a9eff`)
- AI color: muted crimson (`#e05555`)
- Accent / gold: aged parchment gold (`#c9a84c`)
- Text: warm parchment (`#d4c9a8`)
- Fog: near-black (`#080a08`)

Typography: use Google Fonts. Suggested pairing — `Cinzel` (display/headers) + `Crimson Text` (body/log). Avoid generic fonts like Inter, Roboto, Arial.

Do **not** use default browser styling for any element. All UI should feel crafted and intentional.

### 11.2 Canvas Rendering
- Each cell should be approximately 56–64px square (adjust based on viewport)
- Cells have a small inset padding to create visible gutters between them
- Each tile type has a distinct base color (neutral / unowned), player-owned color, and AI-owned color
- Each tile type has a distinct icon/glyph rendered centered in the cell (use Unicode symbols or drawn shapes)
- Owned tiles have a colored border matching the owning player's color
- Valid move tiles are highlighted with a semi-transparent overlay and a colored border (suggest yellow-green)
- Fogged tiles are rendered as a flat dark rectangle with subtle texture; no icon or color shown
- Wizard teleport phase: highlight all unclaimed non-Mountain tiles in a distinct color (suggest purple)

### 11.3 Tile Visual Reference

| Tile | Suggested Base Color | Suggested Icon |
|------|---------------------|----------------|
| Forest | dark green `#2d4a2d` | ♣ or tree glyph |
| Plains | muted yellow-green `#6b7a3a` | ~ or ≈ |
| Tower | dark navy `#3a3a5c` | ▲ |
| Cave | deep grey-purple `#2a2a38` | ○ |
| Mountain | charcoal `#3a3a3a` | ◆ |
| Wizard | deep violet `#4a2a60` | ✦ |
| Barbarian | dark rust `#5c2e18` | ⚔ |
| Domain | aged brown `#6b5a38` | ⬡ |

Player-owned tiles shift toward blue; AI-owned tiles shift toward crimson.

### 11.4 Screens

**Title/Setup Screen:**
- Full-screen dark overlay
- Game title (`DOMINION`) in large Cinzel font with subtle glow animation
- Tagline in italic Crimson Text
- Setup card with the configuration fields (Section 3.1)
- "Begin Conquest" button

**Game Screen:**
- Header row: Player HUD (left) | Title + turn indicator (center) | AI HUD (right)
- Canvas (centered, with subtle box shadow)
- Bottom bar: Event log (left) | Control buttons (right: New Game, Toggle Fog)
- Tile legend below the canvas

**End Screen:**
- Modal overlay with result (VICTORY / DEFEAT / DRAW) in large styled text
- Final score display
- "Play Again" button returning to title screen

### 11.5 Wizard Prompt (Human Player)
When the player claims a Wizard tile, display a modal overlay asking:
- **Invoke Wizard** — activates the teleport for their next move
- **Decline** — ends the turn normally, power is lost

### 11.6 Responsiveness
The canvas should scale so the full board is visible on common screen sizes. If the board would overflow the viewport, reduce cell size accordingly (minimum ~40px per cell).

---

## 12. Implementation Notes for the Coding Agent

### 12.1 State Management
Maintain a single global game state object `G` containing:
```javascript
G = {
  W, H,               // board dimensions
  board,              // flat array of cell objects
  fog,                // Set of revealed tile indices (shared)
  turn,               // PLAYER or AI
  phase,              // 'normal' | 'wizard-prompt' | 'wizard-teleport' | 'ai-thinking' | 'gameover'
  wizardActiveFor,    // NONE | PLAYER | AI — who has an active wizard power pending
  validMoves,         // Set of valid move indices for current player
  gameOver,           // boolean
  rng,                // seeded PRNG function
}
```

### 12.2 Key Functions to Implement
- `generateBoard(rng, W, H)` — populate `G.board` using PRNG
- `computeFog()` — recompute the shared fog set from all owned tiles
- `computeValidMoves(owner)` — return Set of valid move indices
- `claimTile(index, owner)` — set owner, recompute fog, check Barbarian reveals
- `triggerBarbarians(index)` — execute sweep, reset owners, recompute fog
- `checkWinCondition()` — return winner or null
- `minimaxRoot(depth)` — return best move index for AI
- `minimaxAlphaBeta(depth, alpha, beta, isMaximizing)` — recursive search
- `heuristic()` — return numeric board evaluation
- `render()` — draw entire board to canvas
- `handlePlayerClick(x, y)` — process human input

### 12.3 Performance Considerations
- Minimax at depth 4 on a 16×12 board can be slow if not optimized. Implement move ordering (sort by strategic value before searching) to maximize pruning effectiveness.
- Snapshot/restore of board state should avoid deep cloning complex objects — a flat array of `{type, owner, used}` tuples copies efficiently.
- Consider a 400–600ms artificial delay before the AI move to give the UI time to render the "AI is thinking…" state before the JS thread blocks.

### 12.4 Barbarian Timing Detail
After every `claimTile` call, recompute fog and then check: for every Barbarian tile that is now revealed (in `fog`) but was not previously revealed, trigger it. Track the pre-claim fog snapshot to detect newly revealed tiles.

### 12.5 Seeded PRNG
Implement mulberry32 or a similar seedable PRNG. Hash the seed string to an integer using FNV-1a or similar before passing to the PRNG constructor.

```javascript
function hashStr(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return h;
}

function mulberry32(seed) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
```

---

## 13. Tile Behavior Quick Reference

| Tile | Claimable? | Expansion Adds... | Vision | Special |
|------|-----------|------------------|--------|---------|
| Domain | Yes | Cardinal dist ≤ 1 | 1 | Starting tile |
| Forest | Yes | Cardinal dist ≤ 1 | 1 | — |
| Plains | Yes | Cardinal dist ≤ 2 | 2 | — |
| Tower | Yes | Cardinal dist ≤ 3 (teleport-style) | 3 | Pick ONE target |
| Cave | Yes | All unclaimed revealed Caves | 1 | Reveals all Caves globally |
| Mountain | **No** | Nothing | 0 | Impassable |
| Wizard | Yes | Normal (dist ≤ 1 from nearby tiles) | 1 | On claim: prompt to invoke teleport next turn |
| Barbarian | Yes | Cardinal dist ≤ 1 | 1 | Triggers sweep on reveal or claim |

---

## 14. Out of Scope

The following are explicitly **not** required:
- Multiplayer networking
- Save/load game state
- Mobile touch optimization (mouse/click only is fine)
- Animations (moves can be instant)
- Sound effects
- Undo functionality