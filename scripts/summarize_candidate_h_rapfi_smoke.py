#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "eval_logs" / "integration_eval"
ANALYSIS_DIR = ROOT / "analysis" / "integration_eval"
STDOUT_LOG = LOG_DIR / "candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.stdout.log"
ENGINE_LOG = LOG_DIR / "candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log"
CSV_OUT = ANALYSIS_DIR / "candidate_h_rapfi_smoke_summary.csv"
REPORT_OUT = ANALYSIS_DIR / "candidate_h_rapfi_smoke_report.md"

DECISION_RE = re.compile(
    r"move_count=(?P<ply>\d+).*?final=\(x=(?P<x>\d+),y=(?P<y>\d+),"
)
FINISHED_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>[^ ]+) vs (?P<white>[^)]+)\): (?P<result>\d+-\d+) \{(?P<reason>[^}]+)\}"
)
SCORE_RE = re.compile(r"Score of neural vs rapfi_fast: (?P<w>\d+) - (?P<l>\d+) - (?P<d>\d+)")


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def parse_stdout(text: str) -> tuple[list[dict[str, str]], str]:
    games: list[dict[str, str]] = []
    for match in FINISHED_RE.finditer(text):
        raw_result = match.group("result")
        if match.group("black") == "neural":
            neural_result = raw_result
        else:
            black_score, white_score = raw_result.split("-")
            neural_result = f"{white_score}-{black_score}"
        games.append(
            {
                "game": match.group("game"),
                "result": neural_result,
                "raw_result": raw_result,
                "black": match.group("black"),
                "white": match.group("white"),
                "reason": match.group("reason"),
            }
        )
    score = "unknown"
    score_match = None
    for score_match in SCORE_RE.finditer(text):
        pass
    if score_match:
        score = f"{score_match.group('w')}-{score_match.group('l')}-{score_match.group('d')}"
    return games, score


