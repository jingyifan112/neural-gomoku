#include "cnn_infer.h"
#include "mcts_c.h"
#include "search_safety_c.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *read_file(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) {
        return NULL;
    }
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return NULL;
    }
    long size = ftell(file);
    if (size < 0) {
        fclose(file);
        return NULL;
    }
    rewind(file);
    char *data = (char *)calloc((size_t)size + 1, 1);
    if (!data) {
        fclose(file);
        return NULL;
    }
    if (fread(data, 1, (size_t)size, file) != (size_t)size) {
        free(data);
        fclose(file);
        return NULL;
    }
    fclose(file);
    return data;
}

static int json_string_field(const char *json, const char *field, char *out, size_t out_size) {
    char needle[64];
    snprintf(needle, sizeof(needle), "\"%s\"", field);
    const char *pos = strstr(json, needle);
    if (!pos) {
        return 0;
    }
    pos = strchr(pos + strlen(needle), ':');
    if (!pos) {
        return 0;
    }
    pos = strchr(pos, '"');
    if (!pos) {
        return 0;
    }
    pos++;
    const char *end = strchr(pos, '"');
    if (!end) {
        return 0;
    }
    size_t len = (size_t)(end - pos);
    if (len >= out_size) {
        len = out_size - 1;
    }
    memcpy(out, pos, len);
    out[len] = '\0';
    return 1;
}

static int parse_last_move(const char *json) {
    const char *pos = strstr(json, "\"last_move\"");
    int row = -1;
    int col = -1;
    if (!pos || sscanf(pos, "\"last_move\"%*[^[][%d%*[, ]%d]", &row, &col) != 2) {
        return -1;
    }
    return row * GOMOKU_BOARD_SIZE + col;
}

static int parse_position(const char *path, char *case_name, size_t case_name_size, CBoard *board) {
    char *json = read_file(path);
    if (!json) {
        fprintf(stderr, "failed to read position: %s\n", path);
        return 0;
    }

    char current_player[8];
    if (!json_string_field(json, "name", case_name, case_name_size) || !json_string_field(json, "current_player", current_player, sizeof(current_player))) {
        fprintf(stderr, "position is missing name or current_player\n");
        free(json);
        return 0;
    }

    board_init(board);
    board->current_player = current_player[0] == 'O' ? GOMOKU_WHITE : GOMOKU_BLACK;
    board->last_move = parse_last_move(json);
    board->move_count = 0;
    memset(board->cells, 0, sizeof(board->cells));

    const char *board_pos = strstr(json, "\"board\"");
    if (!board_pos) {
        fprintf(stderr, "position is missing board\n");
        free(json);
        return 0;
    }
    const char *row = strchr(board_pos, '[');
    if (!row) {
        free(json);
        return 0;
    }
    for (int r = 0; r < GOMOKU_BOARD_SIZE; r++) {
        row = strchr(row, '"');
        if (!row) {
            fprintf(stderr, "position board has fewer than %d rows\n", GOMOKU_BOARD_SIZE);
            free(json);
            return 0;
        }
        row++;
        for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
            char ch = row[c];
            int value = GOMOKU_EMPTY;
            if (ch == 'X') {
                value = GOMOKU_BLACK;
            } else if (ch == 'O') {
                value = GOMOKU_WHITE;
            } else if (ch != '.') {
                fprintf(stderr, "invalid board character %c at (%d,%d)\n", ch, r, c);
                free(json);
                return 0;
            }
            board->cells[r * GOMOKU_BOARD_SIZE + c] = value;
            if (value != GOMOKU_EMPTY) {
                board->move_count++;
            }
        }
        row += GOMOKU_BOARD_SIZE + 1;
    }

    free(json);
    return 1;
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

static int legal_move_count(const CBoard *board) {
    int count = 0;
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        count += board_is_legal(board, i) ? 1 : 0;
    }
    return count;
}

static void print_move(int action) {
    if (action < 0) {
        printf("none");
        return;
    }
    printf("(%d,%d)", action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE);
}

int main(int argc, char **argv) {
    const char *weights_path = argc > 1 ? argv[1] : "weights/9x9_weights.bin";
    const char *position_path = argc > 2 ? argv[2] : "../diagnostics/positions/human_play_cross_center_reference.json";
    int mcts_sims = argc > 3 ? atoi(argv[3]) : 256;

    CBoard board;
    char case_name[128];
    if (!parse_position(position_path, case_name, sizeof(case_name), &board)) {
        return 1;
    }

    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float value = 0.0f;
    encode(&board, input, legal_mask);
    cnn_forward(&weights, input, logits, &value);
    int direct_move = cnn_top_legal_move(logits, legal_mask);

    MCTSConfigC raw_config = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 0};
    MCTSConfigC safe_config = {.simulations = mcts_sims, .c_puct = 1.5f, .use_safety = 1};
    int raw_mcts_move = mcts_sims > 0 ? mcts_select_move(&weights, &board, &raw_config) : -1;
    int safety_move = mcts_sims > 0 ? mcts_select_move(&weights, &board, &safe_config) : safety_select_move(&board, logits, 1);
    int final_move = safety_move;

    printf("case_name=%s\n", case_name);
    printf("board_size=%d\n", GOMOKU_BOARD_SIZE);
    printf("current_player=%c\n", board.current_player == GOMOKU_WHITE ? 'O' : 'X');
    printf("legal_move_count=%d\n", legal_move_count(&board));
    printf("direct_policy_top=");
    print_move(direct_move);
    printf("\n");
    printf("value=%.6f\n", value);
    printf("raw_mcts_selected=");
    print_move(raw_mcts_move);
    printf("\n");
    printf("safety_adjusted_selected=");
    print_move(safety_move);
    printf("\n");
    printf("final_selected=");
    print_move(final_move);
    printf("\n");
    printf("weights_path=%s\n", weights_path);
    printf("mcts_sims=%d\n", mcts_sims);

    cnn_free_weights(&weights);
    return 0;
}
