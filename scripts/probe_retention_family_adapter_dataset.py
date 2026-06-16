#!/usr/bin/env python3
"""
Probe a retention-family adapter dataset with an existing checkpoint.

This is a thin adapter-aware wrapper around probe_teacher_divergence_retention_dataset.py.

It:
- reads retention_family_training_consumer_adapter_*_dataset.json
- writes a temporary plain row-list dataset for the existing probe script
- runs the existing probe script
- enriches the resulting CSV with retention-family adapter metadata
- writes an adapter-aware probe CSV and MD report

No training, checkpoint save, C export, benchmark, or promotion is run.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence


DEFAULT_PROBE_SCRIPT = Path("scripts/probe_teacher_divergence_retention_dataset.py")
DEFAULT_TMP_DIR = Path("analysis/integration_eval/adapter_probe_tmp")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def read_adapter_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
        return obj.get("metadata", {}), obj["rows"]
    if isinstance(obj, list):
        return {}, obj
    raise SystemExit(f"ERROR: no rows found in adapter JSON: {path}")


def adapter_meta(row: dict[str, Any]) -> dict[str, Any]:
    meta = row.get("retention_family_consumer_adapter")
    if isinstance(meta, dict):
        return meta
    return {}


def write_plain_dataset(path: Path, rows: list[dict[str, Any]]) -> None:
    """
    The legacy probe has historically consumed a plain list-style dataset.
    Keep all row fields intact, including adapter metadata, but write a list
    to maximize compatibility with older scripts.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def normalize_probe_row(raw: dict[str, str], adapter_row: dict[str, Any], index: int) -> dict[str, Any]:
    meta = adapter_meta(adapter_row)
    out: dict[str, Any] = dict(raw)

    out["adapter_row_index"] = index
    out["family_id"] = clean(meta.get("family_id"))
    out["source"] = clean(meta.get("source"))
    out["source_path"] = clean(meta.get("source_path"))
    out["policy_target"] = clean(meta.get("policy_target"))
    out["teacher_move"] = clean(adapter_row.get("teacher_move") or meta.get("teacher_move"))
    out["gate_scope"] = clean(meta.get("gate_scope"))
    out["allowed_as_only_sibling_family_gate"] = clean(meta.get("allowed_as_only_sibling_family_gate"))
    out["train_use_policy"] = clean(meta.get("train_use_policy"))
    out["eval_use_policy"] = clean(meta.get("eval_use_policy"))
    out["risk_flags"] = clean(meta.get("risk_flags"))
    out["adapter_side"] = clean(meta.get("adapter_side"))
    out["compat_split"] = clean(meta.get("compat_split"))
    out["compat_role"] = clean(meta.get("compat_role"))
    out["materialized_role"] = clean(meta.get("materialized_role"))
    out["proposed_split"] = clean(meta.get("proposed_split"))
    out["proposed_role"] = clean(meta.get("proposed_role"))

    # Provide normalized aliases recognized by evaluate_retention_family_adapter_gates.py.
    for src, dst in [
        ("policy_target_rank", "target_rank"),
        ("target_policy_rank", "target_rank"),
        ("teacher_rank", "target_rank"),
        ("rank", "target_rank"),
        ("policy_target_prob", "target_prob"),
        ("target_policy_prob", "target_prob"),
        ("teacher_prob", "target_prob"),
        ("prob", "target_prob"),
    ]:
        if not clean(out.get(dst)) and clean(out.get(src)):
            out[dst] = clean(out.get(src))

    if not clean(out.get("top1")):
        rank = clean(out.get("target_rank"))
        if rank:
            try:
                out["top1"] = "yes" if int(float(rank)) == 1 else "no"
            except Exception:
                out["top1"] = ""

    return out


