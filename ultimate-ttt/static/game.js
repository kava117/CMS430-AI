"use strict";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let gameState = null;
let humanPlayer = 1;   // 1 = X, 2 = O
let waiting = false;   // true while waiting for API response

// ---------------------------------------------------------------------------
// Panel helpers
// ---------------------------------------------------------------------------
function showSetupPanel() {
  document.getElementById("setup-panel").classList.remove("hidden");
  document.getElementById("game-panel").classList.add("hidden");
}

function showGamePanel() {
  document.getElementById("setup-panel").classList.add("hidden");
  document.getElementById("game-panel").classList.remove("hidden");
}

// ---------------------------------------------------------------------------
// Status bar
// ---------------------------------------------------------------------------
function updateStatus(state, isThinking) {
  const el = document.getElementById("status");
  if (state.is_terminal) {
    if (state.winner === humanPlayer) {
      el.textContent = "You win! 🎉";
    } else if (state.winner === 0) {
      el.textContent = "Draw.";
    } else {
      el.textContent = "AI wins.";
    }
    return;
  }
  if (isThinking) {
    el.textContent = "AI is thinking...";
    return;
  }
  const isHumanTurn = state.current_player === humanPlayer;
  if (isHumanTurn) {
    const boardMsg = state.active_board !== null
      ? `You must play in board ${state.active_board + 1}.`
      : "You may play anywhere.";
    el.textContent = `Your turn — ${boardMsg}`;
  } else {
    el.textContent = "AI is thinking...";
  }
}

// ---------------------------------------------------------------------------
// Board rendering
// ---------------------------------------------------------------------------
function renderBoard(state, flashCell) {
  const boardEl = document.getElementById("board");
  boardEl.innerHTML = "";

  const legal = new Set();
  if (!state.is_terminal && !waiting && state.current_player === humanPlayer) {
    // Compute legal moves from state
    for (let b = 0; b < 9; b++) {
      if (state.active_board !== null && state.active_board !== b) continue;
      if (state.meta_board[b] !== 0) continue;
      for (let c = 0; c < 9; c++) {
        if (state.board[b][c] === 0) {
          legal.add(`${b},${c}`);
        }
      }
    }
    // If active_board is set but that board is claimed/full, allow all active boards
    if (state.active_board !== null && state.meta_board[state.active_board] !== 0) {
      for (let b = 0; b < 9; b++) {
        if (state.meta_board[b] !== 0) continue;
        for (let c = 0; c < 9; c++) {
          if (state.board[b][c] === 0) {
            legal.add(`${b},${c}`);
          }
        }
      }
    }
  }

  for (let b = 0; b < 9; b++) {
    const subEl = document.createElement("div");
    subEl.classList.add("sub-board");
    subEl.dataset.board = b;

    const isActive = !state.is_terminal && (
      state.active_board === b ||
      (state.active_board === null && state.meta_board[b] === 0) ||
      (state.active_board !== null && state.meta_board[state.active_board] !== 0 && state.meta_board[b] === 0)
    );

    if (isActive) subEl.classList.add("active-board");
    if (state.meta_board[b] !== 0) subEl.classList.add("claimed");

    for (let c = 0; c < 9; c++) {
      const cellEl = document.createElement("div");
      cellEl.classList.add("cell");
      cellEl.dataset.board = b;
      cellEl.dataset.cell = c;

      const val = state.board[b][c];
      if (val === 1) {
        cellEl.textContent = "X";
        cellEl.classList.add("x");
      } else if (val === 2) {
        cellEl.textContent = "O";
        cellEl.classList.add("o");
      }

      // AI flash highlight
      if (flashCell && flashCell[0] === b && flashCell[1] === c) {
        cellEl.classList.add("ai-flash");
      }

      if (legal.has(`${b},${c}`)) {
        cellEl.classList.add("legal");
        cellEl.addEventListener("click", () => onCellClick(b, c));
      }

      subEl.appendChild(cellEl);
    }

    // Claimed overlay
    if (state.meta_board[b] !== 0) {
      const overlay = document.createElement("div");
      overlay.classList.add("claim-overlay");
      if (state.meta_board[b] === 1) {
        overlay.textContent = "X";
        overlay.classList.add("x");
      } else if (state.meta_board[b] === 2) {
        overlay.textContent = "O";
        overlay.classList.add("o");
      } else {
        overlay.textContent = "Draw";
        overlay.classList.add("draw");
      }
      subEl.appendChild(overlay);
    }

    boardEl.appendChild(subEl);
  }
}

// ---------------------------------------------------------------------------
// Cell click handler
// ---------------------------------------------------------------------------
async function onCellClick(boardIdx, cellIdx) {
  if (waiting) return;
  waiting = true;
  updateStatus(gameState, true);
  renderBoard(gameState, null);

  try {
    const resp = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board_index: boardIdx, cell_index: cellIdx }),
    });
    const data = await resp.json();

    if (data.error) {
      console.warn("Move error:", data.error);
      waiting = false;
      updateStatus(gameState, false);
      renderBoard(gameState, null);
      return;
    }

    gameState = data.state;

    if (data.ai_move) {
      // Flash AI move for 600ms before rendering final state
      const [ab, ac] = data.ai_move;
      renderBoard(gameState, [ab, ac]);
      updateStatus(gameState, false);
      await new Promise(r => setTimeout(r, 600));
    }

    renderBoard(gameState, null);
    updateStatus(gameState, false);

    if (gameState.is_terminal) {
      setTimeout(showSetupPanel, 2500);
    }
  } catch (err) {
    console.error("Fetch error:", err);
  } finally {
    waiting = false;
  }
}

// ---------------------------------------------------------------------------
// Start game
// ---------------------------------------------------------------------------
async function startGame() {
  const difficulty = document.getElementById("difficulty").value;
  const side = document.getElementById("side").value;
  humanPlayer = side === "X" ? 1 : 2;
  waiting = true;

  showGamePanel();
  document.getElementById("status").textContent = "Starting...";

  try {
    const resp = await fetch("/api/new_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ difficulty, human_plays: side }),
    });
    const data = await resp.json();
    gameState = data.state;

    if (data.ai_move) {
      const [ab, ac] = data.ai_move;
      renderBoard(gameState, [ab, ac]);
      updateStatus(gameState, false);
      await new Promise(r => setTimeout(r, 600));
    }

    renderBoard(gameState, null);
    updateStatus(gameState, false);
  } catch (err) {
    console.error("Start game error:", err);
  } finally {
    waiting = false;
  }
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
document.getElementById("start-btn").addEventListener("click", startGame);
document.getElementById("new-game-btn").addEventListener("click", showSetupPanel);
