# Analysis tools

This directory is for lightweight v11-to-v12 failure analysis artifacts. The tools here do not train models, modify checkpoints, or change model/search code.

## Compare decision logs

Use `scripts/compare_decision_logs.py` when two pbrain debug logs should be aligned by game and `move_count`, for example v10 vs v11 on the same Rapfi games:

```bash
python scripts/compare_decision_logs.py \
  eval_logs/2026-06-02_v10_mcts32_debug_vs_rapfi_g2.log \
  eval_logs/2026-06-02_v11_mcts32_debug_vs_rapfi_g2.log \
  --left-label v10 \
  --right-label v11 \
  --output-csv analysis/v10_v11_decision_diff.csv
```

The CSV reports one row for each differing aligned decision by default. Use `--all` to include matching decisions too.

Important columns:
- `value_delta_right_minus_left` and `value_diff`: value-head change between logs.
- `direct_diff`: raw policy top move changed.
- `policy_safety_diff`: policy move after tactical safety changed.
- `mcts_raw_diff`: raw MCTS-selected move changed.
- `mcts_safety_diff`: MCTS plus safety move changed.
- `final_diff`: actual pbrain move changed.

Rows where `direct_diff=True` but `final_diff=False` are especially useful for checking whether MCTS or safety is hiding model differences.

## Extract Rapfi failure positions

Use `scripts/extract_rapfi_failure_positions.py` on Rapfi benchmark logs with debug decisions:

```bash
python scripts/extract_rapfi_failure_positions.py \
  eval_logs/2026-06-02_v11_mcts32_debug_vs_rapfi_g2.log
```

By default this writes:
- `analysis/rapfi_failure_positions.csv`
- `analysis/rapfi_failure_positions.json`

The CSV is flat, one row per neural `DEBUG_DECISION` line from games where a neural engine lost to Rapfi. The JSON is grouped by game and keeps the Rapfi bestlines and debug decisions together.

Important fields:
- `game_number`, `side_to_move`, `game_result`, `loss_reason`: game outcome context.
- `previous_rapfi_bestline` and `next_rapfi_bestline`: nearest Rapfi `Bestline` context around a neural decision.
- `all_rapfi_bestlines`: all Rapfi bestlines seen in that game.
- `direct`, `policy_safety`, `mcts_raw`, `mcts_safety`, `final`: neural decision pipeline outputs.
- `final_neural_moves_near_end`: the last neural final moves in that game, useful for quickly locating the losing phase.
- `debug_decision_line`: original log line for replay or deeper parsing.

Use `--include-all-games` if you want wins, draws, or non-Rapfi games included during parser debugging. Use `--near-end-count N` to change how many final neural moves are summarized near the end.

## Build Rapfi failure set

Use `scripts/build_rapfi_failure_set.py` after `analysis/rapfi_failure_positions.json` exists:

```bash
python scripts/build_rapfi_failure_set.py
```

By default this selects the late-game review positions from game 1 at move counts 38, 44, 46, and 48, plus game 2 at move counts 29, 31, and 33. It writes:
- `analysis/rapfi_failure_set.csv`
- `analysis/rapfi_failure_set.json`

The output is a small position-level review set with policy/MCTS/final move fields and nearby Rapfi bestlines. `failure_type` and `notes` are intentionally left as `needs_review` placeholders until the positions are hand-labeled.
