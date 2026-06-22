from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


OUT_FIELDS = [
    "manifest_id",
    "status_before",
    "status_after",
    "bucket_after",
    "target_rc",
    "target_legal",
    "before_target_rank",
    "before_target_prob",
    "current_best_direct_rc",
    "current_best_direct_prob",
    "suppress_count",
    "primary_suppress_rc",
    "suppress_rcs",
    "suppress_source",
    "needs_suppress_build_after",
    "excluded",
    "exclude_reason",
    "notes",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build suppress candidates from current_best top policy list for probe-filled rows."
    )
    ap.add_argument(
        "--probe-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill_report.md"),
    )
    ap.add_argument("--max-suppress", type=int, default=5)
    ap.add_argument("--min-suppress", type=int, default=3)
    return ap.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def parse_rc(value: Any) -> tuple[int, int] | None:
    if value in (None, "", []):
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return parse_rc(json.loads(s))
        except Exception:
            pass
        nums = []
        cur = ""
        for ch in s:
            if ch.isdigit() or ch == "-":
                cur += ch
            elif cur:
                nums.append(int(cur))
                cur = ""
        if cur:
            nums.append(int(cur))
        if len(nums) >= 2:
            return (nums[0], nums[1])
    return None


def parse_rc_list(value: str) -> list[tuple[int, int]]:
    if not value:
        return []
    try:
        obj = json.loads(value)
    except Exception:
        return []
    out: list[tuple[int, int]] = []
    if isinstance(obj, list):
        for item in obj:
            rc = parse_rc(item)
            if rc is not None:
                out.append(rc)
    return out


def rc_json(rc: tuple[int, int] | None) -> str:
    if rc is None:
        return ""
    return json.dumps([rc[0], rc[1]])


def rcs_json(rcs: list[tuple[int, int]]) -> str:
    return json.dumps([[r, c] for r, c in rcs])


def build_suppress_candidates(row: dict[str, str], max_suppress: int) -> tuple[list[tuple[int, int]], str]:
    target = parse_rc(row.get("target_rc", ""))
    direct = parse_rc(row.get("current_best_direct_rc", ""))
    top_rcs = parse_rc_list(row.get("current_best_top_policy_rcs", ""))

    candidates: list[tuple[int, int]] = []

    def add(rc: tuple[int, int] | None) -> None:
        if rc is None:
            return
        if target is not None and rc == target:
            return
        if rc in candidates:
            return
        r, c = rc
        if not (0 <= r < 15 and 0 <= c < 15):
            return
        candidates.append(rc)

    add(direct)
    for rc in top_rcs:
        add(rc)
        if len(candidates) >= max_suppress:
            break

    source = "current_best_direct_plus_top_policy"
    if direct is not None and target is not None and direct == target:
        source = "top_policy_excluding_target_direct_equals_target"

    return candidates[:max_suppress], source


