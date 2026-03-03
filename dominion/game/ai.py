import math
from game.constants import (
    MOUNTAIN, CAVE, WIZARD, BARBARIAN,
    NONE, PLAYER, AI,
    STRATEGIC_VALUE,
)
from game.moves import compute_valid_moves
from game.claim import claim_tile, check_win_condition, snapshot_board, restore_board


def heuristic(G: dict) -> float:
    """Evaluate board state from AI's perspective (positive = good for AI)."""
    board = G['board']
    W, H = G['W'], G['H']
    fog = G['fog']

    claimable = [c for c in board if c['type'] != MOUNTAIN]
    ai_count = sum(1 for c in claimable if c['owner'] == AI)
    player_count = sum(1 for c in claimable if c['owner'] == PLAYER)

    ai_frontier = len(compute_valid_moves(G, AI))
    player_frontier = len(compute_valid_moves(G, PLAYER))

    # Cave control bonus
    caves_owned_by_ai = sum(1 for c in board if c['type'] == CAVE and c['owner'] == AI)
    caves_owned_by_player = sum(1 for c in board if c['type'] == CAVE and c['owner'] == PLAYER)
    cave_control = caves_owned_by_ai - caves_owned_by_player

    # Wizard reserve bonus (AI has unused wizard)
    wizard_reserve = sum(
        1 for c in board
        if c['type'] == WIZARD and c['owner'] == AI and not c['used']
    )

    # Barbarian exposure penalty: count owned tiles sharing row (W>=H) or col (H>W)
    # with a fogged (unrevealed) Barbarian
    def barb_exposure(owner: int) -> int:
        exposure = 0
        fogged_barbs = [
            i for i, c in enumerate(board)
            if c['type'] == BARBARIAN and c['owner'] == NONE and i not in fog
        ]
        if W >= H:
            # Row-based: check rows of fogged barbarians
            barb_rows = {i // W for i in fogged_barbs}
            for i, c in enumerate(board):
                if c['owner'] == owner and (i // W) in barb_rows:
                    exposure += 1
        else:
            # Column-based: check columns of fogged barbarians
            barb_cols = {i % W for i in fogged_barbs}
            for i, c in enumerate(board):
                if c['owner'] == owner and (i % W) in barb_cols:
                    exposure += 1
        return exposure

    ai_exposure = barb_exposure(AI)
    player_exposure = barb_exposure(PLAYER)

    score = (
        2.0 * (ai_count - player_count) +
        0.5 * (ai_frontier - player_frontier) +
        1.5 * cave_control +
        0.8 * wizard_reserve +
        0.3 * (player_exposure - ai_exposure)
    )
    return score


def minimax_alpha_beta(
    G: dict,
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
) -> float:
    """Minimax with alpha-beta pruning. Returns heuristic score."""
    # Check terminal condition
    winner = check_win_condition(G)
    if winner == AI:
        return 10000.0 + depth  # Prefer faster wins
    if winner == PLAYER:
        return -10000.0 - depth
    if winner == 'DRAW':
        return 0.0

    if depth == 0:
        return heuristic(G)

    board = G['board']
    active_owner = AI if is_maximizing else PLAYER
    moves = compute_valid_moves(G, active_owner)

    if not moves:
        # Pass-through: opponent gets another turn
        return minimax_alpha_beta(G, depth - 1, alpha, beta, not is_maximizing)

    # Sort moves by strategic value descending (move ordering for pruning)
    sorted_moves = sorted(moves, key=lambda i: STRATEGIC_VALUE.get(board[i]['type'], 0), reverse=True)

    if is_maximizing:
        best = -math.inf
        for move_idx in sorted_moves:
            snap = snapshot_board(G)
            waf_backup = G.get('wizard_active_for', NONE)

            is_wizard = claim_tile(G, move_idx, AI, minimax_mode=True)
            if is_wizard and not board[move_idx]['used']:
                # AI gets wizard teleport — simulate wizard decision immediately
                from game.ai import wizard_teleport_decision
                tele = wizard_teleport_decision(G)
                if tele is not None:
                    G['wizard_active_for'] = AI
                    board[move_idx]['used'] = True

            val = minimax_alpha_beta(G, depth - 1, alpha, beta, False)

            G['wizard_active_for'] = waf_backup
            restore_board(G, snap)

            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for move_idx in sorted_moves:
            snap = snapshot_board(G)
            waf_backup = G.get('wizard_active_for', NONE)

            claim_tile(G, move_idx, PLAYER, minimax_mode=True)

            val = minimax_alpha_beta(G, depth - 1, alpha, beta, True)

            G['wizard_active_for'] = waf_backup
            restore_board(G, snap)

            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def minimax_root(G: dict, depth: int) -> int:
    """Return the index of the best AI move."""
    board = G['board']
    moves = compute_valid_moves(G, AI)

    if not moves:
        return -1

    sorted_moves = sorted(moves, key=lambda i: STRATEGIC_VALUE.get(board[i]['type'], 0), reverse=True)

    best_val = -math.inf
    best_move = sorted_moves[0]

    for move_idx in sorted_moves:
        snap = snapshot_board(G)
        waf_backup = G.get('wizard_active_for', NONE)

        claim_tile(G, move_idx, AI, minimax_mode=True)

        val = minimax_alpha_beta(G, depth - 1, -math.inf, math.inf, False)

        G['wizard_active_for'] = waf_backup
        restore_board(G, snap)

        if val > best_val:
            best_val = val
            best_move = move_idx

    return best_move


def wizard_teleport_decision(G: dict) -> int | None:
    """
    Find the best tile for AI wizard teleport.
    Returns index if strategic value > 2, else None (decline).
    """
    board = G['board']
    fog = G['fog']

    best_val = -1.0
    best_idx = None

    for i, c in enumerate(board):
        if c['owner'] != NONE or c['type'] == MOUNTAIN or i not in fog:
            continue
        val = STRATEGIC_VALUE.get(c['type'], 0)
        if val > best_val:
            best_val = val
            best_idx = i

    if best_val > 2:
        return best_idx
    return None
