#include "cnn_infer.h"
#include "mcts_c.h"
#include "search_safety_c.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *name;
    CBoard board;
    int expected_moves[2];
    int expected_count;
    const char *note;
} TacticalCase;

typedef struct {
    const char *weights_path;
    int mcts_sims;
    float c_puct;
    int debug;
} BenchmarkConfig;

static int cell(int row, int col) {
    return row * GOMOKU_BOARD_SIZE + col;
}

static void set_stone(TacticalCase *tc, int row, int col, int player) {
    tc->board.cells[cell(row, col)] = player;
    tc->board.move_count++;
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

static void render(const CBoard *board) {
    printf("   ");
    for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
        printf(" %d", c);
    }
    printf("\n");
    for (int r = 0; r < GOMOKU_BOARD_SIZE; r++) {
        printf("%2d ", r);
        for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
            int v = board->cells[cell(r, c)];
            char ch = v == GOMOKU_BLACK ? 'X' : (v == GOMOKU_WHITE ? 'O' : '.');
            printf(" %c", ch);
        }
        printf("\n");
    }
}

static int is_expected(const TacticalCase *tc, int move) {
    for (int i = 0; i < tc->expected_count; i++) {
        if (move == tc->expected_moves[i]) {
            return 1;
        }
    }
    return 0;
}

static void print_expected(const TacticalCase *tc) {
    for (int i = 0; i < tc->expected_count; i++) {
        int move = tc->expected_moves[i];
        printf("%s(%d,%d)", i == 0 ? "" : " or ", move / GOMOKU_BOARD_SIZE, move % GOMOKU_BOARD_SIZE);
    }
}

static void print_move(int move) {
    if (move < 0) {
        printf("none");
        return;
    }
    printf("(%d,%d)", move / GOMOKU_BOARD_SIZE, move % GOMOKU_BOARD_SIZE);
}

static int compare_child_stats(const void *a, const void *b) {
    const MCTSRootChildStatsC *left = (const MCTSRootChildStatsC *)a;
    const MCTSRootChildStatsC *right = (const MCTSRootChildStatsC *)b;
    if (left->visits != right->visits) {
        return right->visits - left->visits;
    }
    if (left->prior < right->prior) {
        return 1;
    }
    if (left->prior > right->prior) {
        return -1;
    }
    return left->move - right->move;
}

static void print_root_children_debug(const MCTSRootChildStatsC stats[GOMOKU_BOARD_CELLS], int count) {
    MCTSRootChildStatsC sorted[GOMOKU_BOARD_CELLS];
    int limit = count < 10 ? count : 10;
    memcpy(sorted, stats, sizeof(MCTSRootChildStatsC) * (size_t)count);
    qsort(sorted, (size_t)count, sizeof(MCTSRootChildStatsC), compare_child_stats);

    printf("  top root children by visits:\n");
    for (int i = 0; i < limit; i++) {
        printf(
            "    %2d. move=",
            i + 1
        );
        print_move(sorted[i].move);
        printf(
            " prior=%.6f visits=%d q_value=%.6f\n",
            sorted[i].prior,
            sorted[i].visits,
            sorted[i].q_value
        );
    }
}

static TacticalCase opponent_four_one_endpoint(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "opponent_four_one_endpoint";
    tc.board.current_player = GOMOKU_BLACK;
    tc.board.last_move = cell(4, 4);
    tc.expected_moves[0] = cell(4, 5);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Opponent O has OOOO with one playable endpoint; model X should block.";
    set_stone(&tc, 4, 0, GOMOKU_BLACK);
    set_stone(&tc, 4, 1, GOMOKU_WHITE);
    set_stone(&tc, 4, 2, GOMOKU_WHITE);
    set_stone(&tc, 4, 3, GOMOKU_WHITE);
    set_stone(&tc, 4, 4, GOMOKU_WHITE);
    return tc;
}

static TacticalCase opponent_open_three(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "opponent_open_three";
    tc.board.current_player = GOMOKU_BLACK;
    tc.board.last_move = cell(4, 4);
    tc.expected_moves[0] = cell(4, 1);
    tc.expected_moves[1] = cell(4, 5);
    tc.expected_count = 2;
    tc.note = "Opponent O has .OOO.; either endpoint is an expected direct-policy block candidate.";
    set_stone(&tc, 4, 2, GOMOKU_WHITE);
    set_stone(&tc, 4, 3, GOMOKU_WHITE);
    set_stone(&tc, 4, 4, GOMOKU_WHITE);
    set_stone(&tc, 2, 2, GOMOKU_BLACK);
    set_stone(&tc, 6, 6, GOMOKU_BLACK);
    return tc;
}

