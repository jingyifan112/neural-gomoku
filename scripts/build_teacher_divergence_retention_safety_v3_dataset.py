#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval")

CLEAN_V2_DATASET = OUT_DIR / "teacher_divergence_retention_clean_v2_dataset.json"
SAFETY_CANDIDATES = OUT_DIR / "safety_block_candidate_manifest.json"

OUT_DATASET = OUT_DIR / "teacher_divergence_retention_safety_v3_dataset.json"
OUT_MANIFEST = OUT_DIR / "teacher_divergence_retention_safety_v3_manifest.csv"
OUT_REPORT = OUT_DIR / "teacher_divergence_retention_safety_v3_report.md"
OUT_ACCEPTANCE_JSON = OUT_DIR / "teacher_divergence_retention_safety_v3_acceptance.json"
OUT_ACCEPTANCE_MD = OUT_DIR / "teacher_divergence_retention_safety_v3_acceptance.md"


SNAPSHOT_PRIORITY = {
    "b_mcts16": 0,
    "candidate_c_mcts16": 1,
    "candidate_d_mcts32_nearend": 2,
    "candidate_d_move15_mcts16": 3,
}


def stable_hash(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def norm(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()


def norm_move(x: Any) -> str:
    return norm(x).replace(" ", "")


def truthy(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    return norm(x).lower() in {"true", "1", "yes"}


def is_move(x: Any) -> bool:
    s = norm_move(x).lower()
    if not s:
        return False
    return s not in {"na", "n/a", "nan", "none", "null", "unknown", "no_move", "pass", "resign"}


def load_clean_v2_rows() -> list[dict[str, Any]]:
    obj = json.loads(CLEAN_V2_DATASET.read_text(encoding="utf-8"))
    rows = obj.get("rows", [])
    return [r for r in rows if isinstance(r, dict)]


def load_candidate_rows() -> list[dict[str, Any]]:
    obj = json.loads(SAFETY_CANDIDATES.read_text(encoding="utf-8"))
    rows = obj.get("candidates", [])
    return [r for r in rows if isinstance(r, dict)]


def source_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(r["source_id"]) for r in rows if r.get("source_id")}


def make_v3_row(c: dict[str, Any]) -> dict[str, Any]:
    sample_id = norm(c.get("sample_id"))
    row_id = f"tdiv_safety_block_current_best_{sample_id}"
    source_id = f"safety_block_current_best_{sample_id}"

    return {
        "id": row_id,
        "split": "train_candidate",
        "role": "teacher_divergence",
        "bucket": "safety_block_immediate_threat_candidate",
        "source_path": norm(c.get("eval_path")),
        "source_id": source_id,
        "board_size": 15,
        "win_length": 5,
        "game_number": norm(c.get("game_number")),
        "move_count": norm(c.get("move_count")),
        "side_to_move": norm(c.get("side_to_move")),
        "board": c.get("board", ""),
        "policy_target": norm_move(c.get("policy_target")),
        "teacher_move": norm_move(c.get("teacher_move") or c.get("policy_target")),
        "value_target": "",
        "label_type": "policy_teacher_safety_block",
        "suggested_weight": 1.5,
        "heldout": False,
        "metadata": {
            "clean_v3_source": "safety_block_candidate_manifest",
            "original_sample_id": sample_id,
            "eval_family": norm(c.get("eval_family")),
            "snapshot_family": norm(c.get("snapshot_family")),
            "snapshot_path": norm(c.get("snapshot_path")),
            "snapshot_index": c.get("snapshot_index", ""),
            "target_reason": norm(c.get("target_reason")),
            "expected_blocking_moves": norm(c.get("expected_blocking_moves")),
            "opponent_immediate_winning_moves": norm(c.get("opponent_immediate_winning_moves")),
            "logged_direct": norm_move(c.get("logged_direct")),
            "direct_policy_top_move": norm_move(c.get("direct_policy_top_move")),
            "logged_policy_safety": norm_move(c.get("logged_policy_safety")),
            "logged_mcts_raw": norm_move(c.get("logged_mcts_raw")),
            "logged_mcts_safety": norm_move(c.get("logged_mcts_safety")),
            "logged_final": norm_move(c.get("logged_final")),
            "direct_misses_expected_block": truthy(c.get("direct_misses_expected_block")),
            "direct_top_misses_expected_block": truthy(c.get("direct_top_misses_expected_block")),
            "logged_final_blocks_immediate_win": norm(c.get("logged_final_blocks_immediate_win")),
            "labeled_failure_type": norm(c.get("labeled_failure_type")),
            "preliminary_failure_type": norm(c.get("preliminary_failure_type")),
            "model_value_estimate": norm(c.get("model_value_estimate")),
            "direct_policy_top_prob": norm(c.get("direct_policy_top_prob")),
            "board_digest": norm(c.get("board_digest")) or stable_hash(c.get("board", "")),
            "acceptance_filter": "current_best_only_unique_sample_snapshot_priority",
        },
    }


def candidate_acceptance_reason(c: dict[str, Any], existing_ids: set[str]) -> tuple[bool, str]:
    sample_id = norm(c.get("sample_id"))
    source_id = f"safety_block_current_best_{sample_id}"

    if norm(c.get("eval_family")) != "current_best":
        return False, "not_current_best_eval_family"
    if truthy(c.get("already_in_clean_v2")):
        return False, "candidate_marked_already_in_clean_v2"
    if sample_id in existing_ids or source_id in existing_ids:
        return False, "source_id_already_in_clean_v2"
    if norm(c.get("suggested_split")) != "train_candidate_candidate":
        return False, "not_train_candidate_candidate"
    if norm(c.get("role_guess")) != "safety_block_teacher_candidate":
        return False, "not_safety_block_teacher_candidate"
    if norm(c.get("target_reason")) != "logged_final_is_expected_block":
        return False, "target_not_confirmed_by_logged_final"
    if not truthy(c.get("direct_misses_expected_block")):
        return False, "direct_does_not_miss_expected_block"
    if not truthy(c.get("direct_top_misses_expected_block")):
        return False, "direct_top_does_not_miss_expected_block"
    if not is_move(c.get("policy_target")):
        return False, "missing_policy_target"
    if not c.get("board"):
        return False, "missing_board"

    return True, "accepted"


def select_unique_candidates(candidates: list[dict[str, Any]], existing_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = []
    eligible_by_sample: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for c in candidates:
        ok, reason = candidate_acceptance_reason(c, existing_ids)
        sample_id = norm(c.get("sample_id"))
        manifest.append({
            "candidate_source_id": norm(c.get("source_id")),
            "sample_id": sample_id,
            "accepted": False,
            "skip_reason": reason if not ok else "eligible_pending_dedupe",
            "eval_family": norm(c.get("eval_family")),
            "snapshot_family": norm(c.get("snapshot_family")),
            "game_number": norm(c.get("game_number")),
            "move_count": norm(c.get("move_count")),
            "side_to_move": norm(c.get("side_to_move")),
            "policy_target": norm_move(c.get("policy_target")),
            "expected_blocking_moves": norm(c.get("expected_blocking_moves")),
            "logged_direct": norm_move(c.get("logged_direct")),
            "direct_policy_top_move": norm_move(c.get("direct_policy_top_move")),
            "logged_final": norm_move(c.get("logged_final")),
            "board_digest": norm(c.get("board_digest")) or stable_hash(c.get("board", "")),
            "source_path": norm(c.get("eval_path")),
            "snapshot_path": norm(c.get("snapshot_path")),
        })
        if ok:
            eligible_by_sample[sample_id].append(c)

    selected = []
    selected_keys = set()

    for sample_id, rows in sorted(eligible_by_sample.items()):
        # Reject if targets conflict for the same sample.
        targets = {norm_move(r.get("policy_target")) for r in rows}
        if len(targets) != 1:
            for m in manifest:
                if m["sample_id"] == sample_id and m["skip_reason"] == "eligible_pending_dedupe":
                    m["skip_reason"] = "conflicting_targets_for_sample"
            continue

        rows = sorted(
            rows,
            key=lambda r: (
                SNAPSHOT_PRIORITY.get(norm(r.get("snapshot_family")), 99),
                norm(r.get("snapshot_path")),
                int(r.get("snapshot_index") or 0),
            ),
        )
        chosen = rows[0]
        chosen_key = (
            sample_id,
            norm(chosen.get("eval_family")),
            norm(chosen.get("snapshot_family")),
            norm(chosen.get("board_digest")),
            norm_move(chosen.get("policy_target")),
        )
        selected_keys.add(chosen_key)
        selected.append(chosen)

    for m in manifest:
        if m["skip_reason"] != "eligible_pending_dedupe":
            continue
        key = (
            m["sample_id"],
            m["eval_family"],
            m["snapshot_family"],
            m["board_digest"],
            m["policy_target"],
        )
        if key in selected_keys:
            m["accepted"] = True
            m["skip_reason"] = ""
        else:
            m["skip_reason"] = "deduped_lower_priority_snapshot"

    return selected, manifest


def validate_dataset(rows: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors = []
    warnings = []

    ids = [r.get("id") for r in rows]
    dup_ids = [k for k, v in Counter(ids).items() if k and v > 1]
    if dup_ids:
        errors.append(f"duplicate ids: {dup_ids}")

    sids = [r.get("source_id") for r in rows if r.get("source_id")]
    dup_sids = [k for k, v in Counter(sids).items() if k and v > 1]
    if dup_sids:
        errors.append(f"duplicate source_ids: {dup_sids}")

    missing_board = [r.get("id") for r in rows if not r.get("board")]
    if missing_board:
        errors.append(f"missing board rows: {missing_board[:10]}")

    missing_target = [r.get("id") for r in rows if not r.get("policy_target") or not r.get("teacher_move")]
    if missing_target:
        errors.append(f"missing target rows: {missing_target[:10]}")

    bad_retention = [
        r.get("id") for r in rows
        if r.get("role") == "heldout_retention_anchor" and r.get("split") != "heldout_retention"
    ]
    if bad_retention:
        errors.append(f"retention leaked into train: {bad_retention}")

    if len(new_rows) == 0:
        warnings.append("no new v3 safety-block rows accepted")

    return {
        "errors": errors,
        "warnings": warnings,
        "dataset_rows": len(rows),
        "new_rows": len(new_rows),
        "split_counts": dict(Counter(r.get("split") for r in rows)),
        "role_counts": dict(Counter(r.get("role") for r in rows)),
        "bucket_counts": dict(Counter(r.get("bucket") for r in rows)),
        "new_source_ids": [r["source_id"] for r in new_rows],
    }


def write_outputs(v2_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]], manifest: list[dict[str, Any]], validation: dict[str, Any]) -> None:
    all_rows = sorted(
        v2_rows + new_rows,
        key=lambda r: (r.get("split", ""), r.get("role", ""), r.get("bucket", ""), r.get("id", "")),
    )

    obj = {
        "note": "Safety v3 dataset = clean v2 plus accepted current-best safety-block train candidates. Data/report only; no training/export/benchmark run.",
        "base_dataset": str(CLEAN_V2_DATASET),
        "candidate_manifest": str(SAFETY_CANDIDATES),
        "counts": {
            "base_rows": len(v2_rows),
            "new_safety_block_rows": len(new_rows),
            "dataset_rows": len(all_rows),
            "split_counts": validation["split_counts"],
            "role_counts": validation["role_counts"],
            "bucket_counts": validation["bucket_counts"],
        },
        "rows": all_rows,
    }
    OUT_DATASET.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

    fields = [
        "candidate_source_id", "sample_id", "accepted", "skip_reason",
        "eval_family", "snapshot_family", "game_number", "move_count", "side_to_move",
        "policy_target", "expected_blocking_moves", "logged_direct",
        "direct_policy_top_move", "logged_final", "board_digest", "source_path", "snapshot_path",
    ]
    with OUT_MANIFEST.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for r in sorted(manifest, key=lambda x: (x["accepted"] is False, x["sample_id"], x["eval_family"], x["snapshot_family"])):
            writer.writerow({k: r.get(k, "") for k in fields})

    accepted_manifest = [r for r in manifest if r["accepted"]]
    skipped_manifest = [r for r in manifest if not r["accepted"]]

    decision = "ACCEPT" if not validation["errors"] else "REJECT"
    if decision == "ACCEPT" and validation["warnings"]:
        decision = "ACCEPT_WITH_WARNINGS"

    acceptance = {
        "decision": decision,
        "decision_notes": (
            [
                "safety v3 dataset passes structural validation",
                "only current_best eval-family safety-block candidates are accepted",
                "one candidate per sample_id is retained using snapshot priority",
                "no training/export/benchmark has been run",
            ]
            if decision.startswith("ACCEPT")
            else validation["errors"]
        ),
        "validation": validation,
        "manifest_counts": {
            "manifest_rows": len(manifest),
            "accepted_rows": len(accepted_manifest),
            "skipped_rows": len(skipped_manifest),
            "skip_reason_counts": dict(Counter(r["skip_reason"] or "accepted" for r in manifest)),
        },
        "accepted_samples": [
            {
                "source_id": r["source_id"],
                "sample_id": r["metadata"]["original_sample_id"],
                "side": r["side_to_move"],
                "target": r["policy_target"],
                "expected": r["metadata"]["expected_blocking_moves"],
                "logged_direct": r["metadata"]["logged_direct"],
                "direct_policy_top_move": r["metadata"]["direct_policy_top_move"],
                "logged_final": r["metadata"]["logged_final"],
                "snapshot_family": r["metadata"]["snapshot_family"],
            }
            for r in new_rows
        ],
    }
    OUT_ACCEPTANCE_JSON.write_text(json.dumps(acceptance, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append("# Safety v3 teacher-divergence / retention dataset report")
    md.append("")
    md.append("This step builds dataset/manifest/report artifacts only. It does not train, export, benchmark, or modify model weights.")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- base clean v2 rows: {len(v2_rows)}")
    md.append(f"- accepted new safety-block rows: {len(new_rows)}")
    md.append(f"- total v3 dataset rows: {len(all_rows)}")
    md.append("")
    md.append("## Dataset split counts")
    md.append("")
    md.append("| split | count |")
    md.append("|---|---:|")
    for k, v in Counter(r.get("split") for r in all_rows).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Dataset bucket counts")
    md.append("")
    md.append("| bucket | count |")
    md.append("|---|---:|")
    for k, v in Counter(r.get("bucket") for r in all_rows).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Accepted safety-block rows")
    md.append("")
    md.append("| source_id | sample | side | target | expected | direct | top | final | snapshot |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in new_rows:
        meta = r["metadata"]
        md.append(
            f"| `{r['source_id']}` | `{meta['original_sample_id']}` | {r['side_to_move']} | "
            f"`{r['policy_target']}` | `{meta['expected_blocking_moves']}` | "
            f"`{meta['logged_direct']}` | `{meta['direct_policy_top_move']}` | "
            f"`{meta['logged_final']}` | {meta['snapshot_family']} |"
        )
    md.append("")
    md.append("## Manifest skip reason counts")
    md.append("")
    md.append("| reason | count |")
    md.append("|---|---:|")
    for k, v in Counter(r["skip_reason"] or "accepted" for r in manifest).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Acceptance")
    md.append("")
    md.append(f"- decision: {decision}")
    for note in acceptance["decision_notes"]:
        md.append(f"- {note}")
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("- These new rows are immediate-threat safety-block teacher candidates, not capacity or training evidence.")
    md.append("- They are accepted only as a small v3 dataset expansion for future training/probe experiments.")
    md.append("- Held-out retention rows from clean v2 remain held out.")
    md.append("")

    OUT_REPORT.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    amd = []
    amd.append("# Safety v3 dataset acceptance report")
    amd.append("")
    amd.append(f"## Decision: {decision}")
    amd.append("")
    for note in acceptance["decision_notes"]:
        amd.append(f"- {note}")
    amd.append("")
    amd.append("## Counts")
    amd.append("")
    amd.append(f"- base rows: {len(v2_rows)}")
    amd.append(f"- new rows: {len(new_rows)}")
    amd.append(f"- total rows: {len(all_rows)}")
    amd.append(f"- manifest rows: {len(manifest)}")
    amd.append(f"- accepted manifest rows: {len(accepted_manifest)}")
    amd.append(f"- skipped manifest rows: {len(skipped_manifest)}")
    amd.append("")
    amd.append("## Validation")
    amd.append("")
    amd.append(f"- errors: {validation['errors']}")
    amd.append(f"- warnings: {validation['warnings']}")
    amd.append("")
    amd.append("## Accepted samples")
    amd.append("")
    amd.append("| sample | side | target | expected | direct | top | final | snapshot |")
    amd.append("|---|---|---|---|---|---|---|---|")
    for r in new_rows:
        meta = r["metadata"]
        amd.append(
            f"| `{meta['original_sample_id']}` | {r['side_to_move']} | `{r['policy_target']}` | "
            f"`{meta['expected_blocking_moves']}` | `{meta['logged_direct']}` | "
            f"`{meta['direct_policy_top_move']}` | `{meta['logged_final']}` | {meta['snapshot_family']} |"
        )
    amd.append("")
    amd.append("## Boundary")
    amd.append("")
    amd.append("- Accepted for dataset/manifest/report tracking only.")
    amd.append("- Do not train from this until a separate probe plan is created.")
    amd.append("- Do not export C weights from this step.")
    OUT_ACCEPTANCE_MD.write_text("\n".join(amd).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    v2_rows = load_clean_v2_rows()
    candidates = load_candidate_rows()

    existing_ids = source_ids(v2_rows)
    selected_candidates, manifest = select_unique_candidates(candidates, existing_ids)
    new_rows = [make_v3_row(c) for c in selected_candidates]

    validation = validate_dataset(v2_rows + new_rows, new_rows)
    write_outputs(v2_rows, new_rows, manifest, validation)

    print("wrote", OUT_DATASET)
    print("wrote", OUT_MANIFEST)
    print("wrote", OUT_REPORT)
    print("wrote", OUT_ACCEPTANCE_JSON)
    print("wrote", OUT_ACCEPTANCE_MD)
    print()
    print("base_rows", len(v2_rows))
    print("candidate_rows", len(candidates))
    print("accepted_new_rows", len(new_rows))
    print("total_v3_rows", len(v2_rows) + len(new_rows))
    print("validation_errors", validation["errors"])
    print("validation_warnings", validation["warnings"])
    print("split_counts", validation["split_counts"])
    print("bucket_counts", validation["bucket_counts"])

    acceptance = json.loads(OUT_ACCEPTANCE_JSON.read_text(encoding="utf-8"))
    print("decision", acceptance["decision"])
    print("skip_reason_counts", acceptance["manifest_counts"]["skip_reason_counts"])


if __name__ == "__main__":
    main()
