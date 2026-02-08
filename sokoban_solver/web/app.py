"""Flask backend for Sokoban Solver web interface."""

import sys
import os

# Add parent directory to path so we can import core/solver modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from solver.astar import solve_puzzle

app = Flask(__name__)
CORS(app)

# Pre-designed puzzles (all verified solvable)
PRESET_PUZZLES = {
    "easy_1": {
        "name": "Easy Puzzle 1",
        "difficulty": "easy",
        "puzzle": (
            "####\n"
            "#. #\n"
            "#$ #\n"
            "#@ #\n"
            "####"
        ),
    },
    "easy_2": {
        "name": "Easy Puzzle 2",
        "difficulty": "easy",
        "puzzle": (
            "######\n"
            "# @  #\n"
            "# $  #\n"
            "#    #\n"
            "# .  #\n"
            "######"
        ),
    },
    "easy_3": {
        "name": "Easy Puzzle 3",
        "difficulty": "easy",
        "puzzle": (
            "#####\n"
            "#.  #\n"
            "#   #\n"
            "#$  #\n"
            "#@  #\n"
            "#####"
        ),
    },
    "medium_1": {
        "name": "Medium Puzzle 1",
        "difficulty": "medium",
        "puzzle": (
            "####\n"
            "# .#\n"
            "#  ###\n"
            "#*@  #\n"
            "#  $ #\n"
            "#  ###\n"
            "####"
        ),
    },
    "medium_2": {
        "name": "Medium Puzzle 2",
        "difficulty": "medium",
        "puzzle": (
            "######\n"
            "#    #\n"
            "# $$ #\n"
            "# .. #\n"
            "# @  #\n"
            "######"
        ),
    },
    "medium_3": {
        "name": "Medium Puzzle 3",
        "difficulty": "medium",
        "puzzle": (
            "########\n"
            "#      #\n"
            "# $$$  #\n"
            "# ...  #\n"
            "#@     #\n"
            "########"
        ),
    },
    "hard_1": {
        "name": "Hard Puzzle 1",
        "difficulty": "hard",
        "puzzle": (
            "########\n"
            "#      #\n"
            "# .$   #\n"
            "# . $  #\n"
            "# .$   #\n"
            "#  @   #\n"
            "########"
        ),
    },
}


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/puzzles', methods=['GET'])
def get_puzzles():
    """Return list of available preset puzzles."""
    puzzles = [
        {"id": pid, "name": info["name"], "difficulty": info["difficulty"]}
        for pid, info in PRESET_PUZZLES.items()
    ]
    return jsonify({"puzzles": puzzles})


@app.route('/api/puzzle/<puzzle_id>', methods=['GET'])
def get_puzzle(puzzle_id):
    """Return a specific puzzle by ID."""
    if puzzle_id not in PRESET_PUZZLES:
        return jsonify({"error": "Puzzle not found"}), 404

    info = PRESET_PUZZLES[puzzle_id]
    puzzle_string = info["puzzle"]
    grid = [list(line) for line in puzzle_string.split('\n')]

    return jsonify({
        "id": puzzle_id,
        "puzzle": puzzle_string,
        "grid": grid,
    })


@app.route('/api/solve', methods=['POST'])
def solve():
    """Solve a submitted puzzle."""
    try:
        data = request.get_json()
        puzzle_string = data.get('puzzle')
        timeout = data.get('timeout', 60)
        max_states = data.get('max_states', 10_000_000)

        if not puzzle_string:
            return jsonify({
                "success": False,
                "error": "No puzzle provided",
            }), 400

        result = solve_puzzle(puzzle_string, timeout=timeout, max_states=max_states)

        if result['success']:
            return jsonify({
                "success": True,
                "solution": result['solution'],
                "moves": list(result['solution']),
                "length": len(result['solution']),
                "stats": result['stats'],
                "initial_state": result['initial_state'],
                "pushed_boxes": result.get('pushed_boxes', []),
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error'),
                "reason": result.get('reason', 'unknown'),
                "stats": result.get('stats', {}),
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "reason": "server_error",
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_puzzle():
    """Validate a user-created puzzle grid."""
    data = request.get_json()
    grid = data.get('grid')

    if not grid or not isinstance(grid, list):
        return jsonify({"valid": False, "errors": ["No grid provided"], "warnings": []})

    errors = []
    warnings = []

    player_count = sum(row.count('@') + row.count('+') for row in grid)
    box_count = sum(row.count('$') + row.count('*') for row in grid)
    goal_count = sum(row.count('.') + row.count('*') + row.count('+') for row in grid)

    if player_count == 0:
        errors.append("Must have exactly one player (@)")
    elif player_count > 1:
        errors.append("Can only have one player")

    if box_count == 0:
        errors.append("Must have at least one box ($)")

    if goal_count == 0:
        errors.append("Must have at least one goal (.)")

    if box_count != goal_count and box_count > 0 and goal_count > 0:
        warnings.append(
            f"Box count ({box_count}) doesn't match goal count ({goal_count})"
        )

    return jsonify({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
