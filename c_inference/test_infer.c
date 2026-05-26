#include "cnn_infer.h"

#include <math.h>
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

static int read_top_move(const char *path) {
    FILE *file = fopen(path, "r");
    if (!file) {
        perror(path);
        return -1;
    }
    int move = -1;
    fscanf(file, "%d", &move);
    fclose(file);
    return move;
}

static float max_abs_diff(const float *a, const float *b, size_t count) {
    float max_diff = 0.0f;
    for (size_t i = 0; i < count; i++) {
        float diff = fabsf(a[i] - b[i]);
        if (diff > max_diff) {
            max_diff = diff;
        }
    }
    return max_diff;
}

int main(int argc, char **argv) {
    const char *weights_path = argc > 1 ? argv[1] : "weights/9x9_weights.bin";
    const char *ref_dir = argc > 2 ? argv[2] : "reference/case0";

    char path[512];
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float ref_logits[GOMOKU_BOARD_CELLS];
    float ref_probs[GOMOKU_BOARD_CELLS];
    float ref_value[1];

    snprintf(path, sizeof(path), "%s/input.bin", ref_dir);
    if (!read_floats(path, input, GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s/legal_mask.bin", ref_dir);
    if (!read_floats(path, legal_mask, GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s/policy_logits.bin", ref_dir);
    if (!read_floats(path, ref_logits, GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s/policy_probs.bin", ref_dir);
    if (!read_floats(path, ref_probs, GOMOKU_BOARD_CELLS)) return 1;
    snprintf(path, sizeof(path), "%s/value.bin", ref_dir);
    if (!read_floats(path, ref_value, 1)) return 1;
    snprintf(path, sizeof(path), "%s/top_legal_move.txt", ref_dir);
    int ref_top = read_top_move(path);
    if (ref_top < 0) return 1;

    CnnWeights weights;
    if (!cnn_load_weights(weights_path, &weights)) {
        return 1;
    }

    float logits[GOMOKU_BOARD_CELLS];
    float probs[GOMOKU_BOARD_CELLS];
    float value = 0.0f;
    cnn_forward(&weights, input, logits, &value);
    cnn_masked_softmax(logits, legal_mask, probs);
    int top = cnn_top_legal_move(logits, legal_mask);

    float logits_diff = max_abs_diff(logits, ref_logits, GOMOKU_BOARD_CELLS);
    float probs_diff = max_abs_diff(probs, ref_probs, GOMOKU_BOARD_CELLS);
    float value_diff = fabsf(value - ref_value[0]);

    printf("policy_logits_max_abs_diff %.9g\n", logits_diff);
    printf("policy_probs_max_abs_diff %.9g\n", probs_diff);
    printf("value_abs_diff %.9g\n", value_diff);
    printf("top_legal_move C=%d Python=%d\n", top, ref_top);

    cnn_free_weights(&weights);

    if (logits_diff > 1e-4f || value_diff > 1e-4f || top != ref_top) {
        return 1;
    }
    return 0;
}
