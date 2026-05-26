#include "cnn_infer.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IDX3(c, h, w) (((c) * GOMOKU_BOARD_SIZE + (h)) * GOMOKU_BOARD_SIZE + (w))

static const float *take(const float **cursor, size_t count) {
    const float *ptr = *cursor;
    *cursor += count;
    return ptr;
}

static void map_weight_pointers(CnnWeights *weights) {
    const float *cursor = weights->data;
    weights->stem_w = take(&cursor, GOMOKU_CHANNELS * GOMOKU_INPUT_CHANNELS * 3 * 3);
    weights->stem_b = take(&cursor, GOMOKU_CHANNELS);
    for (int block = 0; block < GOMOKU_BLOCKS; block++) {
        weights->block_conv1_w[block] = take(&cursor, GOMOKU_CHANNELS * GOMOKU_CHANNELS * 3 * 3);
        weights->block_conv1_b[block] = take(&cursor, GOMOKU_CHANNELS);
        weights->block_conv2_w[block] = take(&cursor, GOMOKU_CHANNELS * GOMOKU_CHANNELS * 3 * 3);
        weights->block_conv2_b[block] = take(&cursor, GOMOKU_CHANNELS);
    }
    weights->policy_conv_w = take(&cursor, GOMOKU_POLICY_CHANNELS * GOMOKU_CHANNELS);
    weights->policy_conv_b = take(&cursor, GOMOKU_POLICY_CHANNELS);
    weights->policy_linear_w = take(&cursor, GOMOKU_BOARD_CELLS * GOMOKU_POLICY_CHANNELS * GOMOKU_BOARD_CELLS);
    weights->policy_linear_b = take(&cursor, GOMOKU_BOARD_CELLS);
    weights->value_conv_w = take(&cursor, GOMOKU_CHANNELS);
    weights->value_conv_b = take(&cursor, 1);
    weights->value_fc1_w = take(&cursor, GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS);
    weights->value_fc1_b = take(&cursor, GOMOKU_CHANNELS);
    weights->value_fc2_w = take(&cursor, GOMOKU_CHANNELS);
    weights->value_fc2_b = take(&cursor, 1);
}

int cnn_load_weights(const char *path, CnnWeights *weights) {
    memset(weights, 0, sizeof(*weights));
    FILE *file = fopen(path, "rb");
    if (!file) {
        perror(path);
        return 0;
    }

    weights->data = (float *)malloc(sizeof(float) * GOMOKU_WEIGHT_FLOATS);
    if (!weights->data) {
        fclose(file);
        return 0;
    }

    size_t read = fread(weights->data, sizeof(float), GOMOKU_WEIGHT_FLOATS, file);
    fclose(file);
    if (read != GOMOKU_WEIGHT_FLOATS) {
        fprintf(stderr, "expected %d floats, read %zu\n", GOMOKU_WEIGHT_FLOATS, read);
        cnn_free_weights(weights);
        return 0;
    }

    map_weight_pointers(weights);
    return 1;
}

void cnn_free_weights(CnnWeights *weights) {
    free(weights->data);
    memset(weights, 0, sizeof(*weights));
}

static float relu(float x) {
    return x > 0.0f ? x : 0.0f;
}

static void conv3x3(
    const float *input,
    int in_channels,
    float *output,
    int out_channels,
    const float *weight,
    const float *bias
) {
    for (int oc = 0; oc < out_channels; oc++) {
        for (int h = 0; h < GOMOKU_BOARD_SIZE; h++) {
            for (int w = 0; w < GOMOKU_BOARD_SIZE; w++) {
                float sum = bias[oc];
                for (int ic = 0; ic < in_channels; ic++) {
                    for (int kh = 0; kh < 3; kh++) {
                        int ih = h + kh - 1;
                        if (ih < 0 || ih >= GOMOKU_BOARD_SIZE) {
                            continue;
                        }
                        for (int kw = 0; kw < 3; kw++) {
                            int iw = w + kw - 1;
                            if (iw < 0 || iw >= GOMOKU_BOARD_SIZE) {
                                continue;
                            }
                            size_t wi = (((oc * in_channels + ic) * 3 + kh) * 3 + kw);
                            sum += weight[wi] * input[IDX3(ic, ih, iw)];
                        }
                    }
                }
                output[IDX3(oc, h, w)] = sum;
            }
        }
    }
}

