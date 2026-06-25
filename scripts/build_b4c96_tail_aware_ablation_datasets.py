#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


SOURCE_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json"
)
FORENSICS_CSV = Path("analysis/integration_eval/b4c96_stagec_failure_forensics.csv")
RUN1_SUMMARY = Path("analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv")

OUT_A4 = Path("analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json")
OUT_A5 = Path("analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json")

OUT_DIR = Path("analysis/integration_eval/b4c96_tail_aware_ablation_dataset_adapter")
MANIFEST_CSV = OUT_DIR / "dataset_manifest.csv"
SUMMARY_JSON = OUT_DIR / "dataset_adapter_summary.json"
REPORT_MD = OUT_DIR / "dataset_adapter_report.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def get_weight(sample: dict[str, Any]) -> float:
    return float(sample.get("effective_sample_weight", sample.get("sample_weight", 1.0)))


def set_weight(sample: dict[str, Any], weight: float) -> None:
    sample["effective_sample_weight"] = float(weight)
    if "sample_weight" in sample:
        sample["sample_weight"] = float(weight)


def suppress_count(sample: dict[str, Any]) -> int:
    return len(sample.get("suppress_rcs", []))


def target_suppress_count(samples: list[dict[str, Any]]) -> int:
    counts = Counter(suppress_count(s) for s in samples)
    if not counts:
        raise ValueError("empty source samples")
    if len(counts) != 1:
        raise ValueError(f"source train samples have variable suppress counts: {dict(counts)}")
    return next(iter(counts))


def load_severe_case_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()

    severe: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            case_id = row.get("case_id", "")
            blob = " ".join(str(v) for v in row.values())
            if "severe_core_regression" in blob or "core_regressed" in blob:
                if case_id:
                    severe.add(case_id)
    return severe


def clone_original_train(sample: dict[str, Any], *, severe_ids: set[str], downweight_severe: bool) -> dict[str, Any]:
    out = copy.deepcopy(sample)
    original_weight = get_weight(out)
    out["adapter_role"] = "original_train"
    out["adapter_source_group"] = "samples"
    out["adapter_original_case_id"] = sample.get("case_id", "")

    if downweight_severe and str(sample.get("case_id", "")) in severe_ids:
        out["adapter_weight_policy"] = "severe_core_regression_downweight_0_5"
        set_weight(out, original_weight * 0.5)
    else:
        out["adapter_weight_policy"] = "unchanged"
        set_weight(out, original_weight)
    return out


def clone_tail_guard(sample: dict[str, Any], *, guard_weight: float, suffix: str) -> dict[str, Any]:
    out = copy.deepcopy(sample)
    original_case_id = str(sample.get("case_id", "unknown"))
    out["adapter_role"] = "tail_guard_train"
    out["adapter_source_group"] = "tail_eval_samples"
    out["adapter_original_case_id"] = original_case_id
    out["adapter_weight_policy"] = f"tail_guard_weight_{guard_weight}"
    out["case_id"] = f"{original_case_id}__{suffix}"
    set_weight(out, guard_weight)
    return out


def weight_stats(samples: list[dict[str, Any]]) -> dict[str, float]:
    weights = [get_weight(s) for s in samples]
    return {
        "weight_min": float(min(weights)) if weights else 0.0,
        "weight_mean": float(mean(weights)) if weights else 0.0,
        "weight_max": float(max(weights)) if weights else 0.0,
        "weight_sum": float(sum(weights)),
    }