static TacticalCase model_four_can_win(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "model_four_can_win";
    tc.board.current_player = GOMOKU_BLACK;
    tc.board.last_move = cell(3, 3);
    tc.expected_moves[0] = cell(3, 4);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Model X has XXXX.; expected direct winning move.";
    set_stone(&tc, 3, 0, GOMOKU_BLACK);
    set_stone(&tc, 3, 1, GOMOKU_BLACK);
    set_stone(&tc, 3, 2, GOMOKU_BLACK);
    set_stone(&tc, 3, 3, GOMOKU_BLACK);
    set_stone(&tc, 0, 0, GOMOKU_WHITE);
    set_stone(&tc, 1, 1, GOMOKU_WHITE);
    return tc;
}

static TacticalCase broken_four_pattern(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "broken_four_pattern";
    tc.board.current_player = GOMOKU_BLACK;
    tc.board.last_move = cell(5, 4);
    tc.expected_moves[0] = cell(5, 3);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Model X has XX.XX; expected fill-gap winning move.";
    set_stone(&tc, 5, 1, GOMOKU_BLACK);
    set_stone(&tc, 5, 2, GOMOKU_BLACK);
    set_stone(&tc, 5, 4, GOMOKU_BLACK);
    set_stone(&tc, 5, 5, GOMOKU_BLACK);
    set_stone(&tc, 0, 8, GOMOKU_WHITE);
    set_stone(&tc, 1, 8, GOMOKU_WHITE);
    return tc;
}

static TacticalCase mcts_safety_must_block_four(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "mcts_safety_must_block_four";
    tc.board.current_player = GOMOKU_BLACK;
    tc.board.last_move = cell(2, 5);
    tc.expected_moves[0] = cell(2, 6);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Regression: MCTS+safety must block opponent OOOO. before final selection.";
    set_stone(&tc, 2, 1, GOMOKU_BLACK);
    set_stone(&tc, 2, 2, GOMOKU_WHITE);
    set_stone(&tc, 2, 3, GOMOKU_WHITE);
    set_stone(&tc, 2, 4, GOMOKU_WHITE);
    set_stone(&tc, 2, 5, GOMOKU_WHITE);
    set_stone(&tc, 7, 7, GOMOKU_BLACK);
    return tc;
}

static TacticalCase human_play_vertical_four_must_block(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "human_play_vertical_four_must_block";
    tc.board.current_player = GOMOKU_WHITE;
    tc.board.last_move = cell(6, 3);
    tc.expected_moves[0] = cell(7, 3);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Regression from C play: AI O must block X vertical four before X wins at (7,3).";
    set_stone(&tc, 2, 3, GOMOKU_WHITE);
    set_stone(&tc, 2, 6, GOMOKU_WHITE);
    set_stone(&tc, 3, 3, GOMOKU_BLACK);
    set_stone(&tc, 4, 2, GOMOKU_BLACK);
    set_stone(&tc, 4, 3, GOMOKU_BLACK);
    set_stone(&tc, 4, 4, GOMOKU_BLACK);
    set_stone(&tc, 5, 3, GOMOKU_BLACK);
    set_stone(&tc, 5, 4, GOMOKU_WHITE);
    set_stone(&tc, 6, 3, GOMOKU_BLACK);
    set_stone(&tc, 6, 6, GOMOKU_WHITE);
    set_stone(&tc, 7, 0, GOMOKU_WHITE);
    set_stone(&tc, 8, 6, GOMOKU_WHITE);
    return tc;
}

