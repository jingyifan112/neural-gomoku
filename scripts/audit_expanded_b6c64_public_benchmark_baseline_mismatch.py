#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_baseline_mismatch_audit")
OUT_JSON = OUT_DIR / "baseline_mismatch_audit.json"
OUT_MD = OUT_DIR / "baseline_mismatch_audit.md"

SCORE_LADDER = Path("analysis/public_benchmark_eval/gomocup2026_score_ladder_summary.csv")
BEFORE_PREFIX_TXT = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_preflight/before_tactical_mid_anchor_source_prefix.txt")
AFTER_PREFIX_TXT = Path("analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/tactical_mid_run_prefix.txt")
RUN_BEFORE = Path("analysis/public_benchmark_eval/local_runs/run_neural_current_best_mcts16.sh")
RUN_AFTER = Path("analysis/public_benchmark_eval/local_runs/run_neural_expanded_data_b6c64_mcts16.sh")

SCORE_RE = re.compile(
    r"Score of (?P<engine>.+?) vs (?P<opponent>.+?): "
    r"(?P<wins>\d+) - (?P<losses>\d+) - (?P<draws>\d+)\s+"
    r"\[(?P<rate>[0-9.]+)\]\s+(?P<games>\d+)"
)

def score_from_log(prefix: Path):
    log = Path(str(prefix) + ".log")
    matches = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = SCORE_RE.search(line)
        if m:
            d = m.groupdict()
            w = int(d["wins"])
            l = int(d["losses"])
            dr = int(d["draws"])
            games = int(d["games"])
            matches.append({
                "engine": d["engine"],
                "opponent": d["opponent"],
                "wins": w,
                "losses": l,
                "draws": dr,
                "games": games,
                "score": w + 0.5 * dr,
                "score_rate": float(d["rate"]),
                "prefix": str(prefix),
                "log": str(log),
            })
    if not matches:
        raise RuntimeError(f"no score line in {log}")
    return matches[-1]

def archived_score(engine: str, baseline: str):
    with SCORE_LADDER.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    matches = [r for r in rows if r.get("engine") == engine and r.get("baseline") == baseline]
    if not matches:
        return None
    r = matches[0]
    return {
        "engine": r.get("engine"),
        "opponent": r.get("baseline"),
        "wins": int(r.get("wins")),
        "losses": int(r.get("losses")),
        "draws": int(r.get("draws")),
        "games": int(r.get("games")),
        "score": float(r.get("score")),
        "score_rate": float(r.get("score_rate")),
        "source": str(SCORE_LADDER),
    }

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    before_prefix = Path(BEFORE_PREFIX_TXT.read_text(encoding="utf-8").strip())
    after_prefix = Path(AFTER_PREFIX_TXT.read_text(encoding="utf-8").strip())

    archived_before = archived_score("neural_current_best_mcts16", "tactical_mid")
    archived_strong = archived_score("rapfi_full", "tactical_mid")
    local_before = score_from_log(before_prefix)
    local_after = score_from_log(after_prefix)

    before_runner = RUN_BEFORE.read_text(encoding="utf-8") if RUN_BEFORE.exists() else ""
    after_runner = RUN_AFTER.read_text(encoding="utf-8") if RUN_AFTER.exists() else ""

    mismatch = archived_before is not None and archived_before["score"] != local_before["score"]

    decision = "BASELINE_MISMATCH_REQUIRES_RUNNER_AUDIT" if mismatch else "BASELINE_MATCHES_ARCHIVED_SCORE"

    summary = {
        "decision": decision,
        "not_training": True,
        "not_checkpoint": True,
        "not_promotion": True,
        "archived_before": archived_before,
        "local_before_rerun": local_before,
        "local_after_candidate": local_after,
        "archived_strong": archived_strong,
        "deltas": {
            "local_after_minus_local_before_score": local_after["score"] - local_before["score"],
            "local_after_minus_archived_before_score": None if archived_before is None else local_after["score"] - archived_before["score"],
            "local_before_minus_archived_before_score": None if archived_before is None else local_before["score"] - archived_before["score"],
        },
        "runner_paths": {
            "before_runner": str(RUN_BEFORE),
            "after_runner": str(RUN_AFTER),
        },
        "runner_contents": {
            "before_runner": before_runner,
            "after_runner": after_runner,
        },
        "interpretation": (
            "The current local before rerun did not reproduce the archived current-best tactical_mid score. "
            "Do not use the archived 7.0/24 threshold as if it came from the current local runner until the runner/weights mismatch is resolved."
            if mismatch else
            "The current local before rerun matches the archived score."
        ),
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Expanded b6c64 public benchmark baseline mismatch audit")
    lines.append("")
    lines.append(f"- decision: `{decision}`")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no promotion/current_best overwrite")
    lines.append("")
    lines.append("## Score comparison")
    lines.append("")
    lines.append("| source | engine | opponent | W | L | D | score | score rate |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    if archived_before:
        lines.append(
            f"| archived score ladder | `{archived_before['engine']}` | `{archived_before['opponent']}` | "
            f"{archived_before['wins']} | {archived_before['losses']} | {archived_before['draws']} | "
            f"{archived_before['score']:.1f}/{archived_before['games']} | {archived_before['score_rate']:.3f} |"
        )
    lines.append(
        f"| current local before rerun | `{local_before['engine']}` | `{local_before['opponent']}` | "
        f"{local_before['wins']} | {local_before['losses']} | {local_before['draws']} | "
        f"{local_before['score']:.1f}/{local_before['games']} | {local_before['score_rate']:.3f} |"
    )
    lines.append(
        f"| current local after candidate | `{local_after['engine']}` | `{local_after['opponent']}` | "
        f"{local_after['wins']} | {local_after['losses']} | {local_after['draws']} | "
        f"{local_after['score']:.1f}/{local_after['games']} | {local_after['score_rate']:.3f} |"
    )
    if archived_strong:
        lines.append(
            f"| archived strong reference | `{archived_strong['engine']}` | `{archived_strong['opponent']}` | "
            f"{archived_strong['wins']} | {archived_strong['losses']} | {archived_strong['draws']} | "
            f"{archived_strong['score']:.1f}/{archived_strong['games']} | {archived_strong['score_rate']:.3f} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(summary["interpretation"])
    lines.append("")
    lines.append("## Runner paths")
    lines.append("")
    lines.append(f"- before runner: `{RUN_BEFORE}`")
    lines.append(f"- after runner: `{RUN_AFTER}`")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Inspect the before runner weights/binary. If it points to the b6c64 capacity checkpoint rather than the archived current-best model, "
        "then the old 7.0/24 score is not an apples-to-apples local baseline for the current anchor dry-run."
    )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("archived_before:", archived_before)
    print("local_before:", local_before)
    print("local_after:", local_after)
    print("deltas:", summary["deltas"])
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_MD)

if __name__ == "__main__":
    main()