def build_dataset(
    source: dict[str, Any],
    *,
    name: str,
    out_path: Path,
    severe_ids: set[str],
    downweight_severe: bool,
    tail_guard_weight: float,
) -> dict[str, Any]:
    train_samples = list(source["samples"])
    protected_eval = list(source["protected_eval_samples"])
    tail_eval = list(source["tail_eval_samples"])

    train_suppress_count = target_suppress_count(train_samples)

    adapted_train: list[dict[str, Any]] = [
        clone_original_train(s, severe_ids=severe_ids, downweight_severe=downweight_severe)
        for s in train_samples
    ]

    added_tail_guards = []
    skipped_tail_guards = []
    for s in tail_eval:
        if suppress_count(s) == train_suppress_count:
            added_tail_guards.append(clone_tail_guard(s, guard_weight=tail_guard_weight, suffix="tail_guard"))
        else:
            skipped_tail_guards.append(str(s.get("case_id", "unknown")))

    adapted_train.extend(added_tail_guards)

    output = copy.deepcopy(source)
    output["name"] = name
    output["samples"] = adapted_train
    output["adapter_metadata"] = {
        "adapter": "b4c96_tail_aware_ablation_dataset_adapter",
        "source_dataset": str(SOURCE_DATASET),
        "source_train_rows": len(train_samples),
        "source_protected_eval_rows": len(protected_eval),
        "source_tail_eval_rows": len(tail_eval),
        "output_train_rows": len(adapted_train),
        "train_suppress_count": train_suppress_count,
        "tail_guard_weight": tail_guard_weight,
        "added_tail_guard_rows": len(added_tail_guards),
        "skipped_tail_guard_rows": len(skipped_tail_guards),
        "skipped_tail_guard_case_ids": skipped_tail_guards,
        "downweight_severe": bool(downweight_severe),
        "severe_case_ids_loaded": sorted(severe_ids),
        "severe_case_ids_in_train": sorted(
            str(s.get("case_id", "")) for s in train_samples if str(s.get("case_id", "")) in severe_ids
        ),
        "scope": "no-save ablation dataset only; not promotion-valid by itself",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    stats = weight_stats(adapted_train)
    severe_downweighted = sum(
        1 for s in adapted_train if s.get("adapter_weight_policy") == "severe_core_regression_downweight_0_5"
    )

    return {
        "name": name,
        "path": str(out_path),
        "source_train_rows": len(train_samples),
        "protected_eval_rows": len(protected_eval),
        "tail_eval_rows": len(tail_eval),
        "output_train_rows": len(adapted_train),
        "added_tail_guard_rows": len(added_tail_guards),
        "skipped_tail_guard_rows": len(skipped_tail_guards),
        "severe_downweighted_rows": severe_downweighted,
        "train_suppress_count": train_suppress_count,
        **stats,
    }


def write_manifest(rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "name",
        "path",
        "source_train_rows",
        "protected_eval_rows",
        "tail_eval_rows",
        "output_train_rows",
        "added_tail_guard_rows",
        "skipped_tail_guard_rows",
        "severe_downweighted_rows",
        "train_suppress_count",
        "weight_min",
        "weight_mean",
        "weight_max",
        "weight_sum",
    ]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_report(rows: list[dict[str, Any]], severe_ids: set[str]) -> None:
    lines: list[str] = []
    lines += ["# b4c96 tail-aware ablation dataset adapter report", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Dataset adapter only.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]
    lines += ["## Inputs", ""]
    lines += [
        f"- source_dataset: `{SOURCE_DATASET}`",
        f"- forensics_csv: `{FORENSICS_CSV}`",
        f"- run1_summary: `{RUN1_SUMMARY}`",
        f"- severe_case_ids_loaded: {len(severe_ids)}",
        "",
    ]

    lines += ["## Output datasets", ""]
    lines += [
        "| dataset | output_train_rows | added_tail_guard_rows | severe_downweighted_rows | weight_sum | path |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['output_train_rows']} | {r['added_tail_guard_rows']} | "
            f"{r['severe_downweighted_rows']} | {float(r['weight_sum']):.6f} | `{r['path']}` |"
        )

    lines += ["", "## Dataset meanings", ""]
    lines += [
        "- A4 adds compatible tail evaluation rows into the no-save training samples as low-weight tail guards.",
        "- A5 does the same and additionally downweights train rows that overlap severe/core-regression forensics IDs.",
        "- These datasets are no-save ablation inputs only; they are not promotion-valid heldout evidence.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "`B4C96_TAIL_AWARE_ABLATION_DATASET_ADAPTER_READY`",
        "",
        "Next step: run A4/A5 no-save ablations through the b4c96-safe wrapper.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    source = read_json(SOURCE_DATASET)
    for key in ["samples", "protected_eval_samples", "tail_eval_samples"]:
        if key not in source:
            raise ValueError(f"source dataset missing {key}")

    severe_ids = load_severe_case_ids(FORENSICS_CSV)

    rows = [
        build_dataset(
            source,
            name="b4c96_tail_aware_ablation_A4_tail_guard_dataset",
            out_path=OUT_A4,
            severe_ids=severe_ids,
            downweight_severe=False,
            tail_guard_weight=0.75,
        ),
        build_dataset(
            source,
            name="b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset",
            out_path=OUT_A5,
            severe_ids=severe_ids,
            downweight_severe=True,
            tail_guard_weight=0.75,
        ),
    ]

    write_manifest(rows)
    SUMMARY_JSON.write_text(json.dumps({"rows": rows, "severe_case_ids": sorted(severe_ids)}, indent=2) + "\n")
    write_report(rows, severe_ids)

    print("source_dataset:", SOURCE_DATASET)
    print("forensics_csv:", FORENSICS_CSV, "exists=", FORENSICS_CSV.exists())
    print("severe_case_ids_loaded:", len(severe_ids))
    for row in rows:
        print(
            row["name"],
            "output_train_rows=", row["output_train_rows"],
            "added_tail_guard_rows=", row["added_tail_guard_rows"],
            "severe_downweighted_rows=", row["severe_downweighted_rows"],
            "weight_sum=", f"{float(row['weight_sum']):.6f}",
        )
    print("manifest:", MANIFEST_CSV)
    print("summary_json:", SUMMARY_JSON)
    print("report:", REPORT_MD)
    print("status: dataset adapter only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
