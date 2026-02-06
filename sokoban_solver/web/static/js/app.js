/**
 * Main application logic for Sokoban Solver web interface.
 */

let currentPuzzle = null;   // { id, puzzle, grid }
let solution = null;        // result from solver API
let initialState = null;    // { player, boxes, goals } extracted from grid
let currentMove = 0;
let isPlaying = false;
let playInterval = null;
let renderer = null;

// ─── Initialization ────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    renderer = new PuzzleRenderer(document.getElementById('puzzle-canvas'));
    await loadPuzzleList();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('solve-btn').addEventListener('click', solvePuzzle);
    document.getElementById('play-btn').addEventListener('click', playSolution);
    document.getElementById('pause-btn').addEventListener('click', pauseSolution);
    document.getElementById('reset-btn').addEventListener('click', resetSolution);
    document.getElementById('step-btn').addEventListener('click', stepForward);

    const speedSlider = document.getElementById('speed-slider');
    speedSlider.addEventListener('input', (e) => {
        document.getElementById('speed-value').textContent = e.target.value;
        // Update interval if currently playing
        if (isPlaying) {
            pauseSolution();
            playSolution();
        }
    });
}

// ─── Puzzle List ───────────────────────────────────────────────

async function loadPuzzleList() {
    try {
        const data = await SolverAPI.getPuzzles();
        const listDiv = document.getElementById('puzzle-list');
        listDiv.innerHTML = '';

        data.puzzles.forEach(puzzle => {
            const btn = document.createElement('button');
            btn.className = 'puzzle-btn';
            btn.innerHTML = `${puzzle.name}<br><span class="difficulty">${puzzle.difficulty}</span>`;
            btn.dataset.puzzleId = puzzle.id;
            btn.addEventListener('click', () => selectPuzzle(puzzle.id, btn));
            listDiv.appendChild(btn);
        });
    } catch (err) {
        setStatus('Failed to load puzzle list.', 'error');
    }
}

