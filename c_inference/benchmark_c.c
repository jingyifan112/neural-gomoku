#include "cnn_infer.h"

#include <stdio.h>
#include <string.h>

#define EMPTY 0
#define BLACK 1
#define WHITE -1

typedef struct {
    const char *name;
    int board[GOMOKU_BOARD_CELLS];
    int current_player;
    int last_move;
    int expected_moves[2];
    int expected_count;
    const char *note;
} TacticalCase;

static int cell(int row, int col) {
    return row * GOMOKU_BOARD_SIZE + col;
}

static void set_stone(TacticalCase *tc, int row, int col, int player) {
    tc->board[cell(row, col)] = player;
}

static void encode(const int board[GOMOKU_BOARD_CELLS], int current_player, int last_move, float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS], float legal_mask[GOMOKU_BOARD_CELLS]) {
    memset(input, 0, sizeof(float) * GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS);
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        input[i] = board[i] == current_player ? 1.0f : 0.0f;
        input[GOMOKU_BOARD_CELLS + i] = board[i] == -current_player ? 1.0f : 0.0f;
        legal_mask[i] = board[i] == EMPTY ? 1.0f : 0.0f;
    }
    if (last_move >= 0) {
        input[2 * GOMOKU_BOARD_CELLS + last_move] = 1.0f;
    }
}

static void render(const int board[GOMOKU_BOARD_CELLS]) {
    printf("   ");
    for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
        printf(" %d", c);
    }
    printf("\n");
    for (int r = 0; r < GOMOKU_BOARD_SIZE; r++) {
        printf("%2d ", r);
        for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
            int v = board[cell(r, c)];
            char ch = v == BLACK ? 'X' : (v == WHITE ? 'O' : '.');
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

static TacticalCase opponent_four_one_endpoint(void) {
    TacticalCase tc = {
        .name = "opponent_four_one_endpoint",
        .current_player = BLACK,
        .last_move = cell(4, 3),
        .expected_moves = {cell(4, 4), -1},
        .expected_count = 1,
        .note = "Opponent O has OOOO with one playable endpoint; model X should block.",
    };
    set_stone(&tc, 4, 0, BLACK);
    set_stone(&tc, 4, 1, WHITE);
    set_stone(&tc, 4, 2, WHITE);
    set_stone(&tc, 4, 3, WHITE);
    set_stone(&tc, 4, 4, WHITE);
    set_stone(&tc, 4, 5, EMPTY);
    tc.board[cell(4, 0)] = BLACK;
    tc.expected_moves[0] = cell(4, 5);
    return tc;
}

static TacticalCase opponent_open_three(void) {
    TacticalCase tc = {
        .name = "opponent_open_three",
        .current_player = BLACK,
        .last_move = cell(4, 4),
        .expected_moves = {cell(4, 1), cell(4, 5)},
        .expected_count = 2,
        .note = "Opponent O has .OOO.; either endpoint is an expected direct-policy block candidate.",
    };
    set_stone(&tc, 4, 2, WHITE);
    set_stone(&tc, 4, 3, WHITE);
    set_stone(&tc, 4, 4, WHITE);
    set_stone(&tc, 2, 2, BLACK);
    set_stone(&tc, 6, 6, BLACK);
    return tc;
}

static TacticalCase model_four_can_win(void) {
    TacticalCase tc = {
        .name = "model_four_can_win",
        .current_player = BLACK,
        .last_move = cell(3, 3),
        .expected_moves = {cell(3, 4), -1},
        .expected_count = 1,
        .note = "Model X has XXXX.; expected direct winning move.",
    };
    set_stone(&tc, 3, 0, BLACK);
    set_stone(&tc, 3, 1, BLACK);
    set_stone(&tc, 3, 2, BLACK);
    set_stone(&tc, 3, 3, BLACK);
    set_stone(&tc, 0, 0, WHITE);
    set_stone(&tc, 1, 1, WHITE);
    return tc;
}

static TacticalCase broken_four_pattern(void) {
    TacticalCase tc = {
        .name = "broken_four_pattern",
        .current_player = BLACK,
        .last_move = cell(5, 4),
        .expected_moves = {cell(5, 3), -1},
        .expected_count = 1,
        .note = "Model X has XX.XX; expected fill-gap winning move.",
    };
    set_stone(&tc, 5, 1, BLACK);
    set_stone(&tc, 5, 2, BLACK);
    set_stone(&tc, 5, 4, BLACK);
    set_stone(&tc, 5, 5, BLACK);
    set_stone(&tc, 0, 8, WHITE);
    set_stone(&tc, 1, 8, WHITE);
    return tc;
}

static int run_case(const CnnWeights *weights, const TacticalCase *tc) {
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float probs[GOMOKU_BOARD_CELLS];
    float value = 0.0f;

    encode(tc->board, tc->current_player, tc->last_move, input, legal_mask);
    cnn_forward(weights, input, logits, &value);
    cnn_masked_softmax(logits, legal_mask, probs);
    int move = cnn_top_legal_move(logits, legal_mask);
    int pass = is_expected(tc, move);

    printf("case %-28s %s\n", tc->name, pass ? "PASS" : "FAIL");
    printf("  note: %s\n", tc->note);
    printf("  selected: (%d,%d) logit=%.6f prob=%.6f value=%.6f\n", move / GOMOKU_BOARD_SIZE, move % GOMOKU_BOARD_SIZE, logits[move], probs[move], value);
    printf("  expected: ");
    print_expected(tc);
    printf("\n");
    if (!pass) {
        render(tc->board);
    }
    return pass;
}

int main(int argc, char **argv) {
    const char *weights_path = argc > 1 ? argv[1] : "weights/9x9_weights.bin";
    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    TacticalCase cases[] = {
        opponent_four_one_endpoint(),
        opponent_open_three(),
        model_four_can_win(),
        broken_four_pattern(),
    };
    int total = (int)(sizeof(cases) / sizeof(cases[0]));
    int passed = 0;
    for (int i = 0; i < total; i++) {
        passed += run_case(&weights, &cases[i]);
    }

    printf("accuracy %d/%d %.2f%%\n", passed, total, 100.0 * (double)passed / (double)total);
    cnn_free_weights(&weights);
    return 0;
}
