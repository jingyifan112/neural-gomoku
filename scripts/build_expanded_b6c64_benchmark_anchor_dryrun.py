#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter
from pathlib import Path


LOCAL_RUNS = Path("analysis/public_benchmark_eval/local_runs")
AFTER_PREFIX_TXT = Path(
    "analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/tactical_mid_run_prefix.txt"
)
BEFORE_PREFIX_TXT = Path(
    "analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_preflight/before_tactical_mid_anchor_source_prefix.txt"
)
OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun")
OUT_JSON = OUT_DIR / "benchmark_anchor_source.json"
OUT_CSV = OUT_DIR / "benchmark_anchor_manifest.csv"
OUT_SUMMARY = OUT_DIR / "benchmark_anchor_dryrun_summary.json"
OUT_MD = OUT_DIR / "benchmark_anchor_dryrun_report.md"

SCORE_RE = re.compile(
    r"Score of (?P<engine>.+?) vs (?P<opponent>.+?): "
    r"(?P<wins>\d+) - (?P<losses>\d+) - (?P<draws>\d+)\s+"
    r"\[(?P<rate>[0-9.]+)\]\s+(?P<games>\d+)"
)

FINISHED_RE = re.compile(r"Finished game (\d+) \(([^)]+)\): ([^\s]+) \{(.+)\}")


def split_sgf_trees(text: str) -> list[str]:
    trees = []
    start = None
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                trees.append(text[start : i + 1])
                start = None
    return trees


def sgf_coord_to_xy(coord: str):
    if not coord or len(coord) < 2:
        return None
    return ord(coord[0].lower()) - ord("a"), ord(coord[1].lower()) - ord("a")


def parse_sgf_moves(tree: str):
    moves = []
    for color, coord in re.findall(r";\s*([BW])\[([A-Za-z]{2})\]", tree):
        xy = sgf_coord_to_xy(coord)
        if xy is not None:
            moves.append((color, xy[0], xy[1]))
    return moves


def read_score(log_path: Path) -> dict:
    matches = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SCORE_RE.search(line)
        if m:
            d = m.groupdict()
            matches.append(
                {
                    "engine": d["engine"],
                    "opponent": d["opponent"],
                    "wins": int(d["wins"]),
                    "losses": int(d["losses"]),
                    "draws": int(d["draws"]),
                    "rate": float(d["rate"]),
                    "games": int(d["games"]),
                    "score": int(d["wins"]) + 0.5 * int(d["draws"]),
                    "log": str(log_path),
                    "prefix": str(log_path)[:-4],
                }
            )
    if not matches:
        raise RuntimeError(f"no score lines found in {log_path}")
    return matches[-1]


def parse_log_rows(log_path: Path, neural_name: str) -> dict[int, dict]:
    rows = {}
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = FINISHED_RE.search(line)
        if not m:
            continue
        game = int(m.group(1))
        pairing = m.group(2)
        raw_result = m.group(3)
        reason = m.group(4)
        left, right = [x.strip() for x in pairing.split(" vs ")]
        if neural_name not in {left, right}:
            continue

        neural_is_left = left == neural_name
        neural_color = "B" if neural_is_left else "W"

        if raw_result == "1/2-1/2":
            neural_result = "D"
        elif raw_result == "1-0":
            neural_result = "W" if neural_is_left else "L"
        elif raw_result == "0-1":
            neural_result = "W" if not neural_is_left else "L"
        else:
            neural_result = "?"

        rows[game] = {
            "game": game,
            "pairing": pairing,
            "raw_result": raw_result,
            "reason": reason,
            "neural_color": neural_color,
            "neural_result": neural_result,
        }
    return rows


def board_rows_from_state(state: dict[tuple[int, int], str]) -> list[str]:
    rows = []
    for y in range(15):
        chars = []
        for x in range(15):
            color = state.get((x, y))
            if color == "B":
                chars.append("X")
            elif color == "W":
                chars.append("O")
            else:
                chars.append(".")
        rows.append("".join(chars))
    return rows


def select_neural_anchor_indices(moves, neural_color: str, max_per_game: int = 8) -> list[int]:
    neural_indices = [i for i, (c, _, _) in enumerate(moves) if c == neural_color]
    if len(neural_indices) <= max_per_game:
        return neural_indices
    # Use later positions because tactical_mid failures usually emerge in middle/endgame.
    return neural_indices[-max_per_game:]


