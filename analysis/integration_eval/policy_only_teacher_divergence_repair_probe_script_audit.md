# Policy-only teacher-divergence repair probe script audit

## Scope

- Branch: `exp/15x15-policy-only-teacher-divergence-repair-probe`
- Base audit: `analysis/integration_eval/teacher_divergence_signal_audit.md`
- Intended probe: policy-only teacher-divergence repair using the 25 priority Rapfi teacher rows.
- Preferred dataset/objective: pairwise policy margin teacher-vs-current/model move.
- Explicitly out of scope: value regression, C export, public benchmark, promotion.

## Git context

```text
branch: exp/15x15-policy-only-teacher-divergence-repair-probe
head: e45e55f Add teacher divergence signal audit

## exp/15x15-policy-only-teacher-divergence-repair-probe
?? analysis/integration_eval/adapter_probe_tmp/
?? analysis/integration_eval/b_mcts16_debug_failure_positions.csv
?? analysis/integration_eval/b_mcts16_debug_failure_positions.json
?? analysis/integration_eval/b_mcts16_debug_failure_set.csv
?? analysis/integration_eval/b_mcts16_debug_failure_set.json
?? analysis/integration_eval/b_mcts16_debug_failure_snapshots.json
?? analysis/integration_eval/b_mcts16_debug_failure_snapshots.md
?? analysis/integration_eval/b_mcts16_debug_hand_review.md
?? analysis/integration_eval/b_mcts16_debug_targets.txt
?? analysis/integration_eval/candidate_c_conservative_rapfi_failure_eval.csv
?? analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_dataset.json
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_positions.csv
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_positions.json
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_set.csv
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_set.json
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.json
?? analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.md
?? analysis/integration_eval/candidate_c_mcts16_debug_targets.txt
?? analysis/integration_eval/candidate_c_mcts16_debug_threat_analysis.csv
?? analysis/integration_eval/candidate_c_mcts16_debug_threat_analysis.md
?? analysis/integration_eval/candidate_d_g2_m15_diagnostic_dataset.json
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_positions.csv
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_positions.json
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_set.csv
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_set.json
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json
?? analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.md
?? analysis/integration_eval/candidate_d_mcts32_debug_targets.txt
?? analysis/integration_eval/candidate_d_mcts32_debug_threat_analysis.csv
?? analysis/integration_eval/candidate_d_mcts32_debug_threat_analysis.md
?? analysis/integration_eval/candidate_d_mcts32_nearend_failure_set.csv
?? analysis/integration_eval/candidate_d_mcts32_nearend_failure_set.json
?? analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.json
?? analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.md
?? analysis/integration_eval/candidate_d_mcts32_nearend_threat_analysis.csv
?? analysis/integration_eval/candidate_d_mcts32_nearend_threat_analysis.md
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_positions.csv
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_positions.json
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_set.csv
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_set.json
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.json
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.md
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_targets.txt
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_threat_analysis.csv
?? analysis/integration_eval/candidate_d_move15_mcts16_debug_threat_analysis.md
?? analysis/integration_eval/candidate_e_g2_m13_diagnostic_dataset.json
?? analysis/integration_eval/candidate_e_g2_m17_diagnostic_dataset.json
?? analysis/integration_eval/current_best_margin_3pair_b_rapfi_failure_eval.csv
?? analysis/integration_eval/current_best_margin_candidate_c_conservative_dataset.json
?? analysis/integration_eval/current_best_margin_candidate_c_dataset.json
?? analysis/integration_eval/current_best_rapfi_failure_eval.csv
?? analysis/integration_eval/debug_artifact_deep_schema_audit.json
?? analysis/integration_eval/debug_artifact_deep_schema_audit.md
?? analysis/integration_eval/teacher_divergence_data_inventory.json
?? analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv
?? analysis/integration_eval/teacher_divergence_data_inventory_report.md
?? analysis/integration_eval/teacher_divergence_expansion_candidate_manifest.csv
?? analysis/integration_eval/teacher_divergence_expansion_source_audit.csv
?? analysis/integration_eval/teacher_divergence_expansion_source_audit.json
?? analysis/integration_eval/teacher_divergence_expansion_source_audit.md
?? analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json
?? analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv
?? analysis/integration_eval/teacher_divergence_retention_expanded_report.md
?? analysis/integration_eval/teacher_divergence_retention_expanded_source_audit.json
?? analysis/integration_eval/teacher_divergence_source_schema_audit.json
?? analysis/integration_eval/teacher_divergence_source_schema_audit.md
?? analysis/v12l_eval/
?? analysis/v12l_margin_repair_dataset_g2m13_m15_3pair.json
?? analysis/v12l_margin_repair_dataset_g2m13_m15_3pair_eval_list.json
?? c-gomoku-cli.1.log
?? c_inference/compare_candidate_c_g2_m19
?? c_inference/compare_candidate_c_g2_m19.c
?? c_inference/compare_v12l_snapshots
?? c_inference/pbrain-neural-gomoku-b6c64
?? checkpoints/
?? eval_logs/integration/
?? eval_logs/rapfi_smoke/
?? eval_logs/v12l_margin/
?? scripts/audit_debug_artifact_deep_schema.py
?? scripts/audit_teacher_divergence_expansion_sources.py
?? scripts/audit_teacher_divergence_source_schema.py
?? scripts/build_teacher_divergence_data_inventory.py
?? scripts/build_teacher_divergence_retention_expanded_dataset.py
```

## Candidate script matrix

