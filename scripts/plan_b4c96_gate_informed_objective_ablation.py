#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_FORENSICS_SUMMARY = "analysis/integration_eval/b4c96_stagec_failure_forensics_summary.json"
DEFAULT_OUT_CSV = "analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.csv"
DEFAULT_OUT_JSON = "analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.json"
DEFAULT_OUT_MD = "analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.md"


SCRIPT_CANDIDATES = [
    "scripts/train_rapfi_teacher_policy_rank_topk_probe.py",
    "scripts/probe_policy_rank_topk_protected_nosave.py",
    "scripts/evaluate_policy_rank_topk_gate_b4c96.py",
]


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def has_any(text: str, needles: list[str]) -> bool:
    return any(n in text for n in needles)


def extract_add_arguments(text: str) -> list[str]:
    args = []
    for line in text.splitlines():
        m = re.search(r"add_argument\(([^)]*)\)", line)
        if not m:
            continue
        chunk = m.group(1)
        arg = chunk.split(",")[0].strip().strip("'").strip('"')
        if arg.startswith("--"):
            args.append(arg)
    return args


def inspect_script(path: Path) -> dict:
    text = read_text(path)
    args = extract_add_arguments(text)
    arg_set = set(args)
    arch_args = [
        "--channels",
        "--blocks",
        "--model-channels",
        "--model-blocks",
        "--model-a-channels",
        "--model-a-blocks",
        "--model-b-channels",
        "--model-b-blocks",
        "--board-size",
        "--win-length",
    ]
    return {
        "script": str(path),
        "exists": path.exists(),
        "add_arguments": args,
        "has_no_save": "--no-save" in arg_set or "--dry-run" in arg_set or "nosave" in path.name,
        "has_out_checkpoint": "--out-checkpoint" in arg_set,
        "has_architecture_args": any(a in arg_set for a in arch_args),
        "has_b4c96_dual_arch_args": {
            "--model-a-channels",
            "--model-a-blocks",
            "--model-b-channels",
            "--model-b-blocks",
        }.issubset(arg_set),
        "imports_load_compatible_checkpoint": "load_compatible_checkpoint" in text,
        "mentions_channels_blocks": has_any(text, ["channels", "blocks", "num_channels", "num_blocks"]),
    }