def build_anchors_for_run(prefix: Path, run_label: str, max_per_game: int = 8) -> tuple[dict, list[dict]]:
    log_path = Path(str(prefix) + ".log")
    sgf_path = Path(str(prefix) + ".sgf")
    score = read_score(log_path)
    neural_name = score["engine"]
    log_rows = parse_log_rows(log_path, neural_name)
    sgf_trees = split_sgf_trees(sgf_path.read_text(encoding="utf-8", errors="replace"))

    anchors = []
    result_counts = Counter()

    for game in sorted(log_rows):
        if game - 1 >= len(sgf_trees):
            continue
        info = log_rows[game]
        result_counts[info["neural_result"]] += 1

        moves = parse_sgf_moves(sgf_trees[game - 1])
        chosen_indices = set(select_neural_anchor_indices(moves, info["neural_color"], max_per_game=max_per_game))

        state = {}
        for ply_index, (color, x, y) in enumerate(moves):
            if ply_index in chosen_indices:
                anchor_id = f"{run_label}_g{game:02d}_ply{ply_index:03d}_{color}_{x}_{y}"
                anchors.append(
                    {
                        "anchor_id": anchor_id,
                        "run_label": run_label,
                        "source_prefix": str(prefix),
                        "source_log": str(log_path),
                        "source_sgf": str(sgf_path),
                        "game": game,
                        "neural_name": neural_name,
                        "neural_color": info["neural_color"],
                        "neural_result": info["neural_result"],
                        "reason": info["reason"],
                        "ply_before_move": ply_index,
                        "side_to_move": "black" if color == "B" else "white",
                        "move_played_xy": [x, y],
                        "move_played_rc": [y, x],
                        "role": "public_tactical_mid_kl_anchor",
                        "anchor_policy": "reference_model_kl_anchor",
                        "board_rows": board_rows_from_state(state),
                    }
                )
            state[(x, y)] = color

    run_summary = {
        "run_label": run_label,
        "prefix": str(prefix),
        "log": str(log_path),
        "sgf": str(sgf_path),
        "engine": score["engine"],
        "opponent": score["opponent"],
        "games": score["games"],
        "wins": score["wins"],
        "losses": score["losses"],
        "draws": score["draws"],
        "score": score["score"],
        "score_rate": score["rate"],
        "result_counts_from_games": dict(result_counts),
        "anchors": len(anchors),
        "max_anchors_per_game": max_per_game,
    }
    return run_summary, anchors


