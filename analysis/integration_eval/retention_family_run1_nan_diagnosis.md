# Retention family run1 NaN diagnosis

Scope: run1 NaN diagnosis only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Run1 status

- wrapper overall_status: `gates_failed`
- gates_passed: `False`
- checkpoint_action: `quarantined_failed_candidate_checkpoint`
- gate decision: `FAIL`
- gate failures: `['eval rank regressions 8 > 0', 'eval top1 losses: 3', 'critical 7,9 eval gate regressed', 'no train-side row improved']`

## Dataset summary

- row_count: 2
- split_counts: `{'train_candidate': 2}`
- label_type_counts: `{'nonheldout_retention_anchor': 2}`
- target_cell_counts: `{'empty': 2}`
- board_format_counts: `{'matrix_list': 2}`
- finding_counts: `{'train_rank_regressed': 2}`

## Train rows

| idx | family | target | cell | label_type | before_rank | after_rank | before_prob | after_prob | findings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:ea22cc14729b88fd | 7,10 | empty | nonheldout_retention_anchor | 5 | 143 | 0.08013152 |  | train_rank_regressed |
| 2 | bd:ea22cc14729b88fd | 10,7 | empty | nonheldout_retention_anchor | 2 | 107 | 0.10073036 |  | train_rank_regressed |

## Likely causes

- `run1_training_report_or_wrapper_records_failed_probe`

## Training-script relevant lines

