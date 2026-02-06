/**
 * API communication layer for Sokoban Solver.
 */
const SolverAPI = {
    /**
     * Fetch the list of available preset puzzles.
     * @returns {Promise<{puzzles: Array}>}
     */
    async getPuzzles() {
        const response = await fetch('/api/puzzles');
        return response.json();
    },

    /**
     * Fetch a specific puzzle by ID.
     * @param {string} puzzleId
     * @returns {Promise<{id, puzzle, grid}>}
     */
    async getPuzzle(puzzleId) {
        const response = await fetch(`/api/puzzle/${puzzleId}`);
        if (!response.ok) {
            throw new Error(`Puzzle not found: ${puzzleId}`);
        }
        return response.json();
    },

    /**
     * Submit a puzzle to the solver.
     * @param {string} puzzleString - Standard Sokoban text format.
     * @param {object} options - Optional timeout and max_states.
     * @returns {Promise<object>} - Solve result.
     */
    async solve(puzzleString, options = {}) {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                puzzle: puzzleString,
                timeout: options.timeout || 60,
                max_states: options.max_states || 10000000,
            }),
        });
        return response.json();
    },
};
