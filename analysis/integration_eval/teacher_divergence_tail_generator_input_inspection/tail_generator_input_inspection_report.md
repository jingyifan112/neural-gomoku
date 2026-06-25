# Teacher-divergence tail generator input inspection

## Scope

- Input/schema inspection only.
- No source generation run.
- No dataset build.
- No training.
- No checkpoint read/write.
- No C export, no public benchmark, no promotion.

## Upstream

- preflight decision: `TAIL_GENERATION_PREFLIGHT_READY_WITH_LOCAL_TEACHER_ENGINE`
- tail gap: `12`

## JSON inputs

### board_snapshots

- exists: `True`
- type: `list`
- top keys: `[]`
- candidate lists:
  - `$` len=32 sample_type=dict keys=['board_snapshot_after_decision', 'board_snapshot_before_decision', 'direct', 'failure_type', 'final', 'game_number', 'loss_reason', 'mcts_raw', 'mcts_safety', 'move_count', 'next_rapfi_bestline', 'notes', 'policy_safety', 'previous_rapfi_bestline', 'side_to_move', 'value']
- common keys:
  - game_number:5, move_count:5, side_to_move:5, value:5, direct:5, policy_safety:5, mcts_raw:5, mcts_safety:5, final:5, previous_rapfi_bestline:5, next_rapfi_bestline:5, board_snapshot_before_decision:5, board_snapshot_after_decision:5, loss_reason:5, failure_type:5, notes:5

### base_multisuppress_dataset

