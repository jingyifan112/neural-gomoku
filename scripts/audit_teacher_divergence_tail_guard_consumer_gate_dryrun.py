#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_guard_consumer_gate_dryrun_audit")
OUT_CSV = OUT_DIR / "tail_guard_consumer_gate_dryrun_audit.csv"
OUT_SUMMARY = OUT_DIR / "tail_guard_consumer_gate_dryrun_audit_summary.json"
OUT_REPORT = OUT_DIR / "tail_guard_consumer_gate_dryrun_audit_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Audit whether the generated-tail dry-run dataset is consumable by the b4c96 "
            "no-save wrapper schema. Audit only: no training, no checkpoint save."
        )
    )
    p.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json"
        ),
    )
    p.add_argument(
        "--wrapper",
        type=Path,
        default=Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py"),
    )
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--expected-samples", type=int, default=4)
    p.add_argument("--expected-protected", type=int, default=15)
    p.add_argument("--expected-tail", type=int, default=15)
    p.add_argument("--expected-quarantine", type=int, default=3)
    p.add_argument("--expected-generated-tail", type=int, default=12)
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_rc(rc: Any, board_size: int) -> tuple[int, int]:
    if not isinstance(rc, list) or len(rc) != 2:
        raise ValueError(f"bad rc: {rc!r}")
    r, c = int(rc[0]), int(rc[1])
    if not (0 <= r < board_size and 0 <= c < board_size):
        raise ValueError(f"rc out of range: {rc!r}")
    return r, c


def validate_board(board: Any, board_size: int) -> list[list[int]]:
    if not isinstance(board, list) or len(board) != board_size:
        raise ValueError("board must be board_size x board_size list")
    out: list[list[int]] = []
    for row in board:
        if not isinstance(row, list) or len(row) != board_size:
            raise ValueError("board row has wrong length")
        out.append([int(x) for x in row])
    return out


def legal_empty(board: list[list[int]], rc: tuple[int, int]) -> bool:
    r, c = rc
    return int(board[r][c]) == 0


def row_identity(row: dict[str, Any], board_size: int) -> tuple[str, int, int]:
    board = validate_board(row["board"], board_size)
    target = validate_rc(row["target_rc"], board_size)
    board_key = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return board_key, target[0], target[1]


