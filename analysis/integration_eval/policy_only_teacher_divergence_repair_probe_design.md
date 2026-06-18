# Policy-only teacher-divergence repair probe design

## Scope lock

- Branch: `exp/15x15-policy-only-teacher-divergence-repair-probe`
- Base commit: `e45e55f Add teacher divergence signal audit`
- Goal: small policy-only teacher-divergence repair probe using the 25 priority Rapfi teacher rows.
- Preferred objective: pairwise policy margin, teacher move over current/model move.
- Explicit non-goals: value regression, value-head ranking, C export, public benchmark, promotion.

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
?? analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md
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

## Script decision

### Preferred training reuse

Use `scripts/train_rapfi_teacher_policy_margin.py` as the first implementation target, but run/configure it as strictly policy-only:

- set `--ce-weight 0` for the first probe;
- keep pairwise margin as the primary supervised signal;
- keep `--anchor-kl-weight` small if retention anchors are included;
- do not add value loss or value regression targets;
- write checkpoint only as a probe artifact, not as a promoted candidate.

### Fallback/reference

Use `scripts/train_v12l_margin_repair_frozen_bn.py` only as reference if the Rapfi margin trainer cannot consume the 25-row dataset cleanly. Avoid the older mixed-CE/regression-gated/value-ranking scripts.

## Script argument surfaces

### `scripts/train_rapfi_teacher_policy_margin.py`

```text
22: def parse_args() -> argparse.Namespace:
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
46:     return parser.parse_args()
319:     args = parse_args()
```

### `scripts/train_v12l_margin_repair_frozen_bn.py`

```text
14: def parse_args() -> argparse.Namespace:
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
29:     return parser.parse_args()
101:     args = parse_args()
```

### `scripts/build_v12l_margin_repair_dataset.py`

```text
158:     parser = argparse.ArgumentParser()
159:     parser.add_argument(
164:     parser.add_argument(
169:     parser.add_argument("--dry-run", action="store_true")
170:     args = parser.parse_args()
```

### `scripts/evaluate_teacher_divergence_policy_probe_gates.py`

```text
37: def parse_args() -> argparse.Namespace:
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
59:     return parser.parse_args()
320:     args = parse_args()
```

## Loss / objective audit hits

### `scripts/train_rapfi_teacher_policy_margin.py`