def parse_game2_decisions(text: str) -> dict[int, str]:
    in_game2 = False
    moves: dict[int, str] = {}
    for line in text.splitlines():
        if "Started game 2" in line:
            in_game2 = True
        elif "Finished game 2" in line:
            in_game2 = False
        if not in_game2 or "_DECISION" not in line:
            continue
        match = DECISION_RE.search(line)
        if match:
            moves[int(match.group("ply"))] = f"{match.group('x')},{match.group('y')}"
    return moves


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    stdout_text = read(STDOUT_LOG)
    engine_text = read(ENGINE_LOG)
    games, score = parse_stdout(stdout_text)
    game2_moves = parse_game2_decisions(stdout_text)

    rows = [
        {
            "candidate": "Candidate D baseline",
            "stage": "mcts16",
            "status": "baseline",
            "score_neural_w_l_d": "0-2-0",
            "game1_result": "0-1",
            "game2_result": "0-1",
            "game2_ply13_move": "5,8",
            "game2_ply15_move": "7,10",
            "game2_ply17_move": "9,10",
            "game2_ply15_teacher_followed": "no",
            "game2_ply17_teacher_followed": "no",
            "notes": "Prior Candidate D mcts16 smoke baseline.",
        },
        {
            "candidate": "Candidate H",
            "stage": "mcts16",
            "status": "run",
            "score_neural_w_l_d": score,
            "game1_result": games[0]["result"] if len(games) > 0 else "unknown",
            "game2_result": games[1]["result"] if len(games) > 1 else "unknown",
            "game2_ply13_move": game2_moves.get(13, "missing"),
            "game2_ply15_move": game2_moves.get(15, "missing"),
            "game2_ply17_move": game2_moves.get(17, "missing"),
            "game2_ply15_teacher_followed": "no",
            "game2_ply17_teacher_followed": "no",
            "notes": "No score improvement over Candidate D; game2 line diverged before the fixed Candidate D teacher-disagreement board.",
        },
        {
            "candidate": "Candidate H",
            "stage": "mcts32",
            "status": "skipped",
            "score_neural_w_l_d": "not_run",
            "game1_result": "not_run",
            "game2_result": "not_run",
            "game2_ply13_move": "not_run",
            "game2_ply15_move": "not_run",
            "game2_ply17_move": "not_run",
            "game2_ply15_teacher_followed": "not_run",
            "game2_ply17_teacher_followed": "not_run",
            "notes": "Stage 2 gate required mcts16 improvement over Candidate D; Candidate H stayed 0-2.",
        },
    ]

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Candidate H Rapfi Smoke Report",
        "",
        "## Setup",
        "",
        "- Candidate H C weights: `weights/15x15_candidate_h_value_ranking_weights.bin`",
        "- Candidate H manifest: `weights/15x15_candidate_h_value_ranking_manifest.json`",
        "- Wrapper scripts:",
        "  - `/Users/jing1fan/gomoku_public_benchmark/run_neural_candidate_h_value_mcts16_debug.sh`",
        "  - `/Users/jing1fan/gomoku_public_benchmark/run_neural_candidate_h_value_mcts32_debug.sh`",
        "- Match settings: board 15x15, rule 0, 2 games, Rapfi depth 1, Rapfi `tc=1/1`, neural `tc=60/5`, `drawafter=225`, debug enabled.",
        "- No current_best weights were overwritten.",
        "",
        "## Stage Results",
        "",
        "| Candidate | Stage | Status | Score | Game 1 | Game 2 |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        report.append(
            f"| {row['candidate']} | {row['stage']} | {row['status']} | {row['score_neural_w_l_d']} | {row['game1_result']} | {row['game2_result']} |"
        )
    report.extend(
        [
            "",
            "Candidate H mcts16 did not improve over the Candidate D baseline (`0-2`), so the required Stage 2 mcts32 smoke was skipped.",
            "",
            "## Game 2 Decision Trace",
            "",
            "| Candidate | ply13 | ply15 | ply17 | ply15 teacher 7,9? | ply17 teacher 9,9? |",
            "|---|---:|---:|---:|---|---|",
            "| Candidate D baseline mcts16 | 5,8 | 7,10 | 9,10 | no | no |",
            f"| Candidate H mcts16 | {game2_moves.get(13, 'missing')} | {game2_moves.get(15, 'missing')} | {game2_moves.get(17, 'missing')} | no | no |",
            "",
            f"First game2 divergence from the Candidate D mcts16 baseline is ply13: Candidate D played `5,8`, while Candidate H played `{game2_moves.get(13, 'missing')}`.",
            "",
            "Important nuance: the Candidate H smoke line diverged from the Candidate D failure line before the original teacher-disagreement board. Therefore the fixed-position C probes remain valid, but the live mcts16 match did not exercise the exact ply15/ply17 board states where Candidate H selected the teacher moves in C verification.",
            "",
            "## Logs",
            "",
            "- Stage 1 stdout: `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.stdout.log`",
            "- Stage 1 engine I/O: `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log`",
            "- Misconfigured timing dry-run engine I/O, excluded from gate: `eval_logs/integration_eval/candidate_h_mcts16_misconfigured_tc_engine_io.log`",
            "",
            "## Prior Gates",
            "",
            "- Python-vs-C parity passed on ply15, ply17, and repair anchor.",
            "- C tactical benchmark passed 7/7 for direct, policy+safety, mcts_raw, and mcts+safety.",
            "- C probes selected teacher moves at the fixed ply15 and ply17 disagreement positions; repair anchor remained rank 2.",
            "- `pytest -q` previously passed: 13 tests.",
            "",
            "## Recommendation",
            "",
            "Reject Candidate H as a promotion candidate for now. The policy/value fixes worked on fixed probes but did not improve the live Rapfi mcts16 smoke score. The next experiment should continue teacher dataset expansion from live smoke failures, especially earlier game2 positions now appearing before the old ply15/ply17 disagreement, then repeat the policy-first gate before any value tuning.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")
    print(f"wrote {CSV_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
