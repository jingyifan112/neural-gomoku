from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT_DIR = Path("analysis/integration_eval")
OUT_DATASET = OUT_DIR / "teacher_divergence_retention_dataset.json"
OUT_MANIFEST = OUT_DIR / "teacher_divergence_retention_manifest.csv"
OUT_REPORT = OUT_DIR / "teacher_divergence_retention_report.md"

PUBLIC_REPAIR_DATASET = Path(
    "analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json"
)
PUBLIC_CANDIDATES_CSV = Path(
    "analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv"
)

RETENTION_ANCHOR_SOURCES = [
    Path("analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json"),
    Path("analysis/integration_eval/current_best_margin_candidate_c_anchors.json"),
    Path("analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json"),
]

REFERENCE_SOURCES = [
    Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.json"),
    Path("analysis/integration_eval/candidate_g_teacher_seed_manifest.json"),
    Path("analysis/integration_eval/candidate_i_rapfi_requery_census.csv"),
    Path("analysis/integration_eval/candidate_d_teacher_disagreement_census.csv"),
]


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_records(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for key in ("rows", "samples", "data", "examples", "positions", "manifest"):
            val = obj.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
    return []


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_obj(obj: Any) -> str:
    return hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()[:16]


def first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        val = row.get(key)
        if val not in (None, "", "NA", "nan", "None"):
            return val
    return None


def normalize_move(v: Any) -> str | None:
    if v in (None, "", "NA", "nan", "None"):
        return None
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        if "," in s:
            parts = [p.strip() for p in s.split(",")]
            if len(parts) == 2 and all(p.lstrip("-").isdigit() for p in parts):
                return f"{int(parts[0])},{int(parts[1])}"
        return s
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return f"{int(v[0])},{int(v[1])}"
    if isinstance(v, dict):
        if "x" in v and "y" in v:
            return f"{int(v['x'])},{int(v['y'])}"
        if "row" in v and "col" in v:
            return f"{int(v['col'])},{int(v['row'])}"
    return str(v)


def find_board(row: dict[str, Any]) -> Any:
    for key in [
        "board",
        "board_snapshot_before_decision",
        "board_before",
        "position",
        "snapshot",
        "stones",
    ]:
        val = row.get(key)
        if val not in (None, "", "NA"):
            return val
    return None


def infer_board_size(board: Any, fallback: Any = None) -> int | None:
    if fallback not in (None, "", "NA", "nan", "None"):
        try:
            return int(fallback)
        except Exception:
            pass
    if isinstance(board, list):
        return len(board)
    return None


def boolish(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def floatish(v: Any) -> float | None:
    if v in (None, "", "NA", "nan", "None"):
        return None
    try:
        return float(v)
    except Exception:
        return None


def suggested_teacher_weight(meta: dict[str, Any]) -> float:
    priority = boolish(meta.get("priority_candidate"))
    numeric_gap = boolish(meta.get("numeric_gap_candidate"))
    policy_candidate = boolish(meta.get("policy_candidate"))
    gap = floatish(meta.get("numeric_gap_value"))

    if priority and numeric_gap:
        return 2.0
    if numeric_gap and gap is not None and gap >= 300:
        return 2.0
    if policy_candidate:
        return 1.5
    return 1.0


def make_row_id(prefix: str, source_id: str, existing: set[str]) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(source_id))
    candidate = f"{prefix}_{safe}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    i = 2
    while f"{candidate}_{i}" in existing:
        i += 1
    out = f"{candidate}_{i}"
    existing.add(out)
    return out


def add_or_skip(
    *,
    rows: list[dict[str, Any]],
    manifest: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    used_ids: set[str],
    dedupe: dict[tuple[str, str, str], str],
    prefix: str,
    split: str,
    role: str,
    bucket: str,
    source_path: Path,
    source_id: str,
    raw_row: dict[str, Any],
    policy_target: Any,
    teacher_move: Any = None,
    current_best_direct_move: Any = None,
    current_best_matches_teacher: Any = None,
    suggested_weight: float = 1.0,
    notes: str = "",
) -> None:
    board = find_board(raw_row)
    target = normalize_move(policy_target)
    teacher = normalize_move(teacher_move) or target
    model_move = normalize_move(current_best_direct_move)

    base_manifest = {
        "dataset_id": "",
        "included": "False",
        "skip_reason": "",
        "split": split,
        "role": role,
        "bucket": bucket,
        "source_path": str(source_path),
        "source_id": source_id,
        "game_number": raw_row.get("game_number", ""),
        "move_count": raw_row.get("move_count", ""),
        "side_to_move": raw_row.get("side_to_move", ""),
        "policy_target": target or "",
        "teacher_move": teacher or "",
        "current_best_direct_move": model_move or "",
        "current_best_matches_teacher": current_best_matches_teacher,
        "labeled_failure_type": raw_row.get("labeled_failure_type", raw_row.get("failure_type", "")),
        "numeric_gap_value": raw_row.get("numeric_gap_value", ""),
        "suggested_weight": suggested_weight,
        "board_digest": "",
        "duplicate_of": "",
        "notes": notes,
    }

    if board is None:
        base_manifest["skip_reason"] = "missing_board"
        manifest.append(base_manifest)
        skipped.append(dict(base_manifest))
        return

    if target is None:
        base_manifest["skip_reason"] = "missing_policy_target"
        manifest.append(base_manifest)
        skipped.append(dict(base_manifest))
        return

    board_digest = digest_obj(board)
    dedupe_key = (split, board_digest, target)
    if dedupe_key in dedupe:
        base_manifest["skip_reason"] = "duplicate_split_board_target"
        base_manifest["board_digest"] = board_digest
        base_manifest["duplicate_of"] = dedupe[dedupe_key]
        manifest.append(base_manifest)
        skipped.append(dict(base_manifest))
        return

    dataset_id = make_row_id(prefix, source_id, used_ids)
    dedupe[dedupe_key] = dataset_id

    board_size = infer_board_size(board, raw_row.get("board_size"))
    win_length = raw_row.get("win_length", 5)

    out = {
        "id": dataset_id,
        "split": split,
        "role": role,
        "bucket": bucket,
        "source_path": str(source_path),
        "source_id": source_id,
        "board_size": board_size,
        "win_length": int(win_length) if str(win_length).isdigit() else win_length,
        "game_number": raw_row.get("game_number"),
        "move_count": raw_row.get("move_count"),
        "side_to_move": raw_row.get("side_to_move"),
        "board": board,
        "policy_target": target,
        "teacher_move": teacher,
        "value_target": raw_row.get("value_target"),
        "label_type": raw_row.get("label_type", "policy_target"),
        "suggested_weight": suggested_weight,
        "heldout": split.startswith("heldout"),
        "metadata": {
            "current_best_direct_move": model_move,
            "current_best_matches_teacher": current_best_matches_teacher,
            "teacher_eval_before": raw_row.get("teacher_eval_before"),
            "teacher_eval_kind": raw_row.get("teacher_eval_kind"),
            "teacher_pv_before": raw_row.get("teacher_pv_before"),
            "teacher_query_status": raw_row.get("teacher_query_status"),
            "labeled_failure_type": raw_row.get("labeled_failure_type", raw_row.get("failure_type")),
            "numeric_gap_available": raw_row.get("numeric_gap_available"),
            "numeric_gap_value": raw_row.get("numeric_gap_value"),
            "reason": raw_row.get("reason"),
            "notes": notes,
            "board_digest": board_digest,
        },
    }

    rows.append(out)

    base_manifest["dataset_id"] = dataset_id
    base_manifest["included"] = "True"
    base_manifest["board_digest"] = board_digest
    manifest.append(base_manifest)


def build() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    used_ids: set[str] = set()
    dedupe: dict[tuple[str, str, str], str] = {}
    rows: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    candidates = {
        r.get("sample_id"): r
        for r in load_csv(PUBLIC_CANDIDATES_CSV)
        if r.get("sample_id")
    }

    # 1) Train-side teacher-divergence samples from public benchmark Rapfi re-query.
    if PUBLIC_REPAIR_DATASET.exists():
        repair_records = json_records(load_json(PUBLIC_REPAIR_DATASET))
        for record in repair_records:
            source_id = str(first_present(record, ["id", "sample_id", "case_id"]) or f"row{len(rows)}")
            meta = candidates.get(source_id, {})
            merged = dict(record)
            merged.update({k: v for k, v in meta.items() if k not in merged or merged.get(k) in (None, "", "NA")})

            add_or_skip(
                rows=rows,
                manifest=manifest,
                skipped=skipped,
                used_ids=used_ids,
                dedupe=dedupe,
                prefix="tdiv",
                split="train_teacher_divergence",
                role="teacher_divergence",
                bucket=str(
                    first_present(
                        merged,
                        ["suggested_bucket", "labeled_failure_type", "label_type"],
                    )
                    or "public_benchmark_rapfi_requery"
                ),
                source_path=PUBLIC_REPAIR_DATASET,
                source_id=source_id,
                raw_row=merged,
                policy_target=first_present(merged, ["policy_target", "teacher_move"]),
                teacher_move=first_present(merged, ["teacher_move", "policy_target"]),
                current_best_direct_move=first_present(merged, ["current_best_direct_move", "model_direct_move"]),
                current_best_matches_teacher=first_present(
                    merged,
                    ["current_best_matches_teacher", "model_matches_rapfi_best_before"],
                ),
                suggested_weight=suggested_teacher_weight(merged),
                notes="public benchmark corpus8 selected; Rapfi re-query teacher label",
            )

    # 2) Held-out retention anchors. These are explicitly NOT train split.
    for source_path in RETENTION_ANCHOR_SOURCES:
        if not source_path.exists():
            skipped.append({
                "source_path": str(source_path),
                "skip_reason": "missing_source",
            })
            continue

        anchor_records = json_records(load_json(source_path))
        for idx, record in enumerate(anchor_records):
            source_id = str(first_present(record, ["case_id", "id", "sample_id"]) or f"{source_path.stem}_{idx}")
            add_or_skip(
                rows=rows,
                manifest=manifest,
                skipped=skipped,
                used_ids=used_ids,
                dedupe=dedupe,
                prefix="holdout",
                split="heldout_retention",
                role="heldout_retention_anchor",
                bucket=str(first_present(record, ["reason", "source"]) or source_path.stem),
                source_path=source_path,
                source_id=source_id,
                raw_row=record,
                policy_target=first_present(record, ["target_xy", "policy_target", "target_move"]),
                teacher_move=first_present(record, ["target_xy", "policy_target", "target_move"]),
                current_best_direct_move=first_present(record, ["target_xy", "policy_target", "target_move"]),
                current_best_matches_teacher="retention_anchor",
                suggested_weight=0.0,
                notes="held-out current-best retention anchor; do not train on this split",
            )

    dataset = {
        "name": "teacher_divergence_retention_dataset",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Build a reviewable dataset from public benchmark Rapfi teacher-divergence "
            "samples plus held-out retention anchors. This artifact is for dataset/manifest/report "
            "review only; no training, export, or benchmark is run by this script."
        ),
        "important_split_rule": (
            "Rows with split=heldout_retention are regression/retention probes and must not be "
            "used as training rows unless a later experiment explicitly changes the protocol."
        ),
        "sources": {
            "public_repair_dataset": str(PUBLIC_REPAIR_DATASET),
            "public_candidates_csv": str(PUBLIC_CANDIDATES_CSV),
            "retention_anchor_sources": [str(p) for p in RETENTION_ANCHOR_SOURCES],
            "reference_sources_not_consumed": [str(p) for p in REFERENCE_SOURCES],
        },
        "summary": {
            "total_included_rows": len(rows),
            "total_manifest_rows": len(manifest),
            "total_skipped_rows": len(skipped),
            "split_counts": dict(Counter(r["split"] for r in rows)),
            "role_counts": dict(Counter(r["role"] for r in rows)),
            "bucket_counts": dict(Counter(r["bucket"] for r in rows)),
        },
        "rows": rows,
        "skipped": skipped,
    }
    return dataset, manifest, skipped


