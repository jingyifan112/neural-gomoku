#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_generator_input_inspection")
OUT_JSON = OUT_DIR / "tail_generator_input_inspection_summary.json"
OUT_MD = OUT_DIR / "tail_generator_input_inspection_report.md"

INPUT_PATHS = {
    "board_snapshots": Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    "base_multisuppress_dataset": Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"),
    "base_margin_dataset": Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
    "b4c96_nosave_wrapper": Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py"),
    "rank_topk_gate": Path("scripts/evaluate_policy_rank_topk_gate_b4c96.py"),
    "tail_preflight": Path("analysis/integration_eval/teacher_divergence_tail_generation_preflight/tail_generation_preflight_summary.json"),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_text(path: Path, limit: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def walk_lists(obj: Any, path: str = "$") -> list[tuple[str, int, Any]]:
    out = []
    if isinstance(obj, list):
        sample = obj[0] if obj else None
        out.append((path, len(obj), sample))
        for i, v in enumerate(obj[:3]):
            out.extend(walk_lists(v, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(walk_lists(v, f"{path}.{k}"))
    return out


def walk_dicts(obj: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    out = []
    if isinstance(obj, dict):
        out.append((path, obj))
        for k, v in obj.items():
            out.extend(walk_dicts(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            out.extend(walk_dicts(v, f"{path}[{i}]"))
    return out


def summarize_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    obj = read_json(path)
    lists = walk_lists(obj)
    dicts = walk_dicts(obj)

    candidate_lists = []
    for p, n, sample in lists:
        keys = sorted(sample.keys()) if isinstance(sample, dict) else []
        candidate_lists.append({
            "path": p,
            "length": n,
            "sample_type": type(sample).__name__,
            "sample_keys": keys[:80],
        })

    key_counter = Counter()
    dict_examples = []
    for p, d in dicts:
        for k in d.keys():
            key_counter[str(k)] += 1
        if len(dict_examples) < 8:
            dict_examples.append({
                "path": p,
                "keys": sorted(map(str, d.keys()))[:80],
            })

    return {
        "exists": True,
        "type": type(obj).__name__,
        "top_keys": sorted(obj.keys()) if isinstance(obj, dict) else [],
        "candidate_lists": candidate_lists[:20],
        "common_keys": key_counter.most_common(80),
        "dict_examples": dict_examples,
    }


def summarize_script(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    text = safe_text(path)
    lines = text.splitlines()

    functions = []
    classes = []
    arg_lines = []
    checkpoint_lines = []
    save_lines = []
    rapfi_lines = []
    rank_lines = []
    dataset_lines = []

    for i, line in enumerate(lines, start=1):
        s = line.strip()
        if s.startswith("def "):
            functions.append({"line": i, "text": s})
        if s.startswith("class "):
            classes.append({"line": i, "text": s})
        if "add_argument" in s:
            arg_lines.append({"line": i, "text": s[:220]})
        if "checkpoint" in s.lower() or "load_model" in s or "load_compatible_checkpoint" in s:
            checkpoint_lines.append({"line": i, "text": s[:220]})
        if "torch.save" in s or "out_checkpoint" in s:
            save_lines.append({"line": i, "text": s[:220]})
        if "rapfi" in s.lower():
            rapfi_lines.append({"line": i, "text": s[:220]})
        if "rank" in s.lower() or "topk" in s.lower() or "top_k" in s.lower():
            rank_lines.append({"line": i, "text": s[:220]})
        if "samples" in s or "protected" in s or "tail" in s or "suppress_rcs" in s:
            dataset_lines.append({"line": i, "text": s[:220]})

    return {
        "exists": True,
        "line_count": len(lines),
        "functions": functions,
        "classes": classes,
        "arg_lines": arg_lines[:80],
        "checkpoint_lines": checkpoint_lines[:80],
        "save_lines": save_lines[:40],
        "rapfi_lines": rapfi_lines[:80],
        "rank_lines": rank_lines[:80],
        "dataset_lines": dataset_lines[:100],
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    json_summaries = {}
    for name in [
        "board_snapshots",
        "base_multisuppress_dataset",
        "base_margin_dataset",
        "tail_preflight",
    ]:
        json_summaries[name] = summarize_json(INPUT_PATHS[name])

    script_summaries = {}
    for name in [
        "b4c96_nosave_wrapper",
        "rank_topk_gate",
    ]:
        script_summaries[name] = summarize_script(INPUT_PATHS[name])

    preflight = read_json(INPUT_PATHS["tail_preflight"]) if INPUT_PATHS["tail_preflight"].exists() else {}

    board_summary = json_summaries["board_snapshots"]
    multisuppress_summary = json_summaries["base_multisuppress_dataset"]

    likely_snapshot_list = None
    if board_summary.get("exists"):
        for item in board_summary.get("candidate_lists", []):
            keys = set(item.get("sample_keys", []))
            if {"board", "side"} & keys or {"moves", "winner", "game_id"} & keys:
                likely_snapshot_list = item
                break

    likely_sample_list = None
    if multisuppress_summary.get("exists"):
        for item in multisuppress_summary.get("candidate_lists", []):
            keys = set(item.get("sample_keys", []))
            if {"target_rc", "suppress_rcs"} <= keys or {"teacher_move", "target_rc"} <= keys:
                likely_sample_list = item
                break

    decision = (
        "TAIL_GENERATOR_INPUTS_INSPECTED_READY_FOR_DRAFT"
        if likely_snapshot_list and likely_sample_list
        else "TAIL_GENERATOR_INPUTS_INSPECTED_NEED_MANUAL_SCHEMA_PATCH"
    )

    summary = {
        "decision": decision,
        "scope": "input/schema inspection only; no source generation/dataset build/training/checkpoint/export/benchmark/promotion",
        "inputs": {k: str(v) for k, v in INPUT_PATHS.items()},
        "upstream_preflight_decision": preflight.get("decision"),
        "tail_gap": preflight.get("prereq_status", {}).get("tail_gap"),
        "json_summaries": json_summaries,
        "script_summaries": script_summaries,
        "likely_snapshot_list": likely_snapshot_list,
        "likely_multisuppress_sample_list": likely_sample_list,
        "recommended_next": (
            "Draft guarded tail candidate generator using inspected schemas."
            if decision == "TAIL_GENERATOR_INPUTS_INSPECTED_READY_FOR_DRAFT"
            else "Patch generator assumptions manually from report before drafting generator."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines += ["# Teacher-divergence tail generator input inspection", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Input/schema inspection only.",
        "- No source generation run.",
        "- No dataset build.",
        "- No training.",
        "- No checkpoint read/write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Upstream", ""]
    lines += [
        f"- preflight decision: `{preflight.get('decision')}`",
        f"- tail gap: `{preflight.get('prereq_status', {}).get('tail_gap')}`",
        "",
    ]

    lines += ["## JSON inputs", ""]
    for name, s in json_summaries.items():
        lines += [f"### {name}", ""]
        lines += [f"- exists: `{s.get('exists')}`"]
        if s.get("exists"):
            lines += [f"- type: `{s.get('type')}`"]
            lines += [f"- top keys: `{s.get('top_keys')}`"]
            lines += ["- candidate lists:"]
            for item in s.get("candidate_lists", [])[:8]:
                lines.append(
                    f"  - `{item['path']}` len={item['length']} sample_type={item['sample_type']} keys={item['sample_keys'][:30]}"
                )
            lines += ["- common keys:"]
            lines.append("  - " + ", ".join([f"{k}:{v}" for k, v in s.get("common_keys", [])[:30]]))
        lines.append("")

    lines += ["## Script inputs", ""]
    for name, s in script_summaries.items():
        lines += [f"### {name}", ""]
        lines += [f"- exists: `{s.get('exists')}`"]
        if s.get("exists"):
            lines += [f"- line_count: `{s.get('line_count')}`"]
            lines += ["- functions:"]
            for fn in s.get("functions", [])[:30]:
                lines.append(f"  - L{fn['line']}: `{fn['text']}`")
            lines += ["- checkpoint-related lines:"]
            for row in s.get("checkpoint_lines", [])[:20]:
                lines.append(f"  - L{row['line']}: `{row['text']}`")
            lines += ["- dataset-related lines:"]
            for row in s.get("dataset_lines", [])[:30]:
                lines.append(f"  - L{row['line']}: `{row['text']}`")
        lines.append("")

    lines += ["## Inferred schema anchors", ""]
    lines += [
        f"- likely snapshot list: `{likely_snapshot_list}`",
        f"- likely multisuppress sample list: `{likely_sample_list}`",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    lines += ["## Final note", ""]
    lines += [
        "This inspection does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("upstream_preflight_decision:", preflight.get("decision"))
    print("tail_gap:", preflight.get("prereq_status", {}).get("tail_gap"))
    print("likely_snapshot_list:", likely_snapshot_list)
    print("likely_multisuppress_sample_list:", likely_sample_list)
    print("out_json:", OUT_JSON)
    print("out_report:", OUT_MD)
    print("status: schema/input inspection only; no generation/dataset build/training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