```text
13: from gomoku_agent.model import PolicyValueNet
23:     parser = argparse.ArgumentParser(description="Train Rapfi teacher policy pairwise margin repair checkpoint.")
27:         default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
37:     parser.add_argument("--margin", type=float, default=1.0)
40:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
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
143: def configure_policy_head_trainable(model: PolicyValueNet) -> list[torch.nn.Parameter]:
145:         parameter.requires_grad = name.startswith("policy.")
149:         raise ValueError("policy_head selected no trainable parameters")
151:     print(f"train_scope=policy_head")
158: def set_policy_head_training_mode(model: PolicyValueNet) -> None:
162: def masked_log_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
163:     return F.log_softmax(logits.masked_fill(legal_mask <= 0, -1e9), dim=-1)
166: def masked_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
167:     return torch.exp(masked_log_softmax(logits, legal_mask))
176: def make_margin_tensors(
192:             raise ValueError(f"{sample['case_id']}: target_rc is not legal")
194:             raise ValueError(f"{sample['case_id']}: suppress_rc is not legal")
218: def diagnose_cases(label: str, model: PolicyValueNet, samples: list[dict[str, Any]], device: torch.device) -> None:
230:         logits, _values = model(state)
231:         probs = masked_softmax(logits, mask)[0]
232:         logits0 = logits[0]
236:         target_logit = float(logits0[target_action].item())
237:         suppress_logit = float(logits0[suppress_action].item())
247:             f"target_logit={target_logit:.6f} "
248:             f"suppress_logit={suppress_logit:.6f} "
249:             f"gap={target_logit - suppress_logit:.6f}"
254:     model: PolicyValueNet,
255:     reference_model: PolicyValueNet,
256:     margin_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
260:     states, legal_masks, target_actions, suppress_actions, weights = margin_tensors
263:         configure_policy_head_trainable(model),
270:         ref_anchor_logits, _ref_values = reference_model(anchor_states)
271:         ref_anchor_probs = masked_softmax(ref_anchor_logits, anchor_masks)
274:         set_policy_head_training_mode(model)
275:         logits, _values = model(states)
277:         target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
278:         suppress_logits = logits.gather(1, suppress_actions.unsqueeze(1)).squeeze(1)
279:         gaps = target_logits - suppress_logits
280:         per_row_margin = F.relu(args.margin - gaps)
281:         margin_loss = (per_row_margin * weights).sum() / weights.sum()
283:         log_probs = masked_log_softmax(logits, legal_masks)
285:         ce_loss = (ce_per_row * weights).sum() / weights.sum()
287:         anchor_logits, _anchor_values = model(anchor_states)
288:         anchor_log_probs = masked_log_softmax(anchor_logits, anchor_masks)
289:         anchor_kl = (
293:         loss = margin_loss + args.anchor_kl_weight * anchor_kl + args.ce_weight * ce_loss
296:         loss.backward()
304:                 f"loss={float(loss.item()):.6f} "
305:                 f"margin_loss={float(margin_loss.item()):.6f} "
306:                 f"anchor_kl={float(anchor_kl.item()):.6f} "
307:                 f"ce={float(ce_loss.item()):.6f} "
315:         raise ValueError("refusing to write checkpoints/15x15_current_best.pt")
331:     samples = load_margin_samples(args.dataset)
333:     margin_tensors = make_margin_tensors(samples, device)
341:     print(f"margin samples: {len(samples)}")
344:     print("NOTE: policy-head-only training; never writes checkpoints/15x15_current_best.pt")
351:     train(model, reference_model, margin_tensors, anchor_tensors, args)
355:     torch.save(
362:             "rapfi_teacher_policy_margin": {
367:                 "margin": args.margin,
370:                 "anchor_kl_weight": args.anchor_kl_weight,
371:                 "ce_weight": args.ce_weight,
373:                 "train_scope": "policy_head",
```

### `scripts/train_v12l_margin_repair_frozen_bn.py`

```text
11: import train_v12l_margin_repair as base
15:     parser = argparse.ArgumentParser(description="Train v12l margin repair with frozen BatchNorm stats.")
16:     parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
21:     parser.add_argument("--margin", type=float, default=1.0)
24:     parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
39:     model: base.PolicyValueNet,
40:     reference_model: base.PolicyValueNet,
41:     margin_tensors,
45:     states, legal_masks, target_actions, suppress_actions = margin_tensors
49:         raise ValueError(f"--case-weights must have {len(target_actions)} values")
60:         logits, _values = model(states)
61:         target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
62:         suppress_logits = logits.gather(1, suppress_actions.unsqueeze(1)).squeeze(1)
63:         gaps = target_logits - suppress_logits
65:         per_case_margin = F.relu(args.margin - gaps)
66:         margin_loss = (weights * per_case_margin).sum() / weights.sum()
68:         anchor_kl = torch.tensor(0.0, device=states.device)
69:         if anchor_tensors is not None and args.anchor_kl_weight > 0:
71:             current_logits, _current_values = model(anchor_states)
73:                 ref_logits, _ref_values = reference_model(anchor_states)
74:                 ref_probs = base.masked_softmax(ref_logits, anchor_masks)
76:             current_log_probs = base.masked_log_softmax(current_logits, anchor_masks)
77:             anchor_kl = (
81:         loss = margin_loss + args.anchor_kl_weight * anchor_kl
84:         loss.backward()
92:                 f"loss={float(loss.item()):.6f} "
93:                 f"margin_loss={float(margin_loss.item()):.6f} "
94:                 f"anchor_kl={float(anchor_kl.item()):.6f} "
115:     samples = base.load_margin_cases(args.dataset)
121:     print(f"margin samples: {len(samples)}")
127:     margin_tensors = base.make_margin_tensors(samples, device)
136:     train_frozen_bn(model, reference_model, margin_tensors, anchor_tensors, args)
142:     torch.save(
149:             "v12l_margin_repair_frozen_bn": {
153:                 "margin": args.margin,
156:                 "anchor_kl_weight": args.anchor_kl_weight,
```

