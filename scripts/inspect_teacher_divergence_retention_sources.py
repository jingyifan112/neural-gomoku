from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

OUT_DIR = Path("analysis/integration_eval")
OUT_JSON = OUT_DIR / "teacher_divergence_retention_source_audit.json"
OUT_MD = OUT_DIR / "teacher_divergence_retention_source_audit.md"

SOURCES = [
    # public benchmark / Rapfi re-query
    "analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv",
    "analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv",
    "analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv",
    "analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json",
    "analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json",
    "analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json",
    "analysis/public_benchmark_eval/corpus8_selected_snapshot_targets.csv",
    "analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv",
    "analysis/public_benchmark_eval/current_best_failure_set_eval.csv",

    # earlier teacher-divergence diagnostics
    "analysis/integration_eval/candidate_i_rapfi_requery_census.csv",
    "analysis/integration_eval/candidate_i_smoke_failure_census.csv",
    "analysis/integration_eval/candidate_d_teacher_disagreement_census.csv",
    "analysis/integration_eval/candidate_g_teacher_seed_dataset.json",
    "analysis/integration_eval/candidate_g_teacher_seed_manifest.json",

    # retention / conservative anchors
    "analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json",
    "analysis/integration_eval/current_best_margin_candidate_c_anchors.json",
    "analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json",
    "analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json",
    "analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json",
    "analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json",
]


def preview_value(v: Any, max_len: int = 160) -> str:
    s = repr(v)
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def inspect_csv(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    columns = list(reader.fieldnames or [])
    nonempty = {}
    examples = {}
    unique_counts = {}

    for col in columns:
        values = [r.get(col, "") for r in rows]
        filled = [v for v in values if v not in ("", None, "NA", "nan", "None")]
        nonempty[col] = len(filled)
        examples[col] = preview_value(filled[0]) if filled else ""
        if len(filled) <= 200:
            unique_counts[col] = len(set(filled))

    return {
        "kind": "csv",
        "path": str(path),
        "exists": True,
        "rows": len(rows),
        "columns": columns,
        "nonempty": nonempty,
        "unique_counts": unique_counts,
        "examples": examples,
        "sample_rows": rows[:3],
    }


def summarize_json_obj(obj: Any) -> dict[str, Any]:
    if isinstance(obj, list):
        item_types = Counter(type(x).__name__ for x in obj)
        first = obj[0] if obj else None
        first_keys = list(first.keys()) if isinstance(first, dict) else []
        return {
            "top_type": "list",
            "length": len(obj),
            "item_types": dict(item_types),
            "first_keys": first_keys,
            "first_item": first,
        }

    if isinstance(obj, dict):
        summary = {
            "top_type": "dict",
            "top_keys": list(obj.keys()),
            "top_key_summaries": {},
        }
        for k, v in obj.items():
            if isinstance(v, list):
                first = v[0] if v else None
                summary["top_key_summaries"][k] = {
                    "type": "list",
                    "length": len(v),
                    "first_keys": list(first.keys()) if isinstance(first, dict) else [],
                    "first_item_preview": first,
                }
            elif isinstance(v, dict):
                summary["top_key_summaries"][k] = {
                    "type": "dict",
                    "keys": list(v.keys())[:50],
                    "num_keys": len(v),
                }
            else:
                summary["top_key_summaries"][k] = {
                    "type": type(v).__name__,
                    "preview": preview_value(v),
                }
        return summary

    return {
        "top_type": type(obj).__name__,
        "preview": preview_value(obj),
    }


def inspect_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out = {
        "kind": "json",
        "path": str(path),
        "exists": True,
    }
    out.update(summarize_json_obj(obj))
    return out


def inspect_path(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        return {
            "path": path_str,
            "exists": False,
        }

    if path.suffix == ".csv":
        return inspect_csv(path)
    if path.suffix == ".json":
        return inspect_json(path)

    return {
        "path": str(path),
        "exists": True,
        "kind": path.suffix,
        "size_bytes": path.stat().st_size,
    }


def md_escape(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")



def clean_markdown_lines(lines: list[str]) -> str:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned) + "\n"

def write_md(audit: list[dict[str, Any]]) -> None:
    lines = []
    lines.append("# Teacher divergence / retention source audit")
    lines.append("")
    lines.append("Purpose: inspect available source schemas before building a new dataset/manifest/report.")
    lines.append("")
    lines.append("## Source summary")
    lines.append("")
    lines.append("| path | kind | rows/length | notes |")
    lines.append("|---|---:|---:|---|")

    for item in audit:
        path = item["path"]
        if not item.get("exists"):
            lines.append(f"| `{md_escape(path)}` | missing |  | missing |")
            continue

        kind = item.get("kind", item.get("top_type", "unknown"))
        rows = item.get("rows", item.get("length", ""))
        notes = ""
        if item.get("kind") == "csv":
            notes = f"{len(item.get('columns', []))} columns"
        elif item.get("kind") == "json":
            if item.get("top_type") == "list":
                notes = f"first keys: {', '.join(item.get('first_keys', [])[:12])}"
            elif item.get("top_type") == "dict":
                notes = f"top keys: {', '.join(item.get('top_keys', [])[:12])}"
        lines.append(f"| `{md_escape(path)}` | {md_escape(kind)} | {md_escape(rows)} | {md_escape(notes)} |")

    lines.append("")
    lines.append("## CSV columns")
    for item in audit:
        if item.get("kind") != "csv" or not item.get("exists"):
            continue
        lines.append("")
        lines.append(f"### `{item['path']}`")
        lines.append("")
        lines.append("| column | nonempty | unique | example |")
        lines.append("|---|---:|---:|---|")
        for col in item["columns"]:
            lines.append(
                f"| `{md_escape(col)}` | "
                f"{item['nonempty'].get(col, '')} | "
                f"{item['unique_counts'].get(col, '')} | "
                f"{md_escape(item['examples'].get(col, ''))} |"
            )

    lines.append("")
    lines.append("## JSON structures")
    for item in audit:
        if item.get("kind") != "json" or not item.get("exists"):
            continue
        lines.append("")
        lines.append(f"### `{item['path']}`")
        lines.append("")
        lines.append("```json")
        compact = {k: v for k, v in item.items() if k not in {"first_item", "sample_rows"}}
        lines.append(json.dumps(compact, indent=2, ensure_ascii=False)[:4000])
        lines.append("```")

    OUT_MD.write_text(clean_markdown_lines(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = [inspect_path(p) for p in SOURCES]

    OUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md(audit)

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print()
    print("=== source summary ===")
    for item in audit:
        if not item.get("exists"):
            print(f"MISSING {item['path']}")
            continue
        if item.get("kind") == "csv":
            print(f"CSV  rows={item['rows']:>3} cols={len(item['columns']):>2}  {item['path']}")
        elif item.get("kind") == "json":
            if item.get("top_type") == "list":
                print(f"JSON list len={item['length']:>3}  {item['path']}")
            else:
                print(f"JSON dict keys={len(item.get('top_keys', [])):>2}  {item['path']}")
        else:
            print(f"FILE {item['path']}")

    print()
    print("=== git status ===")
    import subprocess
    subprocess.run(["git", "status", "-sb"], check=False)


if __name__ == "__main__":
    main()
