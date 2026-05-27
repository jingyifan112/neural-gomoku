#ifndef GOMOKU_MCTS_C_H
#define GOMOKU_MCTS_C_H

#include "cnn_infer.h"
#include "search_safety_c.h"

typedef struct {
    int simulations;
    float c_puct;
    int use_safety;
} MCTSConfigC;

typedef struct {
    int move;
    float prior;
    int visits;
    float q_value;
} MCTSRootChildStatsC;

typedef struct MCTSNode MCTSNode;

int mcts_select_move(const CnnWeights *weights, const CBoard *board, const MCTSConfigC *config);
int mcts_collect_root_child_stats(
    const CnnWeights *weights,
    const CBoard *board,
    const MCTSConfigC *config,
    MCTSRootChildStatsC stats[GOMOKU_BOARD_CELLS]
);

#endif
