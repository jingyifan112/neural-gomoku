from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any


INTEREST_TERMS = [
    "teacher",
    "divergence",
    "corpus8",
    "failure",
    "rapfi",
    "rank_topk",
    "multisuppress",
    "scoregap",
    "snapshot",
    "candidate",
]

ROW_KEYS = [
    "samples",
    "rows",
    "data",
    "protected_eval_samples",
    "tail_eval_samples",
]

FIELD_GROUPS = {
    "board": ["board", "board_snapshot_before_decision"],
    "side": ["current_player", "side_to_move"],
    "target": ["target_rc", "target_xy", "teacher_move"],
    "rank": ["before_target_rank", "target_rank"],
    "prob": ["before_target_prob", "target_prob"],
    "suppress": ["suppress_rcs", "suppress_candidates", "suppress_rc", "primary_suppress_rc"],
    "teacher_eval": ["teacher_eval_before", "teacher_eval_kind", "numeric_gap_value", "numeric_gap_available"],
    "source_trace": ["case_id", "source", "game_number", "move_count"],
    "bucket": ["bucket", "suggested_bucket", "protected_objective_role", "label_type"],
}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Inventory tracked teacher-divergence candidate source files."
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_source_inventory_audit.csv"),
    )
    ap.add_argument(
        "--out-md",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_source_inventory_audit.md"),
    )
    return ap.parse_args()


def git_tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [Path(line.strip()) for line in proc.stdout.splitlines() if line.strip()]


def is_candidate(path: Path) -> bool:
    s = str(path)
    if not (
        s.startswith("analysis/")
        or s.startswith("eval_logs/")
        or s.startswith("scripts/")
    ):
        return False
    if path.suffix.lower() not in {".json", ".csv", ".md", ".log", ".txt", ".py"}:
        return False
    low = s.lower()
    return any(term in low for term in INTEREST_TERMS)


def load_json_rows(path: Path) -> tuple[str, int, dict[str, int], list[str], dict[str, int]]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "json_unreadable", 0, {}, [], {}

    sections: dict[str, int] = {}
    example_keys: list[str] = []
    field_hits = {name: 0 for name in FIELD_GROUPS}

    if isinstance(obj, list):
        rows = obj
        sections["top_level_list"] = len(rows)
    elif isinstance(obj, dict):
        rows = []
        for key in ROW_KEYS:
            value = obj.get(key)
            if isinstance(value, list):
                sections[key] = len(value)
                rows.extend(value)
    else:
        rows = []

    dict_rows = [r for r in rows if isinstance(r, dict)]
    if dict_rows:
        example_keys = sorted(dict_rows[0].keys())
        for row in dict_rows:
            for group, fields in FIELD_GROUPS.items():
                if any(field in row and row.get(field) not in (None, "", []) for field in fields):
                    field_hits[group] += 1

    return "json", len(dict_rows), sections, example_keys, field_hits


def load_csv_rows(path: Path) -> tuple[str, int, list[str], dict[str, int]]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fields = list(reader.fieldnames or [])
    except Exception:
        return "csv_unreadable", 0, [], {}

    field_hits = {name: 0 for name in FIELD_GROUPS}
    for row in rows:
        for group, candidates in FIELD_GROUPS.items():
            if any(field in row and row.get(field) not in (None, "", []) for field in candidates):
                field_hits[group] += 1

    return "csv", len(rows), fields, field_hits


def inspect_text(path: Path) -> tuple[str, int]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "text_unreadable", 0
    lines = text.splitlines()
    return "text", len(lines)


def inventory_file(path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": str(path),
        "suffix": path.suffix.lower(),
        "exists": int(path.exists()),
        "kind": "",
        "row_count": "",
        "line_count": "",
        "sections": "",
        "example_keys_or_fields": "",
    }

    for group in FIELD_GROUPS:
        row[f"{group}_rows"] = ""

    if not path.exists():
        row["kind"] = "missing"
        return row

    if path.suffix.lower() == ".json":
        kind, n, sections, keys, hits = load_json_rows(path)
        row["kind"] = kind
        row["row_count"] = n
        row["sections"] = json.dumps(sections, sort_keys=True)
        row["example_keys_or_fields"] = " ".join(keys[:80])
        for group, value in hits.items():
            row[f"{group}_rows"] = value
    elif path.suffix.lower() == ".csv":
        kind, n, fields, hits = load_csv_rows(path)
        row["kind"] = kind
        row["row_count"] = n
        row["example_keys_or_fields"] = " ".join(fields[:80])
        for group, value in hits.items():
            row[f"{group}_rows"] = value
    else:
        kind, line_count = inspect_text(path)
        row["kind"] = kind
        row["line_count"] = line_count

    return row


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "path",
        "suffix",
        "exists",
        "kind",
        "row_count",
        "line_count",
        "sections",
        "example_keys_or_fields",
    ] + [f"{group}_rows" for group in FIELD_GROUPS]

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in fields})


