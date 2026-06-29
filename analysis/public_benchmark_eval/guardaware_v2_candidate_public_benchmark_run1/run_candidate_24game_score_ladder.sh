#!/bin/sh
set -eu

CLI="/Users/jing1fan/gomoku_public_benchmark/c-gomoku-cli-main/src/c-gomoku-cli"
OPENINGS="/Users/jing1fan/gomoku_public_benchmark/gomocup2026_public_score/freestyle15_openings.txt"
OUT_DIR="/Users/jing1fan/neural-gomoku/analysis/public_benchmark_eval/guardaware_v2_candidate_public_benchmark_run1"

run_match() {
  label="$1"
  neural_name="$2"
  neural_cmd="$3"
  opponent_name="$4"
  opponent_cmd="$5"
  opponent_extra="$6"
  games="$7"

  log="$OUT_DIR/${label}.log"

  echo
  echo "=== RUN $label ==="
  echo "neural=$neural_name"
  echo "opponent=$opponent_name"
  echo "log=$log"

  if [ -n "$opponent_extra" ]; then
    "$CLI"       -engine name="$neural_name" cmd="$neural_cmd" tc=60/5       -engine name="$opponent_name" cmd="$opponent_cmd" tc=1/1 $opponent_extra       -rule 0       -boardsize 15       -games "$games"       -drawafter 225       -repeat       -openings file="$OPENINGS" order=sequential       2>&1 | tee "$log"
  else
    "$CLI"       -engine name="$neural_name" cmd="$neural_cmd" tc=60/5       -engine name="$opponent_name" cmd="$opponent_cmd" tc=60/5       -rule 0       -boardsize 15       -games "$games"       -drawafter 225       -repeat       -openings file="$OPENINGS" order=sequential       2>&1 | tee "$log"
  fi

  echo
  echo "=== SCORE $label ==="
  grep -E "Score of|Finished game" "$log" | tail -8 || true
}

run_match "candidate_mcts32_vs_random_24g"   "neural_guardaware_v2_mcts32" "/Users/jing1fan/gomoku_public_benchmark/run_neural_guardaware_v2_candidate_mcts32.sh"   "random" "/Users/jing1fan/gomoku_public_benchmark/run_random.sh" "" 24

run_match "candidate_mcts32_vs_tactical_lite_24g"   "neural_guardaware_v2_mcts32" "/Users/jing1fan/gomoku_public_benchmark/run_neural_guardaware_v2_candidate_mcts32.sh"   "tactical_lite" "/Users/jing1fan/gomoku_public_benchmark/run_tactical_lite.sh" "" 24

run_match "candidate_mcts16_vs_tactical_mid_24g"   "neural_guardaware_v2_mcts16" "/Users/jing1fan/gomoku_public_benchmark/run_neural_guardaware_v2_candidate_mcts16.sh"   "tactical_mid" "/Users/jing1fan/gomoku_public_benchmark/run_tactical_mid.sh" "" 24

run_match "candidate_mcts16_vs_tactical_plus_24g"   "neural_guardaware_v2_mcts16" "/Users/jing1fan/gomoku_public_benchmark/run_neural_guardaware_v2_candidate_mcts16.sh"   "tactical_plus" "/Users/jing1fan/gomoku_public_benchmark/run_tactical_plus.sh" "" 24

run_match "candidate_mcts32_vs_rapfi_fast_depth1_24g"   "neural_guardaware_v2_mcts32" "/Users/jing1fan/gomoku_public_benchmark/run_neural_guardaware_v2_candidate_mcts32.sh"   "rapfi_fast" "/Users/jing1fan/gomoku_public_benchmark/run_rapfi.sh" "depth=1" 24

echo
echo "=== all ladder runs complete ==="
