#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any


TAIL_SCHEMA_RECOVERY = Path("analysis/integration_eval/teacher_divergence_tail_schema_recovery/tail_source_schema_recovery_summary.json")
TAIL_PLAN = Path("analysis/integration_eval/teacher_divergence_tail_source_generation_plan/tail_source_generation_summary.json")
SOURCE_AUDIT = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_audit_summary.json")
EXPANSION_TARGETS = Path("analysis/integration_eval/teacher_divergence_expansion_targets/expansion_targets_summary.json")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_generation_preflight")
OUT_CSV = OUT_DIR / "tail_generation_prereq_manifest.csv"
OUT_JSON = OUT_DIR / "tail_generation_preflight_summary.json"
OUT_MD = OUT_DIR / "tail_generation_preflight_report.md"

LIKELY_REQUIRED_FILES = [
    Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
    Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),
    Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py"),
]

EXTERNAL_LIKELY_FILES = [
    Path("~/gomoku_public_benchmark/run_rapfi.sh").expanduser(),
    Path("~/gomoku_public_benchmark/rapfi").expanduser(),
    Path("~/gomoku_public_benchmark/Rapfi").expanduser(),
]


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def safe_read_text(path: Path, limit: int = 300_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def discover_files() -> list[Path]:
    patterns = [
        "scripts/*teacher*.py",
        "scripts/*rapfi*.py",
        "scripts/*policy*.py",
        "scripts/*margin*.py",
        "scripts/*multisuppress*.py",
        "scripts/*rank*topk*.py",
        "analysis/public_benchmark_eval/*teacher*",
        "analysis/public_benchmark_eval/*snapshot*",
        "analysis/integration_eval/*teacher*",
        "analysis/integration_eval/**/*teacher*",
        "analysis/integration_eval/**/*tail*",
        "analysis/integration_eval/**/*source*",
    ]
    out: list[Path] = []
    seen: set[str] = set()
    for pat in patterns:
        for p in Path(".").glob(pat):
            if p.is_file():
                s = str(p)
                if s not in seen:
                    seen.add(s)
                    out.append(p)
    return sorted(out, key=lambda p: str(p))


def classify_file(path: Path) -> dict[str, Any]:
    text = safe_read_text(path)
    lower = text.lower()

    kind = "unknown"
    if path.suffix == ".py":
        kind = "script"
    elif path.suffix == ".json":
        kind = "json"
    elif path.suffix == ".csv":
        kind = "csv"
    elif path.suffix == ".md":
        kind = "report"

    tags: list[str] = []
    for token, tag in [
        ("rapfi", "rapfi"),
        ("teacher", "teacher"),
        ("tail", "tail"),
        ("rank_gt50", "rank_gt50"),
        ("rank>50", "rank_gt50"),
        ("target_rc", "target_schema"),
        ("suppress_rcs", "multisuppress_schema"),
        ("before_target_rank", "rank_schema"),
        ("board", "board_schema"),
        ("checkpoint", "checkpoint"),
        ("torch.save", "save_sensitive"),
        ("out_checkpoint", "save_sensitive"),
        ("no-save", "nosave"),
        ("no checkpoint", "nosave"),
        ("policy", "policy"),
        ("margin", "margin"),
        ("topk", "topk"),
        ("top-k", "topk"),
    ]:
        if token in lower:
            tags.append(tag)

    has_board_schema = "board" in lower or "board_size" in lower
    has_teacher_schema = "teacher" in lower or "rapfi" in lower
    has_rank_schema = "rank" in lower or "before_target_rank" in lower
    has_multisuppress_schema = "suppress_rcs" in lower and "target_rc" in lower
    has_generation_signal = (
        path.suffix == ".py"
        and has_board_schema
        and has_teacher_schema
        and ("write_text" in lower or "csv" in lower or "json" in lower)
    )

    return {
        "kind": kind,
        "size": path.stat().st_size if path.exists() else 0,
        "tags": sorted(set(tags)),
        "has_board_schema": has_board_schema,
        "has_teacher_schema": has_teacher_schema,
        "has_rank_schema": has_rank_schema,
        "has_multisuppress_schema": has_multisuppress_schema,
        "has_generation_signal": has_generation_signal,
    }


def main() -> int:
    for p in [TAIL_SCHEMA_RECOVERY, TAIL_PLAN, SOURCE_AUDIT, EXPANSION_TARGETS]:
        if not p.exists():
            raise FileNotFoundError(p)

    tail_recovery = read_json(TAIL_SCHEMA_RECOVERY)
    tail_plan = read_json(TAIL_PLAN)
    source_audit = read_json(SOURCE_AUDIT)
    expansion_targets = read_json(EXPANSION_TARGETS)

    discovered = discover_files()

    rows: list[dict[str, Any]] = []

    for p in LIKELY_REQUIRED_FILES:
        info = classify_file(p) if p.exists() else {
            "kind": "missing",
            "size": 0,
            "tags": [],
            "has_board_schema": False,
            "has_teacher_schema": False,
            "has_rank_schema": False,
            "has_multisuppress_schema": False,
            "has_generation_signal": False,
        }
        rows.append({
            "path": str(p),
            "category": "required_repo_file",
            "exists": p.exists(),
            **info,
        })

    for p in EXTERNAL_LIKELY_FILES:
        rows.append({
            "path": str(p),
            "category": "external_teacher_engine_candidate",
            "exists": p.exists(),
            "kind": "external",
            "size": p.stat().st_size if p.exists() and p.is_file() else 0,
            "tags": ["rapfi", "teacher_engine"] if p.exists() else [],
            "has_board_schema": False,
            "has_teacher_schema": p.exists(),
            "has_rank_schema": False,
            "has_multisuppress_schema": False,
            "has_generation_signal": False,
        })

    for p in discovered:
        info = classify_file(p)
        rows.append({
            "path": str(p),
            "category": "discovered_repo_artifact",
            "exists": True,
            **info,
        })

    # Deduplicate rows by path/category pair, preserving category-specific required rows.
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for r in rows:
        key = (str(r["path"]), str(r["category"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    has_board_snapshots = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json").exists()
    has_current_b4c64 = Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt").exists()
    has_b4c96_probe = Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt").exists()
    has_nosave_wrapper = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py").exists()
    has_external_rapfi = any(p.exists() for p in EXTERNAL_LIKELY_FILES)

    generation_scripts = [
        r for r in deduped
        if r["kind"] == "script" and r["has_generation_signal"]
    ]
    multisuppress_artifacts = [
        r for r in deduped
        if r["has_multisuppress_schema"]
    ]

    tail_gap = int(tail_plan.get("tail_gap", 12))
    unique_tail_recovered = int(tail_recovery.get("unique_tail_recovered", 0))
    unique_materializable_tail = int(tail_recovery.get("unique_materializable_tail_recovered", 0))

    prereq_status = {
        "has_board_snapshots": has_board_snapshots,
        "has_current_b4c64_checkpoint": has_current_b4c64,
        "has_b4c96_probe_checkpoint": has_b4c96_probe,
        "has_nosave_wrapper": has_nosave_wrapper,
        "has_external_rapfi_candidate": has_external_rapfi,
        "generation_script_candidates": len(generation_scripts),
        "multisuppress_schema_artifacts": len(multisuppress_artifacts),
        "tail_gap": tail_gap,
        "unique_tail_recovered_from_old_sources": unique_tail_recovered,
        "unique_materializable_tail_from_old_sources": unique_materializable_tail,
    }

    has_local_generation_base = (
        has_board_snapshots
        and has_current_b4c64
        and has_b4c96_probe
        and has_nosave_wrapper
        and len(multisuppress_artifacts) > 0
    )

    if has_local_generation_base and has_external_rapfi:
        decision = "TAIL_GENERATION_PREFLIGHT_READY_WITH_LOCAL_TEACHER_ENGINE"
    elif has_local_generation_base:
        decision = "TAIL_GENERATION_PREFLIGHT_READY_BUT_TEACHER_ENGINE_UNCONFIRMED"
    else:
        decision = "TAIL_GENERATION_PREFLIGHT_BLOCKED_MISSING_LOCAL_PREREQS"

    next_actions = [
        {
            "order": 1,
            "action": "Build a tail candidate source generator that enumerates additional positions and scores model policy rank.",
            "requires": "board snapshots or expanded failure positions plus b4c64/b4c96 scoring path",
            "allowed": "yes",
            "training": "no",
        },
        {
            "order": 2,
            "action": "Attach or call Rapfi teacher only if a local teacher executable/script is available.",
            "requires": "run_rapfi.sh or equivalent local Rapfi command",
            "allowed": "conditional",
            "training": "no",
        },
        {
            "order": 3,
            "action": "Materialize tail candidates as heldout tail_guard rows only after >=12 valid rank>50 or near-tail candidates exist.",
            "requires": "candidate manifest with board/side/target/suppress_rcs/rank fields",
            "allowed": "later",
            "training": "no",
        },
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "path",
        "category",
        "exists",
        "kind",
        "size",
        "tags",
        "has_board_schema",
        "has_teacher_schema",
        "has_rank_schema",
        "has_multisuppress_schema",
        "has_generation_signal",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in deduped:
            row = dict(r)
            row["tags"] = ";".join(row.get("tags", []))
            w.writerow({k: row.get(k, "") for k in fields})

    summary = {
        "decision": decision,
        "scope": "preflight only; no source generation run/dataset build/training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "tail_schema_recovery": str(TAIL_SCHEMA_RECOVERY),
            "tail_plan": str(TAIL_PLAN),
            "source_audit": str(SOURCE_AUDIT),
            "expansion_targets": str(EXPANSION_TARGETS),
        },
        "upstream_decisions": {
            "tail_schema_recovery_decision": tail_recovery.get("decision"),
            "tail_plan_decision": tail_plan.get("decision"),
            "source_audit_decision": source_audit.get("decision"),
            "expansion_targets_decision": expansion_targets.get("decision"),
        },
        "prereq_status": prereq_status,
        "generation_script_candidates": [r["path"] for r in generation_scripts[:25]],
        "multisuppress_schema_artifacts": [r["path"] for r in multisuppress_artifacts[:25]],
        "next_actions": next_actions,
        "recommended_next_branch": "exp/15x15-teacher-divergence-tail-candidate-generator",
        "recommended_next_step": "Write a generator/review script for new tail guard candidates, guarded by no-training/no-checkpoint constraints.",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence tail generation preflight", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Preflight only.",
        "- No source generation run.",
        "- No dataset build.",
        "- No training.",
        "- No checkpoint read or write beyond file existence checks.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Upstream decisions", ""]
    for k, v in summary["upstream_decisions"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    lines += ["## Prerequisite status", ""]
    lines += ["| prereq | value |", "|---|---:|"]
    for k, v in prereq_status.items():
        lines.append(f"| {k} | `{v}` |")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    if decision == "TAIL_GENERATION_PREFLIGHT_READY_WITH_LOCAL_TEACHER_ENGINE":
        lines += [
            "Local prerequisites appear sufficient to design a guarded tail candidate generator with local teacher labeling.",
            "",
        ]
    elif decision == "TAIL_GENERATION_PREFLIGHT_READY_BUT_TEACHER_ENGINE_UNCONFIRMED":
        lines += [
            "Local repo prerequisites exist, but the external Rapfi teacher command was not confirmed by file existence checks.",
            "",
            "The next generator branch should either use an existing teacher-labeled source or require the user to provide/confirm the Rapfi command before teacher labeling.",
            "",
        ]
    else:
        lines += [
            "Required local prerequisites are missing. Do not write a generator until missing inputs are resolved.",
            "",
        ]

    lines += ["## Next actions", ""]
    lines += ["| order | action | requires | training |", "|---:|---|---|---|"]
    for row in next_actions:
        lines.append(
            f"| {row['order']} | {row['action']} | {row['requires']} | {row['training']} |"
        )
    lines.append("")

    lines += ["## Final note", ""]
    lines += [
        "This preflight does not authorize source generation into a train dataset, training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("prereq_status:", prereq_status)
    print("generation_script_candidates:", len(generation_scripts))
    print("multisuppress_schema_artifacts:", len(multisuppress_artifacts))
    print("out_csv:", OUT_CSV)
    print("out_json:", OUT_JSON)
    print("out_report:", OUT_MD)
    print("status: preflight only; no source generation/dataset build/training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
