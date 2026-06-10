#include "cnn_infer.h"

#include <stdio.h>
#include <stdlib.h>

static int read_floats(const char *path, float *out, size_t count) {
    FILE *file = fopen(path, "rb");
    if (!file) {
        perror(path);
        return 0;
    }
    size_t read = fread(out, sizeof(float), count, file);
    fclose(file);
    if (read != count) {
        fprintf(stderr, "%s: expected %zu floats, read %zu\n", path, count, read);
        return 0;
    }
    return 1;
}

static int write_floats(const char *path, const float *data, size_t count) {
    FILE *file = fopen(path, "wb");
    if (!file) {
        perror(path);
        return 0;
    }
    size_t written = fwrite(data, sizeof(float), count, file);
    fclose(file);
    if (written != count) {
        fprintf(stderr, "%s: expected to write %zu floats, wrote %zu\n", path, count, written);
        return 0;
    }
    return 1;
}

static int write_top_move(const char *path, int top_move) {
    FILE *file = fopen(path, "w");
    if (!file) {
        perror(path);
        return 0;
    }
    fprintf(file, "%d\n", top_move);
    fclose(file);
    return 1;
}

int main(int argc, char **argv) {
    if (argc != 6) {
        fprintf(stderr, "usage: %s weights input.bin legal_mask.bin output_prefix top_move.txt\n", argv[0]);
        return 2;
    }

    const char *weights_path = argv[1];
    const char *input_path = argv[2];
    const char *legal_path = argv[3];
    const char *output_prefix = argv[4];
    const char *top_path = argv[5];

    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    if (!read_floats(input_path, input, GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS)) return 1;
    if (!read_floats(legal_path, legal_mask, GOMOKU_BOARD_CELLS)) return 1;

    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    float logits[GOMOKU_BOARD_CELLS];
    float probs[GOMOKU_BOARD_CELLS];
    float value[1] = {0.0f};
    cnn_forward(&weights, input, logits, &value[0]);
    cnn_masked_softmax(logits, legal_mask, probs);
    int top_move = cnn_top_legal_move(logits, legal_mask);

    char path[512];
    snprintf(path, sizeof(path), "%s_policy_logits.bin", output_prefix);
    if (!write_floats(path, logits, GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s_policy_probs.bin", output_prefix);
    if (!write_floats(path, probs, GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s_value.bin", output_prefix);
    if (!write_floats(path, value, 1)) return 1;
    if (!write_top_move(top_path, top_move)) return 1;

    cnn_free_weights(&weights);
    return 0;
}
