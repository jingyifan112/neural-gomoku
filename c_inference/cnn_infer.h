#ifndef GOMOKU_CNN_INFER_H
#define GOMOKU_CNN_INFER_H

#include <stddef.h>

#define GOMOKU_BOARD_SIZE 9
#define GOMOKU_BOARD_CELLS 81
#define GOMOKU_INPUT_CHANNELS 3
#define GOMOKU_CHANNELS 64
#define GOMOKU_BLOCKS 4
#define GOMOKU_POLICY_CHANNELS 2
#define GOMOKU_WEIGHT_FLOATS 315927

typedef struct {
    float *data;

    const float *stem_w;
    const float *stem_b;
    const float *block_conv1_w[GOMOKU_BLOCKS];
    const float *block_conv1_b[GOMOKU_BLOCKS];
    const float *block_conv2_w[GOMOKU_BLOCKS];
    const float *block_conv2_b[GOMOKU_BLOCKS];
    const float *policy_conv_w;
    const float *policy_conv_b;
    const float *policy_linear_w;
    const float *policy_linear_b;
    const float *value_conv_w;
    const float *value_conv_b;
    const float *value_fc1_w;
    const float *value_fc1_b;
    const float *value_fc2_w;
    const float *value_fc2_b;
} CnnWeights;

int cnn_load_weights(const char *path, CnnWeights *weights);
void cnn_free_weights(CnnWeights *weights);

void cnn_forward(const CnnWeights *weights, const float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS], float policy_logits[GOMOKU_BOARD_CELLS], float *value);
void cnn_masked_softmax(const float logits[GOMOKU_BOARD_CELLS], const float legal_mask[GOMOKU_BOARD_CELLS], float probs[GOMOKU_BOARD_CELLS]);
int cnn_top_legal_move(const float logits[GOMOKU_BOARD_CELLS], const float legal_mask[GOMOKU_BOARD_CELLS]);

#endif
