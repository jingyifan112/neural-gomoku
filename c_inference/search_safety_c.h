#ifndef GOMOKU_SEARCH_SAFETY_C_H
#define GOMOKU_SEARCH_SAFETY_C_H

#include "cnn_infer.h"

#define GOMOKU_EMPTY 0
#define GOMOKU_BLACK 1
#define GOMOKU_WHITE -1
#define GOMOKU_WIN_LENGTH 5

typedef struct {
    int cells[GOMOKU_BOARD_CELLS];
    int current_player;
    int last_move;
    int move_count;
} CBoard;

void board_init(CBoard *board);
int board_is_legal(const CBoard *board, int action);
int board_apply_move(CBoard *board, int action);
int board_has_win_from(const CBoard *board, int action, int player);
int board_immediate_winning_moves(const CBoard *board, int player, int moves[GOMOKU_BOARD_CELLS]);
int safety_opponent_has_forcing_terminal_reply(const CBoard *board_after_our_move);
int safety_move_is_safe(const CBoard *board, int action);
int safety_select_move(const CBoard *board, const float policy_scores[GOMOKU_BOARD_CELLS], int use_safety);

#endif