| script | exists | verdict | positives | cautions | excludes |
|---|---:|---|---|---|---|
| `scripts/train_rapfi_teacher_policy_margin.py` | yes | likely preferred reuse candidate | policy-related, pairwise/margin signal present, Rapfi teacher-related | CE/mixed-CE signal; not first choice if pairwise margin exists | - |
| `scripts/build_v12l_margin_repair_dataset.py` | yes | reference only | pairwise/margin signal present, Rapfi teacher-related | mentions value; verify it is not trained/regressed, CE/mixed-CE signal; not first choice if pairwise margin exists | - |
| `scripts/train_teacher_divergence_policy_anchor_probe.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present | mentions value; verify it is not trained/regressed, CE/mixed-CE signal; not first choice if pairwise margin exists | export/C path mention; should be out of scope for this probe, benchmark/promotion mention; should be out of scope |
| `scripts/train_teacher_divergence_policy_probe.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present | mentions value; verify it is not trained/regressed, CE/mixed-CE signal; not first choice if pairwise margin exists | export/C path mention; should be out of scope for this probe, benchmark/promotion mention; should be out of scope |
| `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present | mentions value; verify it is not trained/regressed, CE/mixed-CE signal; not first choice if pairwise margin exists | export/C path mention; should be out of scope for this probe, benchmark/promotion mention; should be out of scope |
| `scripts/evaluate_teacher_divergence_policy_probe_gates.py` | yes | exclude for this first probe | policy-related | CE/mixed-CE signal; not first choice if pairwise margin exists | regression/value-style objective risk, export/C path mention; should be out of scope for this probe |
| `scripts/build_candidate_g_teacher_policy_dataset.py` | yes | exclude for this first probe | policy-related, Rapfi teacher-related | - | regression/value-style objective risk |
| `scripts/train_candidate_g_teacher_policy.py` | yes | possible fallback / reference | policy-related | mentions value; verify it is not trained/regressed | - |
| `scripts/train_candidate_g_policy_first_dry_run.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present, Rapfi teacher-related | mentions value; verify it is not trained/regressed, CE/mixed-CE signal; not first choice if pairwise margin exists | regression/value-style objective risk, export/C path mention; should be out of scope for this probe, benchmark/promotion mention; should be out of scope |
| `scripts/run_teacher_divergence_regression_gated_policy_probe.py` | yes | exclude for this first probe | policy-related | CE/mixed-CE signal; not first choice if pairwise margin exists | regression/value-style objective risk, export/C path mention; should be out of scope for this probe, benchmark/promotion mention; should be out of scope |
| `scripts/train_candidate_h_value_ranking.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present | mentions value; verify it is not trained/regressed | regression/value-style objective risk |
| `scripts/train_v12l_margin_repair.py` | yes | exclude for this first probe | policy-related, pairwise/margin signal present | mentions value; verify it is not trained/regressed | regression/value-style objective risk |
| `scripts/train_v12l_margin_repair_frozen_bn.py` | yes | likely preferred reuse candidate | policy-related, pairwise/margin signal present | - | - |

## Argument surfaces

### `scripts/train_rapfi_teacher_policy_margin.py`

```text
23:     parser = argparse.ArgumentParser(description="Train Rapfi teacher policy pairwise margin repair checkpoint.")
24:     parser.add_argument(
29:     parser.add_argument(
34:     parser.add_argument("--init-checkpoint", type=Path, required=True)
35:     parser.add_argument("--reference-checkpoint", type=Path, required=True)
36:     parser.add_argument("--out-checkpoint", type=Path, required=True)
37:     parser.add_argument("--margin", type=float, default=1.0)
38:     parser.add_argument("--lr", type=float, default=5e-6)
39:     parser.add_argument("--epochs", type=int, default=40)
40:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
41:     parser.add_argument("--ce-weight", type=float, default=0.10)
42:     parser.add_argument("--weight-decay", type=float, default=1e-5)
43:     parser.add_argument("--seed", type=int, default=29)
44:     parser.add_argument("--print-every", type=int, default=5)
45:     parser.add_argument("--dry-run", action="store_true")
```

### `scripts/build_v12l_margin_repair_dataset.py`

```text
158:     parser = argparse.ArgumentParser()
159:     parser.add_argument(
164:     parser.add_argument(
169:     parser.add_argument("--dry-run", action="store_true")
```

### `scripts/train_teacher_divergence_policy_anchor_probe.py`

```text
41:     parser = argparse.ArgumentParser(
47:     parser.add_argument(
52:     parser.add_argument(
57:     parser.add_argument(
62:     parser.add_argument(
67:     parser.add_argument(
72:     parser.add_argument("--board-size", type=int, default=15)
73:     parser.add_argument("--win-length", type=int, default=5)
74:     parser.add_argument("--channels", type=int, default=64)
75:     parser.add_argument("--blocks", type=int, default=4)
76:     parser.add_argument("--epochs", type=int, default=80)
77:     parser.add_argument("--lr", type=float, default=3e-5)
78:     parser.add_argument("--kl-weight", type=float, default=0.35)
79:     parser.add_argument(
87:     parser.add_argument("--weight-decay", type=float, default=1e-4)
88:     parser.add_argument("--seed", type=int, default=17)
89:     parser.add_argument("--print-every", type=int, default=10)
90:     parser.add_argument(
95:     parser.add_argument("--dry-run", action="store_true")
96:     parser.add_argument("--no-save", action="store_true")
97:     parser.add_argument("--no-strict-splits", action="store_true")
98:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
```

### `scripts/train_teacher_divergence_policy_probe.py`

```text
41:     parser = argparse.ArgumentParser(
47:     parser.add_argument(
52:     parser.add_argument(
57:     parser.add_argument(
62:     parser.add_argument(
67:     parser.add_argument(
72:     parser.add_argument("--board-size", type=int, default=15)
73:     parser.add_argument("--win-length", type=int, default=5)
74:     parser.add_argument("--channels", type=int, default=64)
75:     parser.add_argument("--blocks", type=int, default=4)
76:     parser.add_argument("--epochs", type=int, default=80)
77:     parser.add_argument("--lr", type=float, default=3e-5)
78:     parser.add_argument("--kl-weight", type=float, default=0.25)
79:     parser.add_argument("--weight-decay", type=float, default=1e-4)
80:     parser.add_argument("--seed", type=int, default=17)
81:     parser.add_argument("--print-every", type=int, default=10)
82:     parser.add_argument(
87:     parser.add_argument("--dry-run", action="store_true")
88:     parser.add_argument("--no-save", action="store_true")
89:     parser.add_argument("--no-strict-splits", action="store_true")
90:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
```

### `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py`

```text
41:     parser = argparse.ArgumentParser(
47:     parser.add_argument(
52:     parser.add_argument(
57:     parser.add_argument(
62:     parser.add_argument(
67:     parser.add_argument(
72:     parser.add_argument("--board-size", type=int, default=15)
73:     parser.add_argument("--win-length", type=int, default=5)
74:     parser.add_argument("--channels", type=int, default=64)
75:     parser.add_argument("--blocks", type=int, default=4)
76:     parser.add_argument("--epochs", type=int, default=80)
77:     parser.add_argument("--lr", type=float, default=3e-5)
78:     parser.add_argument("--kl-weight", type=float, default=0.35)
79:     parser.add_argument(
87:     parser.add_argument("--weight-decay", type=float, default=1e-4)
88:     parser.add_argument("--seed", type=int, default=17)
89:     parser.add_argument("--print-every", type=int, default=10)
90:     parser.add_argument(
95:     parser.add_argument(
100:     parser.add_argument(
106:     parser.add_argument(
113:     parser.add_argument(
118:     parser.add_argument("--dry-run", action="store_true")
119:     parser.add_argument("--no-save", action="store_true")
120:     parser.add_argument("--no-strict-splits", action="store_true")
121:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
```

### `scripts/evaluate_teacher_divergence_policy_probe_gates.py`

```text
38:     parser = argparse.ArgumentParser(
41:     parser.add_argument(
46:     parser.add_argument(
51:     parser.add_argument("--min-candidate-rank-improved", type=int, default=8)
52:     parser.add_argument("--min-candidate-prob-improved", type=int, default=8)
53:     parser.add_argument("--max-candidate-prob-regressed", type=int, default=0)
54:     parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
55:     parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
56:     parser.add_argument("--max-heldout-prob-regressed", type=int, default=4)
57:     parser.add_argument("--max-heldout-rank-regressed", type=int, default=3)
58:     parser.add_argument("--allow-heldout-top1-loss", action="store_true")
```

### `scripts/build_candidate_g_teacher_policy_dataset.py`

```text
192:     parser = argparse.ArgumentParser(description="Build Candidate G teacher policy-distillation dataset.")
193:     parser.add_argument(
198:     parser.add_argument("--no-symmetry-augment", action="store_true")
199:     parser.add_argument("--no-tactical-anchors", action="store_true")
```

### `scripts/train_candidate_g_teacher_policy.py`

```text
17:     parser = argparse.ArgumentParser(description="Train Candidate G teacher policy-distillation checkpoint.")
18:     parser.add_argument(
23:     parser.add_argument("--init-checkpoint", type=Path, required=True)
24:     parser.add_argument(
29:     parser.add_argument("--epochs", type=int, default=80)
30:     parser.add_argument("--lr", type=float, default=5e-4)
31:     parser.add_argument("--kl-weight", type=float, default=0.15)
32:     parser.add_argument("--weight-decay", type=float, default=1e-4)
33:     parser.add_argument("--seed", type=int, default=17)
34:     parser.add_argument("--print-every", type=int, default=10)
35:     parser.add_argument("--board-size", type=int, default=15)
36:     parser.add_argument("--win-length", type=int, default=5)
37:     parser.add_argument("--channels", type=int, default=64)
38:     parser.add_argument("--blocks", type=int, default=4)
39:     parser.add_argument(
44:     parser.add_argument("--dry-run", action="store_true")
```

### `scripts/train_candidate_g_policy_first_dry_run.py`

```text
39:     parser = argparse.ArgumentParser(
42:     parser.add_argument(
47:     parser.add_argument(
52:     parser.add_argument(
57:     parser.add_argument(
62:     parser.add_argument("--board-size", type=int, default=15)
63:     parser.add_argument("--channels", type=int, default=64)
64:     parser.add_argument("--blocks", type=int, default=4)
65:     parser.add_argument("--epochs", type=int, default=80)
66:     parser.add_argument("--batch-size", type=int, default=14)
67:     parser.add_argument("--lr", type=float, default=3e-5)
68:     parser.add_argument("--weight-decay", type=float, default=1e-4)
69:     parser.add_argument("--kl-anchor", type=float, default=0.25)
70:     parser.add_argument("--seed", type=int, default=17)
71:     parser.add_argument("--min-seed-improved", type=int, default=2)
72:     parser.add_argument("--policy-head-only", action="store_true")
73:     parser.add_argument("--no-save", action="store_true")
74:     parser.add_argument("--strict-g2-move15", action="store_true")
75:     parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
```

### `scripts/run_teacher_divergence_regression_gated_policy_probe.py`

```text
14:     parser = argparse.ArgumentParser(
21:     parser.add_argument(
26:     parser.add_argument("--device", default="cpu")
27:     parser.add_argument("--epochs", type=int, default=80)
28:     parser.add_argument("--lr", type=float, default=3e-5)
29:     parser.add_argument("--kl-weight", type=float, default=0.35)
30:     parser.add_argument(
34:     parser.add_argument("--train-scope", default="policy_head")
35:     parser.add_argument(
40:     parser.add_argument(
45:     parser.add_argument(
51:     parser.add_argument(
58:     parser.add_argument(
63:     parser.add_argument(
68:     parser.add_argument(
73:     parser.add_argument(
79:     parser.add_argument("--min-candidate-rank-improved", type=int, default=8)
80:     parser.add_argument("--min-candidate-prob-improved", type=int, default=8)
81:     parser.add_argument("--max-candidate-prob-regressed", type=int, default=0)
82:     parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
83:     parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
84:     parser.add_argument("--max-heldout-prob-regressed", type=int, default=4)
85:     parser.add_argument("--max-heldout-rank-regressed", type=int, default=3)
86:     parser.add_argument("--allow-heldout-top1-loss", action="store_true")
88:     parser.add_argument(
97:     parser.add_argument(
```

### `scripts/train_candidate_h_value_ranking.py`

```text
26:     parser = argparse.ArgumentParser(description="Train Candidate H value-ranking phase from Candidate G.")
27:     parser.add_argument(
32:     parser.add_argument(
37:     parser.add_argument(
42:     parser.add_argument("--epochs", type=int, default=60)
43:     parser.add_argument("--lr", type=float, default=1e-5)
44:     parser.add_argument("--margin", type=float, default=0.20)
45:     parser.add_argument("--pair-loss-weight", type=float, default=1.0)
46:     parser.add_argument("--anchor-value-weight", type=float, default=0.25)
47:     parser.add_argument("--seed", type=int, default=23)
48:     parser.add_argument("--print-every", type=int, default=10)
49:     parser.add_argument("--board-size", type=int, default=15)
50:     parser.add_argument("--win-length", type=int, default=5)
51:     parser.add_argument("--channels", type=int, default=64)
52:     parser.add_argument("--blocks", type=int, default=4)
53:     parser.add_argument("--dry-run", action="store_true")
```

### `scripts/train_v12l_margin_repair.py`

```text
19:     parser = argparse.ArgumentParser(description="Train v12l pairwise margin repair candidate.")
20:     parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
21:     parser.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/v12i_failure_board_snapshots.json"))
22:     parser.add_argument("--init-checkpoint", type=Path, default=Path("checkpoints/15x15_v12i_candidate.pt"))
23:     parser.add_argument("--reference-checkpoint", type=Path, default=None)
24:     parser.add_argument("--out-checkpoint", type=Path, default=Path("checkpoints/15x15_v12l_margin_candidate.pt"))
25:     parser.add_argument("--margin", type=float, default=1.0)
26:     parser.add_argument("--lr", type=float, default=1e-5)
27:     parser.add_argument("--epochs", type=int, default=40)
28:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
29:     parser.add_argument("--anchor-value-weight", type=float, default=0.0)
30:     parser.add_argument("--batch-size", type=int, default=64)
31:     parser.add_argument("--seed", type=int, default=12)
32:     parser.add_argument("--print-every", type=int, default=5)
33:     parser.add_argument("--dry-run", action="store_true")
```

### `scripts/train_v12l_margin_repair_frozen_bn.py`

```text
15:     parser = argparse.ArgumentParser(description="Train v12l margin repair with frozen BatchNorm stats.")
16:     parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
17:     parser.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/v12i_failure_board_snapshots.json"))
18:     parser.add_argument("--init-checkpoint", type=Path, required=True)
19:     parser.add_argument("--reference-checkpoint", type=Path, required=True)
20:     parser.add_argument("--out-checkpoint", type=Path, required=True)
21:     parser.add_argument("--margin", type=float, default=1.0)
22:     parser.add_argument("--lr", type=float, default=5e-6)
23:     parser.add_argument("--epochs", type=int, default=40)
24:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
25:     parser.add_argument("--case-weights", type=str, default="2.0,1.0")
26:     parser.add_argument("--seed", type=int, default=21)
27:     parser.add_argument("--print-every", type=int, default=5)
28:     parser.add_argument("--dry-run", action="store_true")
```

## Keyword hits

### `scripts/train_rapfi_teacher_policy_margin.py`

```text
12: from gomoku_agent.checkpoint import load_compatible_checkpoint
13: from gomoku_agent.model import PolicyValueNet
22: def parse_args() -> argparse.Namespace:
23:     parser = argparse.ArgumentParser(description="Train Rapfi teacher policy pairwise margin repair checkpoint.")
27:         default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
34:     parser.add_argument("--init-checkpoint", type=Path, required=True)
35:     parser.add_argument("--reference-checkpoint", type=Path, required=True)
36:     parser.add_argument("--out-checkpoint", type=Path, required=True)
37:     parser.add_argument("--margin", type=float, default=1.0)
40:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
41:     parser.add_argument("--ce-weight", type=float, default=0.10)
60:         raise ValueError(f"expected {BOARD_SIZE} board rows, got {len(rows)}")
70:     raise ValueError(f"unknown side_to_move {side!r}")
75:         raise ValueError(f"expected rc with length 2, got {rc!r}")
78:         raise ValueError(f"rc out of range: {rc!r}")
90:         raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
100:         raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
104: def load_margin_samples(path: Path) -> list[dict[str, Any]]:
108:         raise ValueError("empty margin dataset")
128: def load_model(path: Path, device: torch.device) -> PolicyValueNet:
129:     model = PolicyValueNet(board_size=BOARD_SIZE, channels=CHANNELS, blocks=BLOCKS).to(device)
130:     loaded = load_compatible_checkpoint(
133:         device,
139:         raise RuntimeError(f"could not load compatible checkpoint: {path}")
143: def configure_policy_head_trainable(model: PolicyValueNet) -> list[torch.nn.Parameter]:
145:         parameter.requires_grad = name.startswith("policy.")
149:         raise ValueError("policy_head selected no trainable parameters")
151:     print(f"train_scope=policy_head")
158: def set_policy_head_training_mode(model: PolicyValueNet) -> None:
172:     ranked_actions = legal_actions[torch.argsort(probs[legal_actions], descending=True)].tolist()
176: def make_margin_tensors(
177:     samples: list[dict[str, Any]], device: torch.device
183:     weights = []
192:             raise ValueError(f"{sample['case_id']}: target_rc is not legal")
194:             raise ValueError(f"{sample['case_id']}: suppress_rc is not legal")
200:         weights.append(float(sample.get("sample_weight", 1.0)))
203:         torch.tensor(np.stack(states), dtype=torch.float32, device=device),
204:         torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
205:         torch.tensor(target_actions, dtype=torch.long, device=device),
206:         torch.tensor(suppress_actions, dtype=torch.long, device=device),
207:         torch.tensor(weights, dtype=torch.float32, device=device),
211: def make_anchor_tensors(anchors: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
212:     states = torch.tensor(np.stack([anchor["state"] for anchor in anchors]), dtype=torch.float32, device=device)
213:     masks = torch.tensor(np.stack([anchor["legal_mask"] for anchor in anchors]), dtype=torch.float32, device=device)
218: def diagnose_cases(label: str, model: PolicyValueNet, samples: list[dict[str, Any]], device: torch.device) -> None:
226:             device=device,
228:         mask = torch.tensor(legal_mask_from_board(sample["board"]), dtype=torch.float32, device=device).unsqueeze(0)
230:         logits, _values = model(state)
254:     model: PolicyValueNet,
255:     reference_model: PolicyValueNet,
256:     margin_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
258:     args: argparse.Namespace,
260:     states, legal_masks, target_actions, suppress_actions, weights = margin_tensors
263:         configure_policy_head_trainable(model),
268:     reference_model.eval()
270:         ref_anchor_logits, _ref_values = reference_model(anchor_states)
274:         set_policy_head_training_mode(model)
275:         logits, _values = model(states)
280:         per_row_margin = F.relu(args.margin - gaps)
281:         margin_loss = (per_row_margin * weights).sum() / weights.sum()
284:         ce_per_row = -log_probs.gather(1, target_actions.unsqueeze(1)).squeeze(1)
285:         ce_loss = (ce_per_row * weights).sum() / weights.sum()
287:         anchor_logits, _anchor_values = model(anchor_states)
289:         anchor_kl = (
293:         loss = margin_loss + args.anchor_kl_weight * anchor_kl + args.ce_weight * ce_loss
305:                 f"margin_loss={float(margin_loss.item()):.6f} "
306:                 f"anchor_kl={float(anchor_kl.item()):.6f} "
307:                 f"ce={float(ce_loss.item()):.6f} "
315:         raise ValueError("refusing to write checkpoints/15x15_current_best.pt")
320:     assert_not_current_best(args.out_checkpoint)
```

### `scripts/build_v12l_margin_repair_dataset.py`

```text
11: # Coordinates here are from live/C/Rapfi logs: x,y = col,row.
13: MARGIN_CASES = [
20:         "source": "v12i_failure_board_snapshots",
21:         "reason": "CE-only v12k raised target rank/prob but live C final stayed 9,4",
29:         "source": "v12i_failure_board_snapshots",
30:         "reason": "CE-only v12k raised target rank/prob but live C final stayed 6,6",
65:                 raise ValueError(f"unexpected token {tok!r}")
69:         raise ValueError(f"expected {BOARD_SIZE} board rows, found {len(rows)}")
80:     raise ValueError(f"unknown side_to_move: {side!r}")
86:         raise ValueError(f"{case_id}: {label} rc={rc} outside board")
88:         raise ValueError(
89:             f"{case_id}: {label} rc={rc} is occupied with value={board[r][c]}. "
102:         raise ValueError(
111:     if not isinstance(data, list):
112:         raise ValueError("snapshot JSON must be a list")
115:     for spec in MARGIN_CASES:
128:             "source": spec["source"],
148:         "name": "v12l_margin_repair_dataset",
150:             "xy": "external live/C/Rapfi logs: x,y = col,row",
167:         default=Path("analysis/v12l_margin_repair_dataset.json"),
174:     print(f"built {len(dataset['samples'])} v12l margin samples")
```

### `scripts/train_teacher_divergence_policy_anchor_probe.py`

```text
17: from gomoku_agent.checkpoint import load_compatible_checkpoint
18: from gomoku_agent.model import PolicyValueNet
31:     source_id: str
40: def parse_args() -> argparse.Namespace:
43:             "Anchored policy-focused teacher-divergence probe. "
50:         default=Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json"),
53:         "--base-checkpoint",
55:         default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
58:         "--out-checkpoint",
60:         default=Path("checkpoints/15x15_teacher_divergence_policy_anchor_probe.pt"),
65:         default=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv"),
70:         default=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_report.md"),
78:     parser.add_argument("--kl-weight", type=float, default=0.35)
80:         "--anchor-kl-splits",
81:         default="train_candidate,train_teacher_divergence",
83:             "Comma-separated splits used for KL anchoring against the base model. "
92:         choices=("policy_head", "policy_and_tower", "all"),
93:         default="policy_head",
98:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
102: def parse_coord_xy(value: Any) -> tuple[int, int] | None:
103:     if value is None:
105:     if isinstance(value, str):
106:         nums = [int(x) for x in COORD_RE.findall(value)]
110:     if isinstance(value, (list, tuple)) and len(value) >= 2:
111:         return int(value[0]), int(value[1])
112:     if isinstance(value, dict):
113:         if "x" in value and "y" in value:
114:             return int(value["x"]), int(value["y"])
115:         if "col" in value and "row" in value:
116:             return int(value["col"]), int(value["row"])
117:         if "c" in value and "r" in value:
118:             return int(value["c"]), int(value["r"])
125:         raise ValueError(f"xy out of bounds: {xy} for board_size={board_size}")
143:     raise ValueError(f"unsupported side_to_move: {side!r}")
146: def cell_to_int(value: Any) -> int:
147:     if isinstance(value, (int, float)):
148:         iv = int(value)
155:     s = str(value).strip().lower()
163: def parse_board(board_value: Any, board_size: int) -> np.ndarray:
164:     if isinstance(board_value, dict):
165:         if "board" in board_value:
166:             return parse_board(board_value["board"], board_size)
167:         if "grid" in board_value:
168:             return parse_board(board_value["grid"], board_size)
170:     if isinstance(board_value, str):
171:         text_value = board_value.strip()
173:         # Accepted safety_v3 stores board as a stringified list-of-lists.
175:         if text_value.startswith("["):
179:                 parsed = ast.literal_eval(text_value)
180:             except (SyntaxError, ValueError) as exc:
181:                 raise ValueError(
182:                     f"could not parse stringified board list: {text_value[:240]!r}"
187:         if "\\n" in text_value and "\n" not in text_value:
188:             text_value = text_value.replace("\\n", "\n")
190:         if "/" in text_value and "\n" not in text_value:
191:             raw_lines = text_value.split("/")
193:             len([ch for ch in text_value if ch in ".XOxo012+-"])
195:             and "\n" not in text_value
197:             compact = [ch for ch in text_value if ch in ".XOxo012+-"]
203:             raw_lines = text_value.splitlines()
235:             raise ValueError(
237:                 f"raw_lines={len(raw_lines)} repr={board_value[:240]!r}"
243:                 board[r, c] = cell_to_int(token)
246:     if not isinstance(board_value, list):
247:         raise ValueError(f"board must be list/grid/text-grid, got {type(board_value).__name__}")
249:     if len(board_value) != board_size:
250:         raise ValueError(f"board row count {len(board_value)} != board_size {board_size}")
253:     for r, line in enumerate(board_value):
254:         if isinstance(line, str):
259:             raise ValueError(f"board col count at row {r}: {len(tokens)} != {board_size}")
```

### `scripts/train_teacher_divergence_policy_probe.py`

```text
17: from gomoku_agent.checkpoint import load_compatible_checkpoint
18: from gomoku_agent.model import PolicyValueNet
31:     source_id: str
40: def parse_args() -> argparse.Namespace:
43:             "Small policy-focused teacher-divergence probe. "
50:         default=Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json"),
53:         "--base-checkpoint",
55:         default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
58:         "--out-checkpoint",
60:         default=Path("checkpoints/15x15_teacher_divergence_policy_probe.pt"),
65:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_eval.csv"),
70:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_report.md"),
78:     parser.add_argument("--kl-weight", type=float, default=0.25)
84:         choices=("policy_head", "policy_and_tower", "all"),
85:         default="policy_head",
90:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
94: def parse_coord_xy(value: Any) -> tuple[int, int] | None:
95:     if value is None:
97:     if isinstance(value, str):
98:         nums = [int(x) for x in COORD_RE.findall(value)]
102:     if isinstance(value, (list, tuple)) and len(value) >= 2:
103:         return int(value[0]), int(value[1])
104:     if isinstance(value, dict):
105:         if "x" in value and "y" in value:
106:             return int(value["x"]), int(value["y"])
107:         if "col" in value and "row" in value:
108:             return int(value["col"]), int(value["row"])
109:         if "c" in value and "r" in value:
110:             return int(value["c"]), int(value["r"])
117:         raise ValueError(f"xy out of bounds: {xy} for board_size={board_size}")
135:     raise ValueError(f"unsupported side_to_move: {side!r}")
138: def cell_to_int(value: Any) -> int:
139:     if isinstance(value, (int, float)):
140:         iv = int(value)
147:     s = str(value).strip().lower()
155: def parse_board(board_value: Any, board_size: int) -> np.ndarray:
156:     if isinstance(board_value, dict):
157:         if "board" in board_value:
158:             return parse_board(board_value["board"], board_size)
159:         if "grid" in board_value:
160:             return parse_board(board_value["grid"], board_size)
162:     if isinstance(board_value, str):
163:         text_value = board_value.strip()
165:         # Accepted safety_v3 stores board as a stringified list-of-lists.
167:         if text_value.startswith("["):
171:                 parsed = ast.literal_eval(text_value)
172:             except (SyntaxError, ValueError) as exc:
173:                 raise ValueError(
174:                     f"could not parse stringified board list: {text_value[:240]!r}"
179:         if "\\n" in text_value and "\n" not in text_value:
180:             text_value = text_value.replace("\\n", "\n")
182:         if "/" in text_value and "\n" not in text_value:
183:             raw_lines = text_value.split("/")
185:             len([ch for ch in text_value if ch in ".XOxo012+-"])
187:             and "\n" not in text_value
189:             compact = [ch for ch in text_value if ch in ".XOxo012+-"]
195:             raw_lines = text_value.splitlines()
227:             raise ValueError(
229:                 f"raw_lines={len(raw_lines)} repr={board_value[:240]!r}"
235:                 board[r, c] = cell_to_int(token)
238:     if not isinstance(board_value, list):
239:         raise ValueError(f"board must be list/grid/text-grid, got {type(board_value).__name__}")
241:     if len(board_value) != board_size:
242:         raise ValueError(f"board row count {len(board_value)} != board_size {board_size}")
245:     for r, line in enumerate(board_value):
246:         if isinstance(line, str):
251:             raise ValueError(f"board col count at row {r}: {len(tokens)} != {board_size}")
253:             board[r, c] = cell_to_int(token)
263:     if isinstance(metadata, dict):
272:     for value in candidates:
```

### `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py`

```text
17: from gomoku_agent.checkpoint import load_compatible_checkpoint
18: from gomoku_agent.model import PolicyValueNet
31:     source_id: str
40: def parse_args() -> argparse.Namespace:
43:             "Anchored policy-focused teacher-divergence probe. "
50:         default=Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json"),
53:         "--base-checkpoint",
55:         default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
58:         "--out-checkpoint",
60:         default=Path("checkpoints/15x15_teacher_divergence_policy_mixed_ce_anchor_probe.pt"),
65:         default=Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_eval.csv"),
70:         default=Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_report.md"),
78:     parser.add_argument("--kl-weight", type=float, default=0.35)
80:         "--anchor-kl-splits",
81:         default="train_candidate,train_teacher_divergence",
83:             "Comma-separated splits used for KL anchoring against the base model. "
91:         "--mixed-ce-anchor-splits",
92:         default="train_teacher_divergence",
93:         help="Comma-separated splits to add as low-weight CE anchors.",
96:         "--mixed-ce-anchor-label-types",
98:         help="Optional comma-separated label_type filter for mixed CE anchor rows.",
101:         "--mixed-ce-anchor-weight-scale",
104:         help="Multiplier applied to row weights for mixed CE anchor rows.",
107:         "--mixed-ce-anchor-max-rows",
110:         help="Optional cap for mixed CE anchor rows. 0 means no cap.",
115:         choices=("policy_head", "policy_and_tower", "all"),
116:         default="policy_head",
121:     parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
125: def parse_coord_xy(value: Any) -> tuple[int, int] | None:
126:     if value is None:
128:     if isinstance(value, str):
129:         nums = [int(x) for x in COORD_RE.findall(value)]
133:     if isinstance(value, (list, tuple)) and len(value) >= 2:
134:         return int(value[0]), int(value[1])
135:     if isinstance(value, dict):
136:         if "x" in value and "y" in value:
137:             return int(value["x"]), int(value["y"])
138:         if "col" in value and "row" in value:
139:             return int(value["col"]), int(value["row"])
140:         if "c" in value and "r" in value:
141:             return int(value["c"]), int(value["r"])
148:         raise ValueError(f"xy out of bounds: {xy} for board_size={board_size}")
166:     raise ValueError(f"unsupported side_to_move: {side!r}")
169: def cell_to_int(value: Any) -> int:
170:     if isinstance(value, (int, float)):
171:         iv = int(value)
178:     s = str(value).strip().lower()
186: def parse_board(board_value: Any, board_size: int) -> np.ndarray:
187:     if isinstance(board_value, dict):
188:         if "board" in board_value:
189:             return parse_board(board_value["board"], board_size)
190:         if "grid" in board_value:
191:             return parse_board(board_value["grid"], board_size)
193:     if isinstance(board_value, str):
194:         text_value = board_value.strip()
196:         # Accepted safety_v3 stores board as a stringified list-of-lists.
198:         if text_value.startswith("["):
202:                 parsed = ast.literal_eval(text_value)
203:             except (SyntaxError, ValueError) as exc:
204:                 raise ValueError(
205:                     f"could not parse stringified board list: {text_value[:240]!r}"
210:         if "\\n" in text_value and "\n" not in text_value:
211:             text_value = text_value.replace("\\n", "\n")
213:         if "/" in text_value and "\n" not in text_value:
214:             raw_lines = text_value.split("/")
216:             len([ch for ch in text_value if ch in ".XOxo012+-"])
218:             and "\n" not in text_value
220:             compact = [ch for ch in text_value if ch in ".XOxo012+-"]
226:             raw_lines = text_value.splitlines()
258:             raise ValueError(
```

### `scripts/evaluate_teacher_divergence_policy_probe_gates.py`

```text
20:         name="unanchored_e80_kl025",
21:         eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_probe_eval.csv"),
22:         notes="CE on train_candidate only; KL on train_candidate only; 80 epochs; kl=0.25",
25:         name="anchored_e80_kl035",
26:         eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv"),
27:         notes="CE on train_candidate; KL on train_candidate+train_teacher_divergence; 80 epochs; kl=0.35",
30:         name="anchored_e40_kl075",
31:         eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_e40_kl075_eval.csv"),
32:         notes="CE on train_candidate; KL on train_candidate+train_teacher_divergence; 40 epochs; kl=0.75; no-save",
37: def parse_args() -> argparse.Namespace:
39:         description="Evaluate pass/fail gates for teacher-divergence policy probe CSVs."
44:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_summary.csv"),
49:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_report.md"),
54:     parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
55:     parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
75:         raise ValueError(f"before/after id mismatch: {missing[:10]}")
136: def gate_probe(name: str, stats: dict[str, dict[str, Any]], args: argparse.Namespace) -> tuple[str, list[str]]:
140:     td = stats["train_teacher_divergence"]
156:     if td["prob_regressed"] > args.max_teacher_divergence_prob_regressed:
158:             f"train_teacher_divergence prob_regressed {td['prob_regressed']} > {args.max_teacher_divergence_prob_regressed}"
160:     if td["rank_regressed"] > args.max_teacher_divergence_rank_regressed:
162:             f"train_teacher_divergence rank_regressed {td['rank_regressed']} > {args.max_teacher_divergence_rank_regressed}"
188:     for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
250:     args: argparse.Namespace,
256:     lines.append("# Teacher-divergence policy probe gate report")
260:     lines.append("This report applies fixed regression gates to existing teacher-divergence policy probe CSVs.")
262:     lines.append("It does not train, save checkpoints, export C weights, run benchmarks, promote a model, or make a capacity conclusion.")
269:     lines.append(f"- max train_teacher_divergence probability regressed: {args.max_teacher_divergence_prob_regressed}")
270:     lines.append(f"- max train_teacher_divergence rank regressed: {args.max_teacher_divergence_rank_regressed}")
291:         for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
305:     lines.append("All evaluated probes fail the regression gates.")
307:     lines.append("The anchored e80/kl0.35 probe remains the best failed baseline because it keeps train_candidate rank/probability movement at 8/8 while reducing train_teacher_divergence regressions versus the unanchored probe.")
309:     lines.append("No existing probe should be exported, benchmarked, promoted, or used for a capacity conclusion.")
313:     lines.append("Do not continue blindly sweeping KL weight and epoch count. The next probe should add explicit regression gates before checkpoint saving and should explore mixed low-weight CE anchors on selected train_teacher_divergence rows while keeping heldout_retention evaluation-only.")
```

### `scripts/build_candidate_g_teacher_policy_dataset.py`

```text
13: class TeacherSpec:
19:     policy_targets: tuple[tuple[tuple[int, int], float], ...]
27: BASE_SPECS: tuple[TeacherSpec, ...] = (
28:     TeacherSpec(
29:         case_id="candidate_g_g2_p13_teacher_anchor_8_8",
34:         policy_targets=(((8, 8), 1.0),),
36:         role="nearby_teacher_anchor",
37:         notes="Pre-divergence anchor where Rapfi and Candidate D agree.",
41:     TeacherSpec(
42:         case_id="candidate_g_g2_p15_teacher_7_9_preserve_7_10",
47:         policy_targets=(((7, 9), 0.70), ((7, 10), 0.30)),
49:         role="strong_teacher_divergence",
50:         notes="Main ply15 teacher target while keeping Candidate D repaired move 7,10 policy-visible.",
54:     TeacherSpec(
55:         case_id="candidate_g_g2_p17_teacher_9_9",
60:         policy_targets=(((9, 9), 1.0),),
62:         role="strong_teacher_divergence",
63:         notes="Main ply17 teacher target; census rank was 70.",
67:     TeacherSpec(
68:         case_id="candidate_g_g2_p19_teacher_continuation_10_11",
73:         policy_targets=(((10, 11), 1.0),),
75:         role="nearby_teacher_continuation",
76:         notes="Teacher-aligned MCTS continuation after the divergent segment.",
80:     TeacherSpec(
81:         case_id="candidate_g_g2_p21_teacher_continuation_8_10",
86:         policy_targets=(((8, 10), 1.0),),
88:         role="nearby_teacher_continuation",
89:         notes="Teacher-aligned MCTS continuation after the divergent segment.",
96: TACTICAL_ANCHORS: tuple[TeacherSpec, ...] = (
97:     TeacherSpec(
103:         policy_targets=(((5, 4), 1.0),),
105:         role="tactical_regression_anchor",
110:     TeacherSpec(
116:         policy_targets=(((1, 4), 0.5), ((5, 4), 0.5)),
118:         role="tactical_regression_anchor",
119:         notes="C tactical benchmark anchor: either open-three endpoint is acceptable.",
123:     TeacherSpec(
129:         policy_targets=(((4, 3), 1.0),),
131:         role="tactical_regression_anchor",
136:     TeacherSpec(
142:         policy_targets=(((3, 5), 1.0),),
144:         role="tactical_regression_anchor",
149:     TeacherSpec(
155:         policy_targets=(((6, 2), 1.0),),
157:         role="tactical_regression_anchor",
162:     TeacherSpec(
168:         policy_targets=(((3, 7), 1.0),),
170:         role="tactical_regression_anchor",
175:     TeacherSpec(
181:         policy_targets=(((7, 4), 1.0),),
183:         role="tactical_regression_anchor",
191: def parse_args() -> argparse.Namespace:
192:     parser = argparse.ArgumentParser(description="Build Candidate G teacher policy-distillation dataset.")
196:         default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
222:     raise ValueError(f"unknown transform: {transform}")
241:         raise ValueError("policy target weights must be positive")
252: def make_sample(spec: TeacherSpec, transform: str) -> dict[str, object]:
256:     policy_targets = tuple(
258:         for xy, weight in spec.policy_targets
262:     for target, _ in policy_targets:
265:             raise ValueError(f"{spec.case_id}/{transform}: target {target} is occupied")
279:         "policy_targets": normalize_targets(policy_targets),
302:         "name": "candidate_g_teacher_policy_dataset",
304:         "purpose": "Policy-focused teacher distillation for Candidate D mcts32 game2 teacher disagreements.",
```

### `scripts/train_candidate_g_teacher_policy.py`

```text
12: from gomoku_agent.checkpoint import load_compatible_checkpoint
13: from gomoku_agent.model import PolicyValueNet
16: def parse_args() -> argparse.Namespace:
17:     parser = argparse.ArgumentParser(description="Train Candidate G teacher policy-distillation checkpoint.")
21:         default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
23:     parser.add_argument("--init-checkpoint", type=Path, required=True)
25:         "--out-checkpoint",
27:         default=Path("checkpoints/15x15_candidate_g_teacher_policy.pt"),
31:     parser.add_argument("--kl-weight", type=float, default=0.15)
41:         choices=("policy_head", "policy_and_tower", "all"),
42:         default="policy_head",
63:         raise ValueError(f"{row['id']}: expected {board_size}x{board_size} board")
70:         raise ValueError(f"{row['id']}: expected {board_size}x{board_size} board")
74: def policy_target(row: dict[str, Any], board_size: int) -> np.ndarray:
76:     for item in row["policy_targets"]:
81:         raise ValueError(f"{row['id']}: empty policy target")
90:     targets = np.stack([policy_target(row, board_size) for row in samples])
91:     weights = np.asarray([float(row.get("sample_weight", 1.0)) for row in samples], dtype=np.float32)
97:         torch.tensor(weights, dtype=torch.float32),
101: def load_model(path: Path, args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
102:     model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
103:     loaded = load_compatible_checkpoint(
106:         device,
112:         raise RuntimeError(f"could not load compatible checkpoint: {path}")
116: def configure_trainable(model: PolicyValueNet, train_scope: str) -> list[torch.nn.Parameter]:
120:         elif train_scope == "policy_head":
121:             parameter.requires_grad = name.startswith("policy")
122:         elif train_scope == "policy_and_tower":
123:             parameter.requires_grad = name.startswith(("stem", "tower", "policy"))
125:             raise ValueError(train_scope)
129:         raise ValueError("no trainable parameters selected")
137: def set_training_mode(model: PolicyValueNet, train_scope: str) -> None:
141:     elif train_scope == "policy_head":
142:         model.policy.train()
143:     elif train_scope == "policy_and_tower":
146:         model.policy.train()
148:         raise ValueError(train_scope)
158:     model: PolicyValueNet,
163:     device: torch.device,
166:     logits, values = model(states.to(device))
167:     probs = torch.exp(masked_log_softmax(logits, masks.to(device))).cpu()
175:         ranked = legal[torch.argsort(legal_probs, descending=True)].tolist()
184:             f"{sample['id']} value={float(values[index].item()):.6f} "
189: def train(args: argparse.Namespace) -> None:
192:     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
193:     samples, states_cpu, masks_cpu, targets_cpu, weights_cpu = load_dataset(args.dataset, args.board_size)
194:     print(f"device={device}")
197:     print(f"init_checkpoint={args.init_checkpoint}")
199:     model = load_model(args.init_checkpoint, args, device)
200:     reference = load_model(args.init_checkpoint, args, device)
201:     reference.eval()
202:     for parameter in reference.parameters():
205:     states = states_cpu.to(device)
206:     masks = masks_cpu.to(device)
207:     targets = targets_cpu.to(device)
208:     weights = weights_cpu.to(device)
210:     print_identity_diagnostics("BEFORE", model, samples, states_cpu, masks_cpu, targets_cpu, device)
212:         print("dry-run: no training or checkpoint write")
217:         ref_logits, _ = reference(states)
222:         logits, _values = model(states)
224:         ce_per_row = -(targets * log_probs).sum(dim=-1)
225:         ce_loss = (ce_per_row * weights).sum() / weights.sum()
226:         kl_per_row = (ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - log_probs)).sum(dim=-1)
227:         kl_loss = (kl_per_row * weights).sum() / weights.sum()
228:         loss = ce_loss + args.kl_weight * kl_loss
239:                 f"policy_ce={float(ce_loss.item()):.6f} "
240:                 f"kl={float(kl_loss.item()):.6f}",
244:     print_identity_diagnostics("AFTER", model, samples, states_cpu, masks_cpu, targets_cpu, device)
245:     args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
246:     torch.save(
```

### `scripts/train_candidate_g_policy_first_dry_run.py`

```text
18: from gomoku_agent.model import PolicyValueNet
38: def parse_args() -> argparse.Namespace:
40:         description="Candidate G conservative policy-first distillation dry run."
45:         default=Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.json"),
48:         "--base-checkpoint",
50:         default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
53:         "--out-checkpoint",
55:         default=Path("checkpoints/15x15_candidate_g_policy_first_dry_run.pt"),
60:         default=Path("analysis/integration_eval/candidate_g_policy_first_dry_run_report.md"),
69:     parser.add_argument("--kl-anchor", type=float, default=0.25)
72:     parser.add_argument("--policy-head-only", action="store_true")
75:     parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
81:     if isinstance(data, list):
83:     if isinstance(data, dict):
85:             if key in data and isinstance(data[key], list):
87:     raise ValueError(f"unsupported dataset JSON shape in {path}")
90: def parse_coord(value: Any) -> tuple[int, int] | None:
91:     if value is None:
93:     if isinstance(value, str):
94:         nums = [int(x) for x in COORD_RE.findall(value)]
98:     if isinstance(value, (list, tuple)) and len(value) >= 2:
99:         return int(value[0]), int(value[1])
100:     if isinstance(value, dict):
101:         r = value.get("row", value.get("r", value.get("y")))
102:         c = value.get("col", value.get("c", value.get("x")))
116:     value = first_present(
130:     if isinstance(value, (int, float)):
131:         iv = int(value)
137:     if isinstance(value, str):
138:         s = value.strip().lower()
144:     raise ValueError(
152: def char_to_cell(value: Any) -> int:
153:     if isinstance(value, (int, float)):
154:         iv = int(value)
161:     s = str(value).strip().lower()
172:     if isinstance(board, dict):
178:     if not isinstance(board, list):
179:         raise ValueError("board must be a list/grid or dict containing board/grid")
182:         raise ValueError(f"board row count {len(board)} != board_size {board_size}")
185:         if isinstance(line, str):
190:             raise ValueError(f"board col count at row {r}: {len(tokens)} != {board_size}")
192:             arr[r, c] = char_to_cell(token)
241:         value = row[key]
242:         if isinstance(value, dict):
244:         arr = np.asarray(value, dtype=np.float32)
253:     board_value = first_present(row, ("board", "grid", "position", "board_grid"))
254:     if board_value is not None:
255:         board = parse_board_grid(board_value, board_size)
261:         raise ValueError(f"cannot reconstruct board for row {row.get('id', row.get('row_id'))}")
282:     if isinstance(board_state, dict):
309:     target_value = first_present(
312:             "policy_target_move",
313:             "policy_target",
319:             "teacher_move",
320:             "teacher",
321:             "teacher_coord",
324:     target_rc = parse_coord(target_value)
326:         raise ValueError(f"{row_id}: cannot parse teacher/target move from {target_value!r}")
328:     model_value = first_present(
339:     model_rc = parse_coord(model_value)
346:         raise ValueError(f"{row_id}: target out of range: {target_rc}")
366:             raise ValueError(
392: def load_checkpoint_model(
393:     checkpoint: Path,
394:     device: torch.device,
398: ) -> tuple[PolicyValueNet, dict[str, Any]]:
399:     if not checkpoint.exists():
401:             f"base checkpoint not found: {checkpoint}. "
402:             "Pass --base-checkpoint to the intended 15x15 checkpoint."
405:     payload = torch.load(checkpoint, map_location=device)
```

### `scripts/run_teacher_divergence_regression_gated_policy_probe.py`

```text
6: import subprocess
13: def parse_args() -> argparse.Namespace:
16:             "Run a teacher-divergence anchored policy probe with regression gates. "
17:             "The checkpoint is saved only if gates pass."
24:         default=Path("scripts/train_teacher_divergence_policy_anchor_probe.py"),
26:     parser.add_argument("--device", default="cpu")
29:     parser.add_argument("--kl-weight", type=float, default=0.35)
31:         "--anchor-kl-splits",
32:         default="train_candidate,train_teacher_divergence",
34:     parser.add_argument("--train-scope", default="policy_head")
36:         "--mixed-ce-anchor-splits",
38:         help="Optional pass-through for mixed CE anchor scripts.",
41:         "--mixed-ce-anchor-label-types",
43:         help="Optional pass-through for mixed CE anchor scripts.",
46:         "--mixed-ce-anchor-weight-scale",
49:         help="Optional pass-through for mixed CE anchor scripts.",
52:         "--mixed-ce-anchor-max-rows",
55:         help="Optional pass-through for mixed CE anchor scripts.",
61:         default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv"),
66:         default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_train_report.md"),
71:         default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_gate_report.md"),
74:         "--out-checkpoint",
76:         default=Path("checkpoints/15x15_teacher_divergence_policy_regression_gated_probe.pt"),
82:     parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
83:     parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
93:             "and save the checkpoint. Without this flag, the runner only reports whether "
107: def run_anchor_probe(args: argparse.Namespace, *, no_save: bool) -> None:
111:         "--device",
112:         args.device,
117:         "--kl-weight",
118:         str(args.kl_weight),
119:         "--anchor-kl-splits",
120:         args.anchor_kl_splits,
127:         "--out-checkpoint",
128:         str(args.out_checkpoint),
130:     if args.mixed_ce_anchor_splits is not None:
131:         cmd.extend(["--mixed-ce-anchor-splits", str(args.mixed_ce_anchor_splits)])
132:     if args.mixed_ce_anchor_label_types is not None:
133:         cmd.extend(["--mixed-ce-anchor-label-types", str(args.mixed_ce_anchor_label_types)])
134:     if args.mixed_ce_anchor_weight_scale is not None:
135:         cmd.extend(["--mixed-ce-anchor-weight-scale", str(args.mixed_ce_anchor_weight_scale)])
136:     if args.mixed_ce_anchor_max_rows is not None:
137:         cmd.extend(["--mixed-ce-anchor-max-rows", str(args.mixed_ce_anchor_max_rows)])
146:     subprocess.run(cmd, check=True)
163:         raise ValueError(
226:     required = {"train_candidate", "train_teacher_divergence", "heldout_retention"}
229:         raise ValueError(f"missing required splits in eval CSV: {missing}")
236:     args: argparse.Namespace,
241:     teacher = stats["train_teacher_divergence"]
257:     if teacher["prob_regressed"] > args.max_teacher_divergence_prob_regressed:
259:             f"train_teacher_divergence prob_regressed {teacher['prob_regressed']} > {args.max_teacher_divergence_prob_regressed}"
261:     if teacher["rank_regressed"] > args.max_teacher_divergence_rank_regressed:
263:             f"train_teacher_divergence rank_regressed {teacher['rank_regressed']} > {args.max_teacher_divergence_rank_regressed}"
284:     args: argparse.Namespace,
288:     saved_checkpoint: bool,
293:     lines.append("# Teacher-divergence regression-gated policy probe report")
297:     lines.append("This runner trains/evaluates the anchored policy probe in no-save mode first, applies regression gates, and saves a checkpoint only if gates pass and `--save-on-pass` is set.")
299:     lines.append("It does not export C weights, run benchmarks, promote a model, overwrite current-best, or make a model-capacity conclusion.")
306:     lines.append(f"- kl_weight: {args.kl_weight}")
307:     lines.append(f"- anchor_kl_splits: `{args.anchor_kl_splits}`")
309:     lines.append(f"- mixed_ce_anchor_splits: `{args.mixed_ce_anchor_splits}`")
310:     lines.append(f"- mixed_ce_anchor_label_types: `{args.mixed_ce_anchor_label_types}`")
311:     lines.append(f"- mixed_ce_anchor_weight_scale: {args.mixed_ce_anchor_weight_scale}")
312:     lines.append(f"- mixed_ce_anchor_max_rows: {args.mixed_ce_anchor_max_rows}")
315:     lines.append(f"- out_checkpoint: `{args.out_checkpoint}`")
317:     lines.append(f"- saved_checkpoint: {saved_checkpoint}")
324:     lines.append(f"- max train_teacher_divergence probability regressed: {args.max_teacher_divergence_prob_regressed}")
325:     lines.append(f"- max train_teacher_divergence rank regressed: {args.max_teacher_divergence_rank_regressed}")
345:     for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
359:         lines.append("Passing gates means this probe is eligible for further review. It still does not automatically justify C export, benchmark, promotion, or current-best replacement.")
```

### `scripts/train_candidate_h_value_ranking.py`

```text
13: from gomoku_agent.checkpoint import load_compatible_checkpoint
14: from gomoku_agent.model import PolicyValueNet
18:     "candidate_g_g2_p15_teacher_7_9_preserve_7_10": {"teacher": (7, 9), "original": (7, 10), "weight": 2.0},
19:     "candidate_g_g2_p17_teacher_9_9": {"teacher": (9, 9), "original": (9, 5), "weight": 3.0},
20:     "candidate_g_g2_p19_teacher_continuation_10_11": {"teacher": (10, 11), "original": (9, 9), "weight": 1.0},
21:     "candidate_g_g2_p21_teacher_continuation_8_10": {"teacher": (8, 10), "original": (9, 9), "weight": 1.0},
25: def parse_args() -> argparse.Namespace:
26:     parser = argparse.ArgumentParser(description="Train Candidate H value-ranking phase from Candidate G.")
30:         default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
33:         "--init-checkpoint",
35:         default=Path("checkpoints/15x15_candidate_g_teacher_policy.pt"),
38:         "--out-checkpoint",
40:         default=Path("checkpoints/15x15_candidate_h_value_ranking.pt"),
44:     parser.add_argument("--margin", type=float, default=0.20)
46:     parser.add_argument("--anchor-value-weight", type=float, default=0.25)
76:     raise ValueError(f"unknown transform: {transform}")
106:         raise ValueError(f"{row['id']}: pair move {move_xy} ended the game; expected non-terminal child")
117:     teacher_states: list[np.ndarray] = []
119:     pair_weights: list[float] = []
127:             teacher_xy = transform_xy(spec["teacher"], transform, board_size)
129:             teacher_states.append(child_state_after(row, teacher_xy, board_size, win_length))
131:             pair_weights.append(float(spec["weight"]) * float(row.get("sample_weight", 1.0)))
133:         if row["role"] in {"strong_teacher_divergence", "nearby_teacher_continuation", "tactical_regression_anchor"}:
136:     if not teacher_states:
137:         raise ValueError("no value-ranking pairs built")
140:         torch.tensor(np.stack(teacher_states), dtype=torch.float32),
142:         torch.tensor(pair_weights, dtype=torch.float32),
147: def load_model(path: Path, args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
148:     model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
149:     loaded = load_compatible_checkpoint(
152:         device,
158:         raise RuntimeError(f"could not load compatible checkpoint: {path}")
162: def configure_value_head_only(model: PolicyValueNet) -> list[torch.nn.Parameter]:
164:         parameter.requires_grad = name.startswith(("value_conv", "value_fc"))
173: def value_from_mover_perspective(model: PolicyValueNet, states: torch.Tensor) -> torch.Tensor:
174:     _, values = model(states)
175:     return -values
181:     model: PolicyValueNet,
182:     teacher_states: torch.Tensor,
184:     pair_weights: torch.Tensor,
187:     teacher_values = value_from_mover_perspective(model, teacher_states)
188:     original_values = value_from_mover_perspective(model, original_states)
189:     gaps = teacher_values - original_values
193:     print(f"weighted_avg_gap={float((gaps * pair_weights).sum().item() / pair_weights.sum().item()):.6f}")
196: def train(args: argparse.Namespace) -> None:
199:     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
200:     samples, teacher_cpu, original_cpu, weights_cpu, anchors_cpu = load_dataset(
205:     print(f"device={device}")
207:     print(f"samples={len(samples)} pairs={len(teacher_cpu)} anchors={len(anchors_cpu)}")
208:     print(f"init_checkpoint={args.init_checkpoint}")
210:     model = load_model(args.init_checkpoint, args, device)
211:     reference = load_model(args.init_checkpoint, args, device)
213:     reference.eval()
214:     for parameter in reference.parameters():
217:     teacher_states = teacher_cpu.to(device)
218:     original_states = original_cpu.to(device)
219:     pair_weights = weights_cpu.to(device)
220:     anchor_states = anchors_cpu.to(device)
222:     print_pair_diagnostics("BEFORE", model, teacher_states, original_states, pair_weights)
224:         print("dry-run: no training or checkpoint write")
227:     optimizer = torch.optim.AdamW(configure_value_head_only(model), lr=args.lr, weight_decay=1e-5)
229:         _, ref_anchor_values = reference(anchor_states)
233:         _, teacher_child_values_opponent = model(teacher_states)
234:         _, original_child_values_opponent = model(original_states)
235:         teacher_values = -teacher_child_values_opponent
236:         original_values = -original_child_values_opponent
237:         gaps = teacher_values - original_values
238:         pair_losses = F.relu(args.margin - gaps)
239:         pair_loss = (pair_losses * pair_weights).sum() / pair_weights.sum()
241:         _, anchor_values = model(anchor_states)
```

### `scripts/train_v12l_margin_repair.py`

```text
12: from gomoku_agent.model import PolicyValueNet
18: def parse_args() -> argparse.Namespace:
19:     parser = argparse.ArgumentParser(description="Train v12l pairwise margin repair candidate.")
20:     parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
22:     parser.add_argument("--init-checkpoint", type=Path, default=Path("checkpoints/15x15_v12i_candidate.pt"))
23:     parser.add_argument("--reference-checkpoint", type=Path, default=None)
24:     parser.add_argument("--out-checkpoint", type=Path, default=Path("checkpoints/15x15_v12l_margin_candidate.pt"))
25:     parser.add_argument("--margin", type=float, default=1.0)
28:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
29:     parser.add_argument("--anchor-value-weight", type=float, default=0.0)
37: def load_checkpoint_payload(path: Path, device: torch.device) -> dict[str, Any]:
40:     return torch.load(path, map_location=device)
43: def build_model_from_payload(payload: dict[str, Any], device: torch.device) -> PolicyValueNet:
47:     model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks).to(device)
76:                 raise ValueError(f"unexpected token {tok!r}")
80:         raise ValueError(f"expected {BOARD_SIZE} rows, got {len(rows)}")
90:     raise ValueError(f"unknown side_to_move {side!r}")
95:         raise ValueError(f"expected rc with length 2, got {rc!r}")
98:         raise ValueError(f"last_move rc out of range: {rc!r}")
109:             raise ValueError(f"expected xy with length 2, got {xy!r}")
114:         value = item["last_move"]
115:         if isinstance(value, int):
116:             return _validate_rc([value // BOARD_SIZE, value % BOARD_SIZE])
117:         if isinstance(value, str) and value.isdigit():
118:             action = int(value)
147: def load_margin_cases(dataset_path: Path) -> list[dict[str, Any]]:
151:         raise ValueError("empty margin dataset")
157:         print(f"warning: no anchor snapshots at {snapshot_path}; KL anti-drift disabled")
178: def make_margin_tensors(samples: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
196:         torch.tensor(np.stack(states), dtype=torch.float32, device=device),
197:         torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
198:         torch.tensor(target_actions, dtype=torch.long, device=device),
199:         torch.tensor(suppress_actions, dtype=torch.long, device=device),
203: def make_anchor_tensors(anchors: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor] | None:
206:     states = torch.tensor(np.stack([a["state"] for a in anchors]), dtype=torch.float32, device=device)
207:     masks = torch.tensor(np.stack([a["legal_mask"] for a in anchors]), dtype=torch.float32, device=device)
223:     order = torch.argsort(legal_probs, descending=True)
231:     model: PolicyValueNet,
233:     device: torch.device,
242:             device=device,
244:         mask = torch.tensor(legal_mask_from_board(sample["board"]), dtype=torch.float32, device=device).unsqueeze(0)
246:         logits, value = model(state)
265:         print(f"value={float(value.item()):.6f}")
280:     model: PolicyValueNet,
281:     reference_model: PolicyValueNet,
282:     margin_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
284:     args: argparse.Namespace,
286:     states, legal_masks, target_actions, suppress_actions = margin_tensors
289:     reference_model.eval()
293:         logits, _values = model(states)
298:         margin_loss = F.relu(args.margin - gaps).mean()
300:         anchor_kl = torch.tensor(0.0, device=states.device)
301:         anchor_value_loss = torch.tensor(0.0, device=states.device)
303:         if anchor_tensors is not None and args.anchor_kl_weight > 0:
305:             current_logits, current_values = model(anchor_states)
307:                 ref_logits, ref_values = reference_model(anchor_states)
311:             anchor_kl = (ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - current_log_probs)).sum(dim=-1).mean()
313:             if args.anchor_value_weight > 0:
314:                 anchor_value_loss = F.mse_loss(current_values, ref_values)
316:         loss = margin_loss + args.anchor_kl_weight * anchor_kl + args.anchor_value_weight * anchor_value_loss
328:                 f"margin_loss={float(margin_loss.item()):.6f} "
329:                 f"anchor_kl={float(anchor_kl.item()):.6f} "
340:     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
342:     init_payload = load_checkpoint_payload(args.init_checkpoint, device)
343:     reference_path = args.reference_checkpoint or args.init_checkpoint
344:     reference_payload = load_checkpoint_payload(reference_path, device)
346:     model = build_model_from_payload(init_payload, device)
347:     reference_model = build_model_from_payload(reference_payload, device)
348:     for p in reference_model.parameters():
351:     samples = load_margin_cases(args.dataset)
```

### `scripts/train_v12l_margin_repair_frozen_bn.py`

```text
11: import train_v12l_margin_repair as base
14: def parse_args() -> argparse.Namespace:
15:     parser = argparse.ArgumentParser(description="Train v12l margin repair with frozen BatchNorm stats.")
16:     parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
18:     parser.add_argument("--init-checkpoint", type=Path, required=True)
19:     parser.add_argument("--reference-checkpoint", type=Path, required=True)
20:     parser.add_argument("--out-checkpoint", type=Path, required=True)
21:     parser.add_argument("--margin", type=float, default=1.0)
24:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
25:     parser.add_argument("--case-weights", type=str, default="2.0,1.0")
34:         if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
39:     model: base.PolicyValueNet,
40:     reference_model: base.PolicyValueNet,
41:     margin_tensors,
43:     args: argparse.Namespace,
45:     states, legal_masks, target_actions, suppress_actions = margin_tensors
47:     case_weights = [float(x) for x in args.case_weights.split(",")]
48:     if len(case_weights) != len(target_actions):
49:         raise ValueError(f"--case-weights must have {len(target_actions)} values")
50:     weights = torch.tensor(case_weights, dtype=torch.float32, device=states.device)
54:     reference_model.eval()
60:         logits, _values = model(states)
65:         per_case_margin = F.relu(args.margin - gaps)
66:         margin_loss = (weights * per_case_margin).sum() / weights.sum()
68:         anchor_kl = torch.tensor(0.0, device=states.device)
69:         if anchor_tensors is not None and args.anchor_kl_weight > 0:
71:             current_logits, _current_values = model(anchor_states)
73:                 ref_logits, _ref_values = reference_model(anchor_states)
77:             anchor_kl = (
81:         loss = margin_loss + args.anchor_kl_weight * anchor_kl
93:                 f"margin_loss={float(margin_loss.item()):.6f} "
94:                 f"anchor_kl={float(anchor_kl.item()):.6f} "
105:     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
107:     init_payload = base.load_checkpoint_payload(args.init_checkpoint, device)
108:     ref_payload = base.load_checkpoint_payload(args.reference_checkpoint, device)
110:     model = base.build_model_from_payload(init_payload, device)
111:     reference_model = base.build_model_from_payload(ref_payload, device)
112:     for p in reference_model.parameters():
115:     samples = base.load_margin_cases(args.dataset)
118:     print(f"device: {device}")
119:     print(f"loaded init checkpoint: {args.init_checkpoint}")
120:     print(f"loaded reference checkpoint: {args.reference_checkpoint}")
121:     print(f"margin samples: {len(samples)}")
123:     print(f"case_weights: {args.case_weights}")
124:     print(f"out checkpoint: {args.out_checkpoint}")
125:     print("NOTE: frozen BatchNorm stats; never writes checkpoints/15x15_current_best.pt")
127:     margin_tensors = base.make_margin_tensors(samples, device)
128:     anchor_tensors = base.make_anchor_tensors(anchors, device)
130:     base.diagnose_cases("BEFORE", model, samples, device)
136:     train_frozen_bn(model, reference_model, margin_tensors, anchor_tensors, args)
139:     base.diagnose_cases("AFTER", model, samples, device)
141:     args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
142:     torch.save(
149:             "v12l_margin_repair_frozen_bn": {
150:                 "init_checkpoint": str(args.init_checkpoint),
151:                 "reference_checkpoint": str(args.reference_checkpoint),
153:                 "margin": args.margin,
156:                 "anchor_kl_weight": args.anchor_kl_weight,
157:                 "case_weights": args.case_weights,
161:         args.out_checkpoint,
163:     print(f"saved {args.out_checkpoint}")
```

## Base audit context hits

Source exists: `analysis/integration_eval/teacher_divergence_signal_audit.md`

```text
1: # 15x15 Teacher-Divergence Signal Audit
5: This audit reviews the existing teacher-divergence and Rapfi-teacher supervision artifacts after the capacity-upgrade audit.
19: - validated Rapfi teacher disagreement rows,
20: - policy-only repair targets,
22: - no blind value regression from mixed Rapfi score formats.
24: ## Existing Rapfi teacher candidate set
28: - `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv`
29: - report: `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected_report.md`
34: - concrete teacher rows: `32`
35: - stable teacher move rows: `32`
36: - current_best already matches teacher: `7`
37: - current_best mismatches teacher: `25`
38: - priority candidates: `25`
39: - priority numeric-gap candidates: `12`
40: - priority gap-unavailable candidates: `13`
41: - low-priority already-matched rows: `7`
45: - value regression candidates: `0`
47: ## Recommended supervision interpretation
49: The Rapfi teacher rows should be treated as policy supervision, not direct value regression.
53: - all 32 rows have concrete and stable teacher moves,
54: - 25 rows are priority policy candidates because current_best disagrees with the teacher,
56: - mate and NA rows should not be coerced into numeric value targets,
57: - `value_regression_candidate` is false for every row in this pass.
61: ### Policy repair dataset
65: - `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`
69: - rows: `25`
70: - selection rule: `priority_candidate == true`
72:   - `priority_policy_numeric_gap`: `12`
73:   - `priority_policy_gap_unavailable`: `13`
74: - intended use: policy-only repair or ranking experiment
75: - value targets: blank / masked out
77: ### Pairwise margin dataset
81: - `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`
85: - rows: `25`
88:   - `priority_policy_numeric_gap`: `12`
89:   - `priority_policy_gap_unavailable`: `13`
93: - This is the cleaner next training-signal candidate than direct value regression.
94: - The target should be to rank the Rapfi teacher move above the current_best direct move.
95: - Numeric-gap rows can be used for weighting or priority, but not as direct value labels.
101: - `current_best`: 7 / 32 direct Rapfi-best matches
102: - `candidate_g`: 6 / 32 direct Rapfi-best matches
103: - `candidate_h`: 6 / 32 direct Rapfi-best matches
113: Teacher-divergence retention data closeout records two accepted dataset stages.
119: - `analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json`
120: - `analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv`
121: - `analysis/integration_eval/teacher_divergence_retention_clean_v2_report.md`
126: - train teacher-divergence baseline rows: `25`
134: - `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
135: - `analysis/integration_eval/teacher_divergence_retention_safety_v3_manifest.csv`
136: - `analysis/integration_eval/teacher_divergence_retention_safety_v3_report.md`
141: - train teacher-divergence baseline rows: `25`
143:   - 3 Candidate G teacher-divergence seed rows
153: ## Next training-signal recommendation
155: The next experimental unit should be a small policy-focused teacher-divergence repair probe from current-best-family.
157: Recommended input:
159: - use the 25 priority Rapfi teacher rows,
160: - prefer the pairwise margin dataset as the training target,
162: - include gap-unavailable mate and NA rows as policy targets only,
163: - do not use direct value regression.
167: 1. direct probe on the 25 priority teacher rows,
171: 5. tactical safety regression probe,
186: Proceed toward a policy-only teacher-divergence repair probe.
190: Do not use Rapfi mate or NA rows as numeric value labels.
```

## Initial design decision

1. Use `train_rapfi_teacher_policy_margin.py` as the first reuse candidate if its objective is confirmed to be policy-logit pairwise/margin only.
2. Do not use `run_teacher_divergence_regression_gated_policy_probe.py` for this probe because the audit scope excludes value/regression.
3. Do not use `train_candidate_h_value_ranking.py` for this probe because it is value-ranking/value-head oriented.
4. Treat CE/mixed-CE scripts as fallback/reference only; the first probe should prefer pairwise margin.
5. Add only small, reviewable files on this branch: a priority-row dataset builder/wrapper if needed, a dry-run/eval wrapper if needed, and markdown closeout.
6. Do not export C weights, do not run public benchmark, and do not write promotion language.

## Next implementation target

- Confirm exact schema of the 25 priority Rapfi teacher rows from the base audit or its source manifest.
- Build or reuse a dataset with one row per priority position containing board/state, side-to-move, teacher move, model/current move, and optional teacher confidence/rank metadata.
- Train policy-only margin objective from current best checkpoint, with value head frozen/ignored and no value loss term.
- Evaluate only with lightweight policy gates: teacher rank improvement, teacher-vs-model logit margin, retention-anchor non-regression.
- Stop after probe report; no C export/public benchmark/promotion.
