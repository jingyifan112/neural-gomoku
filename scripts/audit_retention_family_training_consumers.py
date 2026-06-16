#!/usr/bin/env python3
"""
Audit whether current training/data-consumer scripts understand retention-family split artifacts.

This is an audit only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


DEFAULT_TRAIN_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv")
DEFAULT_EVAL_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv")
DEFAULT_SUMMARY_JSON = Path("analysis/integration_eval/retention_family_training_input_dryrun_summary.json")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_training_consumer_audit.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_training_consumer_audit.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_training_consumer_audit.md")

CRITICAL_FAMILY = "bd:ea22cc14729b88fd"

DEFAULT_SCAN_GLOBS = [
    "scripts/*.py",
    "src/**/*.py",
]

EXCLUDE_PATH_PARTS = [
    ".git/",
    "__pycache__/",
    ".pytest_cache/",
]

# Signals we expect a future consumer to understand.
NEW_CONTRACT_STRINGS = [
    "retention_family_training_input_dryrun_train_manifest",
    "retention_family_training_input_dryrun_eval_manifest",
    "train_retention_anchor",
    "nonheldout_retention_anchor",
    "heldout_retention_gate",
    "gate_scope",
    "external_or_family_level_only_not_sibling_only",
    "allowed_as_only_sibling_family_gate",
]

# Old / ambiguous signals that can be risky if used without the new contract.
OLD_OR_AMBIGUOUS_STRINGS = [
    "heldout_retention",
    "retention_anchor",
    "heldout",
    "label_type",
    "role",
    "split",
]

TRAINING_CONSUMER_HINTS = [
    "train",
    "dataset",
    "data",
    "loader",
    "policy",
    "retention",
    "teacher",
    "candidate",
    "probe",
    "gate",
    "eval",
]


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def yes(v: Any) -> bool:
    return clean(v).lower() in {"yes", "true", "1", "y"}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_files(scan_globs: Sequence[str]) -> List[Path]:
    paths: List[Path] = []
    for pat in scan_globs:
        for s in glob.glob(pat, recursive=True):
            p = Path(s)
            if not p.is_file():
                continue
            sp = str(p)
            if any(part in sp for part in EXCLUDE_PATH_PARTS):
                continue
            if p.suffix != ".py":
                continue
            paths.append(p)
    return sorted(set(paths), key=lambda x: str(x))


def count_string_hits(text: str, needles: Sequence[str]) -> Dict[str, int]:
    return {n: text.count(n) for n in needles if text.count(n) > 0}


def line_hits(text: str, needles: Sequence[str], max_hits: int = 12) -> List[str]:
    hits: List[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if any(n in line for n in needles):
            hits.append(f"L{lineno}: {line.strip()[:220]}")
            if len(hits) >= max_hits:
                break
    return hits


def consumer_category(path: Path, text: str) -> str:
    name = path.name.lower()
    body = text.lower()
    joined = f"{name} {body}"

    if "train" in name or "optimizer" in body or "checkpoint" in body:
        return "training_script"
    if "dataset" in name or "dataloader" in body or "loader" in body:
        return "dataset_consumer"
    if "eval" in name or "gate" in name or "heldout" in body:
        return "eval_or_gate_consumer"
    if "retention" in name or "teacher" in name:
        return "retention_or_teacher_tool"
    if any(h in joined for h in TRAINING_CONSUMER_HINTS):
        return "possibly_relevant"
    return "other_python"


def risk_assessment(
    category: str,
    old_hits: Dict[str, int],
    new_hits: Dict[str, int],
    path: Path,
) -> Dict[str, str]:
    mentions_old_heldout = old_hits.get("heldout_retention", 0) > 0
    mentions_any_new = bool(new_hits)

    if category in {"training_script", "dataset_consumer", "eval_or_gate_consumer"}:
        if mentions_any_new:
            return {
                "risk_level": "low_or_adapted",
                "consumer_status": "mentions_new_retention_family_contract",
                "recommendation": "review implementation semantics before enabling training",
            }
        if mentions_old_heldout:
            return {
                "risk_level": "high",
                "consumer_status": "uses_old_heldout_retention_without_new_contract",
                "recommendation": "block training until this consumer is adapted to train/eval manifests and gate_scope",
            }
        if old_hits:
            return {
                "risk_level": "medium",
                "consumer_status": "uses_generic_split_or_role_terms",
                "recommendation": "inspect before training; may need explicit retention-family contract support",
            }
        return {
            "risk_level": "medium",
            "consumer_status": "relevant_consumer_no_retention_family_contract",
            "recommendation": "inspect before training if this script is in the training path",
        }

    if mentions_any_new:
        return {
            "risk_level": "low",
            "consumer_status": "mentions_new_contract_but_not_primary_consumer",
            "recommendation": "likely artifact/report tool; review if used by training",
        }

    if mentions_old_heldout:
        return {
            "risk_level": "medium",
            "consumer_status": "mentions_old_heldout_retention",
            "recommendation": "review if this script affects dataset split or gates",
        }

    return {
        "risk_level": "low",
        "consumer_status": "no_relevant_retention_family_signal",
        "recommendation": "no action for this audit",
    }


def audit_file(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    category = consumer_category(path, text)
    old_hits = count_string_hits(text, OLD_OR_AMBIGUOUS_STRINGS)
    new_hits = count_string_hits(text, NEW_CONTRACT_STRINGS)
    risk = risk_assessment(category, old_hits, new_hits, path)

    return {
        "path": str(path),
        "category": category,
        "risk_level": risk["risk_level"],
        "consumer_status": risk["consumer_status"],
        "recommendation": risk["recommendation"],
        "old_or_ambiguous_hits": ";".join(f"{k}:{v}" for k, v in sorted(old_hits.items())),
        "new_contract_hits": ";".join(f"{k}:{v}" for k, v in sorted(new_hits.items())),
        "old_hit_lines": " || ".join(line_hits(text, OLD_OR_AMBIGUOUS_STRINGS)),
        "new_hit_lines": " || ".join(line_hits(text, NEW_CONTRACT_STRINGS)),
    }


def validate_manifests(
    train_rows: List[Dict[str, str]],
    eval_rows: List[Dict[str, str]],
    summary: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []

    critical_train = [
        r for r in train_rows
        if r.get("family_id") == CRITICAL_FAMILY
    ]
    critical_eval = [
        r for r in eval_rows
        if r.get("family_id") == CRITICAL_FAMILY
    ]

    train_targets = {r.get("policy_target") for r in critical_train}
    eval_targets = {r.get("policy_target") for r in critical_eval}

    for target in ["7,10", "10,7"]:
        if target not in train_targets:
            errors.append(f"critical target {target} missing from train manifest")

    if "7,9" not in eval_targets:
        errors.append("critical target 7,9 missing from eval manifest")

    for r in critical_eval:
        if r.get("policy_target") == "7,9":
            if r.get("gate_scope") != "external_or_family_level_only_not_sibling_only":
                errors.append("critical target 7,9 has wrong gate_scope")
            if r.get("allowed_as_only_sibling_family_gate") == "yes":
                errors.append("critical target 7,9 incorrectly allowed as only sibling-family gate")

    for r in train_rows:
        if r.get("train_use_policy") != "include_as_nonheldout_retention_anchor_candidate":
            errors.append(f"unexpected train_use_policy in train manifest row {r.get('dataset_index')}")

    for r in eval_rows:
        if r.get("eval_use_policy") == "exclude_from_eval_manifest":
            errors.append(f"unexpected exclude eval policy in eval manifest row {r.get('dataset_index')}")

    return {
        "validation_errors": errors,
        "critical_train_targets": sorted(t for t in train_targets if t),
        "critical_eval_targets": sorted(t for t in eval_targets if t),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "summary_counts": summary.get("counts", {}),
    }


def readiness_from_audit(rows: List[Dict[str, Any]], manifest_validation: Dict[str, Any]) -> Dict[str, str]:
    if manifest_validation["validation_errors"]:
        return {
            "readiness": "blocked_manifest_validation_failed",
            "reason": "; ".join(manifest_validation["validation_errors"]),
        }

    high_risk = [
        r for r in rows
        if r["risk_level"] == "high"
    ]

    adapted_primary = [
        r for r in rows
        if r["category"] in {"training_script", "dataset_consumer", "eval_or_gate_consumer"}
        and r["consumer_status"] == "mentions_new_retention_family_contract"
    ]

    old_primary = [
        r for r in rows
        if r["category"] in {"training_script", "dataset_consumer", "eval_or_gate_consumer"}
        and r["consumer_status"] == "uses_old_heldout_retention_without_new_contract"
    ]

    if old_primary and not adapted_primary:
        return {
            "readiness": "blocked_consumer_contract_missing",
            "reason": "primary training/eval consumers mention old heldout_retention but no primary consumer mentions the new train/eval manifest + gate_scope contract",
        }

    if high_risk:
        return {
            "readiness": "blocked_high_risk_consumers_present",
            "reason": f"{len(high_risk)} high-risk consumer files require review/adaptation",
        }

    if not adapted_primary:
        return {
            "readiness": "blocked_no_primary_consumer_adapter_found",
            "reason": "no primary training/eval consumer appears to consume the new retention-family training/eval manifest contract",
        }

    return {
        "readiness": "review_required_before_training",
        "reason": "new contract mentions exist, but implementation semantics still require manual review before training",
    }


def make_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-manifest", type=Path, default=DEFAULT_TRAIN_MANIFEST)
    ap.add_argument("--eval-manifest", type=Path, default=DEFAULT_EVAL_MANIFEST)
    ap.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    ap.add_argument("--scan-glob", action="append", default=[])
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    scan_globs = args.scan_glob or DEFAULT_SCAN_GLOBS

    train_rows = read_csv(args.train_manifest)
    eval_rows = read_csv(args.eval_manifest)
    summary = read_json(args.summary_json)

    manifest_validation = validate_manifests(train_rows, eval_rows, summary)

    scanned_files = discover_files(scan_globs)
    audit_rows = [audit_file(p) for p in scanned_files]

    # Keep the CSV focused on non-trivial/relevant rows.
    relevant_rows = [
        r for r in audit_rows
        if r["risk_level"] != "low"
        or r["new_contract_hits"]
        or r["old_or_ambiguous_hits"]
        or r["category"] != "other_python"
    ]

    readiness = readiness_from_audit(relevant_rows, manifest_validation)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    csv_fields = [
        "path",
        "category",
        "risk_level",
        "consumer_status",
        "recommendation",
        "old_or_ambiguous_hits",
        "new_contract_hits",
        "old_hit_lines",
        "new_hit_lines",
    ]
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, lineterminator="\n")
        w.writeheader()
        for r in relevant_rows:
            w.writerow({k: r.get(k, "") for k in csv_fields})

    risk_counts = Counter(r["risk_level"] for r in relevant_rows)
    category_counts = Counter(r["category"] for r in relevant_rows)
    status_counts = Counter(r["consumer_status"] for r in relevant_rows)

    payload = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "consumer audit only; no training/checkpoint/C export/benchmark/promotion",
            "train_manifest": str(args.train_manifest),
            "eval_manifest": str(args.eval_manifest),
            "summary_json": str(args.summary_json),
            "scan_globs": scan_globs,
            "scanned_file_count": len(scanned_files),
            "reported_file_count": len(relevant_rows),
        },
        "manifest_validation": manifest_validation,
        "readiness": readiness,
        "counts": {
            "risk_counts": dict(sorted(risk_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "reported_files": relevant_rows,
    }
    args.out_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    high_or_medium = [
        r for r in relevant_rows
        if r["risk_level"] in {"high", "medium"}
    ]
    new_contract_files = [
        r for r in relevant_rows
        if r["new_contract_hits"]
    ]

    md = []
    md.append("# Retention family training consumer audit")
    md.append("")
    md.append("Scope: consumer audit only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs")
    md.append("")
    md.append(f"- train manifest: `{args.train_manifest}`")
    md.append(f"- eval manifest: `{args.eval_manifest}`")
    md.append(f"- summary JSON: `{args.summary_json}`")
    md.append(f"- scan globs: `{scan_globs}`")
    md.append("")
    md.append("## Readiness")
    md.append("")
    md.append(f"- readiness: `{readiness['readiness']}`")
    md.append(f"- reason: {readiness['reason']}")
    md.append("")
    md.append("## Manifest validation")
    md.append("")
    md.append(f"- train rows: {manifest_validation['train_rows']}")
    md.append(f"- eval rows: {manifest_validation['eval_rows']}")
    md.append(f"- critical train targets: `{manifest_validation['critical_train_targets']}`")
    md.append(f"- critical eval targets: `{manifest_validation['critical_eval_targets']}`")
    md.append(f"- validation errors: `{manifest_validation['validation_errors']}`")
    md.append("")
    md.append("## Consumer scan summary")
    md.append("")
    md.append(f"- scanned files: {len(scanned_files)}")
    md.append(f"- reported files: {len(relevant_rows)}")
    md.append(f"- risk counts: `{dict(sorted(risk_counts.items()))}`")
    md.append(f"- category counts: `{dict(sorted(category_counts.items()))}`")
    md.append(f"- status counts: `{dict(sorted(status_counts.items()))}`")
    md.append("")
    md.append("## High/medium-risk files")
    md.append("")
    if high_or_medium:
        md.append(make_table(
            [
                "path",
                "category",
                "risk",
                "status",
                "recommendation",
                "old/ambiguous hits",
                "new contract hits",
            ],
            [
                [
                    r["path"],
                    r["category"],
                    r["risk_level"],
                    r["consumer_status"],
                    r["recommendation"],
                    r["old_or_ambiguous_hits"],
                    r["new_contract_hits"],
                ]
                for r in high_or_medium
            ],
        ))
    else:
        md.append("No high/medium-risk files were found.")
    md.append("")
    md.append("## Files mentioning new retention-family contract")
    md.append("")
    if new_contract_files:
        md.append(make_table(
            [
                "path",
                "category",
                "risk",
                "new contract hits",
            ],
            [
                [
                    r["path"],
                    r["category"],
                    r["risk_level"],
                    r["new_contract_hits"],
                ]
                for r in new_contract_files
            ],
        ))
    else:
        md.append("No primary consumer file currently mentions the new retention-family training/eval manifest contract.")
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("- The training-input dry-run artifacts validate the intended split contract for the critical family.")
    md.append("- Current training should remain blocked unless a training/data consumer explicitly reads the train/eval manifests and respects `gate_scope`.")
    md.append("- Any script that still uses `heldout_retention` directly is risky if it is in the active training path.")
    md.append("- The next implementation step should adapt or wrap the training dataset builder to consume `retention_family_training_input_dryrun_train_manifest.csv` and `retention_family_training_input_dryrun_eval_manifest.csv` explicitly.")
    md.append("")
    md.append("## Required consumer contract before training")
    md.append("")
    md.append("A future training consumer must:")
    md.append("")
    md.append("1. Include train-side rows only from the train manifest, with `train_use_policy=include_as_nonheldout_retention_anchor_candidate`.")
    md.append("2. Treat eval manifest rows according to `eval_use_policy` and `gate_scope`.")
    md.append("3. Enforce `external_or_family_level_only_not_sibling_only` as a hard restriction.")
    md.append("4. Avoid using old `heldout_retention` labels alone to decide whether a row is train-side or eval-side.")
    md.append("5. Preserve `family_id`, `policy_target`, and `materialized_reason` in downstream audit artifacts.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("scanned files:", len(scanned_files))
    print("reported files:", len(relevant_rows))
    print("readiness:", readiness["readiness"])
    print("reason:", readiness["reason"])
    print("manifest validation errors:", manifest_validation["validation_errors"])
    print("risk_counts:", dict(sorted(risk_counts.items())))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
