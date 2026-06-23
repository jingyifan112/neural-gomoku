#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Review why run1 next stage routed to blocked review."
    )
    p.add_argument(
        "--dispatch-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch_summary.csv"),
    )
    p.add_argument(
        "--dispatch-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch_decision.json"),
    )
    p.add_argument(
        "--followup-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_followup_summary.csv"),
    )
    p.add_argument(
        "--followup-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_followup_decision.json"),
    )
    p.add_argument(
        "--route-aware-next-stage-spec",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_spec.json"),
    )
    p.add_argument(
        "--route-aware-next-stage-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_summary.csv"),
    )
    p.add_argument(
        "--route-aware-local-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_local_decision_summary.csv"),
    )
    p.add_argument(
        "--post-adapter-route-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_summary.csv"),
    )
    p.add_argument(
        "--direct-adapter-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--candidate-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt"),
    )
    p.add_argument(
        "--current-best-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_blocker_review_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_blocker_review.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metric_map(path: Path) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in read_csv(path)}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def notes(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("notes", default)


def as_int(v: Any) -> int:
    if v in ("", None):
        return 0
    return int(float(v))


def as_float(v: Any) -> float:
    if v in ("", None):
        return 0.0
    return float(v)


def row(metric: str, value: Any, status: str, notes_text: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes_text,
    }


def combined_metric(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for r in rows:
        if r.get("metric") == metric:
            return r.get("value", default)
    return default


def main() -> None:
    args = parse_args()

    required = [
        args.dispatch_summary,
        args.dispatch_decision_json,
        args.followup_summary,
        args.followup_decision_json,
        args.route_aware_next_stage_spec,
        args.route_aware_next_stage_summary,
        args.route_aware_local_summary,
        args.post_adapter_route_summary,
        args.direct_adapter_summary,
        args.direct_manifest,
        args.combined_summary,
        args.current_best_checkpoint,
    ]
    for p in required:
        if not p.exists():
            raise FileNotFoundError(p)

    dispatch = metric_map(args.dispatch_summary)
    followup = metric_map(args.followup_summary)
    route_next = metric_map(args.route_aware_next_stage_summary)
    route_local = metric_map(args.route_aware_local_summary)
    post_adapter = metric_map(args.post_adapter_route_summary)
    direct = metric_map(args.direct_adapter_summary)

    dispatch_json = json.loads(args.dispatch_decision_json.read_text(encoding="utf-8"))
    followup_json = json.loads(args.followup_decision_json.read_text(encoding="utf-8"))
    route_spec = json.loads(args.route_aware_next_stage_spec.read_text(encoding="utf-8"))

    manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    combined_fail_rows = [r for r in combined if r.get("status") == "FAIL"]
    combined_warn_rows = [r for r in combined if r.get("status") == "WARN"]

    trainable_gap_improved = as_int(combined_metric(combined, "gap_improved_rows"))
    trainable_rank_regressed = as_int(combined_metric(combined, "target_rank_regressed_rows"))
    protected_rank_regressed = as_int(combined_metric(combined, "protected_top10_rank_regressed_rows"))
    protected_prob_regressed = as_int(combined_metric(combined, "protected_top10_prob_regressed_rows"))
    tail_rank_regressed = as_int(combined_metric(combined, "tail_rank_gt50_rank_regressed_rows"))
    tail_prob_regressed = as_int(combined_metric(combined, "tail_rank_gt50_prob_regressed_rows"))
    anchor_top1_changed = as_int(combined_metric(combined, "anchor_top1_changed_rows"))
    anchor_max_kl = as_float(combined_metric(combined, "anchor_max_kl"))

    blocker_sources: list[str] = []
    warning_sources: list[str] = []

    for label, m in [
        ("direct_adapter", direct),
        ("post_adapter_route", post_adapter),
        ("route_aware_local", route_local),
        ("route_aware_next_stage", route_next),
        ("dispatch", dispatch),
        ("followup", followup),
    ]:
        bc = as_int(get(m, "blocker_count"))
        wc = as_int(get(m, "warning_count"))
        if bc:
            blocker_sources.append(f"{label}: blocker_count={bc}; {notes(m, 'blocker_count')}")
        if wc:
            warning_sources.append(f"{label}: warning_count={wc}; {notes(m, 'warning_count')}")

    for label, d in [
        ("dispatch_json", dispatch_json),
        ("followup_json", followup_json),
        ("route_next_spec", route_spec),
    ]:
        b = d.get("blockers") or []
        w = d.get("warnings") or []
        if b:
            blocker_sources.append(f"{label}: " + "; ".join(map(str, b)))
        if w:
            warning_sources.append(f"{label}: " + "; ".join(map(str, w)))

    root_causes: list[str] = []
    actions: list[str] = []

    if not candidate_exists:
        root_causes.append("candidate_checkpoint_missing_locally")
        actions.append("Restore or rerun the isolated run1 candidate checkpoint locally before any model-eval path.")
    if not current_best_exists:
        root_causes.append("current_best_checkpoint_missing")
        actions.append("Restore current_best checkpoint path before continuing.")
    if len(combined_fail_rows) > 0:
        root_causes.append("core_reuse_combined_fail_rows")
        actions.append("Inspect combined local comparison FAIL rows before continuing.")
    if trainable_gap_improved != 44:
        root_causes.append("trainable_gap_not_full_improvement")
        actions.append("Do not continue toward eval; revisit training/gate assumptions.")
    if trainable_rank_regressed > 0 or protected_rank_regressed > 0 or tail_rank_regressed > 0:
        root_causes.append("rank_regression_present")
        actions.append("Treat as hard gate failure; repair before continuing.")
    if anchor_top1_changed > 0 or anchor_max_kl > 0.005:
        root_causes.append("anchor_drift_hard_failure")
        actions.append("Treat as hard anchor drift failure; repair before continuing.")
    if get(direct, "adapter_decision") == "DIRECT_PROBE_EVAL_ADAPTER_BLOCKED":
        root_causes.append("direct_probe_adapter_blocked")
        actions.append("Inspect direct adapter blocker notes; likely direct-probe path is not ready.")
    if as_int(get(direct, "direct_ready_inputs_from_selection")) == 0 and len(manifest) == 0:
        root_causes.append("no_direct_ready_inputs")
        actions.append("Prefer core-reuse local decision closeout, or build a narrow adapter for one reviewed fixed-probe source.")
    if protected_prob_regressed > 0 or tail_prob_regressed > 0:
        root_causes.append("probability_regression_warnings_remain")
        actions.append("Carry warnings forward; do not promote without later fixed-probe/heldout evidence.")

    if not root_causes:
        root_causes.append("blocked_route_without_detected_hard_metric_failure")
        actions.append("Inspect generated route scripts for overly strict routing; consider redirect to core-reuse local decision closeout.")

    hard_metric_failure = any(c in root_causes for c in [
        "candidate_checkpoint_missing_locally",
        "current_best_checkpoint_missing",
        "core_reuse_combined_fail_rows",
        "trainable_gap_not_full_improvement",
        "rank_regression_present",
        "anchor_drift_hard_failure",
    ])

    if hard_metric_failure:
        review_decision = "BLOCKED_REVIEW_CONFIRMS_HARD_BLOCKER"
    elif "no_direct_ready_inputs" in root_causes:
        review_decision = "BLOCKED_REVIEW_RECOMMENDS_CORE_REUSE_CLOSEOUT"
    else:
        review_decision = "BLOCKED_REVIEW_RECOMMENDS_ROUTING_PATCH_OR_CORE_CLOSEOUT"

    summary_rows = [
        row("review_decision", review_decision, "INFO", "Blocked review only; no model eval."),
        row("root_cause_count", len(root_causes), "INFO", "; ".join(root_causes)),
        row("action_count", len(actions), "INFO", "; ".join(actions)),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Existence only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("direct_manifest_rows", len(manifest), "INFO"),
        row("direct_ready_inputs_from_selection", get(direct, "direct_ready_inputs_from_selection"), "INFO"),
        row("direct_adapter_decision", get(direct, "adapter_decision"), "INFO"),
        row("post_adapter_final_route_decision", get(post_adapter, "final_route_decision"), "INFO"),
        row("route_aware_local_decision", get(route_local, "local_decision"), "INFO"),
        row("route_aware_next_stage_decision", get(route_next, "next_stage_decision"), "INFO"),
        row("dispatch_decision", get(dispatch, "dispatch_decision"), "INFO"),
        row("followup_decision", get(followup, "followup_decision"), "INFO"),
        row("combined_fail_rows", len(combined_fail_rows), "PASS" if not combined_fail_rows else "FAIL"),
        row("combined_warn_rows", len(combined_warn_rows), "WARN" if combined_warn_rows else "PASS"),
        row("trainable_gap_improved", trainable_gap_improved, "PASS" if trainable_gap_improved == 44 else "FAIL"),
        row("trainable_rank_regressed", trainable_rank_regressed, "PASS" if trainable_rank_regressed == 0 else "FAIL"),
        row("protected_rank_regressed", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        row("tail_rank_regressed", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        row("protected_prob_regressed", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        row("tail_prob_regressed", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        row("anchor_top1_changed", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
        row("would_train", 0, "PASS"),
        row("would_eval_model_now", 0, "PASS"),
        row("would_read_checkpoint_contents_now", 0, "PASS"),
        row("would_write_checkpoint", 0, "PASS"),
        row("would_c_export", 0, "PASS"),
        row("would_public_benchmark", 0, "PASS"),
        row("would_promote", 0, "PASS"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    report = [
        "# Teacher-divergence run1 next-stage blocked review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-next-stage-blocked-review`",
        "",
        "## Scope",
        "",
        "- Reviews why the route-aware next stage became blocked.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Review decision",
        "",
        f"`{review_decision}`",
        "",
        "## Root causes",
        "",
    ]
    for c in root_causes:
        report.append(f"- {c}")

    report.extend([
        "",
        "## Recommended actions",
        "",
    ])
    for a in actions:
        report.append(f"- {a}")

    report.extend([
        "",
        "## Blocker source trace",
        "",
    ])
    if blocker_sources:
        for b in blocker_sources:
            report.append(f"- {b}")
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Warning source trace",
        "",
    ])
    if warning_sources:
        for w in warning_sources:
            report.append(f"- {w}")
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])
    for r in summary_rows:
        report.append(f"| {r['metric']} | {r['value']} | {r['status']} | {r['notes'].replace('|', '\\|')} |")

    report.extend([
        "",
        "## Interpretation",
        "",
    ])

    if review_decision == "BLOCKED_REVIEW_CONFIRMS_HARD_BLOCKER":
        report.append("The blocked route is justified by at least one hard blocker. Do not continue until the blocker is fixed.")
    elif review_decision == "BLOCKED_REVIEW_RECOMMENDS_CORE_REUSE_CLOSEOUT":
        report.append("The main issue appears to be lack of direct-ready inputs, not a hard core metric failure. Prefer a core-reuse local decision closeout, keeping the run1 candidate isolated.")
    else:
        report.append("The route appears blocked without a clear hard metric failure. Consider either patching the routing logic or making a conservative core-reuse local decision closeout.")

    report.extend([
        "",
        "## Final guardrails",
        "",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")

    print("review_decision:", review_decision)
    print("root_causes:", ";".join(root_causes))
    print("actions:", ";".join(actions))
    print("candidate_checkpoint_exists_locally:", int(candidate_exists))
    print("current_best_exists:", int(current_best_exists))
    print("direct_manifest_rows:", len(manifest))
    print("combined_fail_rows:", len(combined_fail_rows))
    print("combined_warn_rows:", len(combined_warn_rows))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("blocked review only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
