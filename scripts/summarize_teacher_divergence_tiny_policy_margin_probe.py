#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


CASE_RE = re.compile(r"^case_id:\s+(?P<case_id>.+)$")
METRIC_RE = re.compile(
    r"target_prob=(?P<target_prob>[-+0-9.eE]+)\s+"
    r"suppress_prob=(?P<suppress_prob>[-+0-9.eE]+)\s+"
    r"target_rank=(?P<target_rank>\d+)\s+"
    r"suppress_rank=(?P<suppress_rank>\d+)\s+"
    r"target_logit=(?P<target_logit>[-+0-9.eE]+)\s+"
    r"suppress_logit=(?P<suppress_logit>[-+0-9.eE]+)\s+"
    r"gap=(?P<gap>[-+0-9.eE]+)"
)
EPOCH_RE = re.compile(
    r"^epoch\s+(?P<epoch>\d+)/(?P<epochs>\d+)\s+"
    r"loss=(?P<loss>[-+0-9.eE]+)\s+"
    r"margin_loss=(?P<margin_loss>[-+0-9.eE]+)\s+"
    r"anchor_kl=(?P<anchor_kl>[-+0-9.eE]+)\s+"
    r"ce=(?P<ce>[-+0-9.eE]+)"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--train-log", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--out-gap-csv", type=Path, required=True)
    p.add_argument("--out-epoch-csv", type=Path, required=True)
    p.add_argument("--out-report", type=Path, required=True)
    p.add_argument("--expected-samples", type=int, default=44)
    return p.parse_args()


