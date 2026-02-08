/**
 * Main application logic for Sokoban Solver web interface.
 */

// ─── Solver Mode State ──────────────────────────────────────────
let currentPuzzle = null;   // { id, puzzle, grid }
let solution = null;        // result from solver API
let initialState = null;    // { player, boxes, goals } extracted from grid
let currentMove = 0;
let isPlaying = false;
let playInterval = null;
let renderer = null;

// ─── Builder Mode State ─────────────────────────────────────────
let builder = null;
let builderRenderer = null;
let builderSolution = null;
let builderInitialState = null;
let builderCurrentMove = 0;
let builderIsPlaying = false;
let builderPlayInterval = null;
let builderGrid = null;  // grid snapshot for playback

// ─── Initialization ────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    renderer = new PuzzleRenderer(document.getElementById('puzzle-canvas'));
    await loadPuzzleList();
    setupEventListeners();
    setupTabs();
    initBuilder();
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
 * Uses pushed_boxes from solver to identify exactly which box is pushed each step.
 */
function getStateAtMove(moveIndex) {
    let player = [...initialState.player];
    let boxes = initialState.boxes.map(b => [...b]);

    for (let i = 0; i < moveIndex; i++) {
        const move = solution.moves[i];
        const [dx, dy] = DIRECTIONS[move];
        const pushedBox = solution.pushed_boxes[i];

        // Find the box at the pushed position
        const bi = boxes.findIndex(b => b[0] === pushedBox[0] && b[1] === pushedBox[1]);

        if (bi >= 0) {
            // Move player to where the box was
            player = [boxes[bi][0], boxes[bi][1]];
            // Move box in push direction
            boxes[bi] = [boxes[bi][0] + dx, boxes[bi][1] + dy];
        }
    }

    return { player, boxes, goals: initialState.goals };
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

// ─── Tab Switching ──────────────────────────────────────────────

function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            // Toggle active tab button
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Toggle mode visibility
            document.getElementById('solver-mode').classList.toggle('hidden', target !== 'solver');
            document.getElementById('builder-mode').classList.toggle('hidden', target !== 'builder');

            // Pause any running playback
            pauseSolution();
            builderPauseSolution();
        });
    });
}

// ─── Builder Mode ───────────────────────────────────────────────

function initBuilder() {
    const canvas = document.getElementById('builder-canvas');
    builder = new PuzzleBuilder(canvas, 8, 8);
    builderRenderer = new PuzzleRenderer(canvas);

    // Tool palette
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            builder.setTool(btn.dataset.tool);
        });
    });

    // Clear grid
    document.getElementById('clear-btn').addEventListener('click', () => {
        builder.clear();
        builderSolution = null;
        builderPauseSolution();
        document.getElementById('builder-controls').classList.add('hidden');
        document.getElementById('builder-stats').classList.add('hidden');
        setBuilderStatus('Grid cleared.', '');
    });

    // Resize grid
    document.getElementById('resize-btn').addEventListener('click', () => {
        const w = parseInt(document.getElementById('grid-width').value) || 8;
        const h = parseInt(document.getElementById('grid-height').value) || 8;
        const cw = Math.max(4, Math.min(20, w));
        const ch = Math.max(4, Math.min(20, h));
        document.getElementById('grid-width').value = cw;
        document.getElementById('grid-height').value = ch;
        builder.resize(cw, ch);
        builderSolution = null;
        builderPauseSolution();
        document.getElementById('builder-controls').classList.add('hidden');
        document.getElementById('builder-stats').classList.add('hidden');
        setBuilderStatus(`Grid resized to ${cw}x${ch}.`, '');
    });

    // Validate
    document.getElementById('validate-btn').addEventListener('click', async () => {
        setBuilderStatus('Validating...', 'loading');
        const result = await builder.validate();

        if (result.valid) {
            let msg = 'Puzzle is valid!';
            if (result.warnings && result.warnings.length > 0) {
                msg += ' Warning: ' + result.warnings.join('; ');
            }
            setBuilderStatus(msg, 'success');
        } else {
            setBuilderStatus('Invalid: ' + result.errors.join('; '), 'error');
        }
    });

    // Solve
    document.getElementById('build-solve-btn').addEventListener('click', builderSolvePuzzle);

    // Playback controls
    document.getElementById('builder-play-btn').addEventListener('click', builderPlaySolution);
    document.getElementById('builder-pause-btn').addEventListener('click', builderPauseSolution);
    document.getElementById('builder-reset-btn').addEventListener('click', builderResetSolution);
    document.getElementById('builder-step-btn').addEventListener('click', builderStepForward);

    const speedSlider = document.getElementById('builder-speed-slider');
    speedSlider.addEventListener('input', (e) => {
        document.getElementById('builder-speed-value').textContent = e.target.value;
        if (builderIsPlaying) {
            builderPauseSolution();
            builderPlaySolution();
        }
    });
}

