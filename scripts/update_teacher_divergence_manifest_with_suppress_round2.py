#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge current_best probe fill round2 and suppress build fill round2 back into teacher-divergence manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv"),
    )
    parser.add_argument(
        "--probe-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv"),
    )
    parser.add_argument(
        "--suppress-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill_round2.csv"),
    )
    parser.add_argument(
        "--out-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_manifest_update_with_suppress_round2_report.md"),
    )
    parser.add_argument("--expected-probe-rows", type=int, default=140)
    parser.add_argument("--expected-suppress-rows", type=int, default=97)
    parser.add_argument("--expected-illegal-rows", type=int, default=43)
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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def index_by_manifest_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        mid = row.get("manifest_id", "").strip()
        if not mid:
            raise RuntimeError(f"{label}: row missing manifest_id: {row}")
        if mid in out:
            raise RuntimeError(f"{label}: duplicate manifest_id {mid}")
        out[mid] = row
    return out


def nondup(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [r for r in rows if is_blank(r.get("duplicate_of"))]


def status_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(r.get("status", "") for r in nondup(rows))


def ready_bucket(row: dict[str, str]) -> str:
    return (
        row.get("ready_bucket")
        or row.get("bucket")
        or row.get("bucket_after")
        or row.get("bucket_before")
        or ""
    )


def ready_bucket_counts(rows: list[dict[str, str]]) -> Counter[str]:
    c: Counter[str] = Counter()
    for r in nondup(rows):
        if r.get("status") == "ready_full_schema":
            c[ready_bucket(r)] += 1
    return c


def ensure_columns(existing: list[str], extra: list[str]) -> list[str]:
    out = list(existing)
    for col in extra:
        if col not in out:
            out.append(col)
    return out


def copy_fields(dst: dict[str, str], src: dict[str, str], fields: list[str]) -> None:
    for f in fields:
        dst[f] = src.get(f, "")


def main() -> None:
    args = parse_args()

    manifest_fields, manifest_rows = read_csv(args.manifest)
    _probe_fields, probe_rows = read_csv(args.probe_fill_csv)
    _suppress_fields, suppress_rows = read_csv(args.suppress_fill_csv)

    if len(probe_rows) != args.expected_probe_rows:
        raise RuntimeError(f"expected {args.expected_probe_rows} probe rows, got {len(probe_rows)}")
    if len(suppress_rows) != args.expected_suppress_rows:
        raise RuntimeError(f"expected {args.expected_suppress_rows} suppress rows, got {len(suppress_rows)}")

    probe_by_id = index_by_manifest_id(probe_rows, "probe_fill")
    suppress_by_id = index_by_manifest_id(suppress_rows, "suppress_fill")

    legal_probe_ids = {
        mid for mid, r in probe_by_id.items()
        if r.get("status_after") == "needs_suppress_build"
        and r.get("target_legal") == "1"
        and r.get("excluded") == "0"
    }
    illegal_probe_ids = {
        mid for mid, r in probe_by_id.items()
        if r.get("target_legal") == "0"
        and r.get("excluded") == "1"
    }

    if len(legal_probe_ids) != args.expected_suppress_rows:
        raise RuntimeError(f"expected {args.expected_suppress_rows} legal probe rows, got {len(legal_probe_ids)}")
    if len(illegal_probe_ids) != args.expected_illegal_rows:
        raise RuntimeError(f"expected {args.expected_illegal_rows} illegal probe rows, got {len(illegal_probe_ids)}")

    if set(suppress_by_id) != legal_probe_ids:
        missing = sorted(legal_probe_ids - set(suppress_by_id))[:10]
        extra = sorted(set(suppress_by_id) - legal_probe_ids)[:10]
        raise RuntimeError(f"suppress ids do not match legal probe ids; missing={missing}; extra={extra}")

    manifest_by_id = index_by_manifest_id(manifest_rows, "manifest")

    missing_probe_ids = sorted(set(probe_by_id) - set(manifest_by_id))
    if missing_probe_ids:
        raise RuntimeError(f"probe ids missing from manifest: {missing_probe_ids[:10]}")

    before_status = status_counts(manifest_rows)
    before_ready_bucket = ready_bucket_counts(manifest_rows)

    extra_columns = [
        "ready_bucket",
        "status_before_round2_merge",
        "status_after_round2_merge",
        "ready_bucket_before_round2_merge",
        "ready_bucket_after_round2_merge",
        "target_action",
        "target_legal",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "current_best_top_policy_rcs",
        "current_best_top_policy_probs",
        "suppress_rc",
        "suppress_rank_in_top_policy",
        "suppress_prob",
        "suppress_prob_gap",
        "suppress_prob_ratio",
        "suppress_candidates_rcs",
        "suppress_candidates_probs",
        "suppress_candidates_ranks",
        "suppress_count",
        "probe_source",
        "suppress_source",
        "rank_prob_available",
        "suppress_available",
        "ready_full_schema_after",
        "excluded",
        "exclude_reason",
        "round2_probe_status_after",
        "round2_suppress_status_after",
        "round2_merge_action",
        "round2_merge_notes",
    ]
    out_fields = ensure_columns(manifest_fields, extra_columns)

    probe_policy_fields = [
        "target_action",
        "target_legal",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "current_best_top_policy_rcs",
        "current_best_top_policy_probs",
        "probe_source",
    ]
    suppress_fields = [
        "suppress_rc",
        "suppress_rank_in_top_policy",
        "suppress_prob",
        "suppress_prob_gap",
        "suppress_prob_ratio",
        "suppress_candidates_rcs",
        "suppress_candidates_probs",
        "suppress_candidates_ranks",
        "suppress_count",
        "suppress_source",
        "ready_full_schema_after",
    ]

    out_rows: list[dict[str, str]] = []
    action_counts: Counter[str] = Counter()

    for row in manifest_rows:
        out = dict(row)
        mid = out.get("manifest_id", "").strip()

        out.setdefault("ready_bucket", ready_bucket(out))
        out["status_before_round2_merge"] = ""
        out["status_after_round2_merge"] = ""
        out["ready_bucket_before_round2_merge"] = ""
        out["ready_bucket_after_round2_merge"] = ""
        out["round2_probe_status_after"] = ""
        out["round2_suppress_status_after"] = ""
        out["round2_merge_action"] = ""
        out["round2_merge_notes"] = ""

        if mid in suppress_by_id:
            probe = probe_by_id[mid]
            suppress = suppress_by_id[mid]
            bucket_after = suppress.get("bucket_after", probe.get("bucket_after", ""))

            out["status_before_round2_merge"] = out.get("status", "")
            out["ready_bucket_before_round2_merge"] = ready_bucket(out)

            out["status"] = "ready_full_schema"
            out["ready_bucket"] = bucket_after
            if "bucket" in out:
                out["bucket"] = bucket_after

            copy_fields(out, probe, probe_policy_fields)
            copy_fields(out, suppress, suppress_fields)

            out["rank_prob_available"] = "1"
            out["suppress_available"] = "1"
            out["ready_full_schema_after"] = "1"
            out["excluded"] = "0"
            out["exclude_reason"] = ""
            out["round2_probe_status_after"] = probe.get("status_after", "")
            out["round2_suppress_status_after"] = suppress.get("status_after", "")
            out["round2_merge_action"] = "probe_and_suppress_built"
            out["round2_merge_notes"] = suppress.get("notes", "ready_full_schema_after_round2")

            out["status_after_round2_merge"] = out.get("status", "")
            out["ready_bucket_after_round2_merge"] = ready_bucket(out)
            action_counts["probe_and_suppress_built"] += 1

        elif mid in illegal_probe_ids:
            probe = probe_by_id[mid]
            bucket_after = probe.get("bucket_after", "unknown_rank") or "unknown_rank"

            out["status_before_round2_merge"] = out.get("status", "")
            out["ready_bucket_before_round2_merge"] = ready_bucket(out)

            out["status"] = "skipped_invalid"
            out["ready_bucket"] = bucket_after
            if "bucket" in out:
                out["bucket"] = bucket_after

            copy_fields(out, probe, probe_policy_fields)

            out["rank_prob_available"] = "0"
            out["suppress_available"] = "0"
            out["ready_full_schema_after"] = "0"
            out["target_legal"] = "0"
            out["excluded"] = "1"
            out["exclude_reason"] = probe.get("exclude_reason", "target_illegal")
            out["round2_probe_status_after"] = probe.get("status_after", "")
            out["round2_suppress_status_after"] = ""
            out["round2_merge_action"] = "probe_target_illegal_skipped"
            out["round2_merge_notes"] = probe.get("notes", "excluded_target_illegal")

            out["status_after_round2_merge"] = out.get("status", "")
            out["ready_bucket_after_round2_merge"] = ready_bucket(out)
            action_counts["probe_target_illegal_skipped"] += 1

        else:
            action_counts["unchanged"] += 1

        for col in out_fields:
            out.setdefault(col, "")

        out_rows.append(out)

    after_status = status_counts(out_rows)
    after_ready_bucket = ready_bucket_counts(out_rows)

    if action_counts["probe_and_suppress_built"] != args.expected_suppress_rows:
        raise RuntimeError(action_counts)
    if action_counts["probe_target_illegal_skipped"] != args.expected_illegal_rows:
        raise RuntimeError(action_counts)

    expected_after = {
        "ready_full_schema": before_status.get("ready_full_schema", 0) + args.expected_suppress_rows,
        "skipped_invalid": before_status.get("skipped_invalid", 0) + args.expected_illegal_rows,
        "needs_current_best_probe": before_status.get("needs_current_best_probe", 0) - args.expected_probe_rows,
        "needs_rapfi_requery": before_status.get("needs_rapfi_requery", 0),
        "needs_board_join": before_status.get("needs_board_join", 0),
    }

    for status, expected in expected_after.items():
        actual = after_status.get(status, 0)
        if actual != expected:
            raise RuntimeError(f"status count mismatch for {status}: expected {expected}, got {actual}")

    write_csv(args.out_manifest, out_fields, out_rows)

    report_lines = [
        "# Teacher-divergence manifest update with suppress round2",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-manifest-update-with-suppress-round2`",
        "",
        "## Scope",
        "",
        "- Merge current_best probe fill round2 into manifest.",
        "- Merge suppress build fill round2 into manifest.",
        "- Convert legal probed rows with suppress candidates to `ready_full_schema`.",
        "- Convert illegal target rows to `skipped_invalid`.",
        "- Does not process `needs_rapfi_requery` rows.",
        "- Does not process `needs_board_join` rows.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{args.manifest}`",
        f"- probe fill CSV: `{args.probe_fill_csv}`",
        f"- suppress fill CSV: `{args.suppress_fill_csv}`",
        "",
        "## Action counts",
        "",
        "| action | rows |",
        "|---|---:|",
    ]

    for key, value in action_counts.most_common():
        report_lines.append(f"| {key} | {value} |")

    report_lines.extend([
        "",
        "## Non-duplicate status counts before",
        "",
        "| status | rows |",
        "|---|---:|",
    ])

    for key, value in before_status.most_common():
        report_lines.append(f"| {key} | {value} |")

    report_lines.extend([
        "",
        "## Non-duplicate status counts after",
        "",
        "| status | rows |",
        "|---|---:|",
    ])

    for key, value in after_status.most_common():
        report_lines.append(f"| {key} | {value} |")

    report_lines.extend([
        "",
        "## Ready bucket counts before",
        "",
        "| ready_bucket | rows |",
        "|---|---:|",
    ])

    for key, value in before_ready_bucket.most_common():
        report_lines.append(f"| {key} | {value} |")

    report_lines.extend([
        "",
        "## Ready bucket counts after",
        "",
        "| ready_bucket | rows |",
        "|---|---:|",
    ])

    for key, value in after_ready_bucket.most_common():
        report_lines.append(f"| {key} | {value} |")

    report_lines.extend([
        "",
        "## Expected after-checks",
        "",
        "| status | expected | actual |",
        "|---|---:|---:|",
    ])

    for key, expected in expected_after.items():
        report_lines.append(f"| {key} | {expected} | {after_status.get(key, 0)} |")

    report_lines.extend([
        "",
        "## Outputs",
        "",
        f"- `{args.out_manifest}`",
        f"- `{args.out_report}`",
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
    args.out_report.write_text("\n".join(report_lines), encoding="utf-8")

    print("manifest_rows:", len(manifest_rows))
    print("non_duplicate_rows:", len(nondup(out_rows)))
    print("action_counts:", json.dumps(dict(action_counts), sort_keys=True))
    print("status_counts_before:", json.dumps(dict(before_status), sort_keys=True))
    print("status_counts_after:", json.dumps(dict(after_status), sort_keys=True))
    print("ready_bucket_counts_before:", json.dumps(dict(before_ready_bucket), sort_keys=True))
    print("ready_bucket_counts_after:", json.dumps(dict(after_ready_bucket), sort_keys=True))
    print("out_manifest:", args.out_manifest)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
