#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


CORE_REUSE = "BLOCKED_REVIEW_RECOMMENDS_CORE_REUSE_CLOSEOUT"
ROUTING_OR_CORE = "BLOCKED_REVIEW_RECOMMENDS_ROUTING_PATCH_OR_CORE_CLOSEOUT"
HARD_BLOCKER = "BLOCKED_REVIEW_CONFIRMS_HARD_BLOCKER"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Follow up run1 next-stage blocker review with conservative closeout routing."
    )
    p.add_argument(
        "--blocker-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_blocker_review_summary.csv"),
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
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_blocker_followup_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_blocker_followup_decision.json"),
    )
    p.add_argument(
        "--out-next-plan",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_blocker_followup_next_plan.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_blocker_followup.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def notes(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("notes", default)


def as_int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


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

    for p in [
        args.blocker_summary,
        args.followup_summary,
        args.followup_decision_json,
        args.dispatch_summary,
        args.dispatch_decision_json,
        args.combined_summary,
        args.direct_manifest,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    blocker = by_metric(read_csv(args.blocker_summary))
    followup = by_metric(read_csv(args.followup_summary))
    dispatch = by_metric(read_csv(args.dispatch_summary))
    followup_json = json.loads(args.followup_decision_json.read_text(encoding="utf-8"))
    dispatch_json = json.loads(args.dispatch_decision_json.read_text(encoding="utf-8"))
    combined = read_csv(args.combined_summary)
    manifest = read_csv(args.direct_manifest)

    review_decision = get(blocker, "review_decision")
    root_causes = get(blocker, "root_cause_count")
    root_cause_notes = notes(blocker, "root_cause_count")
    action_notes = notes(blocker, "action_count")

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

    blockers: list[str] = []
    warnings: list[str] = []

    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint path missing locally")
    if combined_fail_rows:
        blockers.append(f"combined local comparison FAIL rows present: {len(combined_fail_rows)}")
    if trainable_gap_improved != 44:
        blockers.append(f"trainable gap improved rows not 44: {trainable_gap_improved}")
    if trainable_rank_regressed > 0:
        blockers.append(f"trainable rank regressions present: {trainable_rank_regressed}")
    if protected_rank_regressed > 0:
        blockers.append(f"protected rank regressions present: {protected_rank_regressed}")
    if tail_rank_regressed > 0:
        blockers.append(f"tail rank regressions present: {tail_rank_regressed}")
    if anchor_top1_changed > 0:
        blockers.append(f"anchor top1 changes present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        blockers.append(f"anchor max KL too high: {anchor_max_kl:.10f}")

    if combined_warn_rows:
        warnings.append(f"combined WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed > 0:
        warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")

    for label, d in [("followup_json", followup_json), ("dispatch_json", dispatch_json)]:
        for item in d.get("warnings") or []:
            warnings.append(f"{label}: {item}")
        for item in d.get("blockers") or []:
            if review_decision == HARD_BLOCKER:
                blockers.append(f"{label}: {item}")

    if review_decision == CORE_REUSE:
        if blockers:
            followup_decision = "CORE_REUSE_CLOSEOUT_BLOCKED_BY_HARD_METRIC"
            recommended_next = "Fix hard blocker before any closeout."
        else:
            followup_decision = "CORE_REUSE_CLOSEOUT_READY_WITH_WARNINGS"
            recommended_next = "Finalize conservative core-reuse closeout. Keep run1 candidate isolated; do not promote."
    elif review_decision == ROUTING_OR_CORE:
        if blockers:
            followup_decision = "ROUTING_OR_CORE_CLOSEOUT_BLOCKED_BY_HARD_METRIC"
            recommended_next = "Fix hard blocker before routing patch or closeout."
        else:
            followup_decision = "ROUTING_PATCH_OR_CORE_CLOSEOUT_READY"
            recommended_next = "Either patch overly strict routing or proceed with conservative core-reuse closeout."
    elif review_decision == HARD_BLOCKER:
        followup_decision = "HARD_BLOCKER_CLOSEOUT_REQUIRED"
        recommended_next = "Do not continue to eval. Fix the hard blocker first."
    else:
        followup_decision = "UNKNOWN_BLOCKER_REVIEW_DECISION"
        recommended_next = "Inspect blocker review summary."
        blockers.append(f"unknown blocker review decision: {review_decision}")

    promotion_decision = "NO_PROMOTION__RUN1_REMAINS_ISOLATED"
    if followup_decision == "HARD_BLOCKER_CLOSEOUT_REQUIRED":
        promotion_decision = "NO_PROMOTION__HARD_BLOCKER"
    elif followup_decision in {
        "CORE_REUSE_CLOSEOUT_READY_WITH_WARNINGS",
        "ROUTING_PATCH_OR_CORE_CLOSEOUT_READY",
    }:
        promotion_decision = "NO_PROMOTION__LOCAL_CLOSEOUT_ONLY"

    summary_rows = [
        row("followup_decision", followup_decision, "INFO", "Blocked-review follow-up only; no model eval."),
        row("promotion_decision", promotion_decision, "INFO"),
        row("recommended_next", recommended_next, "INFO"),
        row("blocker_review_decision", review_decision, "INFO"),
        row("root_cause_count", root_causes, "INFO", root_cause_notes),
        row("blocker_review_actions", "", "INFO", action_notes),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("dispatch_decision", get(dispatch, "dispatch_decision"), "INFO"),
        row("followup_upstream_decision", get(followup, "followup_decision"), "INFO"),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Existence only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("direct_manifest_rows", len(manifest), "INFO"),
        row("combined_summary_rows", len(combined), "INFO"),
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

    decision = {
        "followup_decision": followup_decision,
        "promotion_decision": promotion_decision,
        "recommended_next": recommended_next,
        "blocker_review_decision": review_decision,
        "root_cause_notes": root_cause_notes,
        "action_notes": action_notes,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "blockers": blockers,
        "warnings": warnings,
    }
    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    next_plan = [
        "# Teacher-divergence run1 blocker follow-up next plan",
        "",
        f"followup_decision={followup_decision}",
        f"promotion_decision={promotion_decision}",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Still forbidden",
        "",
        "- training",
        "- model eval",
        "- checkpoint read/write",
        "- current_best overwrite",
        "- C export",
        "- public benchmark",
        "- promotion",
        "- adding local checkpoint artifacts to git",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        next_plan.extend([f"- {b}" for b in blockers])
    else:
        next_plan.append("- None.")

    next_plan.extend(["", "## Warnings", ""])
    if warnings:
        next_plan.extend([f"- {w}" for w in warnings])
    else:
        next_plan.append("- None.")

    args.out_next_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_next_plan.write_text("\n".join(next_plan), encoding="utf-8")

    report = [
        "# Teacher-divergence run1 blocker follow-up",
        "",
        "## Scope",
        "",
        "- Follows up the next-stage blocked review.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Follow-up decision",
        "",
        f"`{followup_decision}`",
        "",
        "## Promotion decision",
        "",
        f"`{promotion_decision}`",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ]

    for r in summary_rows:
        n = r["notes"].replace("|", "\\|")
        report.append(f"| {r['metric']} | {r['value']} | {r['status']} | {n} |")

    report.extend(["", "## Blockers", ""])
    if blockers:
        report.extend([f"- {b}" for b in blockers])
    else:
        report.append("- None.")

    report.extend(["", "## Warnings", ""])
    if warnings:
        report.extend([f"- {w}" for w in warnings])
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Interpretation",
        "",
    ])

    if followup_decision == "CORE_REUSE_CLOSEOUT_READY_WITH_WARNINGS":
        report.append("Run1 can be closed out conservatively using already-computed core guard outputs. This is not a promotion path.")
    elif followup_decision == "ROUTING_PATCH_OR_CORE_CLOSEOUT_READY":
        report.append("There is no hard metric blocker. Either patch the route logic or close out conservatively with core reuse.")
    elif followup_decision == "HARD_BLOCKER_CLOSEOUT_REQUIRED":
        report.append("A hard blocker remains. Do not proceed to direct eval or promotion.")
    else:
        report.append("Do not proceed until the listed blocker state is resolved.")

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

    print("followup_decision:", followup_decision)
    print("promotion_decision:", promotion_decision)
    print("blocker_review_decision:", review_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("candidate_checkpoint_exists_locally:", int(candidate_exists))
    print("current_best_exists:", int(current_best_exists))
    print("direct_manifest_rows:", len(manifest))
    print("combined_fail_rows:", len(combined_fail_rows))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_next_plan:", args.out_next_plan)
    print("out_report:", args.out_report)
    print("blocked follow-up only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
