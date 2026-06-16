#!/usr/bin/env python3
"""
Materialize retention family split artifacts from retention_family_split_proposal.csv.

This is split-artifact generation only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_PROPOSAL_CSV = Path("analysis/integration_eval/retention_family_split_proposal.csv")
DEFAULT_OUT_MANIFEST_CSV = Path("analysis/integration_eval/retention_family_materialized_split_manifest.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_materialized_split.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_materialized_split_report.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def yes(v: Any) -> bool:
    return clean(v).lower() in {"yes", "true", "1", "y"}


def yn(v: bool) -> str:
    return "yes" if v else "no"


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def split_targets(targets: str) -> List[str]:
    return [x.strip() for x in clean(targets).split(";") if x.strip()]


def materialized_role(row: Dict[str, str]) -> str:
    repeated = yes(row.get("repeated_blocker"))
    sibling_conflict = yes(row.get("sibling_target_conflict"))
    mixed_signal = yes(row.get("mixed_signal_conflict"))
    stable_top1 = yes(row.get("stable_top1_gain"))
    proposal = clean(row.get("split_proposal"))
    outcomes = clean(row.get("outcomes")).lower()
    regression_count = int(clean(row.get("regression_count")) or "0")

    if (
        proposal == "nonheldout_retention_anchor_candidate"
        or repeated
        or regression_count > 0
        or "regression" in outcomes
    ):
        return "nonheldout_retention_anchor"

    if proposal == "heldout_gate_candidate" or stable_top1:
        return "heldout_retention_gate"

    if sibling_conflict or mixed_signal:
        return "heldout_retention_gate_family_conflict_review"

    return "heldout_retention_gate_review"


def materialized_reason(row: Dict[str, str], role: str) -> str:
    repeated = yes(row.get("repeated_blocker"))
    stable_top1 = yes(row.get("stable_top1_gain"))
    sibling_conflict = yes(row.get("sibling_target_conflict"))
    mixed_signal = yes(row.get("mixed_signal_conflict"))
    outcomes = clean(row.get("outcomes"))

    if role == "nonheldout_retention_anchor":
        reasons = []
        if repeated:
            reasons.append("repeated heldout blocker")
        if "regression" in outcomes.lower():
            reasons.append("regression signal")
        if sibling_conflict:
            reasons.append("sibling target conflict family")
        if mixed_signal:
            reasons.append("mixed signal family")
        return "; ".join(reasons) or "promoted from proposal anchor candidate"

    if role == "heldout_retention_gate":
        if sibling_conflict or mixed_signal:
            return "stable top1 gain gate, but not valid as the only sibling-family heldout check"
        if stable_top1:
            return "stable top1 gain gate"
        return "heldout gate candidate from proposal"

    if role == "heldout_retention_gate_family_conflict_review":
        return "family has conflict; keep for review, not as sole sibling gate"

    return "neutral/unknown signal; keep as heldout gate review"


def gate_scope(row: Dict[str, str], role: str) -> str:
    if role.startswith("nonheldout"):
        return "not_a_gate"
    if yes(row.get("sibling_target_conflict")) or yes(row.get("mixed_signal_conflict")):
        return "external_or_family_level_only_not_sibling_only"
    if role == "heldout_retention_gate":
        return "normal_heldout_gate"
    return "review_before_use_as_gate"


def make_md_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def validate_rows(rows: List[Dict[str, str]]) -> None:
    if not rows:
        raise SystemExit("ERROR: proposal CSV has no rows")

    required = [
        "family_id",
        "source",
        "policy_target",
        "split_proposal",
        "repeated_blocker",
        "stable_top1_gain",
        "sibling_target_conflict",
        "mixed_signal_conflict",
        "needs_nonheldout_retention_anchor",
    ]
    missing = [k for k in required if k not in rows[0]]
    if missing:
        raise SystemExit(f"ERROR: proposal CSV missing required columns: {missing}")

    bad = []
    for i, r in enumerate(rows, 1):
        if not clean(r.get("family_id")):
            bad.append((i, "family_id"))
        if not clean(r.get("source")):
            bad.append((i, "source"))
        if not clean(r.get("policy_target")):
            bad.append((i, "policy_target"))
    if bad:
        raise SystemExit(f"ERROR: rows with missing required values: {bad[:20]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposal-csv", type=Path, default=DEFAULT_PROPOSAL_CSV)
    ap.add_argument("--out-manifest-csv", type=Path, default=DEFAULT_OUT_MANIFEST_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    proposal_rows = read_csv(args.proposal_csv)
    validate_rows(proposal_rows)

    materialized_rows: List[Dict[str, str]] = []
    for idx, row in enumerate(proposal_rows, 1):
        role = materialized_role(row)
        scope = gate_scope(row, role)

        out = {
            "materialized_index": str(idx),
            "family_id": clean(row.get("family_id")),
            "source": clean(row.get("source")),
            "row_key": clean(row.get("row_key")),
            "source_path": clean(row.get("source_path")),
            "policy_target": clean(row.get("policy_target")),
            "teacher_move": clean(row.get("teacher_move")),
            "side_to_move": clean(row.get("side_to_move")),
            "last_move": clean(row.get("last_move")),
            "family_targets": clean(row.get("family_targets")),
            "materialized_role": role,
            "gate_scope": scope,
            "allowed_as_only_sibling_family_gate": yn(scope == "normal_heldout_gate"),
            "needs_nonheldout_retention_anchor": clean(row.get("needs_nonheldout_retention_anchor")),
            "repeated_blocker": clean(row.get("repeated_blocker")),
            "stable_top1_gain": clean(row.get("stable_top1_gain")),
            "sibling_target_conflict": clean(row.get("sibling_target_conflict")),
            "mixed_signal_conflict": clean(row.get("mixed_signal_conflict")),
            "outcomes": clean(row.get("outcomes")),
            "regression_count": clean(row.get("regression_count")),
            "gain_count": clean(row.get("gain_count")),
            "top1_gain_count": clean(row.get("top1_gain_count")),
            "input_split_proposal": clean(row.get("split_proposal")),
            "input_reason": clean(row.get("reason")),
            "materialized_reason": materialized_reason(row, role),
        }
        materialized_rows.append(out)

    by_family: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in materialized_rows:
        by_family[r["family_id"]].append(r)

    family_rows = []
    for fid, rs in sorted(by_family.items()):
        role_counts = Counter(r["materialized_role"] for r in rs)
        targets = sorted({r["policy_target"] for r in rs})
        needs_anchor = any(r["materialized_role"] == "nonheldout_retention_anchor" for r in rs)
        has_gate = any(r["materialized_role"].startswith("heldout_retention_gate") for r in rs)
        sibling_conflict = any(yes(r["sibling_target_conflict"]) for r in rs)
        mixed_signal = any(yes(r["mixed_signal_conflict"]) for r in rs)
        only_sibling_safe_gate_count = sum(
            1 for r in rs if r["allowed_as_only_sibling_family_gate"] == "yes"
        )

        if needs_anchor and sibling_conflict:
            family_action = "use_nonheldout_anchor_plus_external_gate"
        elif needs_anchor:
            family_action = "use_nonheldout_anchor"
        elif has_gate:
            family_action = "keep_heldout_gate_or_review"
        else:
            family_action = "manual_review"

        family_rows.append({
            "family_id": fid,
            "row_count": str(len(rs)),
            "targets": ";".join(targets),
            "role_counts": ";".join(f"{k}:{v}" for k, v in sorted(role_counts.items())),
            "needs_nonheldout_retention_anchor": yn(needs_anchor),
            "has_heldout_gate": yn(has_gate),
            "sibling_target_conflict": yn(sibling_conflict),
            "mixed_signal_conflict": yn(mixed_signal),
            "only_sibling_safe_gate_count": str(only_sibling_safe_gate_count),
            "family_action": family_action,
        })

    args.out_manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    manifest_fields = [
        "materialized_index",
        "family_id",
        "source",
        "row_key",
        "source_path",
        "policy_target",
        "teacher_move",
        "side_to_move",
        "last_move",
        "family_targets",
        "materialized_role",
        "gate_scope",
        "allowed_as_only_sibling_family_gate",
        "needs_nonheldout_retention_anchor",
        "repeated_blocker",
        "stable_top1_gain",
        "sibling_target_conflict",
        "mixed_signal_conflict",
        "outcomes",
        "regression_count",
        "gain_count",
        "top1_gain_count",
        "input_split_proposal",
        "input_reason",
        "materialized_reason",
    ]
    with args.out_manifest_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=manifest_fields, lineterminator="\n")
        w.writeheader()
        for r in materialized_rows:
            w.writerow({k: r.get(k, "") for k in manifest_fields})

    payload = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_proposal_csv": str(args.proposal_csv),
            "scope": "split materialization only; no training/checkpoint/C export/benchmark/promotion",
            "row_count": len(materialized_rows),
            "family_count": len(family_rows),
        },
        "family_summary": family_rows,
        "rows": materialized_rows,
    }
    args.out_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    role_counts = Counter(r["materialized_role"] for r in materialized_rows)
    gate_scope_counts = Counter(r["gate_scope"] for r in materialized_rows)

    md = []
    md.append("# Retention family materialized split")
    md.append("")
    md.append("Scope: split artifact generation only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs and outputs")
    md.append("")
    md.append(f"- input proposal CSV: `{args.proposal_csv}`")
    md.append(f"- output manifest CSV: `{args.out_manifest_csv}`")
    md.append(f"- output JSON: `{args.out_json}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- rows: {len(materialized_rows)}")
    md.append(f"- families: {len(family_rows)}")
    md.append(f"- materialized role counts: {dict(sorted(role_counts.items()))}")
    md.append(f"- gate scope counts: {dict(sorted(gate_scope_counts.items()))}")
    md.append(f"- families needing non-heldout retention anchor: {sum(1 for f in family_rows if f['needs_nonheldout_retention_anchor'] == 'yes')}")
    md.append("")

    critical = [f for f in family_rows if f["family_id"] == "bd:ea22cc14729b88fd"]
    if critical:
        md.append("## Critical sibling-conflict family")
        md.append("")
        f = critical[0]
        md.append(f"- family_id: `{f['family_id']}`")
        md.append(f"- targets: `{f['targets']}`")
        md.append(f"- role_counts: `{f['role_counts']}`")
        md.append(f"- family_action: `{f['family_action']}`")
        md.append(
            "- Interpretation: 7,10 and 10,7 move to non-heldout retention anchors; 7,9 can remain a heldout gate, but not as the only sibling-family gate."
        )
        md.append("")

    md.append("## Family summary")
    md.append("")
    md.append(make_md_table(
        [
            "family_id",
            "rows",
            "targets",
            "role_counts",
            "needs_anchor",
            "has_gate",
            "sibling_conflict",
            "mixed_signal",
            "safe_sibling_gates",
            "family_action",
        ],
        [
            [
                f["family_id"],
                f["row_count"],
                f["targets"],
                f["role_counts"],
                f["needs_nonheldout_retention_anchor"],
                f["has_heldout_gate"],
                f["sibling_target_conflict"],
                f["mixed_signal_conflict"],
                f["only_sibling_safe_gate_count"],
                f["family_action"],
            ]
            for f in family_rows
        ],
    ))
    md.append("")

    md.append("## Row manifest")
    md.append("")
    md.append(make_md_table(
        [
            "idx",
            "family_id",
            "source",
            "target",
            "role",
            "gate_scope",
            "only_sibling_gate_ok",
            "reason",
        ],
        [
            [
                r["materialized_index"],
                r["family_id"],
                r["source"],
                r["policy_target"],
                r["materialized_role"],
                r["gate_scope"],
                r["allowed_as_only_sibling_family_gate"],
                r["materialized_reason"],
            ]
            for r in materialized_rows
        ],
    ))
    md.append("")

    md.append("## Usage notes")
    md.append("")
    md.append("- `nonheldout_retention_anchor` rows are intended to remain in the training/anchor side of the next split, not as heldout gates.")
    md.append("- `heldout_retention_gate` rows may be used as heldout checks only according to `gate_scope`.")
    md.append("- `external_or_family_level_only_not_sibling_only` means the row must not be the sole heldout evidence for a sibling target from the same family.")
    md.append("- `heldout_retention_gate_review` rows are retained as review candidates because the available proposal signal is neutral or unknown.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_manifest_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("rows:", len(materialized_rows))
    print("families:", len(family_rows))
    print("role_counts:", dict(sorted(role_counts.items())))
    print("gate_scope_counts:", dict(sorted(gate_scope_counts.items())))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