def status_for_row(row: dict[str, str], suppress_count: int, min_suppress: int) -> tuple[str, int, int, str, str]:
    target_legal = parse_bool(row.get("target_legal", ""))
    bucket = row.get("bucket_after", "")

    if not target_legal:
        return (
            "excluded_target_illegal",
            0,
            1,
            "target_illegal_or_unknown_rank",
            "excluded because target_legal is false",
        )

    if bucket == "unknown_rank":
        return (
            "excluded_unknown_rank",
            0,
            1,
            "unknown_rank",
            "excluded because bucket_after is unknown_rank",
        )

    if suppress_count < min_suppress:
        return (
            "needs_manual_review",
            1,
            0,
            "insufficient_suppress_candidates",
            f"only {suppress_count} suppress candidates built",
        )

    return (
        "ready_full_schema",
        0,
        0,
        "",
        "suppress candidates built",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in OUT_FIELDS})


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def write_report(path: Path, args: argparse.Namespace, input_rows: list[dict[str, str]], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    eligible = [r for r in rows if str(r["excluded"]) == "0"]
    excluded = [r for r in rows if str(r["excluded"]) == "1"]

    lines: list[str] = []
    lines += ["# Teacher-divergence suppress build fill report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-suppress-build-fill`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Build suppress candidates only.",
        "- Input is current_best probe fill output.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- probe_fill_csv: `{args.probe_fill_csv}`",
        f"- max_suppress: {args.max_suppress}",
        f"- min_suppress: {args.min_suppress}",
        f"- input rows: {len(input_rows)}",
        "",
    ]

    lines += ["## Summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| input rows | {len(input_rows)} |",
        f"| output rows | {len(rows)} |",
        f"| eligible non-excluded rows | {len(eligible)} |",
        f"| excluded rows | {len(excluded)} |",
        f"| ready_full_schema rows | {sum(1 for r in rows if r['status_after'] == 'ready_full_schema')} |",
        "",
    ]

    lines += ["## Status after suppress build", ""]
    lines += ["| status_after | rows |", "|---|---:|"]
    for key, n in count_by(rows, "status_after").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Bucket counts for ready rows", ""]
    lines += ["| bucket_after | rows |", "|---|---:|"]
    ready = [r for r in rows if r["status_after"] == "ready_full_schema"]
    for key, n in count_by(ready, "bucket_after").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Exclusion reasons", ""]
    lines += ["| exclude_reason | rows |", "|---|---:|"]
    for key, n in count_by(excluded, "exclude_reason").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Output rows", ""]
    lines += [
        "| manifest_id | status_after | bucket_after | target_rc | suppress_count | primary_suppress_rc | excluded | reason |",
        "|---|---|---|---|---:|---|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['manifest_id']} | {r['status_after']} | {r['bucket_after']} | "
            f"`{r['target_rc']}` | {r['suppress_count']} | `{r['primary_suppress_rc']}` | "
            f"{r['excluded']} | {r['exclude_reason']} |"
        )
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "This branch only fills suppress candidates from current_best top policy moves.",
        "",
        "Rows marked `ready_full_schema` are ready for diagnostics, not training. They should be merged into an updated manifest only after a separate manifest update branch.",
        "",
        "Protected top10 rows remain eval/protection only. Tail rank_gt50 rows remain diagnostic-only. The trainable rank 11-50 bucket is still far below the minimum sample count for training.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "No training.",
        "",
        "No checkpoint.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_rows = read_csv(args.probe_fill_csv)

    out_rows: list[dict[str, Any]] = []
    for row in input_rows:
        suppress_rcs, suppress_source = build_suppress_candidates(row, args.max_suppress)
        primary = suppress_rcs[0] if suppress_rcs else None

        status_after, needs_suppress_build_after, excluded, exclude_reason, notes = status_for_row(
            row=row,
            suppress_count=len(suppress_rcs),
            min_suppress=args.min_suppress,
        )

        out_rows.append(
            {
                "manifest_id": row["manifest_id"],
                "status_before": row["status_after"],
                "status_after": status_after,
                "bucket_after": row["bucket_after"],
                "target_rc": row["target_rc"],
                "target_legal": row["target_legal"],
                "before_target_rank": row["before_target_rank"],
                "before_target_prob": row["before_target_prob"],
                "current_best_direct_rc": row["current_best_direct_rc"],
                "current_best_direct_prob": row["current_best_direct_prob"],
                "suppress_count": len(suppress_rcs),
                "primary_suppress_rc": rc_json(primary),
                "suppress_rcs": rcs_json(suppress_rcs),
                "suppress_source": suppress_source,
                "needs_suppress_build_after": needs_suppress_build_after,
                "excluded": excluded,
                "exclude_reason": exclude_reason,
                "notes": notes,
            }
        )

    write_csv(args.out_csv, out_rows)
    write_report(args.out_report, args, input_rows, out_rows)

    print("input_rows:", len(input_rows))
    print("output_rows:", len(out_rows))
    print("status_after_counts:", json.dumps(count_by(out_rows, "status_after"), sort_keys=True))
    print("bucket_counts_ready:", json.dumps(count_by([r for r in out_rows if r["status_after"] == "ready_full_schema"], "bucket_after"), sort_keys=True))
    print("excluded_counts:", json.dumps(count_by([r for r in out_rows if str(r["excluded"]) == "1"], "exclude_reason"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