async function builderSolvePuzzle() {
    setBuilderStatus('Solving...', 'loading');
    document.getElementById('builder-controls').classList.add('hidden');
    document.getElementById('builder-stats').classList.add('hidden');
    builderPauseSolution();

    try {
        const result = await builder.solve();

        if (result.success) {
            builderSolution = result;
            builderCurrentMove = 0;

            // Snapshot the grid for playback rendering
            builderGrid = builder.grid.map(row => [...row]);

            builderInitialState = {
                player: result.initial_state.player,
                boxes: result.initial_state.boxes,
                goals: result.initial_state.goals,
            };

            // Show stats
            document.getElementById('builder-states').textContent =
                result.stats.states_explored.toLocaleString();
            document.getElementById('builder-time').textContent =
                result.stats.time_elapsed.toFixed(2) + 's';
            document.getElementById('builder-length').textContent = result.length;
            document.getElementById('builder-stats').classList.remove('hidden');

            // Show controls
            document.getElementById('builder-total-moves').textContent = result.length;
            document.getElementById('builder-current-move').textContent = '0';
            document.getElementById('builder-controls').classList.remove('hidden');

            // Render initial state on canvas using PuzzleRenderer
            builderRenderState(builderInitialState);

            setBuilderStatus(
                `Solution found! ${result.length} pushes. Press Play to watch.`,
                'success'
            );
        } else {
            setBuilderStatus(`Failed: ${result.error}`, 'error');
        }
    } catch (err) {
        setBuilderStatus('Error communicating with solver.', 'error');
    }
}

// ─── Builder Playback ───────────────────────────────────────────

function builderPlaySolution() {
    if (!builderSolution || builderIsPlaying) return;
    if (builderCurrentMove >= builderSolution.length) {
        builderResetSolution();
    }

    builderIsPlaying = true;
    const speed = parseInt(document.getElementById('builder-speed-slider').value);
    const delay = 1000 / speed;

    builderPlayInterval = setInterval(() => {
        if (builderCurrentMove < builderSolution.length) {
            builderStepForward();
        } else {
            builderPauseSolution();
            setBuilderStatus('Solution complete!', 'success');
        }
    }, delay);
}

function builderPauseSolution() {
    builderIsPlaying = false;
    if (builderPlayInterval) {
        clearInterval(builderPlayInterval);
        builderPlayInterval = null;
    }
}

function builderResetSolution() {
    builderPauseSolution();
    builderCurrentMove = 0;
    document.getElementById('builder-current-move').textContent = '0';
    if (builderInitialState) {
        builderRenderState(builderInitialState);
    }
    if (builderSolution) {
        setBuilderStatus(
            `Solution: ${builderSolution.length} pushes. Press Play to watch.`,
            'success'
        );
    }
}

function builderStepForward() {
    if (!builderSolution || builderCurrentMove >= builderSolution.length) return;

    builderCurrentMove++;
    const state = builderGetStateAtMove(builderCurrentMove);
    builderRenderState(state);
    document.getElementById('builder-current-move').textContent = builderCurrentMove;

    if (builderCurrentMove >= builderSolution.length) {
        builderPauseSolution();
        setBuilderStatus('Solution complete!', 'success');
    }
}

function builderGetStateAtMove(moveIndex) {
    let player = [...builderInitialState.player];
    let boxes = builderInitialState.boxes.map(b => [...b]);

    for (let i = 0; i < moveIndex; i++) {
        const move = builderSolution.moves[i];
        const [dx, dy] = DIRECTIONS[move];
        const pushedBox = builderSolution.pushed_boxes[i];

        const bi = boxes.findIndex(b => b[0] === pushedBox[0] && b[1] === pushedBox[1]);

        if (bi >= 0) {
            player = [boxes[bi][0], boxes[bi][1]];
            boxes[bi] = [boxes[bi][0] + dx, boxes[bi][1] + dy];
        }
    }

    return { player, boxes, goals: builderInitialState.goals };
}

function builderRenderState(state) {
    if (!builderGrid) return;
    builderRenderer.render(builderGrid, state.player, state.boxes, state.goals);
}

function setBuilderStatus(message, type) {
    const el = document.getElementById('builder-status');
    el.textContent = message;
    el.className = 'status' + (type ? ' ' + type : '');
}
