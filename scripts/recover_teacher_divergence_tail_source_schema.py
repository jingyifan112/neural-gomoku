#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SOURCE_AUDIT_MANIFEST = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_candidate_manifest.csv")
SOURCE_AUDIT_SUMMARY = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_audit_summary.json")
TAIL_PLAN_SUMMARY = Path("analysis/integration_eval/teacher_divergence_tail_source_generation_plan/tail_source_generation_summary.json")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_schema_recovery")
OUT_MANIFEST = OUT_DIR / "tail_source_schema_recovery_manifest.csv"
OUT_SOURCE_SUMMARY = OUT_DIR / "tail_source_schema_recovery_by_source.csv"
OUT_JSON = OUT_DIR / "tail_source_schema_recovery_summary.json"
OUT_MD = OUT_DIR / "tail_source_schema_recovery_report.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if value == "":
            return None
        x = float(value)
        if math.isnan(x):
            return None
        return x
    except Exception:
        return None


def walk_all_dicts(obj: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    if isinstance(obj, dict):
        out.append((path, obj))
        for k, v in obj.items():
            out.extend(walk_all_dicts(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(walk_all_dicts(v, f"{path}[{i}]"))
    return out


def load_source_index(source_path: Path) -> dict[str, dict[str, Any]]:
    if not source_path.exists():
        return {}

    if source_path.suffix.lower() == ".csv":
        rows = read_csv(source_path)
        return {f"$[{i}]": dict(r) for i, r in enumerate(rows)}

    if source_path.suffix.lower() == ".json":
        obj = read_json(source_path)
        return {p: dict(d) for p, d in walk_all_dicts(obj)}

    return {}


def key_values(row: dict[str, Any], pattern: str) -> dict[str, Any]:
    rx = re.compile(pattern, re.IGNORECASE)
    return {k: v for k, v in row.items() if rx.search(str(k))}


def first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in row and row[k] not in ["", None]:
            return row[k]
    return None


def case_id_of(original: dict[str, Any], fallback: str) -> str:
    val = first_present(
        original,
        [
            "case_id",
            "id",
            "sample_id",
            "position_id",
            "source_case_id",
            "legacy_case_id",
            "game_position_id",
            "name",
        ],
    )
    return str(val) if val not in ["", None] else fallback


def recover_numeric_from_keyset(row: dict[str, Any], keys: list[str]) -> tuple[str, float] | tuple[str, None]:
    for k in keys:
        v = as_float(row.get(k))
        if v is not None:
            return k, v
    return "", None


def compact_field_list(fields: dict[str, Any], limit: int = 12) -> str:
    parts = []
    for k, v in fields.items():
        if len(parts) >= limit:
            parts.append("...")
            break
        sval = str(v)
        if len(sval) > 60:
            sval = sval[:57] + "..."
        parts.append(f"{k}={sval}")
    return "; ".join(parts)


def classify_recovery(original: dict[str, Any]) -> dict[str, Any]:
    keys = list(original.keys())
    lower_keys = [str(k).lower() for k in keys]
    blob = json.dumps(original, ensure_ascii=False, sort_keys=True).lower()

    rank_like = [
        k for k in keys
        if "rank" in str(k).lower()
        or str(k).lower() in ["teacher_order", "policy_order", "model_order"]
    ]
    prob_like = [
        k for k in keys
        if "prob" in str(k).lower()
        or "policy_p" in str(k).lower()
        or str(k).lower() in ["p", "prior", "policy"]
    ]
    target_like = [
        k for k in keys
        if "target" in str(k).lower()
        or "teacher" in str(k).lower()
        or str(k).lower() in ["move", "move_rc", "best_move", "teacher_move"]
    ]
    board_like = [k for k in keys if "board" in str(k).lower() or "stones" in str(k).lower()]
    side_like = [
        k for k in keys
        if "side" in str(k).lower()
        or "player" in str(k).lower()
        or "to_move" in str(k).lower()
        or "turn" in str(k).lower()
    ]

    rank_field, recovered_rank = recover_numeric_from_keyset(original, rank_like)
    prob_field, recovered_prob = recover_numeric_from_keyset(original, prob_like)

    explicit_tail_text = any(
        token in blob
        for token in [
            "rank_gt50",
            "rank>50",
            "gt50",
            "tail_rank",
            "tail_guard",
            "tail",
            "rank greater than 50",
        ]
    )
    explicit_protected_text = any(
        token in blob
        for token in [
            "protected_top10",
            "protected_top5",
            "protected_top3",
            "protected_guard",
        ]
    )
    quarantine_text = any(
        token in blob
        for token in [
            "quarantine",
            "severe",
            "core_regressed",
            "regression_sensitive",
            "hard_fail",
        ]
    )

    recovered_tail = bool(
        not quarantine_text
        and (
            explicit_tail_text
            or (recovered_rank is not None and recovered_rank > 50)
        )
    )
    recovered_protected = bool(
        not quarantine_text
        and (
            explicit_protected_text
            or (recovered_rank is not None and recovered_rank <= 10)
        )
    )
    recovered_train = bool(
        not quarantine_text
        and recovered_rank is not None
        and 11 <= recovered_rank <= 50
    )

    has_board = bool(board_like)
    has_target = bool(target_like)
    has_side = bool(side_like)

    if recovered_tail:
        recovered_bucket = "P0_tail_guard_candidate_recovered"
    elif recovered_protected:
        recovered_bucket = "P0_protected_guard_candidate_recovered"
    elif recovered_train:
        recovered_bucket = "P1_train_candidate_recovered"
    elif quarantine_text:
        recovered_bucket = "quarantine_or_negative_recovered"
    elif rank_like or prob_like or target_like or board_like:
        recovered_bucket = "schema_partially_recovered"
    else:
        recovered_bucket = "still_unclassified"

    materializable = bool(
        recovered_bucket in [
            "P0_tail_guard_candidate_recovered",
            "P0_protected_guard_candidate_recovered",
            "P1_train_candidate_recovered",
        ]
        and has_board
        and has_target
        and has_side
    )

    return {
        "rank_like_fields": rank_like,
        "prob_like_fields": prob_like,
        "target_like_fields": target_like,
        "board_like_fields": board_like,
        "side_like_fields": side_like,
        "rank_field": rank_field,
        "recovered_rank": recovered_rank,
        "prob_field": prob_field,
        "recovered_prob": recovered_prob,
        "explicit_tail_text": explicit_tail_text,
        "explicit_protected_text": explicit_protected_text,
        "quarantine_text": quarantine_text,
        "has_board": has_board,
        "has_target": has_target,
        "has_side": has_side,
        "recovered_bucket": recovered_bucket,
        "materializable": materializable,
    }


def main() -> int:
    source_manifest = read_csv(SOURCE_AUDIT_MANIFEST)
    source_audit = read_json(SOURCE_AUDIT_SUMMARY)
    tail_plan = read_json(TAIL_PLAN_SUMMARY)

    unclassified = [
        r for r in source_manifest
        if r.get("recommended_bucket") == "unclassified_review"
    ]

    source_indexes: dict[str, dict[str, dict[str, Any]]] = {}
    output_rows: list[dict[str, Any]] = []

    for row in unclassified:
        source_path = row["source_path"]
        source_json_path = row.get("source_json_path", "")

        if source_path not in source_indexes:
            source_indexes[source_path] = load_source_index(Path(source_path))

        source_index = source_indexes[source_path]
        original = dict(source_index.get(source_json_path, {}))

        # Fallback to manifest row if source path changed or path cannot be recovered.
        if not original:
            original = dict(row)

        fallback = row.get("case_id") or f"{Path(source_path).name}:{source_json_path}"
        case_id = case_id_of(original, fallback=fallback)

        rec = classify_recovery(original)

        output_rows.append(
            {
                "source_path": source_path,
                "source_json_path": source_json_path,
                "case_id": case_id,
                "original_manifest_case_id": row.get("case_id", ""),
                "recovered_bucket": rec["recovered_bucket"],
                "materializable": rec["materializable"],
                "rank_field": rec["rank_field"],
                "recovered_rank": "" if rec["recovered_rank"] is None else rec["recovered_rank"],
                "prob_field": rec["prob_field"],
                "recovered_prob": "" if rec["recovered_prob"] is None else rec["recovered_prob"],
                "has_board": rec["has_board"],
                "has_target": rec["has_target"],
                "has_side": rec["has_side"],
                "explicit_tail_text": rec["explicit_tail_text"],
                "explicit_protected_text": rec["explicit_protected_text"],
                "quarantine_text": rec["quarantine_text"],
                "rank_like_fields": ";".join(map(str, rec["rank_like_fields"])),
                "prob_like_fields": ";".join(map(str, rec["prob_like_fields"])),
                "target_like_fields": ";".join(map(str, rec["target_like_fields"])),
                "board_like_fields": ";".join(map(str, rec["board_like_fields"])),
                "side_like_fields": ";".join(map(str, rec["side_like_fields"])),
                "sample_preview": compact_field_list(original, limit=10),
            }
        )

    bucket_counts = Counter(r["recovered_bucket"] for r in output_rows)
    materializable_counts = Counter(
        r["recovered_bucket"] for r in output_rows if str(r["materializable"]) == "True"
    )

    by_source: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "source_path": "",
        "unclassified_rows": 0,
        "recovered_tail": 0,
        "recovered_protected": 0,
        "recovered_train": 0,
        "materializable_tail": 0,
        "materializable_any": 0,
        "still_unclassified": 0,
    })

    for r in output_rows:
        s = by_source[r["source_path"]]
        s["source_path"] = r["source_path"]
        s["unclassified_rows"] += 1
        if r["recovered_bucket"] == "P0_tail_guard_candidate_recovered":
            s["recovered_tail"] += 1
            if str(r["materializable"]) == "True":
                s["materializable_tail"] += 1
        if r["recovered_bucket"] == "P0_protected_guard_candidate_recovered":
            s["recovered_protected"] += 1
        if r["recovered_bucket"] == "P1_train_candidate_recovered":
            s["recovered_train"] += 1
        if str(r["materializable"]) == "True":
            s["materializable_any"] += 1
        if r["recovered_bucket"] == "still_unclassified":
            s["still_unclassified"] += 1

    source_summary_rows = list(by_source.values())

    tail_unique = {
        r["case_id"] for r in output_rows
        if r["recovered_bucket"] == "P0_tail_guard_candidate_recovered"
    }
    materializable_tail_unique = {
        r["case_id"] for r in output_rows
        if r["recovered_bucket"] == "P0_tail_guard_candidate_recovered"
        and str(r["materializable"]) == "True"
    }

    decision = (
        "TAIL_SCHEMA_RECOVERY_FOUND_MATERIALIZABLE_TAIL"
        if len(materializable_tail_unique) >= 12
        else "TAIL_SCHEMA_RECOVERY_FOUND_PARTIAL_TAIL"
        if len(tail_unique) > 0
        else "TAIL_SCHEMA_RECOVERY_NO_TAIL_FOUND"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_fields = [
        "source_path",
        "source_json_path",
        "case_id",
        "original_manifest_case_id",
        "recovered_bucket",
        "materializable",
        "rank_field",
        "recovered_rank",
        "prob_field",
        "recovered_prob",
        "has_board",
        "has_target",
        "has_side",
        "explicit_tail_text",
        "explicit_protected_text",
        "quarantine_text",
        "rank_like_fields",
        "prob_like_fields",
        "target_like_fields",
        "board_like_fields",
        "side_like_fields",
        "sample_preview",
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=manifest_fields, lineterminator="\n")
        w.writeheader()
        for r in output_rows:
            w.writerow({k: r.get(k, "") for k in manifest_fields})

    source_fields = [
        "source_path",
        "unclassified_rows",
        "recovered_tail",
        "recovered_protected",
        "recovered_train",
        "materializable_tail",
        "materializable_any",
        "still_unclassified",
    ]
    with OUT_SOURCE_SUMMARY.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=source_fields, lineterminator="\n")
        w.writeheader()
        for r in source_summary_rows:
            w.writerow({k: r.get(k, "") for k in source_fields})

    summary = {
        "decision": decision,
        "scope": "schema recovery only; no dataset build/training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "source_audit_manifest": str(SOURCE_AUDIT_MANIFEST),
            "source_audit_summary": str(SOURCE_AUDIT_SUMMARY),
            "tail_plan_summary": str(TAIL_PLAN_SUMMARY),
        },
        "upstream": {
            "source_audit_decision": source_audit.get("decision"),
            "tail_plan_decision": tail_plan.get("decision"),
            "tail_gap": tail_plan.get("tail_gap"),
            "protected_gap": tail_plan.get("protected_gap"),
            "train_gap": tail_plan.get("train_gap"),
        },
        "unclassified_rows": len(unclassified),
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "materializable_counts": dict(sorted(materializable_counts.items())),
        "unique_tail_recovered": len(tail_unique),
        "unique_materializable_tail_recovered": len(materializable_tail_unique),
        "source_summary_rows": source_summary_rows,
        "outputs": {
            "manifest": str(OUT_MANIFEST),
            "source_summary": str(OUT_SOURCE_SUMMARY),
            "summary": str(OUT_JSON),
            "report": str(OUT_MD),
        },
        "recommended_next": (
            "Materialize recovered tail candidate review only."
            if len(materializable_tail_unique) >= 12
            else "Generate new tail source rows or add a source-specific evaluator to recover board/rank metadata."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence tail schema recovery", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Schema recovery only.",
        "- No dataset build.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Upstream", ""]
    lines += [
        f"- source audit decision: `{source_audit.get('decision')}`",
        f"- tail plan decision: `{tail_plan.get('decision')}`",
        f"- tail gap: `{tail_plan.get('tail_gap')}`",
        f"- protected gap: `{tail_plan.get('protected_gap')}`",
        f"- train gap: `{tail_plan.get('train_gap')}`",
        "",
    ]

    lines += ["## Recovery summary", ""]
    lines += [
        f"- unclassified rows reviewed: `{len(unclassified)}`",
        f"- unique tail recovered: `{len(tail_unique)}`",
        f"- unique materializable tail recovered: `{len(materializable_tail_unique)}`",
        "",
    ]

    lines += ["## Bucket counts", ""]
    lines += ["| bucket | rows | materializable rows |", "|---|---:|---:|"]
    all_buckets = sorted(set(bucket_counts) | set(materializable_counts))
    for b in all_buckets:
        lines.append(f"| {b} | {bucket_counts.get(b, 0)} | {materializable_counts.get(b, 0)} |")
    lines.append("")

    lines += ["## Source summary", ""]
    lines += [
        "| source | unclassified | recovered_tail | materializable_tail | recovered_train | still_unclassified |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in source_summary_rows:
        lines.append(
            f"| `{r['source_path']}` | {r['unclassified_rows']} | {r['recovered_tail']} | "
            f"{r['materializable_tail']} | {r['recovered_train']} | {r['still_unclassified']} |"
        )
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    if decision == "TAIL_SCHEMA_RECOVERY_FOUND_MATERIALIZABLE_TAIL":
        lines += [
            "Schema recovery found enough materializable tail candidates for the current P0 tail target.",
            "",
            "Next step should still be review/materialization only, not training.",
            "",
        ]
    elif decision == "TAIL_SCHEMA_RECOVERY_FOUND_PARTIAL_TAIL":
        lines += [
            "Schema recovery found some tail candidates but not enough materializable rows for the P0 tail target.",
            "",
            "Next step should either add source-specific extraction or generate more tail source rows.",
            "",
        ]
    else:
        lines += [
            "Schema recovery did not recover tail guard candidates from the unclassified rows.",
            "",
            "Next step should generate or collect new tail source rows before any dataset materialization.",
            "",
        ]

    lines += ["## Final note", ""]
    lines += [
        "This recovery does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("unclassified_rows:", len(unclassified))
    print("bucket_counts:", dict(sorted(bucket_counts.items())))
    print("materializable_counts:", dict(sorted(materializable_counts.items())))
    print("unique_tail_recovered:", len(tail_unique))
    print("unique_materializable_tail_recovered:", len(materializable_tail_unique))
    print("out_manifest:", OUT_MANIFEST)
    print("out_source_summary:", OUT_SOURCE_SUMMARY)
    print("out_summary:", OUT_JSON)
    print("out_report:", OUT_MD)
    print("status: schema recovery only; no dataset build/training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