def find_before_prefix() -> Path:
    if not BEFORE_PREFIX_TXT.exists():
        raise RuntimeError(f"missing before prefix file: {BEFORE_PREFIX_TXT}")
    prefix = Path(BEFORE_PREFIX_TXT.read_text(encoding="utf-8").strip())
    if not Path(str(prefix) + ".log").exists():
        raise RuntimeError(f"missing before log for prefix: {prefix}")
    if not Path(str(prefix) + ".sgf").exists():
        raise RuntimeError(f"missing before sgf for prefix: {prefix}")
    return prefix


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not AFTER_PREFIX_TXT.exists():
        raise RuntimeError(f"missing after prefix file: {AFTER_PREFIX_TXT}")
    after_prefix = Path(AFTER_PREFIX_TXT.read_text(encoding="utf-8").strip())
    before_prefix = find_before_prefix()

    before_summary, before_anchors = build_anchors_for_run(before_prefix, "before_neural_current_best_mcts16")
    after_summary, after_anchors = build_anchors_for_run(after_prefix, "after_expanded_b6c64_mcts16")

    all_anchors = before_anchors + after_anchors

    # Training usage policy:
    # - before anchors are candidate training KL anchors because they represent the old public benchmark behavior to preserve.
    # - after anchors are regression diagnostic anchors, not CE targets.
    for a in before_anchors:
        a["recommended_use"] = "train_kl_anchor_preserve_before_public_benchmark"
    for a in after_anchors:
        a["recommended_use"] = "diagnostic_regression_anchor_after_candidate"

    summary = {
        "decision": "BENCHMARK_ANCHOR_DRYRUN_READY",
        "not_training": True,
        "not_checkpoint": True,
        "not_promotion": True,
        "benchmark": "gomocup2026_freestyle15_public_openings",
        "opponent": "tactical_mid",
        "before_run": before_summary,
        "after_run": after_summary,
        "anchor_counts": {
            "before_public_kl_anchors": len(before_anchors),
            "after_regression_diagnostic_anchors": len(after_anchors),
            "total": len(all_anchors),
        },
        "recommended_next_step": {
            "name": "benchmark_preserving_training_adapter",
            "description": (
                "Create a trainer adapter that applies CE to teacher-divergence train rows "
                "and KL preservation to before-model public tactical_mid anchors plus protected/tail rows."
            ),
            "local_no_regression_gate": "next public tactical_mid score must be >= current local b6c64 baseline 2.0/24",
            "archived_current_best_aspirational_gate": "archived current-best tactical_mid was 7.0/24; this remains aspirational but is not reproduced by the current local b6c64 runner",
        },
    }

    OUT_JSON.write_text(json.dumps({"summary": summary, "anchors": all_anchors}, indent=2) + "\n", encoding="utf-8")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "anchor_id",
        "run_label",
        "recommended_use",
        "game",
        "neural_name",
        "neural_color",
        "neural_result",
        "ply_before_move",
        "side_to_move",
        "move_played_xy",
        "move_played_rc",
        "role",
        "anchor_policy",
        "reason",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for a in all_anchors:
            row = {k: a.get(k, "") for k in fieldnames}
            row["move_played_xy"] = ",".join(map(str, a["move_played_xy"]))
            row["move_played_rc"] = ",".join(map(str, a["move_played_rc"]))
            writer.writerow(row)

    lines = []
    lines.append("# Expanded b6c64 benchmark anchor dry-run")
    lines.append("")
    lines.append("- decision: `BENCHMARK_ANCHOR_DRYRUN_READY`")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no promotion/current_best overwrite")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Build a public benchmark anchor plan before any benchmark-preserving repair training. "
        "The goal is to preserve the current local b6c64 tactical_mid behavior while applying teacher-divergence repair. The archived 7.0/24 current-best score is tracked separately because the current local runner does not reproduce it."
    )
    lines.append("")
    lines.append("## Runs")
    lines.append("")
    lines.append("| run | engine | W | L | D | score | score rate | anchors |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for s in [before_summary, after_summary]:
        lines.append(
            f"| `{s['run_label']}` | `{s['engine']}` | {s['wins']} | {s['losses']} | {s['draws']} | "
            f"{s['score']:.1f}/{s['games']} | {s['score_rate']:.3f} | {s['anchors']} |"
        )
    lines.append("")
    lines.append("## Anchor counts")
    lines.append("")
    lines.append("| anchor group | count | recommended use |")
    lines.append("|---|---:|---|")
    lines.append(
        f"| before public tactical_mid anchors | {len(before_anchors)} | KL preserve old public benchmark behavior |"
    )
    lines.append(
        f"| after candidate regression anchors | {len(after_anchors)} | diagnostic only; do not use as CE target |"
    )
    lines.append("")
    lines.append("## Next training policy")
    lines.append("")
    lines.append("- CE: only teacher-divergence train rows.")
    lines.append("- KL anchor: before-model public tactical_mid anchors.")
    lines.append("- KL guard: protected/top10 and tail rows.")
    lines.append("- current-local public benchmark no-regression gate: `>= 2.0/24` on tactical_mid.")
    lines.append("- archived-current-best aspirational target: recover toward `>= 7.0/24` on tactical_mid.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- source JSON: `{OUT_JSON}`")
    lines.append(f"- manifest CSV: `{OUT_CSV}`")
    lines.append(f"- summary JSON: `{OUT_SUMMARY}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", summary["decision"])
    print("before_prefix:", before_prefix)
    print("after_prefix:", after_prefix)
    print("before_score:", before_summary["score"], "anchors:", len(before_anchors))
    print("after_score:", after_summary["score"], "anchors:", len(after_anchors))
    print("total_anchors:", len(all_anchors))
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_CSV)
    print("wrote:", OUT_SUMMARY)
    print("wrote:", OUT_MD)


if __name__ == "__main__":
    main()
