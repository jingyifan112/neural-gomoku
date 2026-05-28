#include "cnn_infer.h"
#include "mcts_c.h"
#include "search_safety_c.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void render(const CBoard *board) {
    printf("   ");
    for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
        printf(" %d", c);
    }
    printf("\n");
    for (int r = 0; r < GOMOKU_BOARD_SIZE; r++) {
        printf("%2d ", r);
        for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
            int v = board->cells[r * GOMOKU_BOARD_SIZE + c];
            char ch = v == GOMOKU_BLACK ? 'X' : (v == GOMOKU_WHITE ? 'O' : '.');
            printf(" %c", ch);
        }
        printf("\n");
    }
}

static void encode(const CBoard *board, float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS], float legal_mask[GOMOKU_BOARD_CELLS]) {
    memset(input, 0, sizeof(float) * GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS);
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        input[i] = board->cells[i] == board->current_player ? 1.0f : 0.0f;
        input[GOMOKU_BOARD_CELLS + i] = board->cells[i] == -board->current_player ? 1.0f : 0.0f;
        legal_mask[i] = board->cells[i] == GOMOKU_EMPTY ? 1.0f : 0.0f;
    }
    if (board->last_move >= 0) {
        input[2 * GOMOKU_BOARD_CELLS + board->last_move] = 1.0f;
    }
}

static void print_move(int action) {
    if (action < 0) {
        printf("none");
        return;
    }
    printf("(%d,%d)", action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE);
}

static void print_moves(const int moves[GOMOKU_BOARD_CELLS], int count) {
    if (count <= 0) {
        printf("none");
        return;
    }
    for (int i = 0; i < count; i++) {
        printf("%s", i == 0 ? "" : " ");
        print_move(moves[i]);
    }
}

static void print_ai_debug(
    const CBoard *board,
    int ai_turn,
    int direct_move,
    int raw_mcts_move,
    int safety_move,
    int final_move,
    int use_mcts,
    int use_safety
) {
    int ai_wins[GOMOKU_BOARD_CELLS];
    int opponent_wins[GOMOKU_BOARD_CELLS];
    int ai_win_count = board_immediate_winning_moves(board, board->current_player, ai_wins);
    int opponent_win_count = board_immediate_winning_moves(board, -board->current_player, opponent_wins);
    int raw_move = use_mcts ? raw_mcts_move : direct_move;
    int safety_overrode = use_safety && raw_move >= 0 && final_move >= 0 && raw_move != final_move;

    printf("debug ai_turn=%d move_number=%d current_player=%c\n", ai_turn, board->move_count + 1, board->current_player == GOMOKU_BLACK ? 'X' : 'O');
    printf("  direct_policy_top=");
    print_move(direct_move);
    printf("\n");
    if (use_mcts) {
        printf("  raw_mcts_selected=");
        print_move(raw_mcts_move);
        printf("\n");
    }
    if (use_safety) {
        printf("  safety_adjusted_selected=");
        print_move(safety_move);
        printf("\n");
    }
    printf("  final_selected=");
    print_move(final_move);
    printf("\n");
    printf("  safety_overrode=%s\n", safety_overrode ? "yes" : "no");
    printf("  ai_immediate_wins=");
    print_moves(ai_wins, ai_win_count);
    printf("\n");
    printf("  opponent_immediate_wins=");
    print_moves(opponent_wins, opponent_win_count);
    printf("\n");
}

int main(int argc, char **argv) {
    const char *weights_path = argc > 1 ? argv[1] : "weights/9x9_weights.bin";
    int use_safety = 1;
    int use_mcts = 1;
    int mcts_sims = 64;
    int debug = 0;
    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--no-safety") == 0) {
            use_safety = 0;
        } else if (strcmp(argv[i], "--no-mcts") == 0) {
            use_mcts = 0;
        } else if (strcmp(argv[i], "--mcts-sims") == 0 && i + 1 < argc) {
            mcts_sims = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--debug") == 0) {
            debug = 1;
        }
    }
    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    CBoard board;
    board_init(&board);
    int human_player = GOMOKU_BLACK;
    int ai_turn = 0;
    printf("mode: %s safety=%s mcts_sims=%d\n", use_mcts ? "mcts" : "direct-policy", use_safety ? "on" : "off", mcts_sims);

    while (1) {
        render(&board);
        int action = -1;
        if (board.current_player == human_player) {
            int row = -1;
            int col = -1;
            printf("your move row col> ");
            if (scanf("%d %d", &row, &col) != 2) {
                break;
            }
            if (row < 0 || row >= GOMOKU_BOARD_SIZE || col < 0 || col >= GOMOKU_BOARD_SIZE) {
                printf("invalid move\n");
                continue;
            }
            action = row * GOMOKU_BOARD_SIZE + col;
            if (!board_is_legal(&board, action)) {
                printf("occupied\n");
                continue;
            }
        } else {
            float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
            float legal_mask[GOMOKU_BOARD_CELLS];
            float logits[GOMOKU_BOARD_CELLS];
            float value = 0.0f;

            ai_turn++;
            if (use_mcts) {
                if (debug) {
                    int direct_move = -1;
                    int raw_mcts_move = -1;
                    int safety_move = -1;
                    encode(&board, input, legal_mask);
                    cnn_forward(&weights, input, logits, &value);
                    direct_move = cnn_top_legal_move(logits, legal_mask);
                    MCTSConfigC raw_config = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 0};
                    raw_mcts_move = mcts_select_move(&weights, &board, &raw_config);
                    if (use_safety) {
                        MCTSConfigC safe_config = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 1};
                        safety_move = mcts_select_move(&weights, &board, &safe_config);
                        action = safety_move;
                    } else {
                        action = raw_mcts_move;
                    }
                    print_ai_debug(&board, ai_turn, direct_move, raw_mcts_move, safety_move, action, use_mcts, use_safety);
                } else {
                    MCTSConfigC config = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = use_safety};
                    action = mcts_select_move(&weights, &board, &config);
                }
                printf("model plays: %d %d mode=mcts safety=%s sims=%d\n", action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE, use_safety ? "on" : "off", mcts_sims);
            } else {
                int direct_move = -1;
                int safety_move = -1;
                encode(&board, input, legal_mask);
                cnn_forward(&weights, input, logits, &value);
                direct_move = cnn_top_legal_move(logits, legal_mask);
                safety_move = use_safety ? safety_select_move(&board, logits, 1) : -1;
                action = use_safety && safety_move >= 0 ? safety_move : direct_move;
                if (debug) {
                    print_ai_debug(&board, ai_turn, direct_move, -1, safety_move, action, use_mcts, use_safety);
                }
                printf("model plays: %d %d value=%.4f mode=direct safety=%s\n", action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE, value, use_safety ? "on" : "off");
            }
        }

        int player = board.current_player;
        board_apply_move(&board, action);
        if (board_has_win_from(&board, action, player)) {
            render(&board);
            printf("%s\n", player == human_player ? "you win" : "model wins");
            break;
        }
        if (board.move_count == GOMOKU_BOARD_CELLS) {
            render(&board);
            printf("draw\n");
            break;
        }
    }

    cnn_free_weights(&weights);
    return 0;
}
