#include "mcts_c.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct MCTSNode {
    CBoard board;
    int move_from_parent;
    float prior;
    int visit_count;
    float value_sum;
    int expanded;
    int terminal;
    float terminal_value;
    int child_count;
    struct MCTSNode *children[GOMOKU_BOARD_CELLS];
};

static MCTSNode *node_create(const CBoard *board, int move_from_parent, float prior) {
    MCTSNode *node = (MCTSNode *)calloc(1, sizeof(MCTSNode));
    if (!node) {
        return NULL;
    }
    node->board = *board;
    node->move_from_parent = move_from_parent;
    node->prior = prior;
    return node;
}

static void node_free(MCTSNode *node) {
    if (!node) {
        return;
    }
    for (int i = 0; i < node->child_count; i++) {
        node_free(node->children[i]);
    }
    free(node);
}

static float node_value(const MCTSNode *node) {
    return node->visit_count == 0 ? 0.0f : node->value_sum / (float)node->visit_count;
}

static void encode_board(const CBoard *board, float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS], float legal_mask[GOMOKU_BOARD_CELLS]) {
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

static int board_is_full(const CBoard *board) {
    return board->move_count >= GOMOKU_BOARD_CELLS;
}

static void make_child_board(const CBoard *parent, int action, CBoard *child_board, int *terminal, float *terminal_value) {
    *child_board = *parent;
    int player = parent->current_player;
    board_apply_move(child_board, action);
    if (board_has_win_from(child_board, action, player)) {
        *terminal = 1;
        *terminal_value = -1.0f;
    } else if (board_is_full(child_board)) {
        *terminal = 1;
        *terminal_value = 0.0f;
    } else {
        *terminal = 0;
        *terminal_value = 0.0f;
    }
}

static float expand_node(MCTSNode *node, const CnnWeights *weights) {
    if (node->terminal) {
        node->expanded = 1;
        return node->terminal_value;
    }

    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float priors[GOMOKU_BOARD_CELLS];
    float value = 0.0f;
    encode_board(&node->board, input, legal_mask);
    cnn_forward(weights, input, logits, &value);
    cnn_masked_softmax(logits, legal_mask, priors);

    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (!board_is_legal(&node->board, action)) {
            continue;
        }
        CBoard child_board;
        int terminal = 0;
        float terminal_value = 0.0f;
        make_child_board(&node->board, action, &child_board, &terminal, &terminal_value);
        MCTSNode *child = node_create(&child_board, action, priors[action]);
        if (!child) {
            continue;
        }
        child->terminal = terminal;
        child->terminal_value = terminal_value;
        node->children[node->child_count++] = child;
    }

    node->expanded = 1;
    return value;
}

static MCTSNode *select_child(const MCTSNode *node, const MCTSConfigC *config) {
    MCTSNode *best = NULL;
    float best_score = -INFINITY;
    float parent_sqrt = sqrtf((float)(node->visit_count > 1 ? node->visit_count : 1));
    for (int i = 0; i < node->child_count; i++) {
        MCTSNode *child = node->children[i];
        float q_value = -node_value(child);
        float u_value = config->c_puct * child->prior * parent_sqrt / (1.0f + (float)child->visit_count);
        float score = q_value + u_value;
        if (!best || score > best_score) {
            best = child;
            best_score = score;
        }
    }
    return best;
}

static float search(MCTSNode *node, const CnnWeights *weights, const MCTSConfigC *config) {
    if (node->terminal) {
        node->visit_count++;
        node->value_sum += node->terminal_value;
        return node->terminal_value;
    }

    if (!node->expanded) {
        float value = expand_node(node, weights);
        node->visit_count++;
        node->value_sum += value;
        return value;
    }

    MCTSNode *child = select_child(node, config);
    if (!child) {
        node->visit_count++;
        return 0.0f;
    }

    float child_value = search(child, weights, config);
    float value = -child_value;
    node->visit_count++;
    node->value_sum += value;
    return value;
}

static int best_visit_move(const CBoard *board, const float visits[GOMOKU_BOARD_CELLS], int use_safety) {
    if (use_safety) {
        int safe = safety_select_move(board, visits, 1);
        if (safe >= 0) {
            return safe;
        }
    }

    int best = -1;
    float best_score = -INFINITY;
    for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
        if (board_is_legal(board, action) && (best < 0 || visits[action] > best_score)) {
            best = action;
            best_score = visits[action];
        }
    }
    return best;
}

int mcts_select_move(const CnnWeights *weights, const CBoard *board, const MCTSConfigC *config) {
    float input[GOMOKU_INPUT_CHANNELS * GOMOKU_BOARD_CELLS];
    float legal_mask[GOMOKU_BOARD_CELLS];
    float logits[GOMOKU_BOARD_CELLS];
    float value = 0.0f;
    encode_board(board, input, legal_mask);
    cnn_forward(weights, input, logits, &value);
    (void)value;

    if (config->use_safety) {
        int forced = safety_select_move(board, logits, 1);
        int own_wins[GOMOKU_BOARD_CELLS];
        int opponent_wins[GOMOKU_BOARD_CELLS];
        if (
            board_immediate_winning_moves(board, board->current_player, own_wins) > 0 ||
            board_immediate_winning_moves(board, -board->current_player, opponent_wins) > 0
        ) {
            return forced;
        }
    }

    if (config->simulations <= 0) {
        return safety_select_move(board, logits, config->use_safety);
    }

    MCTSNode *root = node_create(board, -1, 1.0f);
    if (!root) {
        return safety_select_move(board, logits, config->use_safety);
    }
    expand_node(root, weights);
    for (int i = 0; i < config->simulations; i++) {
        search(root, weights, config);
    }

    float visits[GOMOKU_BOARD_CELLS] = {0.0f};
    for (int i = 0; i < root->child_count; i++) {
        MCTSNode *child = root->children[i];
        visits[child->move_from_parent] = (float)child->visit_count;
    }
    int total_visits = 0;
    for (int i = 0; i < GOMOKU_BOARD_CELLS; i++) {
        total_visits += (int)visits[i];
    }
    if (total_visits == 0) {
        for (int action = 0; action < GOMOKU_BOARD_CELLS; action++) {
            if (board_is_legal(board, action)) {
                visits[action] = 1.0f;
            }
        }
    }

    int move = best_visit_move(board, visits, config->use_safety);
    node_free(root);
    return move;
}