static void conv1x1(
    const float *input,
    int in_channels,
    float *output,
    int out_channels,
    const float *weight,
    const float *bias
) {
    for (int oc = 0; oc < out_channels; oc++) {
        for (int cell = 0; cell < GOMOKU_BOARD_CELLS; cell++) {
            float sum = bias[oc];
            for (int ic = 0; ic < in_channels; ic++) {
                sum += weight[oc * in_channels + ic] * input[ic * GOMOKU_BOARD_CELLS + cell];
            }
            output[oc * GOMOKU_BOARD_CELLS + cell] = sum;
        }
    }
}

static void linear(const float *input, float *output, int in_features, int out_features, const float *weight, const float *bias) {
    for (int out = 0; out < out_features; out++) {
        float sum = bias[out];
        const float *row = weight + out * in_features;
        for (int in = 0; in < in_features; in++) {
            sum += row[in] * input[in];
        }
        output[out] = sum;
    }
}

void cnn_forward(const CnnWeights *weights, const float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS], float policy_logits[GOMOKU_BOARD_CELLS], float *value) {
    float x[GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS];
    float y[GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS];
    float residual[GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS];

    conv3x3(input, GOMOKU_INPUT_CHANNELS, x, GOMOKU_CHANNELS, weights->stem_w, weights->stem_b);
    for (int i = 0; i < GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS; i++) {
        x[i] = relu(x[i]);
    }

    for (int block = 0; block < GOMOKU_BLOCKS; block++) {
        memcpy(residual, x, sizeof(x));
        conv3x3(x, GOMOKU_CHANNELS, y, GOMOKU_CHANNELS, weights->block_conv1_w[block], weights->block_conv1_b[block]);
        for (int i = 0; i < GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS; i++) {
            y[i] = relu(y[i]);
        }
        conv3x3(y, GOMOKU_CHANNELS, x, GOMOKU_CHANNELS, weights->block_conv2_w[block], weights->block_conv2_b[block]);
        for (int i = 0; i < GOMOKU_CHANNELS * GOMOKU_BOARD_CELLS; i++) {
            x[i] = relu(x[i] + residual[i]);
        }
    }

    float policy_features[GOMOKU_POLICY_CHANNELS * GOMOKU_BOARD_CELLS];
    conv1x1(x, GOMOKU_CHANNELS, policy_features, GOMOKU_POLICY_CHANNELS, weights->policy_conv_w, weights->policy_conv_b);
    for (int i = 0; i < GOMOKU_POLICY_CHANNELS * GOMOKU_BOARD_CELLS; i++) {
        policy_features[i] = relu(policy_features[i]);
    }
    linear(policy_features, policy_logits, GOMOKU_POLICY_CHANNELS * GOMOKU_BOARD_CELLS, GOMOKU_BOARD_CELLS, weights->policy_linear_w, weights->policy_linear_b);

    float value_features[GOMOKU_BOARD_CELLS];
    conv1x1(x, GOMOKU_CHANNELS, value_features, 1, weights->value_conv_w, weights->value_conv_b);
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        value_features[i] = relu(value_features[i]);
    }
    float hidden[GOMOKU_CHANNELS];
    linear(value_features, hidden, GOMOKU_BOARD_CELLS, GOMOKU_CHANNELS, weights->value_fc1_w, weights->value_fc1_b);
    for (int i = 0; i < GOMOKU_CHANNELS; i++) {
        hidden[i] = relu(hidden[i]);
    }
    float raw_value[1];
    linear(hidden, raw_value, GOMOKU_CHANNELS, 1, weights->value_fc2_w, weights->value_fc2_b);
    *value = tanhf(raw_value[0]);
}

void cnn_masked_softmax(const float logits[GOMOKU_BOARD_CELLS], const float legal_mask[GOMOKU_BOARD_CELLS], float probs[GOMOKU_BOARD_CELLS]) {
    float max_logit = -INFINITY;
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        if (legal_mask[i] > 0.0f && logits[i] > max_logit) {
            max_logit = logits[i];
        }
    }

    float sum = 0.0f;
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        if (legal_mask[i] > 0.0f) {
            probs[i] = expf(logits[i] - max_logit);
            sum += probs[i];
        } else {
            probs[i] = 0.0f;
        }
    }
    if (sum <= 0.0f) {
        return;
    }
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        probs[i] /= sum;
    }
}

int cnn_top_legal_move(const float logits[GOMOKU_BOARD_CELLS], const float legal_mask[GOMOKU_BOARD_CELLS]) {
    int best = -1;
    float best_logit = -INFINITY;
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        if (legal_mask[i] > 0.0f && (best < 0 || logits[i] > best_logit)) {
            best = i;
            best_logit = logits[i];
        }
    }
    return best;
}
