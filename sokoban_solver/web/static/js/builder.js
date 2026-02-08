/**
 * Interactive puzzle builder for Sokoban.
 */
class PuzzleBuilder {
    constructor(canvas, width, height) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.gridWidth = width;
        this.gridHeight = height;
        this.tileSize = 48;
        this.currentTool = '#';

        // Initialize empty grid
        this.grid = this._emptyGrid(width, height);

        // Click and drag support
        this._painting = false;
        this.canvas.addEventListener('mousedown', (e) => this._onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this._onMouseMove(e));
        this.canvas.addEventListener('mouseup', () => { this._painting = false; });
        this.canvas.addEventListener('mouseleave', () => { this._painting = false; });

        this.render();
    }

    // ─── Grid Operations ───────────────────────────────────

    _emptyGrid(w, h) {
        return Array.from({ length: h }, () => Array(w).fill(' '));
    }

    clear() {
        this.grid = this._emptyGrid(this.gridWidth, this.gridHeight);
        this.render();
    }

    resize(newWidth, newHeight) {
        const newGrid = this._emptyGrid(newWidth, newHeight);
        for (let y = 0; y < Math.min(this.gridHeight, newHeight); y++) {
            for (let x = 0; x < Math.min(this.gridWidth, newWidth); x++) {
                newGrid[y][x] = this.grid[y][x];
            }
        }
        this.grid = newGrid;
        this.gridWidth = newWidth;
        this.gridHeight = newHeight;
        this.render();
    }

    setTool(tool) {
        this.currentTool = tool;
    }

    getGridString() {
        return this.grid.map(row => row.join('')).join('\n');
    }

    // ─── Click Handling ────────────────────────────────────

    _cellFromEvent(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((event.clientX - rect.left) / this.tileSize);
        const y = Math.floor((event.clientY - rect.top) / this.tileSize);
        if (x >= 0 && x < this.gridWidth && y >= 0 && y < this.gridHeight) {
            return { x, y };
        }
        return null;
    }

    _placeAt(x, y) {
        const tool = this.currentTool;

        // Eraser just sets to space
        if (tool === 'eraser') {
            this.grid[y][x] = ' ';
            this.render();
            return;
        }

        // Player uniqueness: remove existing player before placing
        if (tool === '@') {
            for (let ry = 0; ry < this.gridHeight; ry++) {
                for (let rx = 0; rx < this.gridWidth; rx++) {
                    if (this.grid[ry][rx] === '@') {
                        this.grid[ry][rx] = ' ';
                    } else if (this.grid[ry][rx] === '+') {
                        this.grid[ry][rx] = '.';
                    }
                }
            }
            // If placing player on a goal, use '+'
            if (this.grid[y][x] === '.') {
                this.grid[y][x] = '+';
            } else {
                this.grid[y][x] = '@';
            }
        } else if (tool === '$') {
            // Box on goal = '*'
            if (this.grid[y][x] === '.') {
                this.grid[y][x] = '*';
            } else {
                this.grid[y][x] = '$';
            }
        } else if (tool === '.') {
            // Goal under existing box = '*', under player = '+'
            if (this.grid[y][x] === '$') {
                this.grid[y][x] = '*';
            } else if (this.grid[y][x] === '@') {
                this.grid[y][x] = '+';
            } else {
                this.grid[y][x] = '.';
            }
        } else {
            this.grid[y][x] = tool;
        }

        this.render();
    }

    _onMouseDown(event) {
        const cell = this._cellFromEvent(event);
        if (cell) {
            this._painting = true;
            this._placeAt(cell.x, cell.y);
        }
    }

    _onMouseMove(event) {
        if (!this._painting) return;
        // Only allow drag-painting for wall, floor, eraser
        if (!['#', ' ', 'eraser'].includes(this.currentTool)) return;
        const cell = this._cellFromEvent(event);
        if (cell) {
            this._placeAt(cell.x, cell.y);
        }
    }

    // ─── API Integration ───────────────────────────────────

    async validate() {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid: this.grid }),
        });
        return response.json();
    }

    async solve() {
        const validation = await this.validate();
        if (!validation.valid) {
            return { success: false, error: validation.errors.join('; '), reason: 'invalid_puzzle' };
        }

        const puzzleString = this.getGridString();
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ puzzle: puzzleString }),
        });
        return response.json();
    }

    // ─── Rendering ─────────────────────────────────────────

    render() {
        this.canvas.width = this.gridWidth * this.tileSize;
        this.canvas.height = this.gridHeight * this.tileSize;

        const colors = {
            wall:       '#5a5a5a',
            floor:      '#2a2a4a',
            goal:       '#3a6a3a',
            box:        '#b87333',
            boxOnGoal:  '#2e8b57',
            player:     '#4169e1',
            playerGoal: '#1e90ff',
            empty:      '#1e1e3a',
        };

        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const ch = this.grid[y][x];
                const px = x * this.tileSize;
                const py = y * this.tileSize;
                const s = this.tileSize;

                // Background
                if (ch === '#') {
                    this.ctx.fillStyle = colors.wall;
                } else {
                    this.ctx.fillStyle = colors.empty;
                }
                this.ctx.fillRect(px, py, s, s);

                // Elements
                if (ch === '.' || ch === '+' || ch === '*') {
                    // Draw goal marker
                    const m = s * 0.3;
                    this.ctx.fillStyle = colors.goal;
                    this.ctx.fillRect(px + m, py + m, s - 2 * m, s - 2 * m);
                }

                if (ch === '$' || ch === '*') {
                    const m = 6;
                    this.ctx.fillStyle = ch === '*' ? colors.boxOnGoal : colors.box;
                    this.ctx.fillRect(px + m, py + m, s - 2 * m, s - 2 * m);
                    this.ctx.strokeStyle = '#654321';
                    this.ctx.lineWidth = 2;
                    this.ctx.strokeRect(px + m, py + m, s - 2 * m, s - 2 * m);
                }

                if (ch === '@' || ch === '+') {
                    this.ctx.fillStyle = ch === '+' ? colors.playerGoal : colors.player;
                    this.ctx.beginPath();
                    this.ctx.arc(px + s / 2, py + s / 2, s / 3, 0, 2 * Math.PI);
                    this.ctx.fill();
                    this.ctx.strokeStyle = '#fff';
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.arc(px + s / 2, py + s / 2, s / 3, 0, 2 * Math.PI);
                    this.ctx.stroke();
                }
            }
        }

        // Grid lines
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 0.5;
        for (let x = 0; x <= this.gridWidth; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.tileSize, 0);
            this.ctx.lineTo(x * this.tileSize, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.gridHeight; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.tileSize);
            this.ctx.lineTo(this.canvas.width, y * this.tileSize);
            this.ctx.stroke();
        }
    }
}