def ablation_rows(summary: dict) -> list[dict]:
    hard_fail_reasons = set(summary.get("hard_fail_reasons", []))
    failure_tags = summary.get("failure_tags", {})

    rows = [
        {
            "ablation_id": "A0_failed_stagec_reference_replay",
            "purpose": "Reference row only; records the failed Stage C behavior already observed.",
            "ce_weight": "",
            "pair_weight": "",
            "worst_weight": "",
            "anchor_kl_weight": "",
            "tail_policy": "none",
            "protected_policy": "none",
            "expected_signal": "baseline_failed_gate",
            "run_now": "no",
            "blocker": "already completed; no rerun needed",
        },
        {
            "ablation_id": "A1_stronger_anchor_balanced_hinge",
            "purpose": "Test whether stronger anchor pressure reduces protected/top5 regression while keeping pair/worst repair active.",
            "ce_weight": "1.0",
            "pair_weight": "0.6",
            "worst_weight": "0.6",
            "anchor_kl_weight": "1.0",
            "tail_policy": "unchanged",
            "protected_policy": "strong_anchor",
            "expected_signal": "protected_regression_down_without_destroying_top10_gain",
            "run_now": "blocked",
            "blocker": "needs b4c96-safe no-save wrapper with architecture args",
        },
        {
            "ablation_id": "A2_light_worst_suppress",
            "purpose": "Test whether reducing worst-suppress pressure avoids severe core regressions from over-suppressing local alternatives.",
            "ce_weight": "1.0",
            "pair_weight": "0.6",
            "worst_weight": "0.2",
            "anchor_kl_weight": "0.8",
            "tail_policy": "unchanged",
            "protected_policy": "anchor_guarded",
            "expected_signal": "fewer worst_gap/hinge regressions",
            "run_now": "blocked",
            "blocker": "needs b4c96-safe no-save wrapper with architecture args",
        },
        {
            "ablation_id": "A3_ce_dominant_rank_repair",
            "purpose": "Test CE-dominant target lift while keeping hinge pressure weak.",
            "ce_weight": "1.5",
            "pair_weight": "0.3",
            "worst_weight": "0.1",
            "anchor_kl_weight": "0.8",
            "tail_policy": "unchanged",
            "protected_policy": "anchor_guarded",
            "expected_signal": "top5/top10 improves with less severe core regression",
            "run_now": "blocked",
            "blocker": "needs b4c96-safe no-save wrapper with architecture args",
        },
        {
            "ablation_id": "A4_tail_capped_training_set",
            "purpose": "Test whether tail rank>50 rows should be capped/pruned before b4c96 training.",
            "ce_weight": "1.0",
            "pair_weight": "0.5",
            "worst_weight": "0.3",
            "anchor_kl_weight": "1.0",
            "tail_policy": "cap_or_prune_rank_gt50",
            "protected_policy": "strong_anchor",
            "expected_signal": "rank_gt50_delta_nonpositive_and_mean_rank_not_worse",
            "run_now": "blocked",
            "blocker": "existing no-save probe has no tail cap/prune option; wrapper/dataset adapter required",
        },
        {
            "ablation_id": "A5_severe_regression_family_downweight",
            "purpose": "Downweight case_ids/games that produced severe core regressions in Stage C.",
            "ce_weight": "1.0",
            "pair_weight": "0.5",
            "worst_weight": "0.3",
            "anchor_kl_weight": "1.0",
            "tail_policy": "tail_cap",
            "protected_policy": "strong_anchor",
            "expected_signal": "reduce g2/g5 severe regression concentration",
            "run_now": "blocked",
            "blocker": "existing no-save probe has no per-row/family reweight option; wrapper/dataset adapter required",
        },
    ]

    if "protected_top10_regression_nonzero" in hard_fail_reasons:
        rows.append(
            {
                "ablation_id": "REQUIRED_GATE_CONSTRAINT_protected",
                "purpose": "Any executable ablation must report protected top10 regression count.",
                "ce_weight": "",
                "pair_weight": "",
                "worst_weight": "",
                "anchor_kl_weight": "",
                "tail_policy": "",
                "protected_policy": "hard_guard",
                "expected_signal": "protected_top10_regression == 0",
                "run_now": "constraint",
                "blocker": "",
            }
        )

    if failure_tags.get("core_regressed", 0) >= 10:
        rows.append(
            {
                "ablation_id": "REQUIRED_GATE_CONSTRAINT_core_regression",
                "purpose": "Any executable ablation must separate useful rows from severe core regressions.",
                "ce_weight": "",
                "pair_weight": "",
                "worst_weight": "",
                "anchor_kl_weight": "",
                "tail_policy": "",
                "protected_policy": "",
                "expected_signal": "severe_core_regression materially below 10",
                "run_now": "constraint",
                "blocker": "",
            }
        )

    return rows