static TacticalCase human_play_prevent_open_four_fork(void) {
    TacticalCase tc = {0};
    board_init(&tc.board);
    tc.name = "human_play_prevent_open_four_fork";
    tc.board.current_player = GOMOKU_WHITE;
    tc.board.last_move = cell(7, 4);
    tc.expected_moves[0] = cell(4, 7);
    tc.expected_moves[1] = -1;
    tc.expected_count = 1;
    tc.note = "Regression from C play: AI O should prevent X from creating two diagonal winning endpoints.";
    set_stone(&tc, 1, 3, GOMOKU_WHITE);
    set_stone(&tc, 1, 5, GOMOKU_WHITE);
    set_stone(&tc, 2, 3, GOMOKU_BLACK);
    set_stone(&tc, 2, 4, GOMOKU_WHITE);
    set_stone(&tc, 2, 6, GOMOKU_WHITE);
    set_stone(&tc, 3, 1, GOMOKU_WHITE);
    set_stone(&tc, 3, 2, GOMOKU_BLACK);
    set_stone(&tc, 3, 3, GOMOKU_BLACK);
    set_stone(&tc, 3, 4, GOMOKU_BLACK);
    set_stone(&tc, 4, 1, GOMOKU_WHITE);
    set_stone(&tc, 4, 2, GOMOKU_BLACK);
    set_stone(&tc, 4, 3, GOMOKU_BLACK);
    set_stone(&tc, 4, 4, GOMOKU_BLACK);
    set_stone(&tc, 5, 1, GOMOKU_BLACK);
    set_stone(&tc, 5, 2, GOMOKU_WHITE);
    set_stone(&tc, 5, 3, GOMOKU_BLACK);
    set_stone(&tc, 5, 4, GOMOKU_WHITE);
    set_stone(&tc, 5, 5, GOMOKU_BLACK);
    set_stone(&tc, 5, 6, GOMOKU_BLACK);
    set_stone(&tc, 6, 0, GOMOKU_BLACK);
    set_stone(&tc, 6, 2, GOMOKU_WHITE);
    set_stone(&tc, 6, 3, GOMOKU_WHITE);
    set_stone(&tc, 6, 5, GOMOKU_BLACK);
    set_stone(&tc, 6, 6, GOMOKU_WHITE);
    set_stone(&tc, 7, 0, GOMOKU_WHITE);
    set_stone(&tc, 7, 4, GOMOKU_BLACK);
    set_stone(&tc, 8, 5, GOMOKU_WHITE);
    return tc;
}

static int run_case(const CnnWeights *weights, const TacticalCase *tc, int case_index, const BenchmarkConfig *config) {
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float probs[GOMOKU_BOARD_CELLS];
    float value = 0.0f;

    encode(&tc->board, input, legal_mask);
    cnn_forward(weights, input, logits, &value);
    cnn_masked_softmax(logits, legal_mask, probs);
    int direct_move = cnn_top_legal_move(logits, legal_mask);
    int safe_move = safety_select_move(&tc->board, logits, 1);
    MCTSConfigC mcts_raw_config = {.simulations = config->mcts_sims, .c_puct = config->c_puct, .use_safety = 0};
    MCTSConfigC mcts_safe_config = {.simulations = config->mcts_sims, .c_puct = config->c_puct, .use_safety = 1};
    int mcts_raw_move = mcts_select_move(weights, &tc->board, &mcts_raw_config);
    int mcts_safe_move = mcts_select_move(weights, &tc->board, &mcts_safe_config);
    int direct_pass = is_expected(tc, direct_move);
    int safe_pass = is_expected(tc, safe_move);
    int mcts_raw_pass = is_expected(tc, mcts_raw_move);
    int mcts_safe_pass = is_expected(tc, mcts_safe_move);

    printf(
        "case %-28s direct=%s safety=%s mcts_raw=%s mcts_safety=%s\n",
        tc->name,
        direct_pass ? "PASS" : "FAIL",
        safe_pass ? "PASS" : "FAIL",
        mcts_raw_pass ? "PASS" : "FAIL",
        mcts_safe_pass ? "PASS" : "FAIL"
    );
    printf("  note: %s\n", tc->note);
    printf(
        "  direct selected: (%d,%d) logit=%.6f prob=%.6f value=%.6f\n",
        direct_move / GOMOKU_BOARD_SIZE,
        direct_move % GOMOKU_BOARD_SIZE,
        logits[direct_move],
        probs[direct_move],
        value
    );
    printf(
        "  safety selected: (%d,%d) logit=%.6f prob=%.6f\n",
        safe_move / GOMOKU_BOARD_SIZE,
        safe_move % GOMOKU_BOARD_SIZE,
        logits[safe_move],
        probs[safe_move]
    );
    printf(
        "  mcts raw selected: (%d,%d)\n",
        mcts_raw_move / GOMOKU_BOARD_SIZE,
        mcts_raw_move % GOMOKU_BOARD_SIZE
    );
    printf(
        "  mcts+safety selected: (%d,%d)\n",
        mcts_safe_move / GOMOKU_BOARD_SIZE,
        mcts_safe_move % GOMOKU_BOARD_SIZE
    );
    printf("  expected: ");
    print_expected(tc);
    printf("\n");
    if (config->debug) {
        MCTSRootChildStatsC root_stats[GOMOKU_BOARD_CELLS];
        int root_count = mcts_collect_root_child_stats(weights, &tc->board, &mcts_raw_config, root_stats);
        printf("  debug case %d name=%s\n", case_index, tc->name);
        printf("  debug expected move: ");
        print_expected(tc);
        printf("\n");
        printf("  debug direct policy top move: ");
        print_move(direct_move);
        printf("\n");
        printf("  debug raw MCTS top move: ");
        print_move(mcts_raw_move);
        printf("\n");
        printf("  debug MCTS+safety top move: ");
        print_move(mcts_safe_move);
        printf("\n");
        print_root_children_debug(root_stats, root_count);
    }
    if (!direct_pass || !safe_pass || !mcts_raw_pass || !mcts_safe_pass) {
        render(&tc->board);
    }
    return (direct_pass ? 1 : 0) | (safe_pass ? 2 : 0) | (mcts_raw_pass ? 4 : 0) | (mcts_safe_pass ? 8 : 0);
}