def load_wrapper_module(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("tail_guard_nosave_wrapper_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import wrapper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_group_rows(
    group_name: str,
    rows: list[dict[str, Any]],
    *,
    board_size: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for idx, row in enumerate(rows):
        case_id = str(row.get("case_id", f"{group_name}_{idx}"))
        status = "PASS"
        issues: list[str] = []

        try:
            board = validate_board(row.get("board"), board_size)
        except Exception as exc:
            board = []
            status = "FAIL"
            issues.append(f"bad_board:{type(exc).__name__}")

        try:
            target = validate_rc(row.get("target_rc"), board_size)
        except Exception as exc:
            target = (-1, -1)
            status = "FAIL"
            issues.append(f"bad_target_rc:{type(exc).__name__}")

        suppress_rcs = row.get("suppress_rcs")
        if not isinstance(suppress_rcs, list) or len(suppress_rcs) < 1:
            status = "FAIL"
            issues.append("missing_suppress_rcs")
        else:
            for j, rc in enumerate(suppress_rcs):
                try:
                    validate_rc(rc, board_size)
                except Exception as exc:
                    status = "FAIL"
                    issues.append(f"bad_suppress_rc_{j}:{type(exc).__name__}")

        if board and target != (-1, -1) and not legal_empty(board, target):
            status = "FAIL"
            issues.append("target_not_empty")

        if group_name == "tail_eval_samples" and row.get("materialization_status") == "dryrun_materialized_tail_eval_only":
            if row.get("training_allowed") is not False:
                status = "FAIL"
                issues.append("generated_tail_training_allowed_not_false")
            try:
                if float(row.get("sample_weight", 1.0)) != 0.0:
                    status = "FAIL"
                    issues.append("generated_tail_sample_weight_not_zero")
            except Exception:
                status = "FAIL"
                issues.append("generated_tail_sample_weight_bad")
            try:
                if float(row.get("effective_sample_weight", 1.0)) != 0.0:
                    status = "FAIL"
                    issues.append("generated_tail_effective_weight_not_zero")
            except Exception:
                status = "FAIL"
                issues.append("generated_tail_effective_weight_bad")
            if row.get("split") != "tail_eval":
                status = "FAIL"
                issues.append("generated_tail_split_not_tail_eval")
            try:
                if int(row.get("before_target_rank", 0)) <= 50:
                    status = "FAIL"
                    issues.append("generated_tail_rank_not_gt50")
            except Exception:
                status = "FAIL"
                issues.append("generated_tail_rank_bad")

        if group_name != "tail_eval_samples" and row.get("materialization_status") == "dryrun_materialized_tail_eval_only":
            status = "FAIL"
            issues.append("generated_tail_row_in_wrong_group")

        out.append(
            {
                "group": group_name,
                "row_index": idx,
                "case_id": case_id,
                "status": status,
                "issues": ";".join(issues),
                "materialization_status": row.get("materialization_status", ""),
                "training_allowed": row.get("training_allowed", ""),
                "before_target_rank": row.get("before_target_rank", ""),
                "target_rc": json.dumps(row.get("target_rc", [])),
                "suppress_count": len(suppress_rcs) if isinstance(suppress_rcs, list) else 0,
            }
        )

    return out


def main() -> int:
    args = parse_args()

    dataset = read_json(args.dataset)
    if not isinstance(dataset, dict):
        raise ValueError("dataset must be dict")

    required = ["samples", "protected_eval_samples", "tail_eval_samples"]
    for key in required:
        if key not in dataset:
            raise ValueError(f"dataset missing required wrapper group: {key}")
        if not isinstance(dataset[key], list) or not dataset[key]:
            raise ValueError(f"dataset group empty or not list: {key}")

    if "quarantine_samples" not in dataset or not isinstance(dataset["quarantine_samples"], list):
        raise ValueError("dataset missing quarantine_samples list")

    wrapper_text = args.wrapper.read_text(encoding="utf-8", errors="replace")
    forbidden_save_token = "torch" + ".save("
    wrapper_has_forbidden_save = forbidden_save_token in wrapper_text

    wrapper_module = load_wrapper_module(args.wrapper)
    wrapper_load_ok = False
    wrapper_load_error = ""
    try:
        loaded = wrapper_module.load_protected_dataset(args.dataset)
        wrapper_load_ok = all(k in loaded for k in required)
    except Exception as exc:
        wrapper_load_error = f"{type(exc).__name__}: {exc}"

    groups = {
        "samples": dataset.get("samples", []),
        "protected_eval_samples": dataset.get("protected_eval_samples", []),
        "tail_eval_samples": dataset.get("tail_eval_samples", []),
        "quarantine_samples": dataset.get("quarantine_samples", []),
    }

    row_audit: list[dict[str, Any]] = []
    for group_name, rows in groups.items():
        row_audit.extend(audit_group_rows(group_name, rows, board_size=args.board_size))

    generated_tail_rows = [
        r for r in groups["tail_eval_samples"]
        if isinstance(r, dict) and r.get("materialization_status") == "dryrun_materialized_tail_eval_only"
    ]
    generated_in_train = [
        r for r in groups["samples"]
        if isinstance(r, dict) and r.get("materialization_status") == "dryrun_materialized_tail_eval_only"
    ]

    duplicate_identities = 0
    seen = set()
    for group_name in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        for row in groups[group_name]:
            try:
                ident = (group_name, row_identity(row, args.board_size))
                # only count duplicates within same consumer group
                if ident in seen:
                    duplicate_identities += 1
                seen.add(ident)
            except Exception:
                pass

    counts = {k: len(v) for k, v in groups.items()}
    expected_counts_ok = (
        counts["samples"] == args.expected_samples
        and counts["protected_eval_samples"] == args.expected_protected
        and counts["tail_eval_samples"] == args.expected_tail
        and counts["quarantine_samples"] == args.expected_quarantine
        and len(generated_tail_rows) == args.expected_generated_tail
    )

    row_failures = [r for r in row_audit if r["status"] != "PASS"]

    hard_failures: list[str] = []
    if not wrapper_load_ok:
        hard_failures.append(f"wrapper_load_failed:{wrapper_load_error}")
    if wrapper_has_forbidden_save:
        hard_failures.append("wrapper_contains_forbidden_checkpoint_save_token")
    if not expected_counts_ok:
        hard_failures.append("expected_counts_mismatch")
    if generated_in_train:
        hard_failures.append("generated_tail_rows_found_in_train_samples")
    if row_failures:
        hard_failures.append(f"row_validation_failures:{len(row_failures)}")
    if duplicate_identities:
        hard_failures.append(f"duplicate_group_identities:{duplicate_identities}")

    decision = (
        "TAIL_GUARD_CONSUMER_GATE_DRYRUN_AUDIT_PASS"
        if not hard_failures
        else "TAIL_GUARD_CONSUMER_GATE_DRYRUN_AUDIT_FAIL"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "group",
            "row_index",
            "case_id",
            "status",
            "issues",
            "materialization_status",
            "training_allowed",
            "before_target_rank",
            "target_rc",
            "suppress_count",
        ]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(row_audit)

    status_counts = Counter(r["status"] for r in row_audit)
    group_counts = Counter(r["group"] for r in row_audit)

    summary = {
        "decision": decision,
        "scope": "consumer/gate dry-run audit only; no training/checkpoint save/export/benchmark/promotion",
        "dataset": str(args.dataset),
        "wrapper": str(args.wrapper),
        "wrapper_load_ok": wrapper_load_ok,
        "wrapper_load_error": wrapper_load_error,
        "wrapper_has_forbidden_save": wrapper_has_forbidden_save,
        "counts": counts,
        "expected_counts": {
            "samples": args.expected_samples,
            "protected_eval_samples": args.expected_protected,
            "tail_eval_samples": args.expected_tail,
            "quarantine_samples": args.expected_quarantine,
            "generated_tail_rows": args.expected_generated_tail,
        },
        "generated_tail_rows": len(generated_tail_rows),
        "generated_tail_rows_in_train_samples": len(generated_in_train),
        "duplicate_group_identities": duplicate_identities,
        "row_status_counts": dict(sorted(status_counts.items())),
        "group_counts": dict(sorted(group_counts.items())),
        "hard_failures": hard_failures,
        "outputs": {
            "row_audit_csv": str(OUT_CSV),
            "summary_json": str(OUT_SUMMARY),
            "report_md": str(OUT_REPORT),
        },
    }
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence tail guard consumer/gate dry-run audit", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Consumer/gate dry-run audit only.",
        "- No training.",
        "- No optimizer step.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- dataset: `{args.dataset}`",
        f"- wrapper: `{args.wrapper}`",
        "",
    ]

    lines += ["## Wrapper compatibility", ""]
    lines += [
        f"- wrapper load ok: `{wrapper_load_ok}`",
        f"- wrapper load error: `{wrapper_load_error}`",
        f"- wrapper forbidden checkpoint save token present: `{wrapper_has_forbidden_save}`",
        "",
    ]

    lines += ["## Counts", ""]
    lines += ["| group | count | expected |", "|---|---:|---:|"]
    for group in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        lines.append(f"| {group} | {counts[group]} | {summary['expected_counts'][group]} |")
    lines.append(f"| generated_tail_rows | {len(generated_tail_rows)} | {args.expected_generated_tail} |")
    lines.append("")

    lines += ["## Row audit", ""]
    lines += ["| status | count |", "|---|---:|"]
    for k, v in sorted(status_counts.items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines += ["## Hard failures", ""]
    if hard_failures:
        for item in hard_failures:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    lines += ["## Final note", ""]
    lines += [
        "This audit does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("wrapper_load_ok:", wrapper_load_ok)
    print("counts:", counts)
    print("generated_tail_rows:", len(generated_tail_rows))
    print("generated_tail_rows_in_train_samples:", len(generated_in_train))
    print("row_status_counts:", dict(sorted(status_counts.items())))
    print("hard_failures:", hard_failures)
    print("out_csv:", OUT_CSV)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: consumer/gate dry-run audit only; no training/checkpoint save/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