def write_md(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    json_rows = [r for r in rows if r["kind"] == "json"]
    csv_rows = [r for r in rows if r["kind"] == "csv"]
    text_rows = [r for r in rows if r["kind"] == "text"]

    usable_json_or_csv = [
        r for r in rows
        if r["kind"] in {"json", "csv"} and str(r.get("row_count", "")) not in {"", "0"}
    ]

    def int_or_zero(v: Any) -> int:
        try:
            return int(v)
        except Exception:
            return 0

    md: list[str] = []
    md += ["# Teacher-divergence source inventory audit", ""]
    md += ["## Branch", "", "`exp/15x15-teacher-divergence-source-inventory-audit`", ""]
    md += ["## Scope", ""]
    md += [
        "- Inventory/audit only.",
        "- Uses `git ls-files`, so it inventories tracked files only.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    md += ["## Summary", ""]
    md += ["| metric | value |", "|---|---:|"]
    md += [
        f"| candidate tracked files | {len(rows)} |",
        f"| json files | {len(json_rows)} |",
        f"| csv files | {len(csv_rows)} |",
        f"| text/report/script files | {len(text_rows)} |",
        f"| json/csv files with rows | {len(usable_json_or_csv)} |",
        f"| total parsed json/csv rows | {sum(int_or_zero(r.get('row_count')) for r in usable_json_or_csv)} |",
        "",
    ]

    md += ["## Field coverage across parsed JSON/CSV sources", ""]
    md += ["| field group | files with coverage | total covered rows |", "|---|---:|---:|"]
    for group in FIELD_GROUPS:
        key = f"{group}_rows"
        files = [r for r in usable_json_or_csv if int_or_zero(r.get(key)) > 0]
        total = sum(int_or_zero(r.get(key)) for r in usable_json_or_csv)
        md.append(f"| {group} | {len(files)} | {total} |")
    md.append("")

    md += ["## Parsed JSON/CSV source files", ""]
    md += [
        "| path | kind | rows | sections | board | side | target | rank | prob | suppress | teacher_eval | source_trace | bucket |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(usable_json_or_csv, key=lambda x: str(x["path"])):
        md.append(
            f"| `{r['path']}` | {r['kind']} | {r['row_count']} | `{r.get('sections', '')}` | "
            f"{r.get('board_rows', '')} | {r.get('side_rows', '')} | {r.get('target_rows', '')} | "
            f"{r.get('rank_rows', '')} | {r.get('prob_rows', '')} | {r.get('suppress_rows', '')} | "
            f"{r.get('teacher_eval_rows', '')} | {r.get('source_trace_rows', '')} | {r.get('bucket_rows', '')} |"
        )
    md.append("")

    md += ["## Candidate text/report/script files", ""]
    md += ["| path | kind | lines |", "|---|---|---:|"]
    for r in sorted(text_rows, key=lambda x: str(x["path"])):
        md.append(f"| `{r['path']}` | {r['kind']} | {r.get('line_count', '')} |")
    md.append("")

    md += ["## Interpretation", ""]
    md += [
        "This audit is a first inventory pass. It does not decide final training eligibility.",
        "",
        "The next step should inspect the parsed JSON/CSV sources with enough board, side, target, rank, suppress, teacher-eval, source-trace, and bucket coverage to decide which can feed an expanded teacher-divergence manifest.",
        "",
        "Untracked local artifacts are intentionally excluded from this report so the committed audit remains reproducible from the repository state.",
        "",
    ]

    md += ["## Recommended next step", ""]
    md += [
        "Open a manifest-design branch that selects concrete tracked sources from this inventory and defines deduplication keys.",
        "",
        "Suggested branch:",
        "",
        "`exp/15x15-teacher-divergence-expanded-manifest-design`",
        "",
    ]

    md += ["## Decision", ""]
    md += [
        "Audit only.",
        "",
        "No training, no checkpoint, no export, no public benchmark, no promotion.",
        "",
    ]

    path.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    args = parse_args()
    tracked = git_tracked_files()
    candidates = sorted([path for path in tracked if is_candidate(path)], key=str)
    rows = [inventory_file(path) for path in candidates]
    write_csv(args.out_csv, rows)
    write_md(args.out_md, rows)

    print("tracked_candidate_files:", len(rows))
    print("out_csv:", args.out_csv)
    print("out_md:", args.out_md)

    parsed = [r for r in rows if r["kind"] in {"json", "csv"} and str(r.get("row_count", "")) not in {"", "0"}]
    print("parsed_json_csv_with_rows:", len(parsed))
    print("total_rows:", sum(int(r["row_count"]) for r in parsed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
