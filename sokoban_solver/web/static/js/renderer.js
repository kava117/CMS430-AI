/**
 * Canvas-based puzzle renderer for Sokoban.
 */
class PuzzleRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.tileSize = 48;
        this.colors = {
            wall:         '#5a5a5a',
            wallStroke:   '#3a3a3a',
            floor:        '#2a2a4a',
            goal:         '#3a6a3a',
            box:          '#b87333',
            boxStroke:    '#8b5a2b',
            boxOnGoal:    '#2e8b57',
            boxGoalStroke:'#1a6b3a',
            player:       '#4169e1',
            playerOnGoal: '#1e90ff',
            outside:      '#1a1a2e',
        };
    }

    /**
     * Render a puzzle state on the canvas.
     *
     * @param {string[][]} grid - 2D character grid (for wall layout).
     * @param {number[]} playerPos - [x, y] of the player.
     * @param {number[][]} boxes - Array of [x, y] box positions.
     * @param {number[][]} goals - Array of [x, y] goal positions.
     */
    render(grid, playerPos, boxes, goals) {
        const rows = grid.length;
        const cols = Math.max(...grid.map(r => r.length));

        this.canvas.width = cols * this.tileSize;
        this.canvas.height = rows * this.tileSize;

        // Build lookup sets for boxes and goals
        const boxSet = new Set(boxes.map(b => `${b[0]},${b[1]}`));
        const goalSet = new Set(goals.map(g => `${g[0]},${g[1]}`));

        // Draw each tile
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const char = (grid[y] && grid[y][x]) || ' ';
                const px = x * this.tileSize;
                const py = y * this.tileSize;
                const key = `${x},${y}`;

                if (char === '#') {
                    this._drawWall(px, py);
                } else if (char === ' ' && !goalSet.has(key) && !boxSet.has(key) &&
                           !(playerPos && playerPos[0] === x && playerPos[1] === y)) {
                    // Check if this is inside the puzzle or outside
                    this._drawOutside(px, py);
                } else {
                    this._drawFloor(px, py);

                    if (goalSet.has(key)) {
                        this._drawGoal(px, py);
                    }

                    if (boxSet.has(key)) {
                        if (goalSet.has(key)) {
                            this._drawBoxOnGoal(px, py);
                        } else {
                            this._drawBox(px, py);
                        }
                    }

                    if (playerPos && playerPos[0] === x && playerPos[1] === y) {
                        this._drawPlayer(px, py, goalSet.has(key));
                    }
                }
            }
        }
    }

    _drawWall(x, y) {
        const s = this.tileSize;
        this.ctx.fillStyle = this.colors.wall;
        this.ctx.fillRect(x, y, s, s);
        this.ctx.strokeStyle = this.colors.wallStroke;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x + 0.5, y + 0.5, s - 1, s - 1);
    }

    _drawFloor(x, y) {
        this.ctx.fillStyle = this.colors.floor;
        this.ctx.fillRect(x, y, this.tileSize, this.tileSize);
    }

    _drawOutside(x, y) {
        this.ctx.fillStyle = this.colors.outside;
        this.ctx.fillRect(x, y, this.tileSize, this.tileSize);
    }

    _drawGoal(x, y) {
        const s = this.tileSize;
        const m = s * 0.3;
        this.ctx.fillStyle = this.colors.goal;
        this.ctx.fillRect(x + m, y + m, s - 2 * m, s - 2 * m);
    }

    _drawBox(x, y) {
        const s = this.tileSize;
        const m = 6;
        this.ctx.fillStyle = this.colors.box;
        this.ctx.fillRect(x + m, y + m, s - 2 * m, s - 2 * m);
        this.ctx.strokeStyle = this.colors.boxStroke;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x + m, y + m, s - 2 * m, s - 2 * m);
        // Cross mark
        this.ctx.strokeStyle = this.colors.boxStroke;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(x + m, y + m);
        this.ctx.lineTo(x + s - m, y + s - m);
        this.ctx.moveTo(x + s - m, y + m);
        this.ctx.lineTo(x + m, y + s - m);
        this.ctx.stroke();
    }

    _drawBoxOnGoal(x, y) {
        const s = this.tileSize;
        const m = 6;
        this.ctx.fillStyle = this.colors.boxOnGoal;
        this.ctx.fillRect(x + m, y + m, s - 2 * m, s - 2 * m);
        this.ctx.strokeStyle = this.colors.boxGoalStroke;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x + m, y + m, s - 2 * m, s - 2 * m);
    }

    _drawPlayer(x, y, onGoal) {
        const s = this.tileSize;
        const cx = x + s / 2;
        const cy = y + s / 2;
        const r = s / 3;

        this.ctx.fillStyle = onGoal ? this.colors.playerOnGoal : this.colors.player;
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        this.ctx.fill();

        // Highlight ring
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        this.ctx.stroke();
    }
}