async function selectPuzzle(puzzleId, btn) {
    try {
        // Highlight active button
        document.querySelectorAll('.puzzle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        currentPuzzle = await SolverAPI.getPuzzle(puzzleId);
        solution = null;
        currentMove = 0;
        pauseSolution();

        // Enable solve button
        document.getElementById('solve-btn').disabled = false;

        // Hide controls and stats
        document.getElementById('controls').classList.add('hidden');
        document.getElementById('stats').classList.add('hidden');

        // Extract initial state and render
        initialState = extractStateFromGrid(currentPuzzle.grid);
        renderState(initialState);

        setStatus('Puzzle loaded. Click "Solve Puzzle" to find the optimal solution.', '');
    } catch (err) {
        setStatus('Failed to load puzzle.', 'error');
    }
}

// ─── Solving ───────────────────────────────────────────────────

async function solvePuzzle() {
    if (!currentPuzzle) return;

    setStatus('Solving...', 'loading');
    document.getElementById('solve-btn').disabled = true;
    document.getElementById('controls').classList.add('hidden');
    document.getElementById('stats').classList.add('hidden');

    try {
        const result = await SolverAPI.solve(currentPuzzle.puzzle);

        if (result.success) {
            solution = result;
            currentMove = 0;

            // Use the initial_state from solver (authoritative positions)
            initialState = {
                player: result.initial_state.player,
                boxes: result.initial_state.boxes,
                goals: result.initial_state.goals,
            };

            // Show stats
            document.getElementById('states').textContent =
                result.stats.states_explored.toLocaleString();
            document.getElementById('time').textContent =
                result.stats.time_elapsed.toFixed(2) + 's';
            document.getElementById('length').textContent = result.length;
            document.getElementById('stats').classList.remove('hidden');

            // Show controls
            document.getElementById('total-moves').textContent = result.length;
            document.getElementById('current-move').textContent = '0';
            document.getElementById('controls').classList.remove('hidden');

            // Render initial state
            renderState(initialState);

            setStatus(
                `Solution found! ${result.length} pushes. Press Play to watch.`,
                'success'
            );
        } else {
            setStatus(`No solution: ${result.error}`, 'error');
        }
    } catch (err) {
        setStatus('Error communicating with solver.', 'error');
    }

    document.getElementById('solve-btn').disabled = false;
}

// ─── Playback ──────────────────────────────────────────────────

function playSolution() {
    if (!solution || isPlaying) return;
    if (currentMove >= solution.length) {
        resetSolution();
    }

    isPlaying = true;
    const speed = parseInt(document.getElementById('speed-slider').value);
    const delay = 1000 / speed;

    playInterval = setInterval(() => {
        if (currentMove < solution.length) {
            stepForward();
        } else {
            pauseSolution();
            setStatus('Solution complete!', 'success');
        }
    }, delay);
}

function pauseSolution() {
    isPlaying = false;
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
}

function resetSolution() {
    pauseSolution();
    currentMove = 0;
    document.getElementById('current-move').textContent = '0';
    renderState(initialState);
    if (solution) {
        setStatus(
            `Solution: ${solution.length} pushes. Press Play to watch.`,
            'success'
        );
    }
}

function stepForward() {
    if (!solution || currentMove >= solution.length) return;

    currentMove++;
    const state = getStateAtMove(currentMove);
    renderState(state);
    document.getElementById('current-move').textContent = currentMove;

    if (currentMove >= solution.length) {
        pauseSolution();
        setStatus('Solution complete!', 'success');
    }
}

// ─── State Reconstruction ──────────────────────────────────────

const DIRECTIONS = {
    'U': [0, -1],
    'D': [0, 1],
    'L': [-1, 0],
    'R': [1, 0],
};

/**
 * Reconstruct the puzzle state after applying the first `moveIndex` moves.
 */
function getStateAtMove(moveIndex) {
    let player = [...initialState.player];
    let boxes = initialState.boxes.map(b => [...b]);

    for (let i = 0; i < moveIndex; i++) {
        const move = solution.moves[i];
        const [dx, dy] = DIRECTIONS[move];

        // Find the box being pushed: it must be adjacent to player in the move direction
        // But player may not be adjacent — they walk first. In our push model,
        // we need to find the box the player pushes.
        // Since moves come from the solver, each move pushes exactly one box.
        // The pushed box is the one where (box - dir) is reachable by the player.
        // For simplicity, we search for a box that can be pushed in this direction.

        let pushed = -1;
        for (let bi = 0; bi < boxes.length; bi++) {
            const bx = boxes[bi][0];
            const by = boxes[bi][1];
            const pushFrom = [bx - dx, by - dy];
            const pushTo = [bx + dx, by + dy];

            // Push-from must be reachable by player (simplified: check it's not a wall/box)
            // Push-to must not be a wall or another box
            // Since we trust solver output, just find the matching push.
            // The player ends up at the box's old position after pushing.

            // Check push-to is not occupied by another box
            const pushToBlocked = boxes.some(
                (ob, oi) => oi !== bi && ob[0] === pushTo[0] && ob[1] === pushTo[1]
            );

            if (!pushToBlocked) {
                // Check the push-from position is reachable from current player
                // (full BFS would be ideal, but for correctness with solver output,
                //  we can do a simpler check — the solver guarantees validity)
                if (isReachable(player, pushFrom, boxes, currentPuzzle.grid)) {
                    pushed = bi;
                    break;
                }
            }
        }

        if (pushed >= 0) {
            // Move player to where the box was
            player = [boxes[pushed][0], boxes[pushed][1]];
            // Move box in direction
            boxes[pushed] = [boxes[pushed][0] + dx, boxes[pushed][1] + dy];
        }
    }

    return { player, boxes, goals: initialState.goals };
}

/**
 * Simple BFS to check if player can reach target without going through boxes or walls.
 */
function isReachable(from, to, boxes, grid) {
    if (from[0] === to[0] && from[1] === to[1]) return true;

    const rows = grid.length;
    const cols = Math.max(...grid.map(r => r.length));
    const boxSet = new Set(boxes.map(b => `${b[0]},${b[1]}`));
    const visited = new Set();
    const queue = [[from[0], from[1]]];
    visited.add(`${from[0]},${from[1]}`);

    while (queue.length > 0) {
        const [cx, cy] = queue.shift();

        for (const [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
            const nx = cx + dx;
            const ny = cy + dy;
            const key = `${nx},${ny}`;

            if (nx < 0 || ny < 0 || nx >= cols || ny >= rows) continue;
            if (visited.has(key)) continue;

            const ch = (grid[ny] && grid[ny][nx]) || '#';
            if (ch === '#') continue;
            if (boxSet.has(key)) continue;

            if (nx === to[0] && ny === to[1]) return true;

            visited.add(key);
            queue.push([nx, ny]);
        }
    }

    return false;
}

// ─── Rendering ─────────────────────────────────────────────────

function renderState(state) {
    if (!currentPuzzle) return;
    // Hide placeholder, show canvas
    const placeholder = document.getElementById('placeholder');
    if (placeholder) placeholder.classList.add('hidden');
    renderer.render(currentPuzzle.grid, state.player, state.boxes, state.goals);
}

// ─── Helpers ───────────────────────────────────────────────────

/**
 * Extract player, boxes, goals from a 2D character grid.
 */
function extractStateFromGrid(grid) {
    let player = null;
    const boxes = [];
    const goals = [];

    for (let y = 0; y < grid.length; y++) {
        for (let x = 0; x < grid[y].length; x++) {
            const ch = grid[y][x];
            if (ch === '@') player = [x, y];
            else if (ch === '+') { player = [x, y]; goals.push([x, y]); }
            else if (ch === '$') boxes.push([x, y]);
            else if (ch === '*') { boxes.push([x, y]); goals.push([x, y]); }
            else if (ch === '.') goals.push([x, y]);
        }
    }

    return { player, boxes, goals };
}

function setStatus(message, type) {
    const el = document.getElementById('status');
    el.textContent = message;
    el.className = 'status' + (type ? ' ' + type : '');
}
