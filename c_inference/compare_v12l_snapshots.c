#include "cnn_infer.h"
#include "mcts_c.h"
#include "search_safety_c.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *name;
    CBoard board;
    int target;
    int suppress;
    const char *target_xy;
    const char *suppress_xy;
} SnapshotCase;

static int cell(int row, int col) {
    return row * GOMOKU_BOARD_SIZE + col;
}

static void set_stone(SnapshotCase *tc, int row, int col, int player) {
    tc->board.cells[cell(row, col)] = player;
    tc->board.move_count++;
}

static void encode_board(
    const CBoard *board,
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS],
    float legal_mask[GOMOKU_BOARD_CELLS]
) {
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

static void print_move_rc(int move) {
    if (move < 0) {
        printf("none");
        return;
    }
    printf("(%d,%d)", move / GOMOKU_BOARD_SIZE, move % GOMOKU_BOARD_SIZE);
}

static void print_move_xy(int move) {
    if (move < 0) {
        printf("none");
        return;
    }
    printf("%d,%d", move % GOMOKU_BOARD_SIZE, move / GOMOKU_BOARD_SIZE);
}

static void print_top5(const float logits[GOMOKU_BOARD_CELLS], const float probs[GOMOKU_BOARD_CELLS], const float legal_mask[GOMOKU_BOARD_CELLS]) {
    int used[GOMOKU_BOARD_CELLS] = {0};
    for (int rank = 1; rank <= 5; rank++) {
        int best = -1;
        float best_logit = -1.0e30f;
        for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
            if (legal_mask[i] <= 0.0f || used[i]) {
                continue;
            }
            if (best < 0 || logits[i] > best_logit) {
                best = i;
                best_logit = logits[i];
            }
        }
        if (best < 0) {
            break;
        }
        used[best] = 1;
        printf("    %d. rc=", rank);
        print_move_rc(best);
        printf(" xy=");
        print_move_xy(best);
        printf(" logit=%.6f prob=%.6f\n", logits[best], probs[best]);
    }
}

static SnapshotCase make_g2_m13(void) {
    SnapshotCase tc;
    memset(&tc, 0, sizeof(tc));
    board_init(&tc.board);
    tc.name = "v12l_g2_m13";
    tc.board.current_player = GOMOKU_WHITE;
    tc.board.last_move = -1;
    tc.target = cell(6, 8);    /* xy 8,6 */
    tc.suppress = cell(4, 9);  /* xy 9,4 */
    tc.target_xy = "8,6";
    tc.suppress_xy = "9,4";

    set_stone(&tc, 5, 4, GOMOKU_BLACK);
    set_stone(&tc, 5, 8, GOMOKU_WHITE);

    set_stone(&tc, 6, 5, GOMOKU_WHITE);
    set_stone(&tc, 6, 7, GOMOKU_WHITE);

    set_stone(&tc, 7, 5, GOMOKU_BLACK);
    set_stone(&tc, 7, 6, GOMOKU_WHITE);
    set_stone(&tc, 7, 7, GOMOKU_BLACK);

    set_stone(&tc, 8, 4, GOMOKU_BLACK);
    set_stone(&tc, 8, 5, GOMOKU_BLACK);
    set_stone(&tc, 8, 6, GOMOKU_BLACK);
    set_stone(&tc, 8, 7, GOMOKU_WHITE);

    set_stone(&tc, 9, 5, GOMOKU_BLACK);

    set_stone(&tc, 10, 4, GOMOKU_WHITE);

    return tc;
}

static SnapshotCase make_g2_m15(void) {
    SnapshotCase tc = make_g2_m13();
    tc.name = "v12l_g2_m15";
    tc.suppress = cell(6, 6);  /* xy 6,6 */
    tc.suppress_xy = "6,6";

    set_stone(&tc, 3, 10, GOMOKU_BLACK);
    set_stone(&tc, 4, 9, GOMOKU_WHITE);

    return tc;
}

static int run_case(const CnnWeights *weights, const SnapshotCase *tc, int mcts_sims) {
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float probs[GOMOKU_BOARD_CELLS];
    float value = 0.0f;

    encode_board(&tc->board, input, legal_mask);
    cnn_forward(weights, input, logits, &value);
    cnn_masked_softmax(logits, legal_mask, probs);

    int direct = cnn_top_legal_move(logits, legal_mask);
    int safety = safety_select_move(&tc->board, logits, 1);

    MCTSConfigC raw_cfg = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 0};
    MCTSConfigC safe_cfg = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 1};

    int mcts_raw = mcts_sims > 0 ? mcts_select_move(weights, &tc->board, &raw_cfg) : -1;
    int mcts_safe = mcts_sims > 0 ? mcts_select_move(weights, &tc->board, &safe_cfg) : -1;

    printf("case %s\n", tc->name);
    printf("  target xy=%s rc=", tc->target_xy);
    print_move_rc(tc->target);
    printf("\n");
    printf("  suppress xy=%s rc=", tc->suppress_xy);
    print_move_rc(tc->suppress);
    printf("\n");
    printf("  value=%.6f\n", value);

    printf("  direct selected rc=");
    print_move_rc(direct);
    printf(" xy=");
    print_move_xy(direct);
    printf(" %s\n", direct == tc->target ? "PASS" : "FAIL");

    printf("  safety selected rc=");
    print_move_rc(safety);
    printf(" xy=");
    print_move_xy(safety);
    printf(" %s\n", safety == tc->target ? "PASS" : "CHECK");

    if (mcts_sims > 0) {
        printf("  mcts_raw selected rc=");
        print_move_rc(mcts_raw);
        printf(" xy=");
        print_move_xy(mcts_raw);
        printf(" %s\n", mcts_raw == tc->target ? "PASS" : "FAIL");

        printf("  mcts_safety selected rc=");
        print_move_rc(mcts_safe);
        printf(" xy=");
        print_move_xy(mcts_safe);
        printf(" %s\n", mcts_safe == tc->target ? "PASS" : "FAIL");
    }

    printf("  target_logit=%.6f suppress_logit=%.6f gap=%.6f\n",
        logits[tc->target],
        logits[tc->suppress],
        logits[tc->target] - logits[tc->suppress]
    );
    printf("  target_prob=%.6f suppress_prob=%.6f\n",
        probs[tc->target],
        probs[tc->suppress]
    );
    printf("  top5:\n");
    print_top5(logits, probs, legal_mask);
    printf("\n");

    return direct == tc->target ? 1 : 0;
}

int main(int argc, char **argv) {
    const char *weights_path = "weights/15x15_v12l_margin_frozenbn_weights.bin";
    int mcts_sims = 4;

    if (argc >= 2) {
        weights_path = argv[1];
    }
    if (argc >= 3) {
        mcts_sims = atoi(argv[2]);
    }

    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    SnapshotCase cases[] = {
        make_g2_m13(),
        make_g2_m15(),
    };

    int passed = 0;
    int total = (int)(sizeof(cases) / sizeof(cases[0]));
    for (int i = 0; i < total; i++) {
        passed += run_case(&weights, &cases[i], mcts_sims);
    }

    printf("v12l_c_direct_snapshot_accuracy %d/%d %.2f%%\n",
        passed,
        total,
        100.0 * (double)passed / (double)total
    );

    cnn_free_weights(&weights);
    return passed == total ? 0 : 1;
}