### `scripts/build_v12l_margin_repair_dataset.py`

```text
13: MARGIN_CASES = [
65:                 raise ValueError(f"unexpected token {tok!r}")
69:         raise ValueError(f"expected {BOARD_SIZE} board rows, found {len(rows)}")
80:     raise ValueError(f"unknown side_to_move: {side!r}")
86:         raise ValueError(f"{case_id}: {label} rc={rc} outside board")
88:         raise ValueError(
89:             f"{case_id}: {label} rc={rc} is occupied with value={board[r][c]}. "
102:         raise ValueError(
112:         raise ValueError("snapshot JSON must be a list")
115:     for spec in MARGIN_CASES:
148:         "name": "v12l_margin_repair_dataset",
167:         default=Path("analysis/v12l_margin_repair_dataset.json"),
174:     print(f"built {len(dataset['samples'])} v12l margin samples")
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
39:         description="Evaluate pass/fail gates for teacher-divergence policy probe CSVs."
44:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_summary.csv"),
49:         default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_report.md"),
58:     parser.add_argument("--allow-heldout-top1-loss", action="store_true")
75:         raise ValueError(f"before/after id mismatch: {missing[:10]}")
173:     if not args.allow_heldout_top1_loss and held["after_top1"] < held["before_top1"]:
256:     lines.append("# Teacher-divergence policy probe gate report")
260:     lines.append("This report applies fixed regression gates to existing teacher-divergence policy probe CSVs.")
273:     lines.append(f"- allow heldout top-1 loss: {args.allow_heldout_top1_loss}")
305:     lines.append("All evaluated probes fail the regression gates.")
307:     lines.append("The anchored e80/kl0.35 probe remains the best failed baseline because it keeps train_candidate rank/probability movement at 8/8 while reducing train_teacher_divergence regressions versus the unanchored probe.")
313:     lines.append("Do not continue blindly sweeping KL weight and epoch count. The next probe should add explicit regression gates before checkpoint saving and should explore mixed low-weight CE anchors on selected train_teacher_divergence rows while keeping heldout_retention evaluation-only.")
```

## Data/source schema inventory

