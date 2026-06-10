#!/bin/sh
set -eu

ROOT="/Users/jing1fan/Documents/Codex/2026-06-09/you-are-working-in-the-neural/neural-gomoku"
BENCH="/Users/jing1fan/gomoku_public_benchmark"
CLI="$BENCH/c-gomoku-cli-main/src/c-gomoku-cli"
OUT_DIR="$ROOT/eval_logs/integration_eval"

stage="${1:-mcts16}"
case "$stage" in
  mcts16)
    neural="$BENCH/run_neural_candidate_h_value_mcts16_debug.sh"
    stdout_log="$OUT_DIR/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.stdout.log"
    engine_log="$OUT_DIR/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log"
    ;;
  mcts32)
    neural="$BENCH/run_neural_candidate_h_value_mcts32_debug.sh"
    stdout_log="$OUT_DIR/candidate_h_mcts32_vs_rapfi_depth1_15x15_smoke.stdout.log"
    engine_log="$OUT_DIR/candidate_h_mcts32_vs_rapfi_depth1_15x15_smoke.engine_io.log"
    ;;
  *)
    echo "usage: $0 [mcts16|mcts32]" >&2
    exit 2
    ;;
esac

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

"$CLI" \
  -engine name=neural cmd="$neural" tc=60/5 tolerance=3000 \
  -engine name=rapfi_fast cmd="$BENCH/run_rapfi.sh" depth=1 tc=1/1 maxmemory=367001600 tolerance=3000 \
  -rule 0 -boardsize 15 -games 2 -rounds 1 -drawafter 225 -debug \
  > "$stdout_log" 2>&1

cp c-gomoku-cli.1.log "$engine_log"