static void usage(const char *program) {
    fprintf(stderr, "usage: %s [weights_path] [--mcts-sims N] [--cpuct X] [--debug]\n", program);
}

int main(int argc, char **argv) {
    BenchmarkConfig config = {
        .weights_path = "weights/9x9_weights.bin",
        .mcts_sims = 64,
        .c_puct = 1.5f,
        .debug = 0,
    };
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--mcts-sims") == 0) {
            if (i + 1 >= argc) {
                usage(argv[0]);
                return 2;
            }
            config.mcts_sims = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--cpuct") == 0) {
            if (i + 1 >= argc) {
                usage(argv[0]);
                return 2;
            }
            config.c_puct = strtof(argv[++i], NULL);
        } else if (strcmp(argv[i], "--debug") == 0) {
            config.debug = 1;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            usage(argv[0]);
            return 0;
        } else if (argv[i][0] != '-') {
            config.weights_path = argv[i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    CnnWeights weights;
    if (!cnn_load_weights(config.weights_path, &weights)) {
        return 1;
    }

    TacticalCase cases[] = {
        opponent_four_one_endpoint(),
        opponent_open_three(),
        model_four_can_win(),
        broken_four_pattern(),
        mcts_safety_must_block_four(),
        human_play_vertical_four_must_block(),
        human_play_prevent_open_four_fork(),
    };
    int total = (int)(sizeof(cases) / sizeof(cases[0]));
    int direct_passed = 0;
    int safety_passed = 0;
    int mcts_raw_passed = 0;
    int mcts_safe_passed = 0;
    for (int i = 0; i < total; i++) {
        int result = run_case(&weights, &cases[i], i, &config);
        direct_passed += (result & 1) ? 1 : 0;
        safety_passed += (result & 2) ? 1 : 0;
        mcts_raw_passed += (result & 4) ? 1 : 0;
        mcts_safe_passed += (result & 8) ? 1 : 0;
    }

    printf("direct_policy_accuracy %d/%d %.2f%%\n", direct_passed, total, 100.0 * (double)direct_passed / (double)total);
    printf("policy_plus_safety_accuracy %d/%d %.2f%%\n", safety_passed, total, 100.0 * (double)safety_passed / (double)total);
    printf("mcts_raw_accuracy %d/%d %.2f%%\n", mcts_raw_passed, total, 100.0 * (double)mcts_raw_passed / (double)total);
    printf("mcts_plus_safety_accuracy %d/%d %.2f%%\n", mcts_safe_passed, total, 100.0 * (double)mcts_safe_passed / (double)total);
    cnn_free_weights(&weights);
    return 0;
}
