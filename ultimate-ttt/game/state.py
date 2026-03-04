import copy

_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6),              # diagonals
]


def check_winner(board: list) -> int:
    """Return 1 if X wins, 2 if O wins, 0 if no winner yet."""
    for a, b, c in _LINES:
        v = board[a]
        if v != 0 and v == board[b] == board[c]:
            return v
    return 0


class GameState:
    def __init__(self):
        self.board = [[0] * 9 for _ in range(9)]
        self.meta_board = [0] * 9
        self.current_player = 1
        self.active_board = None  # None = free choice
        self._terminal = False
        self._winner = None  # 1, 2, 0 (draw), or None (ongoing)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_terminal(self) -> bool:
        return self._terminal

    def get_result(self, perspective_player: int) -> float:
        if not self._terminal:
            raise RuntimeError("get_result called on non-terminal state")
        if self._winner == 0:
            return 0.0
        return 1.0 if self._winner == perspective_player else -1.0

    def get_legal_moves(self) -> list:
        if self._terminal:
            return []
        # Determine which boards are in play
        if self.active_board is not None and self.meta_board[self.active_board] == 0:
            boards = [self.active_board]
        else:
            boards = [b for b in range(9) if self.meta_board[b] == 0]
        return [
            (b, c)
            for b in boards
            for c in range(9)
            if self.board[b][c] == 0
        ]

    # ------------------------------------------------------------------
    # Move application
    # ------------------------------------------------------------------

    def apply_move(self, board_index: int, cell_index: int) -> "GameState":
        ns = self.clone()
        ns.board[board_index][cell_index] = ns.current_player

        # Check small-board outcome
        sb_winner = check_winner(ns.board[board_index])
        if sb_winner:
            ns.meta_board[board_index] = sb_winner
        elif all(ns.board[board_index][c] != 0 for c in range(9)):
            ns.meta_board[board_index] = 3  # draw/full

        # Check meta-board outcome
        meta_winner = check_winner(ns.meta_board)
        if meta_winner:
            ns._terminal = True
            ns._winner = meta_winner
        elif all(ns.meta_board[b] != 0 for b in range(9)):
            ns._terminal = True
            ns._winner = 0

        # Routing
        if not ns._terminal:
            if ns.meta_board[cell_index] == 0:
                ns.active_board = cell_index
            else:
                ns.active_board = None

        # Switch player
        ns.current_player = 2 if self.current_player == 1 else 1
        return ns

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clone(self) -> "GameState":
        ns = GameState.__new__(GameState)
        ns.board = [row[:] for row in self.board]
        ns.meta_board = self.meta_board[:]
        ns.current_player = self.current_player
        ns.active_board = self.active_board
        ns._terminal = self._terminal
        ns._winner = self._winner
        return ns

    def to_dict(self) -> dict:
        return {
            "board": [row[:] for row in self.board],
            "meta_board": self.meta_board[:],
            "current_player": self.current_player,
            "active_board": self.active_board,
            "is_terminal": self._terminal,
            "winner": self._winner,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        gs = cls.__new__(cls)
        gs.board = [list(row) for row in d["board"]]
        gs.meta_board = list(d["meta_board"])
        gs.current_player = d["current_player"]
        gs.active_board = d["active_board"]
        gs._terminal = d["is_terminal"]
        gs._winner = d["winner"]
        return gs
