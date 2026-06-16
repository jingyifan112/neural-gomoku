#!/usr/bin/env python3
"""
Run or preflight a retention-family gated training probe.

Design constraints:
- Train only from the retention-family train manifest.
- Evaluate against the retention-family eval manifest.
- Enforce the critical family gate_scope rule.
- Save/promote checkpoint only when all gates PASS.
- If train/gate fails, do not create/promote final checkpoint.
- This wrapper can run in preflight mode without training.

This script does not export C weights, does not run public benchmarks, and does not promote models.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


CRITICAL_FAMILY = "bd:ea22cc14729b88fd"

DEFAULT_TRAIN_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv")
DEFAULT_EVAL_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv")

DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.md")
DEFAULT_LOG_DIR = Path("eval_logs/integration_eval/retention_family_gated_training_probe")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_manifests(train_rows: List[Dict[str, str]], eval_rows: List[Dict[str, str]]) -> List[str]:
    errors: List[str] = []

    if not train_rows:
        errors.append("train manifest is empty")
    if not eval_rows:
        errors.append("eval manifest is empty")

    train_targets = {
        clean(r.get("policy_target"))
        for r in train_rows
        if clean(r.get("family_id")) == CRITICAL_FAMILY
    }
    eval_targets = {
        clean(r.get("policy_target"))
        for r in eval_rows
        if clean(r.get("family_id")) == CRITICAL_FAMILY
    }

    for target in ["7,10", "10,7"]:
        if target not in train_targets:
            errors.append(f"critical target {target} missing from train manifest")

    if "7,9" not in eval_targets:
        errors.append("critical target 7,9 missing from eval manifest")

    for r in train_rows:
        if clean(r.get("train_use_policy")) != "include_as_nonheldout_retention_anchor_candidate":
            errors.append(
                f"train row {r.get('dataset_index')} has unexpected train_use_policy={r.get('train_use_policy')}"
            )
        if clean(r.get("eval_use_policy")) != "exclude_from_eval_manifest":
            # Not fatal for all possible future manifests, but keep strict for this probe.
            errors.append(
                f"train row {r.get('dataset_index')} has unexpected eval_use_policy={r.get('eval_use_policy')}"
            )

    for r in eval_rows:
        eval_policy = clean(r.get("eval_use_policy"))
        if eval_policy not in {
            "normal_heldout_gate_candidate",
            "restricted_family_level_gate_candidate",
            "review_before_eval_gate_use",
            "heldout_gate_candidate_review_scope",
        }:
            errors.append(
                f"eval row {r.get('dataset_index')} has unexpected eval_use_policy={eval_policy}"
            )

        if clean(r.get("family_id")) == CRITICAL_FAMILY and clean(r.get("policy_target")) == "7,9":
            if clean(r.get("gate_scope")) != "external_or_family_level_only_not_sibling_only":
                errors.append("critical target 7,9 has wrong gate_scope")
            if clean(r.get("allowed_as_only_sibling_family_gate")) == "yes":
                errors.append("critical target 7,9 incorrectly allowed as only sibling-family gate")

    return errors


def run_shell_command(
    label: str,
    command: str,
    log_dir: Path,
    env_extra: Dict[str, str],
) -> Dict[str, Any]:
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)
    stdout_path = log_dir / f"{safe_label}.stdout.log"
    stderr_path = log_dir / f"{safe_label}.stderr.log"

    env = os.environ.copy()
    env.update(env_extra)

    started = now_utc()
    proc = subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    ended = now_utc()

    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    return {
        "label": label,
        "command": command,
        "returncode": proc.returncode,
        "started_at_utc": started,
        "ended_at_utc": ended,
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
        "passed": proc.returncode == 0,
    }


def safe_checkpoint_action(
    candidate_checkpoint: Path,
    final_checkpoint: Optional[Path],
    gates_passed: bool,
    promote_on_pass: bool,
    quarantine_on_fail: bool,
    quarantine_dir: Path,
) -> Dict[str, Any]:
    action = {
        "candidate_checkpoint": str(candidate_checkpoint),
        "candidate_exists": candidate_checkpoint.exists(),
        "final_checkpoint": str(final_checkpoint) if final_checkpoint else "",
        "final_exists_before": final_checkpoint.exists() if final_checkpoint else False,
        "promote_on_pass": promote_on_pass,
        "quarantine_on_fail": quarantine_on_fail,
        "action": "none",
        "error": "",
    }

    if gates_passed:
        if not promote_on_pass:
            action["action"] = "gates_passed_no_promotion_requested"
            return action

        if final_checkpoint is None:
            action["action"] = "gates_passed_no_final_checkpoint_path"
            action["error"] = "final checkpoint path is required for promotion"
            return action

        if not candidate_checkpoint.exists():
            action["action"] = "gates_passed_candidate_missing"
            action["error"] = "candidate checkpoint does not exist, cannot promote"
            return action

        final_checkpoint.parent.mkdir(parents=True, exist_ok=True)
        if final_checkpoint.exists():
            action["action"] = "blocked_final_checkpoint_exists"
            action["error"] = "final checkpoint already exists; refusing to overwrite"
            return action

        shutil.copy2(candidate_checkpoint, final_checkpoint)
        action["action"] = "promoted_candidate_to_final_checkpoint"
        action["final_exists_after"] = final_checkpoint.exists()
        return action

    if not gates_passed and quarantine_on_fail and candidate_checkpoint.exists():
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        dest = quarantine_dir / candidate_checkpoint.name
        if dest.exists():
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            dest = quarantine_dir / f"{candidate_checkpoint.stem}.{suffix}{candidate_checkpoint.suffix}"
        shutil.move(str(candidate_checkpoint), str(dest))
        action["action"] = "quarantined_failed_candidate_checkpoint"
        action["quarantine_path"] = str(dest)
        return action

    if not gates_passed:
        action["action"] = "gates_failed_no_promotion"
        return action

    return action


def make_md_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def write_report(payload: Dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    train_rows = payload["manifest_summary"]["critical_train_rows"]
    eval_rows = payload["manifest_summary"]["critical_eval_rows"]
    command_results = payload.get("command_results", [])

    md: List[str] = []
    md.append("# Retention family gated training probe runner")
    md.append("")
    md.append("Scope: gated training probe wrapper/report. No C export, benchmark, or promotion was run by this wrapper.")
    md.append("")
    md.append("## Mode and readiness")
    md.append("")
    md.append(f"- mode: `{payload['mode']}`")
    md.append(f"- overall_status: `{payload['overall_status']}`")
    md.append(f"- gates_passed: `{payload['gates_passed']}`")
    md.append(f"- train_manifest: `{payload['inputs']['train_manifest']}`")
    md.append(f"- eval_manifest: `{payload['inputs']['eval_manifest']}`")
    md.append(f"- candidate_checkpoint: `{payload['inputs']['candidate_checkpoint']}`")
    md.append(f"- final_checkpoint: `{payload['inputs'].get('final_checkpoint', '')}`")
    md.append("")
    md.append("## Manifest validation")
    md.append("")
    md.append(f"- validation_errors: `{payload['manifest_validation_errors']}`")
    md.append(f"- train_rows: {payload['manifest_summary']['train_rows']}")
    md.append(f"- eval_rows: {payload['manifest_summary']['eval_rows']}")
    md.append(f"- train_policy_counts: `{payload['manifest_summary']['train_policy_counts']}`")
    md.append(f"- eval_policy_counts: `{payload['manifest_summary']['eval_policy_counts']}`")
    md.append("")
    md.append("## Critical family")
    md.append("")
    md.append(f"- family_id: `{CRITICAL_FAMILY}`")
    md.append("")
    md.append("### Train-side critical rows")
    md.append("")
    md.append(make_md_table(
        ["target", "source", "train_policy", "risk_flags", "reason"],
        [
            [
                r.get("policy_target", ""),
                r.get("source", ""),
                r.get("train_use_policy", ""),
                r.get("risk_flags", ""),
                r.get("materialized_reason", ""),
            ]
            for r in train_rows
        ],
    ))
    md.append("")
    md.append("### Eval-side critical rows")
    md.append("")
    md.append(make_md_table(
        ["target", "source", "eval_policy", "gate_scope", "only_sibling_gate_ok", "risk_flags"],
        [
            [
                r.get("policy_target", ""),
                r.get("source", ""),
                r.get("eval_use_policy", ""),
                r.get("gate_scope", ""),
                r.get("allowed_as_only_sibling_family_gate", ""),
                r.get("risk_flags", ""),
            ]
            for r in eval_rows
        ],
    ))
    md.append("")

    md.append("## Command results")
    md.append("")
    if command_results:
        md.append(make_md_table(
            ["label", "returncode", "passed", "stdout_log", "stderr_log"],
            [
                [
                    r["label"],
                    r["returncode"],
                    r["passed"],
                    r["stdout_log"],
                    r["stderr_log"],
                ]
                for r in command_results
            ],
        ))
    else:
        md.append("No train/gate commands were run.")
    md.append("")

    md.append("## Checkpoint action")
    md.append("")
    ck = payload.get("checkpoint_action", {})
    for k in sorted(ck):
        md.append(f"- {k}: `{ck[k]}`")
    md.append("")
    md.append("## Safety interpretation")
    md.append("")
    md.append("- This wrapper requires manifest validation before running training or gates.")
    md.append("- Candidate checkpoints should be written only to the candidate checkpoint path.")
    md.append("- Final checkpoint promotion happens only when all gates pass and `--promote-on-pass` is set.")
    md.append("- On gate failure, the wrapper does not promote the candidate checkpoint.")
    md.append("- This wrapper does not export C weights, does not run public benchmarks, and does not make promotion decisions.")
    md.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "train-and-gate", "gates-only"], default="preflight")
    ap.add_argument("--train-manifest", type=Path, default=DEFAULT_TRAIN_MANIFEST)
    ap.add_argument("--eval-manifest", type=Path, default=DEFAULT_EVAL_MANIFEST)
    ap.add_argument("--candidate-checkpoint", type=Path, required=True)
    ap.add_argument("--final-checkpoint", type=Path, default=None)
    ap.add_argument("--train-cmd", default="")
    ap.add_argument("--gate-cmd", action="append", default=[])
    ap.add_argument("--promote-on-pass", action="store_true")
    ap.add_argument("--quarantine-on-fail", action="store_true")
    ap.add_argument("--quarantine-dir", type=Path, default=Path("checkpoints/failed_retention_family_probe"))
    ap.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    train_rows = read_csv(args.train_manifest)
    eval_rows = read_csv(args.eval_manifest)
    validation_errors = validate_manifests(train_rows, eval_rows)

    critical_train = [
        r for r in train_rows
        if clean(r.get("family_id")) == CRITICAL_FAMILY
    ]
    critical_eval = [
        r for r in eval_rows
        if clean(r.get("family_id")) == CRITICAL_FAMILY
    ]

    train_policy_counts = Counter(clean(r.get("train_use_policy")) for r in train_rows)
    eval_policy_counts = Counter(clean(r.get("eval_use_policy")) for r in eval_rows)

    setup_errors: List[str] = []
    if args.mode == "train-and-gate" and not clean(args.train_cmd):
        setup_errors.append("train-and-gate mode requires --train-cmd")
    if args.mode in {"train-and-gate", "gates-only"} and not args.gate_cmd:
        setup_errors.append(f"{args.mode} mode requires at least one --gate-cmd")
    if args.promote_on_pass and args.final_checkpoint is None:
        setup_errors.append("--promote-on-pass requires --final-checkpoint")
    if args.final_checkpoint and args.final_checkpoint.exists() and args.promote_on_pass:
        setup_errors.append(f"final checkpoint already exists: {args.final_checkpoint}")

    command_results: List[Dict[str, Any]] = []
    gates_passed = False
    overall_status = "preflight_pass"

    env_extra = {
        "RETENTION_FAMILY_TRAIN_MANIFEST": str(args.train_manifest),
        "RETENTION_FAMILY_EVAL_MANIFEST": str(args.eval_manifest),
        "RETENTION_FAMILY_CANDIDATE_CHECKPOINT": str(args.candidate_checkpoint),
        "RETENTION_FAMILY_FINAL_CHECKPOINT": str(args.final_checkpoint or ""),
    }

    if validation_errors or setup_errors:
        overall_status = "blocked_preflight_failed"
    elif args.mode == "preflight":
        overall_status = "preflight_pass"
    else:
        if args.mode == "train-and-gate":
            train_result = run_shell_command("train", args.train_cmd, args.log_dir, env_extra)
            command_results.append(train_result)
            if not train_result["passed"]:
                overall_status = "train_failed"
            else:
                overall_status = "train_passed"

        if overall_status in {"train_passed"} or args.mode == "gates-only":
            gate_passes = []
            for i, cmd in enumerate(args.gate_cmd, 1):
                res = run_shell_command(f"gate_{i}", cmd, args.log_dir, env_extra)
                command_results.append(res)
                gate_passes.append(res["passed"])
            gates_passed = bool(gate_passes) and all(gate_passes)
            overall_status = "gates_passed" if gates_passed else "gates_failed"

    if args.mode == "preflight":
        checkpoint_action = {
            "candidate_checkpoint": str(args.candidate_checkpoint),
            "candidate_exists": args.candidate_checkpoint.exists(),
            "final_checkpoint": str(args.final_checkpoint or ""),
            "action": "preflight_only_no_checkpoint_action",
        }
    else:
        checkpoint_action = safe_checkpoint_action(
            candidate_checkpoint=args.candidate_checkpoint,
            final_checkpoint=args.final_checkpoint,
            gates_passed=gates_passed,
            promote_on_pass=args.promote_on_pass,
            quarantine_on_fail=args.quarantine_on_fail,
            quarantine_dir=args.quarantine_dir,
        )
        if checkpoint_action.get("error"):
            overall_status = f"{overall_status}_checkpoint_action_error"

    payload = {
        "generated_at_utc": now_utc(),
        "mode": args.mode,
        "inputs": {
            "train_manifest": str(args.train_manifest),
            "eval_manifest": str(args.eval_manifest),
            "candidate_checkpoint": str(args.candidate_checkpoint),
            "final_checkpoint": str(args.final_checkpoint or ""),
            "train_cmd": args.train_cmd,
            "gate_cmd": args.gate_cmd,
            "promote_on_pass": args.promote_on_pass,
            "quarantine_on_fail": args.quarantine_on_fail,
        },
        "manifest_validation_errors": validation_errors,
        "setup_errors": setup_errors,
        "manifest_summary": {
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "train_policy_counts": dict(sorted(train_policy_counts.items())),
            "eval_policy_counts": dict(sorted(eval_policy_counts.items())),
            "critical_train_rows": critical_train,
            "critical_eval_rows": critical_eval,
        },
        "command_results": command_results,
        "gates_passed": gates_passed,
        "overall_status": overall_status,
        "checkpoint_action": checkpoint_action,
        "explicit_non_actions": [
            "no C export",
            "no public benchmark",
            "no promotion decision",
        ],
    }

    write_report(payload, args.out_json, args.out_md)

    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("overall_status:", overall_status)
    print("manifest_validation_errors:", validation_errors)
    print("setup_errors:", setup_errors)
    print("gates_passed:", gates_passed)
    print("checkpoint_action:", checkpoint_action.get("action"))

    if overall_status.startswith("blocked") or checkpoint_action.get("error"):
        return 2
    if overall_status in {"train_failed", "gates_failed"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
