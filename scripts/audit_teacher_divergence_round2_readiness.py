#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXPECTED_STATUS_AFTER = {
    "ready_full_schema": 133,
    "skipped_invalid": 51,
    "needs_rapfi_requery": 22,
    "needs_board_join": 41,
    "needs_current_best_probe": 0,
}

EXPECTED_READY_BUCKET_AFTER = {
    "protected_top10": 23,
    "trainable_rank_11_50": 44,
    "tail_rank_gt50": 66,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit round2 teacher-divergence manifest readiness after current_best probe and suppress fill."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_readiness_audit.md"),
    )
    parser.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_readiness_summary.csv"),
    )
    return parser.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def nondup(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [r for r in rows if is_blank(r.get("duplicate_of"))]


def ready_bucket(row: dict[str, str]) -> str:
    return (
        row.get("ready_bucket")
        or row.get("bucket")
        or row.get("bucket_after")
        or row.get("bucket_before")
        or "unknown_bucket"
    )


def source_key(row: dict[str, str]) -> str:
    return row.get("source_class") or row.get("primary_source_path") or "unknown_source"


def family_key(row: dict[str, str]) -> str:
    case_id = row.get("case_id", "")
    if "legacy_g" in case_id:
        return "legacy_game_family"
    if "safety" in case_id:
        return "safety_family"
    if "candidate" in case_id:
        return "candidate_family"
    if case_id:
        return case_id.split("_m")[0]
    src = row.get("primary_source_path", "")
    if src:
        return Path(src).stem
    return "unknown_family"


def has_rank_prob(row: dict[str, str]) -> bool:
    return not is_blank(row.get("before_target_rank")) and not is_blank(row.get("before_target_prob"))


def has_suppress(row: dict[str, str]) -> bool:
    return not is_blank(row.get("suppress_rc")) and not is_blank(row.get("suppress_prob"))


def count_by(rows: list[dict[str, str]], key_fn) -> Counter[str]:
    c: Counter[str] = Counter()
    for row in rows:
        c[str(key_fn(row))] += 1
    return c


def write_summary_csv(path: Path, summary_rows: list[dict[str, str]]) -> None:
    fields = ["group", "key", "rows", "ready_full_schema_rows", "trainable_candidate_rows", "protected_rows", "tail_diagnostic_rows", "missing_rank_prob_rows", "missing_suppress_rows"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)


def make_group_summary(group: str, key: str, rows: list[dict[str, str]]) -> dict[str, str]:
    ready_rows = [r for r in rows if r.get("status") == "ready_full_schema"]
    trainable = [r for r in ready_rows if ready_bucket(r) == "trainable_rank_11_50"]
    protected = [r for r in ready_rows if ready_bucket(r) == "protected_top10"]
    tail = [r for r in ready_rows if ready_bucket(r) == "tail_rank_gt50"]
    missing_rank = [r for r in ready_rows if not has_rank_prob(r)]
    missing_suppress = [r for r in ready_rows if not has_suppress(r)]

    return {
        "group": group,
        "key": key,
        "rows": str(len(rows)),
        "ready_full_schema_rows": str(len(ready_rows)),
        "trainable_candidate_rows": str(len(trainable)),
        "protected_rows": str(len(protected)),
        "tail_diagnostic_rows": str(len(tail)),
        "missing_rank_prob_rows": str(len(missing_rank)),
        "missing_suppress_rows": str(len(missing_suppress)),
    }


def append_counter_table(lines: list[str], title: str, counter: Counter[str]) -> None:
    lines.extend(["", title, "", "| key | rows |", "|---|---:|"])
    if not counter:
        lines.append("| none | 0 |")
        return
    for key, value in counter.most_common():
        lines.append(f"| {key} | {value} |")


def main() -> None:
    args = parse_args()

    _fields, rows = read_csv(args.manifest)
    nd = nondup(rows)

    status = Counter(r.get("status", "") for r in nd)
    ready_rows = [r for r in nd if r.get("status") == "ready_full_schema"]
    ready_bucket_counts = Counter(ready_bucket(r) for r in ready_rows)

    trainable_rows = [r for r in ready_rows if ready_bucket(r) == "trainable_rank_11_50"]
    protected_rows = [r for r in ready_rows if ready_bucket(r) == "protected_top10"]
    tail_rows = [r for r in ready_rows if ready_bucket(r) == "tail_rank_gt50"]

    round2_ready_rows = [
        r for r in ready_rows
        if r.get("round2_merge_action") == "probe_and_suppress_built"
        or r.get("round2_suppress_status_after") == "ready_full_schema"
    ]
    pre_round2_ready_rows = [
        r for r in ready_rows
        if r not in round2_ready_rows
    ]

    missing_rank_prob = [r for r in ready_rows if not has_rank_prob(r)]
    missing_suppress = [r for r in ready_rows if not has_suppress(r)]
    missing_suppress_round2 = [r for r in round2_ready_rows if not has_suppress(r)]
    missing_suppress_pre_round2 = [r for r in pre_round2_ready_rows if not has_suppress(r)]

    merge_action_counts = Counter(r.get("round2_merge_action", "") or "pre_round2_or_unchanged" for r in rows)
    ready_source_counts = count_by(ready_rows, source_key)
    trainable_source_counts = count_by(trainable_rows, source_key)
    trainable_family_counts = count_by(trainable_rows, family_key)
    protected_source_counts = count_by(protected_rows, source_key)
    tail_source_counts = count_by(tail_rows, source_key)

    for key, expected in EXPECTED_STATUS_AFTER.items():
        actual = status.get(key, 0)
        if actual != expected:
            raise RuntimeError(f"status count mismatch for {key}: expected {expected}, got {actual}")

    for key, expected in EXPECTED_READY_BUCKET_AFTER.items():
        actual = ready_bucket_counts.get(key, 0)
        if actual != expected:
            raise RuntimeError(f"ready bucket mismatch for {key}: expected {expected}, got {actual}")

    if len(rows) != 362:
        raise RuntimeError(f"expected 362 manifest rows, got {len(rows)}")
    if len(nd) != 247:
        raise RuntimeError(f"expected 247 non-duplicate rows, got {len(nd)}")
    if missing_rank_prob:
        raise RuntimeError(f"ready rows missing rank/prob: {len(missing_rank_prob)}")
    if missing_suppress_round2:
        raise RuntimeError(f"round2 ready rows missing suppress fields: {len(missing_suppress_round2)}")

    by_status: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    by_bucket: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    by_source: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    by_family: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

    for row in nd:
        by_status[row.get("status", "")].append(row)
        by_source[source_key(row)].append(row)
        by_family[family_key(row)].append(row)
        if row.get("status") == "ready_full_schema":
            by_bucket[ready_bucket(row)].append(row)

    summary_rows: list[dict[str, str]] = []
    for key, group_rows in sorted(by_status.items()):
        summary_rows.append(make_group_summary("status", key, group_rows))
    for key, group_rows in sorted(by_bucket.items()):
        summary_rows.append(make_group_summary("ready_bucket", key, group_rows))
    for key, group_rows in sorted(by_source.items()):
        summary_rows.append(make_group_summary("source", key, group_rows))
    for key, group_rows in sorted(by_family.items()):
        summary_rows.append(make_group_summary("family", key, group_rows))

    write_summary_csv(args.out_summary_csv, summary_rows)

    lines: list[str] = [
        "# Teacher-divergence round2 readiness audit",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-round2-readiness-audit`",
        "",
        "## Scope",
        "",
        "- Audits the manifest after current_best probe round2 and suppress build round2.",
        "- Does not build a training dataset.",
        "- Does not train.",
        "- Does not save a checkpoint.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Input",
        "",
        f"- manifest: `{args.manifest}`",
        "",
        "## Core counts",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| manifest rows | {len(rows)} |",
        f"| non-duplicate rows | {len(nd)} |",
        f"| ready_full_schema rows | {len(ready_rows)} |",
        f"| trainable candidate rows | {len(trainable_rows)} |",
        f"| protected top10 rows | {len(protected_rows)} |",
        f"| tail diagnostic rows | {len(tail_rows)} |",
        f"| ready rows missing rank/prob | {len(missing_rank_prob)} |",
        f"| ready rows missing suppress fields | {len(missing_suppress)} |",
        f"| round2 ready rows missing suppress fields | {len(missing_suppress_round2)} |",
        f"| pre-round2 ready rows missing suppress fields | {len(missing_suppress_pre_round2)} |",
        "",
        "## Readiness interpretation",
        "",
        "- `trainable_rank_11_50` rows are the only immediate candidates for a later dry-run dataset export.",
        "- `protected_top10` rows should remain protection/eval rows unless a later design deliberately includes them.",
        "- `tail_rank_gt50` rows should remain diagnostic-only for now because target visibility is too low.",
        "- `needs_rapfi_requery` and `needs_board_join` remain unresolved and are not included in readiness.",
        "",
        "## Non-duplicate status counts",
        "",
        "| status | rows |",
        "|---|---:|",
    ]

    for key, value in status.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Ready bucket counts",
        "",
        "| ready_bucket | rows | intended use |",
        "|---|---:|---|",
        f"| trainable_rank_11_50 | {ready_bucket_counts.get('trainable_rank_11_50', 0)} | dry-run export candidate |",
        f"| protected_top10 | {ready_bucket_counts.get('protected_top10', 0)} | protection/eval only |",
        f"| tail_rank_gt50 | {ready_bucket_counts.get('tail_rank_gt50', 0)} | diagnostic only |",
        "",
        "## Expected count checks",
        "",
        "| check | expected | actual |",
        "|---|---:|---:|",
    ])

    for key, expected in EXPECTED_STATUS_AFTER.items():
        lines.append(f"| status:{key} | {expected} | {status.get(key, 0)} |")
    for key, expected in EXPECTED_READY_BUCKET_AFTER.items():
        lines.append(f"| ready_bucket:{key} | {expected} | {ready_bucket_counts.get(key, 0)} |")

    append_counter_table(lines, "## Round2 merge action counts", merge_action_counts)
    append_counter_table(lines, "## Ready source counts", ready_source_counts)
    append_counter_table(lines, "## Trainable candidate source counts", trainable_source_counts)
    append_counter_table(lines, "## Trainable candidate family counts", trainable_family_counts)
    append_counter_table(lines, "## Protected source counts", protected_source_counts)
    append_counter_table(lines, "## Tail diagnostic source counts", tail_source_counts)

    lines.extend([
        "",
        "## Recommended next step",
        "",
        "Create a dry-run dataset export plan that selects only `ready_full_schema` rows with `ready_bucket == trainable_rank_11_50`, while keeping protected and tail rows out of training.",
        "",
        "Before actual training, run one more dataset export dry-run and schema validation.",
        "",
        "## Outputs",
        "",
        f"- `{args.out_report}`",
        f"- `{args.out_summary_csv}`",
        "",
        "## Decision",
        "",
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
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("manifest_rows:", len(rows))
    print("non_duplicate_rows:", len(nd))
    print("status_counts:", json.dumps(dict(status), sort_keys=True))
    print("ready_bucket_counts:", json.dumps(dict(ready_bucket_counts), sort_keys=True))
    print("trainable_candidate_rows:", len(trainable_rows))
    print("protected_rows:", len(protected_rows))
    print("tail_diagnostic_rows:", len(tail_rows))
    print("missing_rank_prob:", len(missing_rank_prob))
    print("missing_suppress:", len(missing_suppress))
    print("missing_suppress_round2:", len(missing_suppress_round2))
    print("missing_suppress_pre_round2:", len(missing_suppress_pre_round2))
    print("out_report:", args.out_report)
    print("out_summary_csv:", args.out_summary_csv)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
