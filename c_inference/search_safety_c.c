#include "search_safety_c.h"

#include <math.h>
#include <string.h>

static int row_of(int action) {
    return action / GOMOKU_BOARD_SIZE;
}

static int col_of(int action) {
    return action % GOMOKU_BOARD_SIZE;
}

void board_init(CBoard *board) {
    memset(board, 0, sizeof(*board));
    board->current_player = GOMOKU_BLACK;
    board->last_move = -1;
}

int board_is_legal(const CBoard *board, int action) {
    return action >= 0 && action < GOMOKU_BOARD_CELLS && board->cells[action] == GOMOKU_EMPTY;
}

static int count_dir(const CBoard *board, int row, int col, int dr, int dc, int player) {
    int total = 0;
    row += dr;
    col += dc;
    while (row >= 0 && row < GOMOKU_BOARD_SIZE && col >= 0 && col < GOMOKU_BOARD_SIZE) {
        if (board->cells[row * GOMOKU_BOARD_SIZE + col] != player) {
            break;
        }
        total++;
        row += dr;
        col += dc;
    }
    return total;
}

int board_has_win_from(const CBoard *board, int action, int player) {
    const int dirs[4][2] = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};
    int row = row_of(action);
    int col = col_of(action);
    for (int i = 0; i < 4; i++) {
        int dr = dirs[i][0];
        int dc = dirs[i][1];
        int count = 1 + count_dir(board, row, col, dr, dc, player) + count_dir(board, row, col, -dr, -dc, player);
        if (count >= GOMOKU_WIN_LENGTH) {
            return 1;
        }
    }
    return 0;
}

int board_apply_move(CBoard *board, int action) {
    if (!board_is_legal(board, action)) {
        return 0;
    }
    int player = board->current_player;
    board->cells[action] = player;
    board->last_move = action;
    board->move_count++;
    if (!board_has_win_from(board, action, player) && board->move_count < GOMOKU_BOARD_CELLS) {
        board->current_player = -board->current_player;
    }
    return 1;
}

static int would_win(const CBoard *board, int action, int player) {
    if (!board_is_legal(board, action)) {
        return 0;
    }
    CBoard scratch = *board;
    scratch.cells[action] = player;
    return board_has_win_from(&scratch, action, player);
}

int board_immediate_winning_moves(const CBoard *board, int player, int moves[GOMOKU_BOARD_CELLS]) {
    int count = 0;
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (would_win(board, action, player)) {
            moves[count++] = action;
        }
    }
    return count;
}

int safety_opponent_has_forcing_terminal_reply(const CBoard *board_after_our_move) {
    int opponent = board_after_our_move->current_player;
    int wins[GOMOKU_BOARD_CELLS];
    if (board_immediate_winning_moves(board_after_our_move, opponent, wins) > 0) {
        return 1;
    }

    for (int reply = 0; reply < GOMOKU_BOARD_CELLS; reply++) {
        if (!board_is_legal(board_after_our_move, reply)) {
            continue;
        }
        CBoard scratch = *board_after_our_move;
        int result = board_apply_move(&scratch, reply);
        if (!result) {
            continue;
        }
        if (board_has_win_from(&scratch, reply, opponent)) {
            return 1;
        }

        int future_wins[GOMOKU_BOARD_CELLS];
        if (board_immediate_winning_moves(&scratch, opponent, future_wins) >= 2) {
            return 1;
        }
    }
    return 0;
}

int safety_move_is_safe(const CBoard *board, int action) {
    if (!board_is_legal(board, action)) {
        return 0;
    }
    CBoard scratch = *board;
    if (!board_apply_move(&scratch, action)) {
        return 0;
    }
    if (board_has_win_from(&scratch, action, board->current_player)) {
        return 1;
    }
    return !safety_opponent_has_forcing_terminal_reply(&scratch);
}

static int highest_scored_move(const CBoard *board, const float policy_scores[GOMOKU_BOARD_CELLS]) {
    int best = -1;
    float best_score = -INFINITY;
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (board_is_legal(board, action) && (best < 0 || policy_scores[action] > best_score)) {
            best = action;
            best_score = policy_scores[action];
        }
    }
    return best;
}

static int highest_scored_among(const float policy_scores[GOMOKU_BOARD_CELLS], const int moves[GOMOKU_BOARD_CELLS], int count) {
    int best = moves[0];
    float best_score = policy_scores[best];
    for (int i = 1; i < count; i++) {
        int action = moves[i];
        if (policy_scores[action] > best_score) {
            best = action;
            best_score = policy_scores[action];
        }
    }
    return best;
}

static int opponent_fork_creating_moves(const CBoard *board, int moves[GOMOKU_BOARD_CELLS]) {
    int opponent = -board->current_player;
    int count = 0;
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (!board_is_legal(board, action)) {
            continue;
        }
        CBoard scratch = *board;
        scratch.current_player = opponent;
        if (!board_apply_move(&scratch, action)) {
            continue;
        }

        int future_wins[GOMOKU_BOARD_CELLS];
        if (board_immediate_winning_moves(&scratch, opponent, future_wins) >= 2) {
            moves[count++] = action;
        }
    }
    return count;
}

int safety_select_move(const CBoard *board, const float policy_scores[GOMOKU_BOARD_CELLS], int use_safety) {
    if (!use_safety) {
        return highest_scored_move(board, policy_scores);
    }

    int wins[GOMOKU_BOARD_CELLS];
    int own_win_count = board_immediate_winning_moves(board, board->current_player, wins);
    if (own_win_count > 0) {
        return highest_scored_among(policy_scores, wins, own_win_count);
    }

    int opponent_wins[GOMOKU_BOARD_CELLS];
    int opponent_win_count = board_immediate_winning_moves(board, -board->current_player, opponent_wins);
    if (opponent_win_count > 0) {
        return highest_scored_among(policy_scores, opponent_wins, opponent_win_count);
    }

    int best_safe = -1;
    float best_safe_score = -INFINITY;
    int best_any = -1;
    float best_any_score = -INFINITY;
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (!board_is_legal(board, action)) {
            continue;
        }
        if (best_any < 0 || policy_scores[action] > best_any_score) {
            best_any = action;
            best_any_score = policy_scores[action];
        }
        if (safety_move_is_safe(board, action) && (best_safe < 0 || policy_scores[action] > best_safe_score)) {
            best_safe = action;
            best_safe_score = policy_scores[action];
        }
    }
    if (best_safe >= 0) {
        return best_safe;
    }

    int fork_moves[GOMOKU_BOARD_CELLS];
    int fork_move_count = opponent_fork_creating_moves(board, fork_moves);
    if (fork_move_count > 0) {
        return highest_scored_among(policy_scores, fork_moves, fork_move_count);
    }
    return best_any;
}
