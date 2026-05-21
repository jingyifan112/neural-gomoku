from __future__ import annotations

from dataclasses import dataclass

import numpy as np


EMPTY = 0
BLACK = 1
WHITE = -1


@dataclass(frozen=True)
class MoveResult:
    winner: int | None
    done: bool


class Board:
    """Gomoku rules and tensor encoding.

    This class contains only game legality and terminal-state logic. It does
    not encode strategic rules such as open-threes or must-block moves.
    """

    def __init__(self, size: int = 15, win_length: int = 5):
        if size < win_length:
            raise ValueError("board size must be at least win length")
        self.size = size
        self.win_length = win_length
        self.grid = np.zeros((size, size), dtype=np.int8)
        self.current_player = BLACK
        self.last_move: tuple[int, int] | None = None
        self.move_count = 0

    def clone(self) -> "Board":
        other = Board(self.size, self.win_length)
        other.grid = self.grid.copy()
        other.current_player = self.current_player
        other.last_move = self.last_move
        other.move_count = self.move_count
        return other

    def legal_moves(self) -> np.ndarray:
        return np.flatnonzero(self.grid.reshape(-1) == EMPTY)

    def legal_mask(self) -> np.ndarray:
        return (self.grid.reshape(-1) == EMPTY).astype(np.float32)

    def would_win(self, action: int, player: int | None = None) -> bool:
        row, col = divmod(int(action), self.size)
        if self.grid[row, col] != EMPTY:
            return False
        player = self.current_player if player is None else player
        self.grid[row, col] = player
        won = self._has_five_from(row, col, player)
        self.grid[row, col] = EMPTY
        return won

    def immediate_winning_moves(self, player: int | None = None) -> list[int]:
        player = self.current_player if player is None else player
        return [int(action) for action in self.legal_moves() if self.would_win(int(action), player)]

    def play_flat(self, action: int) -> MoveResult:
        row, col = divmod(int(action), self.size)
        return self.play(row, col)

    def play(self, row: int, col: int) -> MoveResult:
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise ValueError("move is outside the board")
        if self.grid[row, col] != EMPTY:
            raise ValueError("move is not legal")

        player = self.current_player
        self.grid[row, col] = player
        self.last_move = (row, col)
        self.move_count += 1

        winner = player if self._has_five_from(row, col, player) else None
        done = winner is not None or self.move_count == self.size * self.size
        if not done:
            self.current_player = -self.current_player
        return MoveResult(winner=winner, done=done)

    def encode(self) -> np.ndarray:
        """Return CxHxW features from the current player's perspective."""
        current = (self.grid == self.current_player).astype(np.float32)
        opponent = (self.grid == -self.current_player).astype(np.float32)
        last = np.zeros_like(current, dtype=np.float32)
        if self.last_move is not None:
            last[self.last_move] = 1.0
        return np.stack([current, opponent, last], axis=0)

    def render(self) -> str:
        symbols = {BLACK: "X", WHITE: "O", EMPTY: "."}
        header = "   " + " ".join(f"{i:2d}" for i in range(self.size))
        rows = [
            f"{r:2d} " + " ".join(f" {symbols[int(v)]}" for v in self.grid[r])
            for r in range(self.size)
        ]
        return "\n".join([header, *rows])

    def _has_five_from(self, row: int, col: int, player: int) -> bool:
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            count += self._count_direction(row, col, dr, dc, player)
            count += self._count_direction(row, col, -dr, -dc, player)
            if count >= self.win_length:
                return True
        return False

    def _count_direction(self, row: int, col: int, dr: int, dc: int, player: int) -> int:
        total = 0
        r = row + dr
        c = col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.grid[r, c] == player:
            total += 1
            r += dr
            c += dc
        return total