def write_manifest(manifest: list[dict[str, Any]]) -> None:
    fields = [
        "dataset_id",
        "included",
        "skip_reason",
        "split",
        "role",
        "bucket",
        "source_path",
        "source_id",
        "game_number",
        "move_count",
        "side_to_move",
        "policy_target",
        "teacher_move",
        "current_best_direct_move",
        "current_best_matches_teacher",
        "labeled_failure_type",
        "numeric_gap_value",
        "suggested_weight",
        "board_digest",
        "duplicate_of",
        "notes",
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in manifest:
            writer.writerow({k: row.get(k, "") for k in fields})


def write_report(dataset: dict[str, Any], manifest: list[dict[str, Any]], skipped: list[dict[str, Any]]) -> None:
    rows = dataset["rows"]
    lines = []
    lines.append("# Teacher divergence / held-out retention dataset report")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(
        "Build dataset/manifest/report only. No training, no C export, and no public benchmark run was performed."
    )
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- Dataset: `{OUT_DATASET}`")
    lines.append(f"- Manifest: `{OUT_MANIFEST}`")
    lines.append(f"- Report: `{OUT_REPORT}`")
    lines.append("")
    lines.append("## Split rule")
    lines.append("")
    lines.append(
        "`heldout_retention` rows are regression/retention probes. They should be evaluated as held-out anchors, "
        "not consumed as train rows by default."
    )
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Included dataset rows: {len(rows)}")
    lines.append(f"- Manifest rows: {len(manifest)}")
    lines.append(f"- Skipped rows: {len(skipped)}")
    lines.append("")
    lines.append("### Split counts")
    lines.append("")
    lines.append("| split | rows |")
    lines.append("|---|---:|")
    for key, val in Counter(r["split"] for r in rows).most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("### Role counts")
    lines.append("")
    lines.append("| role | rows |")
    lines.append("|---|---:|")
    for key, val in Counter(r["role"] for r in rows).most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("### Bucket counts")
    lines.append("")
    lines.append("| bucket | rows |")
    lines.append("|---|---:|")
    for key, val in Counter(r["bucket"] for r in rows).most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")

    by_source = Counter(r["source_path"] for r in rows)
    lines.append("## Included source counts")
    lines.append("")
    lines.append("| source | rows |")
    lines.append("|---|---:|")
    for key, val in by_source.most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")

    skipped_by_reason = Counter(s.get("skip_reason", "unknown") for s in skipped)
    lines.append("## Skipped rows")
    lines.append("")
    if skipped_by_reason:
        lines.append("| reason | rows |")
        lines.append("|---|---:|")
        for key, val in skipped_by_reason.most_common():
            lines.append(f"| `{key}` | {val} |")
    else:
        lines.append("No skipped rows.")
    lines.append("")

    lines.append("## Train teacher-divergence preview")
    lines.append("")
    lines.append("| id | source_id | side | target | current_best | bucket | weight |")
    lines.append("|---|---|---|---|---|---|---:|")
    for r in [x for x in rows if x["split"] == "train_teacher_divergence"][:20]:
        lines.append(
            f"| `{r['id']}` | `{r['source_id']}` | {r.get('side_to_move')} | "
            f"`{r.get('policy_target')}` | `{r['metadata'].get('current_best_direct_move')}` | "
            f"`{r.get('bucket')}` | {r.get('suggested_weight')} |"
        )
    lines.append("")

    lines.append("## Held-out retention preview")
    lines.append("")
    lines.append("| id | source_id | side | target | bucket | source |")
    lines.append("|---|---|---|---|---|---|")
    for r in [x for x in rows if x["split"] == "heldout_retention"][:30]:
        lines.append(
            f"| `{r['id']}` | `{r['source_id']}` | {r.get('side_to_move')} | "
            f"`{r.get('policy_target')}` | `{r.get('bucket')}` | `{r.get('source_path')}` |"
        )
    lines.append("")

    lines.append("## Next recommended gate before training")
    lines.append("")
    lines.append(
        "Before any training, run a small loader/probe that verifies every included row has a legal target, "
        "the side-to-move convention matches the current training code, and held-out rows remain excluded from train split."
    )
    lines.append("")

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset, manifest, skipped = build()

    OUT_DATASET.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    write_manifest(manifest)
    write_report(dataset, manifest, skipped)

    print(f"wrote {OUT_DATASET}")
    print(f"wrote {OUT_MANIFEST}")
    print(f"wrote {OUT_REPORT}")
    print()
    print("=== summary ===")
    print(json.dumps(dataset["summary"], indent=2, ensure_ascii=False))
    print()
    print("=== split counts ===")
    for k, v in Counter(r["split"] for r in dataset["rows"]).most_common():
        print(f"{k}: {v}")
    print()
    print("=== skipped reasons ===")
    for k, v in Counter(s.get("skip_reason", "unknown") for s in skipped).most_common():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
