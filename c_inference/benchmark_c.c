#include "cnn_infer.h"
#include "search_safety_c.h"

#include <stdio.h>
#include <string.h>

typedef struct {
    const char *name;
    CBoard board;
    int expected_moves[2];
    int expected_count;
    const char *note;
} TacticalCase;

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

static int run_case(const CnnWeights *weights, const TacticalCase *tc) {
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
    int direct_pass = is_expected(tc, direct_move);
    int safe_pass = is_expected(tc, safe_move);

    printf("case %-28s direct=%s safety=%s\n", tc->name, direct_pass ? "PASS" : "FAIL", safe_pass ? "PASS" : "FAIL");
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
    printf("  expected: ");
    print_expected(tc);
    printf("\n");
    if (!direct_pass || !safe_pass) {
        render(&tc->board);
    }
    return (direct_pass ? 1 : 0) | (safe_pass ? 2 : 0);
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
    int direct_passed = 0;
    int safety_passed = 0;
    for (int i = 0; i < total; i++) {
        int result = run_case(&weights, &cases[i]);
        direct_passed += (result & 1) ? 1 : 0;
        safety_passed += (result & 2) ? 1 : 0;
    }

    printf("direct_policy_accuracy %d/%d %.2f%%\n", direct_passed, total, 100.0 * (double)direct_passed / (double)total);
    printf("policy_plus_safety_accuracy %d/%d %.2f%%\n", safety_passed, total, 100.0 * (double)safety_passed / (double)total);
    cnn_free_weights(&weights);
    return 0;
}