- exists: `True`
- type: `dict`
- top keys: `['checkpoint', 'description', 'margin', 'max_suppress', 'name', 'samples', 'skipped', 'source_dataset', 'summary', 'top_k']`
- candidate lists:
  - `$.samples` len=25 sample_type=dict keys=['before_primary_gap', 'before_primary_suppress_rank', 'before_target_prob', 'before_target_rank', 'before_worst_suppress_gap', 'board', 'board_size', 'case_id', 'current_player', 'effective_sample_weight', 'game_number', 'hardness_weight', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'primary_suppress_rc', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_actions_source', 'suppress_candidates', 'suppress_move', 'suppress_rc', 'suppress_rcs', 'suppress_xy', 'target_rc']
  - `$.samples[0].board` len=15 sample_type=list keys=[]
  - `$.samples[0].board[0]` len=15 sample_type=int keys=[]
  - `$.samples[0].board[1]` len=15 sample_type=int keys=[]
  - `$.samples[0].board[2]` len=15 sample_type=int keys=[]
  - `$.samples[0].primary_suppress_rc` len=2 sample_type=int keys=[]
  - `$.samples[0].suppress_candidates` len=5 sample_type=dict keys=['action', 'gap', 'prob', 'rank', 'rc']
  - `$.samples[0].suppress_candidates[0].rc` len=2 sample_type=int keys=[]
- common keys:
  - action:25, gap:25, prob:25, rank:25, rc:25, before_primary_gap:5, before_primary_suppress_rank:5, before_target_prob:5, before_target_rank:5, before_worst_suppress_gap:5, board:5, board_size:5, case_id:5, current_player:5, effective_sample_weight:5, game_number:5, hardness_weight:5, label_type:5, move_count:5, notes:5, numeric_gap_available:5, numeric_gap_value:5, old_final:5, primary_suppress_rc:5, sample_weight:5, side_to_move:5, source:5, suggested_bucket:5, suppress_actions_source:5, suppress_candidates:5

### base_margin_dataset

- exists: `True`
- type: `dict`
- top keys: `['description', 'name', 'samples', 'skipped', 'source_dataset']`
- candidate lists:
  - `$.samples` len=25 sample_type=dict keys=['board', 'board_size', 'case_id', 'current_player', 'game_number', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_move', 'suppress_rc', 'suppress_xy', 'target_rc', 'target_xy', 'teacher_eval_before', 'teacher_eval_kind', 'teacher_move', 'win_length']
  - `$.samples[0].board` len=15 sample_type=list keys=[]
  - `$.samples[0].board[0]` len=15 sample_type=int keys=[]
  - `$.samples[0].board[1]` len=15 sample_type=int keys=[]
  - `$.samples[0].board[2]` len=15 sample_type=int keys=[]
  - `$.samples[0].target_xy` len=2 sample_type=int keys=[]
  - `$.samples[0].target_rc` len=2 sample_type=int keys=[]
  - `$.samples[0].suppress_xy` len=2 sample_type=int keys=[]
- common keys:
  - case_id:5, source:5, board_size:5, win_length:5, game_number:5, move_count:5, side_to_move:5, current_player:5, board:5, target_xy:5, target_rc:5, suppress_xy:5, suppress_rc:5, teacher_move:5, suppress_move:5, old_final:5, sample_weight:5, label_type:5, suggested_bucket:5, teacher_eval_before:5, teacher_eval_kind:5, numeric_gap_available:5, numeric_gap_value:5, notes:5, name:1, description:1, source_dataset:1, samples:1, skipped:1

### tail_preflight

- exists: `True`
- type: `dict`
- top keys: `['decision', 'generation_script_candidates', 'inputs', 'multisuppress_schema_artifacts', 'next_actions', 'prereq_status', 'recommended_next_branch', 'recommended_next_step', 'scope', 'upstream_decisions']`
- candidate lists:
  - `$.generation_script_candidates` len=25 sample_type=str keys=[]
  - `$.multisuppress_schema_artifacts` len=25 sample_type=str keys=[]
  - `$.next_actions` len=3 sample_type=dict keys=['action', 'allowed', 'order', 'requires', 'training']
- common keys:
  - action:3, allowed:3, order:3, requires:3, training:3, generation_script_candidates:2, multisuppress_schema_artifacts:2, decision:1, inputs:1, next_actions:1, prereq_status:1, recommended_next_branch:1, recommended_next_step:1, scope:1, upstream_decisions:1, expansion_targets:1, source_audit:1, tail_plan:1, tail_schema_recovery:1, has_b4c96_probe_checkpoint:1, has_board_snapshots:1, has_current_b4c64_checkpoint:1, has_external_rapfi_candidate:1, has_nosave_wrapper:1, tail_gap:1, unique_materializable_tail_from_old_sources:1, unique_tail_recovered_from_old_sources:1, expansion_targets_decision:1, source_audit_decision:1, tail_plan_decision:1

## Script inputs

### b4c96_nosave_wrapper

- exists: `True`
- line_count: `417`
- functions:
  - L24: `def parse_args() -> argparse.Namespace:`
  - L87: `def validate_args(args: argparse.Namespace) -> None:`
  - L104: `def load_model_b4c96(`
  - L130: `def load_protected_dataset(path: Path) -> dict[str, Any]:`
  - L141: `def summarize_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:`
  - L164: `def verdict(group_rows: list[dict[str, Any]]) -> str:`
  - L190: `def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:`
  - L234: `def write_report(`
  - L321: `def main() -> int:`
- checkpoint-related lines:
  - L13: `from gomoku_agent.checkpoint import load_compatible_checkpoint`
  - L28: `"Optimizer runs in memory only; no checkpoint is saved."`
  - L45: `"--init-checkpoint",`
  - L47: `default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),`
  - L50: `"--reference-checkpoint",`
  - L52: `default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),`
  - L98: `if args.init_checkpoint.name == "15x15_current_best.pt":`
  - L99: `raise ValueError("refusing to use current_best as b4c96 init checkpoint")`
  - L100: `if args.reference_checkpoint.name == "15x15_current_best.pt":`
  - L101: `raise ValueError("refusing to use current_best as b4c96 reference checkpoint")`
  - L104: `def load_model_b4c96(`
  - L105: `checkpoint: Path,`
  - L114: `loaded = load_compatible_checkpoint(`
  - L116: `checkpoint,`
  - L124: `f"could not load compatible checkpoint: {checkpoint} "`
  - L249: `"- No checkpoint is saved.",`
  - L267: `f"- init_checkpoint: `{args.init_checkpoint}`",`
  - L268: `f"- reference_checkpoint: `{args.reference_checkpoint}`",`
  - L314: `"No checkpoint was saved.",`
  - L337: `model = load_model_b4c96(`
- dataset-related lines:
  - L16: `load_anchor_samples,`
  - L27: `"b4c96-safe no-save protected rank/top-k objective ablation wrapper. "`
  - L36: `"rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json"`
  - L73: `"protected_nosave_group_metrics.csv"`
  - L81: `"protected_nosave_report.md"`
  - L130: `def load_protected_dataset(path: Path) -> dict[str, Any]:`
  - L132: `required = ["samples", "protected_eval_samples", "tail_eval_samples"]`
  - L135: `raise ValueError(f"missing {key} in protected dataset: {path}")`
  - L136: `if not data["samples"]:`
  - L137: `raise ValueError("empty train samples")`
  - L167: `protected_group = by_group["protected_eval_top10"]`
  - L168: `tail_group = by_group["tail_eval_rank_gt50"]`
  - L175: `protected_ok = (`
  - L176: `float(protected_group["top10_delta"]) >= 0`
  - L177: `and float(protected_group["rank_gt50_delta"]) <= 0`
  - L178: `and float(protected_group["mean_target_prob_delta"]) >= -0.002`
  - L180: `tail_ok = (`
  - L181: `float(tail_group["rank_gt50_delta"]) <= 0`
  - L182: `and float(tail_group["mean_rank_delta"]) <= 5`
  - L185: `if train_ok and protected_ok and tail_ok:`
  - L244: `lines += ["# b4c96-safe protected no-save objective ablation wrapper report", ""]`
  - L328: `data = load_protected_dataset(args.dataset)`
  - L330: `("train_main_rank_11_50", data["samples"]),`
  - L331: `("protected_eval_top10", data["protected_eval_samples"]),`
  - L332: `("tail_eval_rank_gt50", data["tail_eval_samples"]),`
  - L357: `anchors = load_anchor_samples(args.anchor_snapshots)`
  - L359: `train_tensors = make_multisuppress_tensors(data["samples"], device)`
  - L362: `name: diagnose_summary(model, samples, device)`
  - L363: `for name, samples in groups`
  - L375: `name: diagnose_summary(model, samples, device)`

### rank_topk_gate

- exists: `True`
- line_count: `639`
- functions:
  - L21: `def parse_args() -> argparse.Namespace:`
  - L65: `def validate_arch_args(args: argparse.Namespace) -> None:`
  - L82: `def action_to_rc(action: int, board_size: int) -> list[int]:`
  - L86: `def validate_rc(rc: list[int] | tuple[int, int], board_size: int) -> tuple[int, int]:`
  - L95: `def rc_to_action(rc: list[int] | tuple[int, int], board_size: int) -> int:`
  - L100: `def encode_state(board: list[list[int]], current_player: int, board_size: int) -> np.ndarray:`
  - L110: `def legal_mask_from_board(board: list[list[int]], board_size: int) -> np.ndarray:`
  - L117: `def load_model(`
  - L143: `def load_multisuppress_dataset(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:`
  - L151: `def same_model_path(a: Path, b: Path) -> bool:`
  - L158: `def score_policy(`
  - L243: `def compare_sample(`
  - L287: `def finite_check(rows: list[dict[str, Any]]) -> tuple[bool, list[str]]:`
  - L311: `def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:`
  - L343: `def delta(summary: dict[str, Any], key: str) -> float:`
  - L347: `def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:`
  - L387: `def load_anchor_count(path: Path) -> tuple[int, str]:`
  - L395: `def gate_status(summary: dict[str, Any], finite_ok: bool, self_check: bool) -> tuple[str, list[str]]:`
  - L453: `def write_report(`
  - L553: `def main() -> int:`
- checkpoint-related lines:
  - L13: `from gomoku_agent.checkpoint import load_compatible_checkpoint`
  - L38: `default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),`
  - L43: `default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),`
  - L117: `def load_model(`
  - L118: `checkpoint: Path,`
  - L127: `loaded = load_compatible_checkpoint(`
  - L129: `checkpoint,`
  - L137: `f"could not load compatible checkpoint: {checkpoint} "`
  - L471: `out += ["- Evaluation only: no optimizer, no training, no checkpoint save."]`
  - L561: `model_a = load_model(`
  - L569: `model_b = load_model(`
  - L634: `print("evaluation only; no training/checkpoint/export/benchmark/promotion/manifest modification")`
- dataset-related lines:
  - L145: `rows = dataset.get("samples", [])`
  - L147: `raise ValueError(f"empty or missing samples in dataset: {path}")`
  - L170: `suppress_actions = [rc_to_action(rc, board_size) for rc in sample["suppress_rcs"]]`
  - L171: `primary_action = rc_to_action(sample.get("primary_suppress_rc", sample["suppress_rcs"][0]), board_size)`
  - L257: `"suppress_count": len(sample["suppress_rcs"]),`
  - L281: `"protected_top10_regression": int(int(before["target_rank"]) <= 10 and int(after["target_rank"]) > 10),`
  - L329: `"protected_top10_regressions": int(sum(int(r["protected_top10_regression"]) for r in rows)),`
  - L376: `"protected_top10_regression",`
  - L430: `f"protected_top10_regressions == 0: {summary['protected_top10_regressions']}",`
  - L444: `and int(summary["protected_top10_regressions"]) == 0`
  - L511: `out.append(f"| protected top-10 regressions | {summary['protected_top10_regressions']} |")`
  - L558: `dataset, samples = load_multisuppress_dataset(args.dataset)`
  - L580: `rows = [compare_sample(model_a, model_b, sample, device, args.margin, args.board_size) for sample in samples]`

## Inferred schema anchors

- likely snapshot list: `None`
- likely multisuppress sample list: `{'path': '$.samples', 'length': 25, 'sample_type': 'dict', 'sample_keys': ['before_primary_gap', 'before_primary_suppress_rank', 'before_target_prob', 'before_target_rank', 'before_worst_suppress_gap', 'board', 'board_size', 'case_id', 'current_player', 'effective_sample_weight', 'game_number', 'hardness_weight', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'primary_suppress_rc', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_actions_source', 'suppress_candidates', 'suppress_move', 'suppress_rc', 'suppress_rcs', 'suppress_xy', 'target_rc', 'target_xy', 'teacher_eval_before', 'teacher_eval_kind', 'teacher_move', 'validation_notes', 'win_length']}`

## Decision

`TAIL_GENERATOR_INPUTS_INSPECTED_NEED_MANUAL_SCHEMA_PATCH`

## Final note

This inspection does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