def parse_log(path: Path):
    section = ""
    current_case = ""
    rows = []
    epochs = []
    section_index = {"BEFORE": 0, "AFTER": 0}

    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()

        if s == "BEFORE":
            section = "BEFORE"
            current_case = ""
            continue
        if s == "AFTER":
            section = "AFTER"
            current_case = ""
            continue

        m = EPOCH_RE.match(s)
        if m:
            epochs.append(m.groupdict())
            continue

        m = CASE_RE.match(s)
        if m:
            current_case = m.group("case_id")
            continue

        m = METRIC_RE.search(s)
        if m and section in {"BEFORE", "AFTER"} and current_case:
            d = m.groupdict()
            d["section"] = section
            d["case_id"] = current_case
            d["occurrence_index"] = str(section_index[section])
            section_index[section] += 1
            rows.append(d)

    return rows, epochs


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def main() -> None:
    args = parse_args()

    rows, epochs = parse_log(args.train_log)
    before = [r for r in rows if r["section"] == "BEFORE"]
    after = [r for r in rows if r["section"] == "AFTER"]

    if len(before) != args.expected_samples:
        raise RuntimeError(f"expected {args.expected_samples} BEFORE rows, got {len(before)}")
    if len(after) != args.expected_samples:
        raise RuntimeError(f"expected {args.expected_samples} AFTER rows, got {len(after)}")
    if not args.checkpoint.exists():
        raise RuntimeError(f"checkpoint missing: {args.checkpoint}")

    # Pair rows by occurrence order. case_id is not guaranteed unique.
    gap_rows = []
    duplicate_case_counts = Counter(r["case_id"] for r in before)

    for i, (b, a) in enumerate(zip(before, after)):
        if b["case_id"] != a["case_id"]:
            raise RuntimeError(
                f"BEFORE/AFTER order mismatch at index {i}: {b['case_id']} vs {a['case_id']}"
            )

        case_id = b["case_id"]
        case_key = f"{i:03d}_{case_id}"

        gap_before = float(b["gap"])
        gap_after = float(a["gap"])
        target_prob_before = float(b["target_prob"])
        target_prob_after = float(a["target_prob"])
        suppress_prob_before = float(b["suppress_prob"])
        suppress_prob_after = float(a["suppress_prob"])

        gap_rows.append({
            "row_index": str(i),
            "case_key": case_key,
            "case_id": case_id,
            "case_id_duplicate_count": str(duplicate_case_counts[case_id]),
            "target_prob_before": f"{target_prob_before:.10f}",
            "target_prob_after": f"{target_prob_after:.10f}",
            "target_prob_delta": f"{target_prob_after - target_prob_before:.10f}",
            "suppress_prob_before": f"{suppress_prob_before:.10f}",
            "suppress_prob_after": f"{suppress_prob_after:.10f}",
            "suppress_prob_delta": f"{suppress_prob_after - suppress_prob_before:.10f}",
            "target_rank_before": b["target_rank"],
            "target_rank_after": a["target_rank"],
            "target_rank_delta": str(int(a["target_rank"]) - int(b["target_rank"])),
            "suppress_rank_before": b["suppress_rank"],
            "suppress_rank_after": a["suppress_rank"],
            "suppress_rank_delta": str(int(a["suppress_rank"]) - int(b["suppress_rank"])),
            "gap_before": f"{gap_before:.10f}",
            "gap_after": f"{gap_after:.10f}",
            "gap_delta": f"{gap_after - gap_before:.10f}",
            "gap_improved": "1" if gap_after > gap_before else "0",
            "target_prob_improved": "1" if target_prob_after > target_prob_before else "0",
        })

    args.out_gap_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_gap_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(gap_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(gap_rows)

    args.out_epoch_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_epoch_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["epoch", "epochs", "loss", "margin_loss", "anchor_kl", "ce"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(epochs)

    gap_deltas = [float(r["gap_delta"]) for r in gap_rows]
    target_prob_deltas = [float(r["target_prob_delta"]) for r in gap_rows]
    suppress_prob_deltas = [float(r["suppress_prob_delta"]) for r in gap_rows]
    gap_improved = sum(r["gap_improved"] == "1" for r in gap_rows)
    target_prob_improved = sum(r["target_prob_improved"] == "1" for r in gap_rows)
    duplicate_case_ids = sum(1 for _case_id, count in duplicate_case_counts.items() if count > 1)

    lines = [
        "# Teacher-divergence tiny policy-margin probe e3",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-tiny-policy-margin-probe`",
        "",
        "## Scope",
        "",
        "- Tiny isolated training probe.",
        "- Uses 44-row trainer-ready teacher-divergence dataset.",
        "- Trains policy head only through the existing policy-margin trainer.",
        "- Epochs: 3.",
        "- Saves checkpoint to isolated local path.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| BEFORE rows | {len(before)} |",
        f"| AFTER rows | {len(after)} |",
        f"| unique BEFORE case_id rows | {len(duplicate_case_counts)} |",
        f"| duplicate case_id groups | {duplicate_case_ids} |",
        f"| epochs logged | {len(epochs)} |",
        f"| checkpoint exists locally | {1 if args.checkpoint.exists() else 0} |",
        f"| checkpoint size bytes | {args.checkpoint.stat().st_size} |",
        f"| gap improved rows | {gap_improved} |",
        f"| target prob improved rows | {target_prob_improved} |",
        f"| mean gap delta | {mean(gap_deltas):.10f} |",
        f"| mean target prob delta | {mean(target_prob_deltas):.10f} |",
        f"| mean suppress prob delta | {mean(suppress_prob_deltas):.10f} |",
        "",
        "## Epoch metrics",
        "",
        "| epoch | loss | margin_loss | anchor_kl | ce |",
        "|---:|---:|---:|---:|---:|",
    ]

    for e in epochs:
        lines.append(f"| {e['epoch']} | {e['loss']} | {e['margin_loss']} | {e['anchor_kl']} | {e['ce']} |")

    lines += [
        "",
        "## Worst gap deltas",
        "",
        "| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | suppress_prob_delta |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]

    for r in sorted(gap_rows, key=lambda x: float(x["gap_delta"]))[:10]:
        lines.append(
            f"| {r['row_index']} | {r['case_id']} | {r['gap_before']} | {r['gap_after']} | {r['gap_delta']} | {r['target_prob_delta']} | {r['suppress_prob_delta']} |"
        )

    lines += [
        "",
        "## Best gap deltas",
        "",
        "| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | suppress_prob_delta |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]

    for r in sorted(gap_rows, key=lambda x: float(x["gap_delta"]), reverse=True)[:10]:
        lines.append(
            f"| {r['row_index']} | {r['case_id']} | {r['gap_before']} | {r['gap_after']} | {r['gap_delta']} | {r['target_prob_delta']} | {r['suppress_prob_delta']} |"
        )

    lines += [
        "",
        "## Decision",
        "",
        "This is a local tiny training probe only.",
        "",
        "Do not promote.",
        "",
        "Do not C export.",
        "",
        "Do not run public benchmark.",
        "",
    ]

    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("before_rows:", len(before))
    print("after_rows:", len(after))
    print("unique_before_case_ids:", len(duplicate_case_counts))
    print("duplicate_case_id_groups:", duplicate_case_ids)
    print("epochs_logged:", len(epochs))
    print("checkpoint_exists:", args.checkpoint.exists())
    print("gap_improved_rows:", gap_improved)
    print("target_prob_improved_rows:", target_prob_improved)
    print("mean_gap_delta:", f"{mean(gap_deltas):.10f}")
    print("mean_target_prob_delta:", f"{mean(target_prob_deltas):.10f}")
    print("mean_suppress_prob_delta:", f"{mean(suppress_prob_deltas):.10f}")
    print("out_gap_csv:", args.out_gap_csv)
    print("out_epoch_csv:", args.out_epoch_csv)
    print("out_report:", args.out_report)


if __name__ == "__main__":
    main()