### `analysis/integration_eval/teacher_divergence_signal_audit.md`

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
65: - `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`
69: - rows: `25`
70: - selection rule: `priority_candidate == true`
72:   - `priority_policy_numeric_gap`: `12`
73:   - `priority_policy_gap_unavailable`: `13`
74: - intended use: policy-only repair or ranking experiment
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
163: - do not use direct value regression.
167: 1. direct probe on the 25 priority teacher rows,
186: Proceed toward a policy-only teacher-divergence repair probe.
188: Do not start another blind capacity experiment.
189: Do not promote Candidate G or Candidate H.
190: Do not use Rapfi mate or NA rows as numeric value labels.
191: Do not mix held-out retention rows into training.
```

### `analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv`

```json
{
  "rows": 48,
  "columns": [
    "path",
    "groups",
    "exists",
    "kind",
    "format",
    "rows",
    "file_count",
    "line_count",
    "size_bytes",
    "total_size_bytes",
    "interesting_columns_present",
    "teacher_move_present",
    "teacher_rank_present",
    "model_move_present",
    "score_gap_present",
    "role_counts",
    "error"
  ],
  "sample": {
    "path": "analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json",
    "groups": "[\"retention_anchors\"]",
    "exists": "True",
    "kind": "file",
    "format": "json",
    "rows": "8",
    "file_count": "",
    "line_count": "",
    "size_bytes": "33836",
    "total_size_bytes": "",
    "interesting_columns_present": "",
    "teacher_move_present": "",
    "teacher_rank_present": "",
    "model_move_present": "",
    "score_gap_present": "",
    "role_counts": "{}",
    "error": ""
  },
  "teacher_move_present_counts": {
    "": 25,
    "0": 22,
    "52": 1
  },
  "teacher_rank_present_counts": {
    "": 25,
    "0": 23
  },
  "role_counts_counts": {
    "{}": 32,
    "": 10,
    "{\"heldout_retention_anchor\": 11, \"teacher_divergence\": 25}": 3,
    "{\"general_teacher_aligned_anchor\": 6, \"nearby_nondivergent_anchor\": 5, \"retention_anchor\": 1, \"seed_teacher_divergence\": 2}": 2,
    "{\"heldout_retention_anchor\": 27, \"teacher_divergence\": 25}": 1
  }
}
```

### `analysis/integration_eval/teacher_divergence_expansion_candidate_manifest.csv`

```json
{
  "rows": 0,
  "columns": [
    "include_hint",
    "include_reason",
    "role_guess",
    "source_path",
    "source_index",
    "source_id",
    "game",
    "ply_or_move_count",
    "side",
    "teacher_or_target_move",
    "model_or_current_best_move",
    "teacher_model_disagree",
    "rank",
    "gap",
    "weight",
    "type_or_reason",
    "has_board",
    "board_digest"
  ]
}
```

### `analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv`

```json
{
  "rows": 233,
  "columns": [
    "record_id",
    "base_id",
    "role",
    "split",
    "priority",
    "source_group",
    "source_path",
    "source_index",
    "game_id",
    "ply",
    "side",
    "teacher_move",
    "model_move",
    "teacher_rank",
    "score_gap",
    "weight",
    "has_teacher_move",
    "has_model_move",
    "teacher_model_disagree",
    "include_in_expanded_dataset",
    "duplicate_count",
    "duplicate_sources"
  ],
  "sample": {
    "record_id": "teacher_divergence_tdiv_legacy_g1_m40_19fa82308789",
    "base_id": "tdiv_legacy_g1_m40",
    "role": "teacher_divergence",
    "split": "existing_train",
    "priority": "140",
    "source_group": "existing_td_retention_dataset",
    "source_path": "analysis/integration_eval/teacher_divergence_retention_dataset.json",
    "source_index": "3",
    "game_id": "",
    "ply": "",
    "side": "black",
    "teacher_move": "12,6",
    "model_move": "",
    "teacher_rank": "",
    "score_gap": "",
    "weight": "",
    "has_teacher_move": "True",
    "has_model_move": "False",
    "teacher_model_disagree": "False",
    "include_in_expanded_dataset": "True",
    "duplicate_count": "1",
    "duplicate_sources": "[\"analysis/integration_eval/teacher_divergence_retention_dataset.json\"]"
  },
  "role_counts": {
    "heldout_retention_anchor": 71,
    "audit_only": 64,
    "teacher_divergence": 52,
    "public_failure_snapshot_audit": 46
  },
  "priority_counts": {
    "30": 64,
    "140": 50,
    "0": 46,
    "110": 38,
    "95": 22,
    "105": 11,
    "135": 2
  },
  "source_group_counts": {
    "existing_td_retention_dataset": 88,
    "current_best_rapfi_scoregap": 64,
    "public_failure_snapshots": 46,
    "retention_anchors": 22,
    "candidate_g_seed": 13
  },
  "source_path_counts": {
    "analysis/integration_eval/teacher_divergence_retention_manifest.csv": 52,
    "analysis/integration_eval/teacher_divergence_retention_dataset.json": 36,
    "analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv": 32,
    "analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv": 32,
    "analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json": 32,
    "analysis/integration_eval/candidate_g_teacher_seed_dataset.json": 13,
    "analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json": 8,
    "analysis/rapfi_failure_board_snapshots.json": 7,
    "analysis/rapfi_failure_set_labeled.json": 7,
    "analysis/integration_eval/current_best_margin_candidate_c_anchors.json": 5,
    "analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json": 3,
    "analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json": 3
  },
  "source_index_counts": {
    "0": 13,
    "1": 12,
    "2": 12,
    "3": 11,
    "4": 10,
    "5": 9,
    "6": 9,
    "7": 7,
    "8": 6,
    "10": 6,
    "11": 6,
    "9": 6
  },
  "teacher_move_counts": {
    "": 132,
    "10,7": 15,
    "8,6": 14,
    "7,9": 11,
    "7,5": 5,
    "5,6": 5,
    "5,11": 5,
    "8,5": 4,
    "5,8": 3,
    "8,10": 3,
    "12,6": 2,
    "7,8": 2
  },
  "teacher_rank_counts": {
    "": 233
  },
  "weight_counts": {
    "": 220,
    "0.75": 6,
    "1.0": 4,
    "2.0": 2,
    "1.5": 1
  },
  "has_teacher_move_counts": {
    "False": 132,
    "True": 101
  },
  "teacher_model_disagree_counts": {
    "False": 230,
    "True": 3
  },
  "duplicate_sources_counts": {
    "[\"analysis/integration_eval/teacher_divergence_retention_manifest.csv\"]": 52,
    "[\"analysis/integration_eval/teacher_divergence_retention_dataset.json\"]": 36,
    "[\"analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv\"]": 32,
    "[\"analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv\"]": 32,
    "[\"analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json\"]": 32,
    "[\"analysis/integration_eval/candidate_g_teacher_seed_dataset.json\", \"analysis/integration_eval/candidate_g_teacher_seed_manifest.json\"]": 13,
    "[\"analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json\"]": 8,
    "[\"analysis/rapfi_failure_board_snapshots.json\"]": 7,
    "[\"analysis/rapfi_failure_set_labeled.csv\", \"analysis/rapfi_failure_set_labeled.json\"]": 7,
    "[\"analysis/integration_eval/current_best_margin_candidate_c_anchors.json\", \"analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json\"]": 5,
    "[\"analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json\"]": 3,
    "[\"analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json\"]": 3
  }
}
```

### `analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json`

```json
{
  "type": "dict",
  "keys": [
    "counts",
    "note",
    "records"
  ],
  "records_len": 123,
  "records_first_keys": [
    "base_id",
    "duplicate_count",
    "duplicate_sources",
    "game_id",
    "has_model_move",
    "has_teacher_move",
    "include_in_expanded_dataset",
    "model_move",
    "ply",
    "priority",
    "raw",
    "record_id",
    "role",
    "score_gap",
    "side",
    "source_group",
    "source_index",
    "source_path",
    "split",
    "teacher_model_disagree",
    "teacher_move",
    "teacher_rank",
    "weight"
  ]
}
```

### `analysis/integration_eval/current_best_margin_candidate_c_dataset.json`

```json
{
  "type": "dict",
  "keys": [
    "coordinate_convention",
    "name",
    "samples"
  ],
  "samples_len": 7,
  "samples_first_keys": [
    "board",
    "board_size",
    "board_snapshot_before_decision",
    "case_id",
    "current_player",
    "game_number",
    "move_count",
    "old_final",
    "old_final_xy",
    "reason",
    "side_to_move",
    "source",
    "suppress_rc",
    "suppress_xy",
    "target_rc",
    "target_xy",
    "win_length"
  ]
}
```

### `analysis/integration_eval/current_best_margin_candidate_c_conservative_dataset.json`

```json
{
  "type": "dict",
  "keys": [
    "coordinate_convention",
    "name",
    "samples"
  ],
  "samples_len": 5,
  "samples_first_keys": [
    "board",
    "board_size",
    "board_snapshot_before_decision",
    "case_id",
    "current_player",
    "game_number",
    "move_count",
    "old_final",
    "old_final_xy",
    "reason",
    "side_to_move",
    "source",
    "suppress_rc",
    "suppress_xy",
    "target_rc",
    "target_xy",
    "win_length"
  ]
}
```

### `analysis/v12l_margin_repair_dataset_g2m13_m15_3pair.json`

```json
{
  "type": "dict",
  "keys": [
    "coordinate_convention",
    "name",
    "samples"
  ],
  "samples_len": 3,
  "samples_first_keys": [
    "board",
    "board_size",
    "board_snapshot_before_decision",
    "case_id",
    "current_player",
    "game_number",
    "move_count",
    "old_final",
    "old_final_xy",
    "reason",
    "side_to_move",
    "source",
    "suppress_rc",
    "suppress_xy",
    "target_rc",
    "target_xy",
    "win_length"
  ]
}
```

## Proposed concrete files

Create at most these files on this branch:

1. `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md`
   - Already created.
2. `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md`
   - This file.
3. `scripts/build_policy_only_teacher_divergence_priority_dataset.py`
   - Only if existing dataset builders cannot cleanly emit the 25 priority pairwise rows.
4. `analysis/integration_eval/policy_only_teacher_divergence_priority_dataset.json`
   - Small 25-row dataset, if built.
5. `analysis/integration_eval/policy_only_teacher_divergence_priority_manifest.csv`
   - Traceability manifest, if built.

Do not stage old untracked artifacts. Do not use `git add .`.

## Probe training command sketch, not to run yet

```bash
PYTHONPATH=src python scripts/train_rapfi_teacher_policy_margin.py \
  --dataset analysis/integration_eval/policy_only_teacher_divergence_priority_dataset.json \
  --init-checkpoint checkpoints/15x15_current_best.pt \
  --reference-checkpoint checkpoints/15x15_current_best.pt \
  --out-checkpoint checkpoints/15x15_policy_only_teacher_divergence_repair_probe.pt \
  --margin 1.0 \
  --lr 5e-6 \
  --epochs 40 \
  --anchor-kl-weight 0.05 \
  --ce-weight 0 \
  --dry-run