def make_table(headers: Sequence[str], rows: Sequence[Sequence[Any]], max_rows: int = 200) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter-json", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    ap.add_argument("--output-md", type=Path, required=True)
    ap.add_argument("--probe-script", type=Path, default=DEFAULT_PROBE_SCRIPT)
    ap.add_argument("--tmp-dir", type=Path, default=DEFAULT_TMP_DIR)
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=6)
    ap.add_argument("--device-env", default="")
    args = ap.parse_args()

    metadata, adapter_rows = read_adapter_rows(args.adapter_json)
    if not adapter_rows:
        raise SystemExit(f"ERROR: adapter dataset is empty: {args.adapter_json}")

    stem = args.output_csv.stem
    plain_dataset = args.tmp_dir / f"{stem}.plain_dataset.json"
    raw_csv = args.tmp_dir / f"{stem}.raw_probe.csv"
    raw_md = args.tmp_dir / f"{stem}.raw_probe.md"

    write_plain_dataset(plain_dataset, adapter_rows)

    cmd = [
        sys.executable,
        str(args.probe_script),
        "--dataset",
        str(plain_dataset),
        "--checkpoint",
        str(args.checkpoint),
        "--output-csv",
        str(raw_csv),
        "--output-md",
        str(raw_md),
        "--board-size",
        str(args.board_size),
        "--win-length",
        str(args.win_length),
        "--channels",
        str(args.channels),
        "--blocks",
        str(args.blocks),
    ]

    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_log = args.tmp_dir / f"{stem}.probe.stdout.log"
    stderr_log = args.tmp_dir / f"{stem}.probe.stderr.log"
    stdout_log.write_text(proc.stdout, encoding="utf-8")
    stderr_log.write_text(proc.stderr, encoding="utf-8")

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)

    raw_rows = read_csv(raw_csv)
    if len(raw_rows) != len(adapter_rows):
        raise SystemExit(
            f"ERROR: raw probe rows {len(raw_rows)} != adapter rows {len(adapter_rows)}"
        )

    enriched_rows = [
        normalize_probe_row(raw, adapter_row, i)
        for i, (raw, adapter_row) in enumerate(zip(raw_rows, adapter_rows), 1)
    ]

    existing_fields: list[str] = []
    for r in enriched_rows:
        for k in r:
            if k not in existing_fields:
                existing_fields.append(k)

    preferred = [
        "adapter_row_index",
        "adapter_side",
        "family_id",
        "source",
        "source_path",
        "policy_target",
        "teacher_move",
        "target_rank",
        "target_prob",
        "top1",
        "gate_scope",
        "allowed_as_only_sibling_family_gate",
        "train_use_policy",
        "eval_use_policy",
        "risk_flags",
        "compat_split",
        "compat_role",
        "materialized_role",
        "proposed_split",
        "proposed_role",
    ]
    fieldnames = preferred + [k for k in existing_fields if k not in preferred]

    write_csv(args.output_csv, enriched_rows, fieldnames)

    critical = [
        r for r in enriched_rows
        if r.get("family_id") == "bd:ea22cc14729b88fd"
    ]

    md: list[str] = []
    md.append("# Retention family adapter probe")
    md.append("")
    md.append("Scope: adapter-aware checkpoint probe only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs and outputs")
    md.append("")
    md.append(f"- adapter_json: `{args.adapter_json}`")
    md.append(f"- checkpoint: `{args.checkpoint}`")
    md.append(f"- output_csv: `{args.output_csv}`")
    md.append(f"- output_md: `{args.output_md}`")
    md.append(f"- plain temporary dataset: `{plain_dataset}`")
    md.append(f"- raw probe csv: `{raw_csv}`")
    md.append(f"- raw probe md: `{raw_md}`")
    md.append(f"- stdout log: `{stdout_log}`")
    md.append(f"- stderr log: `{stderr_log}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- adapter rows: {len(adapter_rows)}")
    md.append(f"- raw probe rows: {len(raw_rows)}")
    md.append(f"- enriched rows: {len(enriched_rows)}")
    md.append(f"- adapter metadata: `{metadata}`")
    md.append("")
    md.append("## Critical family rows")
    md.append("")
    if critical:
        md.append(make_table(
            [
                "side",
                "target",
                "rank",
                "prob",
                "top1",
                "gate_scope",
                "only_sibling_gate_ok",
                "risk_flags",
            ],
            [
                [
                    r.get("adapter_side", ""),
                    r.get("policy_target", ""),
                    r.get("target_rank", ""),
                    r.get("target_prob", ""),
                    r.get("top1", ""),
                    r.get("gate_scope", ""),
                    r.get("allowed_as_only_sibling_family_gate", ""),
                    r.get("risk_flags", ""),
                ]
                for r in critical
            ],
        ))
    else:
        md.append("No critical family rows found.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.output_csv)
    print("wrote", args.output_md)
    print("raw probe csv:", raw_csv)
    print("rows:", len(enriched_rows))
    print("critical rows:", len(critical))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
