# Candidate H Rapfi Smoke Report

## Setup

- Candidate H C weights: `weights/15x15_candidate_h_value_ranking_weights.bin`
- Candidate H manifest: `weights/15x15_candidate_h_value_ranking_manifest.json`
- Wrapper scripts:
  - `/Users/jing1fan/gomoku_public_benchmark/run_neural_candidate_h_value_mcts16_debug.sh`
  - `/Users/jing1fan/gomoku_public_benchmark/run_neural_candidate_h_value_mcts32_debug.sh`
- Match settings: board 15x15, rule 0, 2 games, Rapfi depth 1, Rapfi `tc=1/1`, neural `tc=60/5`, `drawafter=225`, debug enabled.
- No current_best weights were overwritten.

## Stage Results

| Candidate | Stage | Status | Score | Game 1 | Game 2 |
|---|---:|---|---:|---:|---:|
| Candidate D baseline | mcts16 | baseline | 0-2-0 | 0-1 | 0-1 |
| Candidate H | mcts16 | run | 0-2-0 | 0-1 | 0-1 |
| Candidate H | mcts32 | skipped | not_run | not_run | not_run |

Candidate H mcts16 did not improve over the Candidate D baseline (`0-2`), so the required Stage 2 mcts32 smoke was skipped.

## Game 2 Decision Trace

| Candidate | ply13 | ply15 | ply17 | ply15 teacher 7,9? | ply17 teacher 9,9? |
|---|---:|---:|---:|---|---|
| Candidate D baseline mcts16 | 5,8 | 7,10 | 9,10 | no | no |
| Candidate H mcts16 | 2,6 | 2,8 | 4,10 | no | no |

First game2 divergence from the Candidate D mcts16 baseline is ply13: Candidate D played `5,8`, while Candidate H played `2,6`.

Important nuance: the Candidate H smoke line diverged from the Candidate D failure line before the original teacher-disagreement board. Therefore the fixed-position C probes remain valid, but the live mcts16 match did not exercise the exact ply15/ply17 board states where Candidate H selected the teacher moves in C verification.

## Logs

- Stage 1 stdout: `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.stdout.log`
- Stage 1 engine I/O: `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log`
- Misconfigured timing dry-run engine I/O, excluded from gate: `eval_logs/integration_eval/candidate_h_mcts16_misconfigured_tc_engine_io.log`

## Prior Gates

- Python-vs-C parity passed on ply15, ply17, and repair anchor.
- C tactical benchmark passed 7/7 for direct, policy+safety, mcts_raw, and mcts+safety.
- C probes selected teacher moves at the fixed ply15 and ply17 disagreement positions; repair anchor remained rank 2.
- `pytest -q` previously passed: 13 tests.

## Recommendation

Reject Candidate H as a promotion candidate for now. The policy/value fixes worked on fixed probes but did not improve the live Rapfi mcts16 smoke score. The next experiment should continue teacher dataset expansion from live smoke failures, especially earlier game2 positions now appearing before the old ply15/ply17 disagreement, then repeat the policy-first gate before any value tuning.