```

This is intentionally a sketch. Confirm the actual checkpoint path and dataset schema before running without `--dry-run`.

## Gate sketch

Use only lightweight policy gates:

- teacher rank improves on priority rows;
- teacher-vs-current/model logit margin improves on priority rows;
- retention anchors do not materially regress;
- no value metrics are used as training targets;
- no C export/public benchmark/promotion language.

## Next decision

After this design audit, inspect whether the 25 priority rows can be extracted directly from an existing manifest. If yes, implement only a small dataset converter. If no, add a minimal builder that reads the audit/source manifest and emits a schema accepted by `train_rapfi_teacher_policy_margin.py` with `--ce-weight 0`.

## Schema resolution after local inspection

The existing pairwise margin dataset already matches the intended probe input:

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`
- rows: `25`
- top-level key: `samples`
- required trainer fields present:
  - `board`
  - `current_player`
  - `target_rc`
  - `suppress_rc`
  - `sample_weight`

Decision: no new 25-row dataset converter is needed for the first probe. Reuse the existing pairwise margin dataset directly.

The trainer must be invoked with `--ce-weight 0` so the first probe remains pairwise-margin-first rather than mixed margin/CE. The trainer is still policy-head-only; value outputs are computed by the network forward pass but are not used as training targets.

## Dry-run validation plan

Run only a dry-run first:

```bash
PYTHONPATH=src python scripts/train_rapfi_teacher_policy_margin.py \
  --dataset analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json \
  --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json \
  --init-checkpoint <current-best-checkpoint> \
  --reference-checkpoint <current-best-checkpoint> \
  --out-checkpoint checkpoints/15x15_policy_only_teacher_divergence_repair_probe.pt \
  --margin 1.0 \
  --lr 5e-6 \
  --epochs 40 \
  --anchor-kl-weight 0.05 \
  --ce-weight 0 \
  --dry-run

