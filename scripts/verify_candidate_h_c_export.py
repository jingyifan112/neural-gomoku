from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evaluate_candidate_g_policy import board_from_dataset_row, load_model, rank_of_action
from gomoku_agent.model import masked_policy


CASE_IDS = (
    "candidate_g_g2_p15_teacher_7_9_preserve_7_10",
    "candidate_g_g2_p17_teacher_9_9",
    "candidate_g_g2_p15_teacher_7_9_preserve_7_10",
)
CASE_LABELS = ("g2_ply15_teacher_disagreement", "g2_ply17_teacher_disagreement", "candidate_d_repair_anchor")
PROBE_MOVES = {
    "g2_ply15_teacher_disagreement": {"teacher": "7,9", "original": "7,10", "repair": "7,10"},
    "g2_ply17_teacher_disagreement": {"teacher": "9,9", "original": "9,5"},
    "candidate_d_repair_anchor": {"teacher": "7,9", "repair": "7,10", "old_bad": "8,8"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Candidate H exported C weights.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_h_value_ranking.pt"),
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("weights/15x15_candidate_h_value_ranking_weights.bin"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("weights/15x15_candidate_h_value_ranking_manifest.json"),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument(
        "--case-dir",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_c_parity_cases"),
    )
    parser.add_argument(
        "--parity-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_c_parity.csv"),
    )
    parser.add_argument(
        "--tactical-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_c_tactical_gate.csv"),
    )
    parser.add_argument(
        "--decision-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_c_decision_probes.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_c_export_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--logits-tolerance", type=float, default=1e-4)
    parser.add_argument("--probs-tolerance", type=float, default=1e-5)
    parser.add_argument("--value-tolerance", type=float, default=1e-4)
    return parser.parse_args()


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def xy_to_action(coord: str, board_size: int) -> int:
    x_text, y_text = coord.split(",", maxsplit=1)
    return int(y_text) * board_size + int(x_text)


def action_to_xy(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def rank_for_probs(probs: np.ndarray, legal: np.ndarray, action: int) -> int | None:
    legal_actions = np.flatnonzero(legal > 0)
    ranked = sorted((int(item) for item in legal_actions), key=lambda move: float(probs[move]), reverse=True)
    if int(action) not in ranked:
        return None
    return ranked.index(int(action)) + 1


def load_identity_samples(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        row["base_case_id"]: row
        for row in data["samples"]
        if row["transform"] == "identity"
    }


@torch.no_grad()
def write_python_reference(
    model,
    row: dict[str, Any],
    case_path: Path,
    args: argparse.Namespace,
    device: torch.device,
) -> dict[str, Any]:
    board = board_from_dataset_row(row, args.board_size, args.win_length)
    state_np = board.encode().astype("<f4")
    legal_np = board.legal_mask().astype("<f4")
    state = torch.tensor(state_np[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(legal_np[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)
    logits_np = logits[0].cpu().numpy().astype("<f4")
    probs_np = probs[0].cpu().numpy().astype("<f4")
    value_np = np.array([float(value[0].item())], dtype="<f4")
    top_legal = int(np.argmax(np.where(legal_np > 0, logits_np, -np.inf)))

    case_path.mkdir(parents=True, exist_ok=True)
    state_np.tofile(case_path / "input.bin")
    legal_np.tofile(case_path / "legal_mask.bin")
    logits_np.tofile(case_path / "python_policy_logits.bin")
    probs_np.tofile(case_path / "python_policy_probs.bin")
    value_np.tofile(case_path / "python_value.bin")
    (case_path / "python_top_legal_move.txt").write_text(f"{top_legal}\n", encoding="utf-8")
    return {
        "board": board,
        "legal": legal_np,
        "logits": logits_np,
        "probs": probs_np,
        "value": float(value_np[0]),
        "top": top_legal,
    }


def run_c_infer(case_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    output_prefix = case_path / "c"
    top_path = case_path / "c_top_legal_move.txt"
    run(
        [
            str(Path("c_inference") / "dump_infer"),
            str(args.weights),
            str(case_path / "input.bin"),
            str(case_path / "legal_mask.bin"),
            str(output_prefix),
            str(top_path),
        ]
    )
    logits = np.fromfile(case_path / "c_policy_logits.bin", dtype="<f4")
    probs = np.fromfile(case_path / "c_policy_probs.bin", dtype="<f4")
    value = float(np.fromfile(case_path / "c_value.bin", dtype="<f4")[0])
    top = int(top_path.read_text(encoding="utf-8").strip())
    return {"logits": logits, "probs": probs, "value": value, "top": top}


def parity_rows(args: argparse.Namespace, model, samples: dict[str, dict[str, Any]], device: torch.device) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    rows = []
    probe_contexts = []
    for label, case_id in zip(CASE_LABELS, CASE_IDS):
        row = samples[case_id]
        case_path = args.case_dir / label
        py = write_python_reference(model, row, case_path, args, device)
        c = run_c_infer(case_path, args)
        logits_diff = float(np.max(np.abs(py["logits"] - c["logits"])))
        probs_diff = float(np.max(np.abs(py["probs"] - c["probs"])))
        value_diff = abs(float(py["value"]) - float(c["value"]))
        top_agree = py["top"] == c["top"]
        rows.append(
            {
                "case": label,
                "policy_logits_max_abs_diff": f"{logits_diff:.9g}",
                "policy_probs_max_abs_diff": f"{probs_diff:.9g}",
                "value_abs_diff": f"{value_diff:.9g}",
                "python_top_legal": action_to_xy(py["top"], args.board_size),
                "c_top_legal": action_to_xy(c["top"], args.board_size),
                "top_legal_agree": str(top_agree),
                "pass": str(
                    logits_diff <= args.logits_tolerance
                    and probs_diff <= args.probs_tolerance
                    and value_diff <= args.value_tolerance
                    and top_agree
                ),
            }
        )
        probe_contexts.append({"label": label, "row": row, "python": py, "c": c})
    return rows, probe_contexts


def decision_probe_rows(args: argparse.Namespace, probe_contexts: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for context in probe_contexts:
        label = context["label"]
        legal = context["python"]["legal"]
        c_probs = context["c"]["probs"]
        c_top = context["c"]["top"]
        for move_label, coord in PROBE_MOVES[label].items():
            action = xy_to_action(coord, args.board_size)
            rank = rank_for_probs(c_probs, legal, action)
            rows.append(
                {
                    "case": label,
                    "move_label": move_label,
                    "move": coord,
                    "c_rank": str(rank) if rank is not None else "ILLEGAL",
                    "c_prob": f"{float(c_probs[action]):.6f}" if rank is not None else "ILLEGAL",
                    "c_top_move": action_to_xy(c_top, args.board_size),
                    "selected_by_c_direct": str(c_top == action),
                }
            )
    return rows


BENCH_RE = re.compile(r"case\s+(?P<case>\S+)\s+direct=(?P<direct>\S+)\s+safety=(?P<safety>\S+)\s+mcts_raw=(?P<mcts_raw>\S+)\s+mcts_safety=(?P<mcts_safety>\S+)")


def tactical_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    result = run([str(Path("c_inference") / "benchmark_c"), str(args.weights), "--mcts-sims", "32"])
    rows = []
    for line in result.stdout.splitlines():
        match = BENCH_RE.search(line)
        if not match:
            continue
        rows.append(
            {
                "case": match.group("case"),
                "direct": match.group("direct"),
                "policy_safety": match.group("safety"),
                "mcts_raw": match.group("mcts_raw"),
                "mcts_safety": match.group("mcts_safety"),
            }
        )
    if len(rows) != 7:
        raise RuntimeError(f"expected 7 C tactical rows, found {len(rows)}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def all_pass(rows: list[dict[str, str]], key: str = "pass") -> bool:
    return all(row[key] == "True" for row in rows)


def tactical_non_regressed(rows: list[dict[str, str]]) -> bool:
    return all(row["direct"] == "PASS" and row["policy_safety"] == "PASS" and row["mcts_safety"] == "PASS" for row in rows)


def probes_pass(rows: list[dict[str, str]]) -> bool:
    by_case = {(row["case"], row["move_label"]): row for row in rows}
    return (
        by_case[("g2_ply15_teacher_disagreement", "teacher")]["c_rank"] == "1"
        and by_case[("g2_ply17_teacher_disagreement", "teacher")]["c_rank"] == "1"
        and int(by_case[("candidate_d_repair_anchor", "repair")]["c_rank"]) <= 3
    )


def write_report(
    args: argparse.Namespace,
    parity: list[dict[str, str]],
    tactical: list[dict[str, str]],
    probes: list[dict[str, str]],
) -> None:
    parity_ok = all_pass(parity)
    tactical_ok = tactical_non_regressed(tactical)
    probe_ok = probes_pass(probes)
    lines = [
        "# Candidate H C export verification",
        "",
        "## Artifacts",
        "",
        f"- checkpoint: `{args.checkpoint}`",
        f"- weights: `{args.weights}`",
        f"- manifest: `{args.manifest}`",
        "",
        "## Parity",
        "",
        "| case | logits diff | probs diff | value diff | top agree | pass |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in parity:
        lines.append(
            f"| {row['case']} | {row['policy_logits_max_abs_diff']} | "
            f"{row['policy_probs_max_abs_diff']} | {row['value_abs_diff']} | "
            f"{row['top_legal_agree']} | {row['pass']} |"
        )
    lines.extend(
        [
            "",
            "## C Tactical Gate",
            "",
            "| metric | pass count |",
            "| --- | ---: |",
            f"| direct | {sum(1 for row in tactical if row['direct'] == 'PASS')}/7 |",
            f"| policy+safety | {sum(1 for row in tactical if row['policy_safety'] == 'PASS')}/7 |",
            f"| mcts_raw | {sum(1 for row in tactical if row['mcts_raw'] == 'PASS')}/7 |",
            f"| mcts+safety | {sum(1 for row in tactical if row['mcts_safety'] == 'PASS')}/7 |",
            "",
            "## C Decision Probes",
            "",
            "| case | move | rank | prob | C top | selected |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in probes:
        lines.append(
            f"| {row['case']} {row['move_label']} | {row['move']} | {row['c_rank']} | "
            f"{row['c_prob']} | {row['c_top_move']} | {row['selected_by_c_direct']} |"
        )
    lines.extend(["", "## Decision", ""])
    if parity_ok and tactical_ok and probe_ok:
        lines.append("C parity, C tactical, and C decision probes pass. Rapfi smoke is now unblocked by the export gates, but was not run in this step.")
    else:
        lines.append("At least one C export gate failed. Do not run Rapfi smoke.")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, args, device)
    model.eval()
    samples = load_identity_samples(args.dataset)

    parity, probe_contexts = parity_rows(args, model, samples, device)
    probes = decision_probe_rows(args, probe_contexts)
    tactical = tactical_rows(args)

    write_csv(args.parity_csv, parity)
    write_csv(args.decision_csv, probes)
    write_csv(args.tactical_csv, tactical)
    write_report(args, parity, tactical, probes)
    print(f"device={device}")
    print(f"wrote {args.parity_csv}")
    print(f"wrote {args.decision_csv}")
    print(f"wrote {args.tactical_csv}")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
