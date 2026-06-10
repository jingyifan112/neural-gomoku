#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCH = Path("/Users/jing1fan/gomoku_public_benchmark")
DEFAULT_CLI = BENCH / "c-gomoku-cli-main/src/c-gomoku-cli"
DEFAULT_RAPFI = BENCH / "run_rapfi.sh"
DEFAULT_WEIGHTS = Path("/Users/jing1fan/neural-gomoku/weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin")
DEFAULT_PBRAIN = Path("/Users/jing1fan/neural-gomoku/c_inference/pbrain-neural-gomoku")
DEFAULT_OPENINGS = ROOT / "analysis/integration_eval/15x15_corpus_openings_offset.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a configurable 15x15 baseline-vs-Rapfi corpus match with full stdout and engine I/O logs."
    )
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--mcts-sims", type=int, default=16)
    parser.add_argument("--move-mode", default="mcts_safe")
    parser.add_argument("--rapfi-depth", type=int, default=1)
    parser.add_argument("--rapfi-tc", default="1/1")
    parser.add_argument("--neural-tc", default="60/5")
    parser.add_argument("--tolerance-ms", type=int, default=3000)
    parser.add_argument("--drawafter", type=int, default=225)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260610)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "eval_logs/integration_eval/15x15_failure_corpus")
    parser.add_argument("--run-name", default="baseline_mcts16_vs_rapfi_depth1")
    parser.add_argument("--cli", type=Path, default=DEFAULT_CLI)
    parser.add_argument("--rapfi-command", type=Path, default=DEFAULT_RAPFI)
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--pbrain", type=Path, default=DEFAULT_PBRAIN)
    parser.add_argument(
        "--neural-command",
        default="",
        help="Optional existing Gomocup engine wrapper. If omitted, a wrapper is generated from --weights/--pbrain.",
    )
    parser.add_argument("--openings-file", type=Path, default=DEFAULT_OPENINGS)
    parser.add_argument("--openings-order", choices=["random", "sequential"], default="random")
    parser.add_argument("--no-openings", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def write_neural_wrapper(args: argparse.Namespace) -> Path:
    wrapper = args.output_dir / f"{args.run_name}.neural.sh"
    wrapper.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                "set -eu",
                f"export NEURAL_GOMOKU_WEIGHTS={shlex.quote(str(args.weights))}",
                f"export NEURAL_GOMOKU_MCTS_SIMS={args.mcts_sims}",
                f"export NEURAL_GOMOKU_MOVE_MODE={shlex.quote(args.move_mode)}",
                "export NEURAL_GOMOKU_DEBUG_DECISION=1",
                f"exec {shlex.quote(str(args.pbrain))}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    return wrapper


def build_command(args: argparse.Namespace, neural_command: str) -> list[str]:
    command = [
        str(args.cli),
        "-engine",
        f"name=neural_baseline_mcts{args.mcts_sims}",
        f"cmd={neural_command}",
        f"tc={args.neural_tc}",
        f"tolerance={args.tolerance_ms}",
        "-engine",
        "name=rapfi_fast",
        f"cmd={args.rapfi_command}",
        f"depth={args.rapfi_depth}",
        f"tc={args.rapfi_tc}",
        "maxmemory=367001600",
        f"tolerance={args.tolerance_ms}",
        "-rule",
        "0",
        "-boardsize",
        "15",
        "-games",
        str(args.games),
        "-rounds",
        str(args.rounds),
        "-drawafter",
        str(args.drawafter),
        "-concurrency",
        str(args.concurrency),
        "-debug",
    ]
    if not args.no_openings:
        if args.openings_file.exists():
            command.extend(
                [
                    "-openings",
                    f"file={args.openings_file}",
                    "type=offset",
                    f"order={args.openings_order}",
                    f"srand={args.seed}",
                    "-repeat",
                    "-transform",
                ]
            )
        else:
            command.extend(["# openings file missing; deterministic start only"])
    return command


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    neural_command = args.neural_command or str(write_neural_wrapper(args))
    command = build_command(args, neural_command)
    stdout_log = args.output_dir / f"{args.run_name}.stdout.log"
    engine_log = args.output_dir / f"{args.run_name}.engine_io.log"
    command_log = args.output_dir / f"{args.run_name}.command.txt"
    command_log.write_text(" ".join(shlex.quote(part) for part in command) + "\n", encoding="utf-8")

    if args.dry_run:
        print(command_log.read_text(encoding="utf-8"), end="")
        print(f"stdout log: {stdout_log}")
        print(f"engine I/O log: {engine_log}")
        return 0

    runnable_command = [part for part in command if not part.startswith("# ")]
    with stdout_log.open("w", encoding="utf-8") as handle:
        subprocess.run(runnable_command, cwd=args.output_dir, stdout=handle, stderr=subprocess.STDOUT, check=True)

    cli_log = args.output_dir / "c-gomoku-cli.1.log"
    if cli_log.exists():
        engine_log.write_text(cli_log.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    else:
        raise FileNotFoundError(f"expected c-gomoku-cli engine log at {cli_log}")

    print(f"wrote {stdout_log}")
    print(f"wrote {engine_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