def build_summary(forensics: dict, inspections: list[dict], rows: list[dict]) -> dict:
    train_script = next((x for x in inspections if x["script"].endswith("train_rapfi_teacher_policy_rank_topk_probe.py")), {})
    nosave_script = next((x for x in inspections if x["script"].endswith("probe_policy_rank_topk_protected_nosave.py")), {})
    gate_script = next((x for x in inspections if x["script"].endswith("evaluate_policy_rank_topk_gate_b4c96.py")), {})

    direct_b4c96_nosave_safe = bool(
        nosave_script.get("exists")
        and nosave_script.get("has_no_save")
        and nosave_script.get("has_architecture_args")
    )

    gate_b4c96_safe = bool(gate_script.get("exists") and gate_script.get("has_b4c96_dual_arch_args"))

    if not direct_b4c96_nosave_safe:
        decision = "ABLATION_PLAN_READY_EXECUTION_BLOCKED_NEEDS_B4C96_SAFE_NOSAVE_WRAPPER"
    elif not gate_b4c96_safe:
        decision = "ABLATION_PLAN_BLOCKED_GATE_NOT_B4C96_SAFE"
    else:
        decision = "ABLATION_PLAN_READY_FOR_NOSAVE_EXECUTION"

    return {
        "branch": "exp/15x15-b4c96-gate-informed-objective-ablation",
        "source_forensics": DEFAULT_FORENSICS_SUMMARY,
        "forensics_diagnosis": forensics.get("diagnosis"),
        "forensics_hard_fail_reasons": forensics.get("hard_fail_reasons", []),
        "forensics_key_counts": {
            "rows": forensics.get("rows"),
            "top5_delta": forensics.get("topk", {}).get("top5_delta"),
            "rank_gt50_delta": forensics.get("topk", {}).get("rank_gt50_delta"),
            "severe_core_regression": forensics.get("outcomes", {}).get("severe_core_regression"),
            "directionally_useful": forensics.get("outcomes", {}).get("directionally_useful"),
            "protected_top10_regression": forensics.get("failure_tags", {}).get("protected_top10_regression"),
        },
        "compatibility": {
            "rank_topk_train_script_has_nosave": train_script.get("has_no_save"),
            "rank_topk_train_script_has_architecture_args": train_script.get("has_architecture_args"),
            "protected_nosave_script_has_nosave": nosave_script.get("has_no_save"),
            "protected_nosave_script_has_architecture_args": nosave_script.get("has_architecture_args"),
            "b4c96_gate_has_dual_arch_args": gate_b4c96_safe,
            "direct_b4c96_nosave_safe": direct_b4c96_nosave_safe,
        },
        "script_inspections": inspections,
        "ablation_rows": len(rows),
        "decision": decision,
        "next_required_action": (
            "Create a b4c96-safe no-save objective ablation wrapper before running any ablation. "
            "The wrapper must expose board-size, win-length, channels, blocks, no-save, and per-ablation weights."
        ),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "ablation_id",
        "purpose",
        "ce_weight",
        "pair_weight",
        "worst_weight",
        "anchor_kl_weight",
        "tail_policy",
        "protected_policy",
        "expected_signal",
        "run_now",
        "blocker",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def md_table(rows: list[dict], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for r in rows:
        vals = [str(r.get(f, "")).replace("\n", " ") for f in fields]
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def write_md(path: Path, summary: dict, rows: list[dict]) -> None:
    lines = []
    lines.append("# b4c96 gate-informed objective ablation plan")
    lines.append("")
    lines.append("## Branch")
    lines.append("")
    lines.append("`exp/15x15-b4c96-gate-informed-objective-ablation`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Planning and compatibility audit only.")
    lines.append("- No training, no checkpoint read, no checkpoint write, no C export, no public benchmark, no promotion.")
    lines.append("")
    lines.append("## Source diagnosis")
    lines.append("")
    lines.append(f"- Forensics diagnosis: `{summary['forensics_diagnosis']}`")
    lines.append(f"- Rows: `{summary['forensics_key_counts']['rows']}`")
    lines.append(f"- Top-5 delta: `{summary['forensics_key_counts']['top5_delta']}`")
    lines.append(f"- Rank>50 delta: `{summary['forensics_key_counts']['rank_gt50_delta']}`")
    lines.append(f"- Severe core regression rows: `{summary['forensics_key_counts']['severe_core_regression']}`")
    lines.append(f"- Directionally useful rows: `{summary['forensics_key_counts']['directionally_useful']}`")
    lines.append(f"- Protected top-10 regression rows: `{summary['forensics_key_counts']['protected_top10_regression']}`")
    lines.append("")
    lines.append("## Compatibility audit")
    lines.append("")
    compat_rows = [{"key": k, "value": v} for k, v in summary["compatibility"].items()]
    lines.extend(md_table(compat_rows, ["key", "value"]))
    lines.append("")
    lines.append("## Ablation plan")
    lines.append("")
    lines.extend(
        md_table(
            rows,
            [
                "ablation_id",
                "ce_weight",
                "pair_weight",
                "worst_weight",
                "anchor_kl_weight",
                "tail_policy",
                "protected_policy",
                "run_now",
                "blocker",
            ],
        )
    )
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"`{summary['decision']}`")
    lines.append("")
    lines.append("## Next required action")
    lines.append("")
    lines.append(summary["next_required_action"])
    lines.append("")
    lines.append("## Final note")
    lines.append("")
    lines.append("Do not execute b4c96 no-save ablations through the existing protected probe until a b4c96-safe wrapper exists.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forensics-summary", default=DEFAULT_FORENSICS_SUMMARY)
    ap.add_argument("--out-csv", default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    forensics_path = Path(args.forensics_summary)
    if not forensics_path.exists():
        raise SystemExit(f"missing forensics summary: {forensics_path}")

    forensics = json.loads(forensics_path.read_text())
    inspections = [inspect_script(Path(p)) for p in SCRIPT_CANDIDATES]
    rows = ablation_rows(forensics)
    summary = build_summary(forensics, inspections, rows)

    write_csv(Path(args.out_csv), rows)
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_md(Path(args.out_md), summary, rows)

    print("wrote:", args.out_csv)
    print("wrote:", args.out_json)
    print("wrote:", args.out_md)
    print("decision:", summary["decision"])
    print("direct_b4c96_nosave_safe:", summary["compatibility"]["direct_b4c96_nosave_safe"])


if __name__ == "__main__":
    main()