| line | text |
| --- | --- |
| 30 |     label_type: str |
| 35 |     target_action: int |
| 36 |     target_xy: tuple[int, int] |
| 37 |     weight: float |
| 78 |     parser.add_argument("--kl-weight", type=float, default=0.35) |
| 87 |     parser.add_argument("--weight-decay", type=float, default=1e-4) |
| 93 |         help="Comma-separated splits to add as low-weight CE anchors.", |
| 98 |         help="Optional comma-separated label_type filter for mixed CE anchor rows.", |
| 101 |         "--mixed-ce-anchor-weight-scale", |
| 104 |         help="Multiplier applied to row weights for mixed CE anchor rows.", |
| 341 | def choose_policy_target(row: dict[str, Any]) -> str: |
| 342 |     for key in ("policy_target", "teacher_move", "target_move"): |
| 346 |     raise ValueError(f"{row.get('id')}: no policy target") |
| 353 |     split_counts = Counter(str(r.get("split")) for r in rows) |
| 355 |     label_counts = Counter(str(r.get("label_type")) for r in rows) |
| 359 |     print(f"split_counts={dict(split_counts)}") |
| 361 |     print(f"label_type_counts={dict(label_counts)}") |
| 369 |         if len(rows) != 44 or dict(split_counts) != expected: |
| 370 |             raise ValueError(f"strict split check failed: rows={len(rows)} split_counts={dict(split_counts)}") |
| 376 |         target_xy = parse_coord_xy(choose_policy_target(row)) |
| 377 |         if target_xy is None: |
| 378 |             raise ValueError(f"{row_id}: could not parse policy target {row.get('policy_target')!r}") |
| 379 |         target_action = xy_to_action(target_xy, board_size) |
| 380 |         if legal[target_action] <= 0: |
| 381 |             raise ValueError(f"{row_id}: target {xy_to_str(target_xy)} is not legal/empty") |
| 389 |                 label_type=str(row.get("label_type", "")), |
| 394 |                 target_action=target_action, |
| 395 |                 target_xy=target_xy, |
| 396 |                 weight=float(row.get("suggested_weight", 1.0)), |
| 403 | def masked_log_softmax(logits: torch.Tensor, masks: torch.Tensor) -> torch.Tensor: |
| 404 |     return F.log_softmax(logits.masked_fill(masks <= 0, -1e9), dim=-1) |
| 469 |     log_probs = masked_log_softmax(logits, masks.to(device)) |
| 483 |         target_rank = ranked.index(row.target_action) + 1 |
| 484 |         target_prob = float(probs[i, row.target_action].item()) |
| 486 |         ce = -math.log(max(target_prob, 1e-12)) |
| 494 |                 "label_type": row.label_type, |
| 497 |                 "policy_target": xy_to_str(row.target_xy), |
| 498 |                 "target_rank": target_rank, |
| 499 |                 "target_prob": f"{target_prob:.8f}", |
| 500 |                 "target_ce": f"{ce:.8f}", |
| 503 |                 "top_matches_target": str(top_action == row.target_action), |
| 506 |                 "suggested_weight": f"{row.weight:.4f}", |
| 521 |         ranks = [int(x["target_rank"]) for x in items] |
| 522 |         probs = [float(x["target_prob"]) for x in items] |
| 523 |         ces = [float(x["target_ce"]) for x in items] |
| 524 |         top1 = sum(x["top_matches_target"] == "True" for x in items) |
| 529 |             "mean_rank": sum(ranks) / len(ranks) if ranks else float("nan"), |
| 530 |             "mean_target_prob": sum(probs) / len(probs) if probs else float("nan"), |
| 531 |             "mean_target_ce": sum(ces) / len(ces) if ces else float("nan"), |
| 544 |         b_rank = int(b["target_rank"]) |
| 545 |         a_rank = int(a["target_rank"]) |
| 546 |         b_prob = float(b["target_prob"]) |
| 547 |         a_prob = float(a["target_prob"]) |
| 573 |         "label_type", |
| 576 |         "policy_target", |
| 577 |         "target_rank", |
| 578 |         "target_prob", |
| 579 |         "target_ce", |
| 582 |         "top_matches_target", |
| 585 |         "suggested_weight", |
| 608 |     split_counts = Counter(r.split for r in rows) |
| 609 |     label_counts = Counter(r.label_type for r in rows) |
| 619 |     lines.append("- Low-weight mixed CE can also train selected anchor rows.") |
| 635 |     lines.append(f"- split_counts: `{dict(split_counts)}`") |
| 637 |     lines.append(f"- label_type_counts: `{dict(label_counts)}`") |
| 644 |     lines.append(f"- kl_weight: {args.kl_weight}") |
| 645 |     lines.append(f"- anchor_kl_splits: `{args.anchor_kl_splits}`") |
| 647 |     lines.append(f"- mixed_ce_anchor_label_types: `{args.mixed_ce_anchor_label_types}`") |
| 648 |     lines.append(f"- mixed_ce_anchor_weight_scale: {args.mixed_ce_anchor_weight_scale}") |
| 650 |     lines.append(f"- weight_decay: {args.weight_decay}") |
| 656 |     lines.append("\| phase \| split \| rows \| top1 \| top1_rate \| mean_rank \| mean_target_prob \| mean_target_ce \|") |
| 666 |                 f"{item['mean_target_prob']:.6f} \| {item['mean_target_ce']:.6f} \|" |
| 683 |     lines.append("\| id \| label_type \| side \| target \| weight \|") |
| 688 |                 f"\| `{r.row_id}` \| `{r.label_type}` \| {r.side_to_move} \| " |
| 689 |                 f"{xy_to_str(r.target_xy)} \| {r.weight:.2f} \|" |
| 696 |         "policy mass toward its targets while tracking retention/teacher-divergence side effects. " |
| 725 |     anchor_kl_splits = tuple( |
| 727 |         for item in str(args.anchor_kl_splits).split(",") |
| 730 |     if "heldout_retention" in anchor_kl_splits and not args.no_strict_splits: |
| 732 |     anchor_indices = [i for i, r in enumerate(rows) if r.split in anchor_kl_splits] |

## Interpretation

This diagnosis separates row-level adapter data validity from legacy training-script compatibility. If train targets are parseable, empty, and finite-weight, then the NaN is more likely caused by how the legacy mixed-CE training script handles the tiny two-row adapter dataset or the adapter role/label_type semantics.

## Explicit non-actions

- No model training was run by this diagnosis.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
