#include "cnn_infer.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EMPTY 0
#define BLACK 1
#define WHITE -1

static void render(const int board[GOMOKU_BOARD_CELLS]) {
    printf("   ");
    for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
        printf(" %d", c);
    }
    printf("\n");
    for (int r = 0; r < GOMOKU_BOARD_SIZE; r++) {
        printf("%2d ", r);
        for (int c = 0; c < GOMOKU_BOARD_SIZE; c++) {
            int v = board[r * GOMOKU_BOARD_SIZE + c];
            char ch = v == BLACK ? 'X' : (v == WHITE ? 'O' : '.');
            printf(" %c", ch);
        }
        printf("\n");
    }
}

static int count_dir(const int board[GOMOKU_BOARD_CELLS], int row, int col, int dr, int dc, int player) {
    int total = 0;
    row += dr;
    col += dc;
    while (row >= 0 && row < GOMOKU_BOARD_SIZE && col >= 0 && col < GOMOKU_BOARD_SIZE) {
        if (board[row * GOMOKU_BOARD_SIZE + col] != player) {
            break;
        }
        total++;
        row += dr;
        col += dc;
    }
    return total;
}

static int has_win(const int board[GOMOKU_BOARD_CELLS], int row, int col, int player) {
    const int dirs[4][2] = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};
    for (int i = 0; i < 4; i++) {
        int dr = dirs[i][0];
        int dc = dirs[i][1];
        int count = 1 + count_dir(board, row, col, dr, dc, player) + count_dir(board, row, col, -dr, -dc, player);
        if (count >= 5) {
            return 1;
        }
    }
    return 0;
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

int main(int argc, char **argv) {
    const char *weights_path = argc > 1 ? argv[1] : "weights/9x9_weights.bin";
    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    int board[GOMOKU_BOARD_CELLS] = {0};
    int current_player = BLACK;
    int human_player = BLACK;
    int last_move = -1;
    int move_count = 0;

    while (1) {
        render(board);
        int action = -1;
        if (current_player == human_player) {
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
            if (board[action] != EMPTY) {
                printf("occupied\n");
                continue;
            }
        } else {
            float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
            float legal_mask[GOMOKU_BOARD_CELLS];
            float logits[GOMOKU_BOARD_CELLS];
            float value = 0.0f;
            encode(board, current_player, last_move, input, legal_mask);
            cnn_forward(&weights, input, logits, &value);
            action = cnn_top_legal_move(logits, legal_mask);
            printf("model plays: %d %d value=%.4f\n", action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE, value);
        }

        board[action] = current_player;
        last_move = action;
        move_count++;
        if (has_win(board, action / GOMOKU_BOARD_SIZE, action % GOMOKU_BOARD_SIZE, current_player)) {
            render(board);
            printf("%s wins\n", current_player == human_player ? "you" : "model");
            break;
        }
        if (move_count == GOMOKU_BOARD_CELLS) {
            render(board);
            printf("draw\n");
            break;
        }
        current_player = -current_player;
    }

    cnn_free_weights(&weights);
    return 0;
}
