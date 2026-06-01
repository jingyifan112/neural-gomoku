#include "mcts_c.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_WEIGHTS_PATH "weights/15x15_smoke_weights.bin"
#define DEFAULT_MCTS_SIMS 256

typedef struct {
    CBoard board;
    CnnWeights weights;
    int weights_loaded;
    int started;
    int engine_player;
    int mcts_sims;
} BrainState;

static void protocol_printf(const char *text) {
    printf("%s\n", text);
    fflush(stdout);
}

static int parse_positive_int(const char *text, int fallback) {
    if (!text || !*text) {
        return fallback;
    }
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || value <= 0 || value > 1000000) {
        return fallback;
    }
    return (int)value;
}

static void strip_newline(char *line) {
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[--len] = '\0';
    }
}

static int action_from_xy(int x, int y) {
    if (x < 0 || x >= GOMOKU_BOARD_SIZE || y < 0 || y >= GOMOKU_BOARD_SIZE) {
        return -1;
    }
    return y * GOMOKU_BOARD_SIZE + x;
}

static void print_action_xy(int action) {
    int row = action / GOMOKU_BOARD_SIZE;
    int col = action % GOMOKU_BOARD_SIZE;
    printf("%d,%d\n", col, row);
    fflush(stdout);
}

static int first_legal_move(const CBoard *board) {
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (board_is_legal(board, action)) {
            return action;
        }
    }
    return -1;
}

static int choose_engine_move(BrainState *state) {
    MCTSConfigC config = {
        .simulations = state->mcts_sims,
        .c_puct = 1.5f,
        .use_safety = 1,
    };
    int action = mcts_select_move(&state->weights, &state->board, &config);
    if (!board_is_legal(&state->board, action)) {
        fprintf(stderr, "selected illegal move %d, falling back to first legal move\n", action);
        action = first_legal_move(&state->board);
    }
    return action;
}

static int apply_move_as(CBoard *board, int player, int action) {
    board->current_player = player;
    return board_apply_move(board, action);
}

static void reset_board_for_start(BrainState *state) {
    board_init(&state->board);
    state->engine_player = GOMOKU_BLACK;
}

static void handle_start(BrainState *state, const char *args) {
    int size = atoi(args);
    if (size != GOMOKU_BOARD_SIZE) {
        protocol_printf("ERROR unsupported board size");
        state->started = 0;
        return;
    }
    reset_board_for_start(state);
    state->started = 1;
    protocol_printf("OK");
}

static void handle_begin(BrainState *state) {
    if (!state->started) {
        protocol_printf("ERROR not started");
        return;
    }
    state->engine_player = GOMOKU_BLACK;
    state->board.current_player = state->engine_player;
    int action = choose_engine_move(state);
    if (action < 0 || !board_apply_move(&state->board, action)) {
        protocol_printf("ERROR no legal move");
        return;
    }
    print_action_xy(action);
}

static void handle_turn(BrainState *state, const char *args) {
    if (!state->started) {
        protocol_printf("ERROR not started");
        return;
    }

    int x = -1;
    int y = -1;
    if (sscanf(args, " %d , %d", &x, &y) != 2) {
        protocol_printf("ERROR invalid TURN");
        return;
    }
    int opponent_action = action_from_xy(x, y);
    if (opponent_action < 0 || !board_is_legal(&state->board, opponent_action)) {
        protocol_printf("ERROR invalid move");
        return;
    }

    if (state->board.move_count == 0) {
        state->engine_player = GOMOKU_WHITE;
    }
    if (!apply_move_as(&state->board, -state->engine_player, opponent_action)) {
        protocol_printf("ERROR invalid move");
        return;
    }

    state->board.current_player = state->engine_player;
    int action = choose_engine_move(state);
    if (action < 0 || !board_apply_move(&state->board, action)) {
        protocol_printf("ERROR no legal move");
        return;
    }
    print_action_xy(action);
}

static void handle_board(BrainState *state) {
    if (!state->started) {
        protocol_printf("ERROR not started");
        return;
    }

    board_init(&state->board);
    char line[256];
    while (fgets(line, sizeof(line), stdin)) {
        strip_newline(line);
        if (strcmp(line, "DONE") == 0) {
            state->board.current_player = state->engine_player;
            int action = choose_engine_move(state);
            if (action < 0 || !board_apply_move(&state->board, action)) {
                protocol_printf("ERROR no legal move");
                return;
            }
            print_action_xy(action);
            return;
        }

        int x = -1;
        int y = -1;
        int field = 0;
        if (sscanf(line, " %d , %d , %d", &x, &y, &field) != 3) {
            fprintf(stderr, "ignored invalid BOARD line: %s\n", line);
            continue;
        }
        int action = action_from_xy(x, y);
        if (action < 0 || field < 1 || field > 2 || state->board.cells[action] != GOMOKU_EMPTY) {
            fprintf(stderr, "ignored invalid BOARD move: %s\n", line);
            continue;
        }
        state->board.cells[action] = field == 1 ? state->engine_player : -state->engine_player;
        state->board.last_move = action;
        state->board.move_count++;
    }
}

static void handle_info(const char *args) {
    fprintf(stderr, "INFO %s\n", args);
}

static void handle_about(void) {
    protocol_printf("name=\"neural-gomoku\", version=\"0.1-9x9-smoke\", author=\"neural-gomoku\"");
}

int main(void) {
    BrainState state;
    memset(&state, 0, sizeof(state));
    state.engine_player = GOMOKU_BLACK;
    state.mcts_sims = parse_positive_int(getenv("NEURAL_GOMOKU_MCTS_SIMS"), DEFAULT_MCTS_SIMS);
    board_init(&state.board);

    const char *weights_path = getenv("NEURAL_GOMOKU_WEIGHTS");
    if (!weights_path || !*weights_path) {
        weights_path = DEFAULT_WEIGHTS_PATH;
    }
    if (!cnn_load_weights(weights_path, &state.weights)) {
        fprintf(stderr, "failed to load weights: %s\n", weights_path);
        return 1;
    }
    state.weights_loaded = 1;
    fprintf(stderr, "loaded weights=%s mcts_sims=%d\n", weights_path, state.mcts_sims);

    char line[256];
    while (fgets(line, sizeof(line), stdin)) {
        strip_newline(line);
        char *command = line;
        while (isspace((unsigned char)*command)) {
            command++;
        }
        char *args = command;
        while (*args && !isspace((unsigned char)*args)) {
            args++;
        }
        if (*args) {
            *args++ = '\0';
        }
        while (isspace((unsigned char)*args)) {
            args++;
        }

        if (strcmp(command, "START") == 0) {
            handle_start(&state, args);
        } else if (strcmp(command, "BEGIN") == 0) {
            handle_begin(&state);
        } else if (strcmp(command, "TURN") == 0) {
            handle_turn(&state, args);
        } else if (strcmp(command, "BOARD") == 0) {
            handle_board(&state);
        } else if (strcmp(command, "INFO") == 0) {
            handle_info(args);
        } else if (strcmp(command, "ABOUT") == 0) {
            handle_about();
        } else if (strcmp(command, "END") == 0) {
            break;
        } else if (*command) {
            protocol_printf("UNKNOWN");
        }
    }

    if (state.weights_loaded) {
        cnn_free_weights(&state.weights);
    }
    return 0;
}
