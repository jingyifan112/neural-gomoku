#!/bin/sh
set -eu

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCH_DIR="${GOMOKU_PUBLIC_BENCH_DIR:-$HOME/gomoku_public_benchmark}"
CLI_DIR="${C_GOMOKU_CLI_DIR:-$BENCH_DIR/c-gomoku-cli-main/src}"

ENGINE_BIN="${NEURAL_ENGINE_BIN:-$REPO_DIR/c_inference/pbrain-neural-gomoku}"
WEIGHTS="${NEURAL_GOMOKU_WEIGHTS:-$REPO_DIR/weights/15x15_current_best_weights.bin}"
OPENINGS="${GOMOKU_OPENINGS:-$REPO_DIR/analysis/public_benchmark_eval/gomocup2026_freestyle15_openings.txt}"

SIMS="${NEURAL_GOMOKU_MCTS_SIMS:-16}"
BASELINE="${1:-tactical_mid}"
GAMES="${GAMES:-24}"

OUT_DIR="$REPO_DIR/analysis/public_benchmark_eval/local_runs"
mkdir -p "$OUT_DIR"

case "$BASELINE" in
  random)
    BASELINE_NAME="random"
    BASELINE_CMD="$BENCH_DIR/run_random.sh"
    BASELINE_TC="10/2"
    ;;
  tactical_lite)
    BASELINE_NAME="tactical_lite"
    BASELINE_CMD="$BENCH_DIR/run_tactical_lite.sh"
    BASELINE_TC="10/2"
    ;;
  tactical_mid)
    BASELINE_NAME="tactical_mid"
    BASELINE_CMD="$BENCH_DIR/run_tactical_mid.sh"
    BASELINE_TC="10/2"
    ;;
  tactical_plus)
    BASELINE_NAME="tactical_plus"
    BASELINE_CMD="$BENCH_DIR/run_tactical_plus.sh"
    BASELINE_TC="10/2"
    ;;
  rapfi_fast)
    BASELINE_NAME="rapfi_fast"
    BASELINE_CMD="$BENCH_DIR/run_rapfi.sh"
    BASELINE_TC="1/1 depth=1"
    ;;
  *)
    echo "unknown baseline: $BASELINE" >&2
    echo "valid: random tactical_lite tactical_mid tactical_plus rapfi_fast" >&2
    exit 2
    ;;
esac

RUN_NEURAL="$OUT_DIR/run_neural_current_best_mcts${SIMS}.sh"
cat > "$RUN_NEURAL" <<RUNEOF
#!/bin/sh
export NEURAL_GOMOKU_WEIGHTS="$WEIGHTS"
export NEURAL_GOMOKU_MCTS_SIMS="$SIMS"
export NEURAL_GOMOKU_MOVE_MODE="mcts_safe"
exec "$ENGINE_BIN"
RUNEOF
chmod +x "$RUN_NEURAL"

STAMP="$(date +%Y%m%d_%H%M%S)"
PREFIX="$OUT_DIR/neural_mcts${SIMS}_vs_${BASELINE_NAME}_${STAMP}"

echo "repo=$REPO_DIR"
echo "cli=$CLI_DIR/c-gomoku-cli"
echo "weights=$WEIGHTS"
echo "openings=$OPENINGS"
echo "baseline=$BASELINE_NAME"
echo "games=$GAMES"
echo "output_prefix=$PREFIX"

cd "$CLI_DIR"

./c-gomoku-cli \
  -engine name="neural_current_best_mcts${SIMS}" cmd="$RUN_NEURAL" tc=60/5 \
  -engine name="$BASELINE_NAME" cmd="$BASELINE_CMD" tc=$BASELINE_TC \
  -rule 0 \
  -boardsize 15 \
  -games "$GAMES" \
  -drawafter 225 \
  -repeat \
  -openings file="$OPENINGS" order=sequential \
  -pgn "$PREFIX.pgn" \
  -sgf "$PREFIX.sgf" \
  -msg "$PREFIX.msg" \
  2>&1 | tee "$PREFIX.log"

echo
echo "=== final score lines ==="
grep "Score of" "$PREFIX.log" | tail -5 || true
