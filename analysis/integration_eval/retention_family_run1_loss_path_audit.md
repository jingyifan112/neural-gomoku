# Retention family run1 loss path audit

Scope: read-only loss-path audit. No training, optimizer step, checkpoint save, C export, benchmark, or promotion was run.

## Train log facts

- exists: `True`
- ce_training_rows: `2`
- anchor_kl_rows: `2`
- mixed_ce_rows: `0`
- epoch_line: `loss=nan main_ce=nan mixed_ce_unscaled=0.000000 mixed_ce=0.000000 anchor_kl=nan`
- train_scope: `policy_head`
- trainable_parameters: `101607`
- contains_loss_nan: `True`
- contains_main_ce_nan: `True`
- contains_anchor_kl_nan: `True`
- contains_checkpoint_written: `True`

## Row weight/probability audit

| idx | split | label_type | target | suggested_weight | suggested_weight_status | weight | weight_status | adapter_target_prob | adapter_target_prob_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | train_candidate | nonheldout_retention_anchor | 7,10 | 0.0 | finite |  | missing |  | missing |
| 2 | train_candidate | nonheldout_retention_anchor | 10,7 | 0.0 | finite |  | missing |  | missing |

## Findings

- `mixed_ce_rows_zero`
- `training_log_loss_nan`
- `training_log_main_ce_nan`
- `training_log_anchor_kl_nan`
- `checkpoint_written_despite_nan_loss`

## Likely causes

- `legacy_trainer_allows_empty_main_ce_path`
- `legacy_trainer_does_not_block_nonfinite_loss_before_optimizer_or_checkpoint`

## Relevant script lines

| line | text |
| --- | --- |
| 60 |         default=Path("checkpoints/15x15_teacher_divergence_policy_mixed_ce_anchor_probe.pt"), |
| 65 |         default=Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_eval.csv"), |
| 70 |         default=Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_report.md"), |
| 529 |             "mean_rank": sum(ranks) / len(ranks) if ranks else float("nan"), |
| 530 |             "mean_target_prob": sum(probs) / len(probs) if probs else float("nan"), |
| 531 |             "mean_target_ce": sum(ces) / len(ces) if ces else float("nan"), |
| 621 |     lines.append("- `heldout_retention` is evaluation-only and is not used in the loss.") |
| 622 |     lines.append("- Value head has no explicit loss in this probe.") |
| 645 |     lines.append(f"- anchor_kl_splits: `{args.anchor_kl_splits}`") |
| 646 |     lines.append(f"- mixed_ce_anchor_splits: `{args.mixed_ce_anchor_splits}`") |
| 647 |     lines.append(f"- mixed_ce_anchor_label_types: `{args.mixed_ce_anchor_label_types}`") |
| 648 |     lines.append(f"- mixed_ce_anchor_weight_scale: {args.mixed_ce_anchor_weight_scale}") |
| 649 |     lines.append(f"- mixed_ce_anchor_max_rows: {args.mixed_ce_anchor_max_rows}") |
| 718 |         strict_splits=not args.no_strict_splits, |
| 722 |     if len(train_indices) != 8 and not args.no_strict_splits: |
| 725 |     anchor_kl_splits = tuple( |
| 727 |         for item in str(args.anchor_kl_splits).split(",") |
| 730 |     if "heldout_retention" in anchor_kl_splits and not args.no_strict_splits: |
| 732 |     anchor_indices = [i for i, r in enumerate(rows) if r.split in anchor_kl_splits] |
| 733 |     if not anchor_indices: |
| 734 |         raise ValueError(f"no KL anchor rows selected by anchor_kl_splits={anchor_kl_splits}") |
| 736 |     mixed_ce_splits = tuple( |
| 738 |         for item in str(args.mixed_ce_anchor_splits).split(",") |
| 741 |     mixed_ce_label_types = tuple( |
| 743 |         for item in str(args.mixed_ce_anchor_label_types).split(",") |
| 746 |     if "heldout_retention" in mixed_ce_splits and not args.no_strict_splits: |
| 749 |     mixed_ce_indices = [ |
| 752 |         if r.split in mixed_ce_splits |
| 753 |         and (not mixed_ce_label_types or r.label_type in mixed_ce_label_types) |
| 755 |     if args.mixed_ce_anchor_max_rows and args.mixed_ce_anchor_max_rows > 0: |
| 756 |         mixed_ce_indices = mixed_ce_indices[: args.mixed_ce_anchor_max_rows] |
| 762 |     print(f"anchor_kl_splits={anchor_kl_splits}") |
| 763 |     print(f"anchor_kl_rows={len(anchor_indices)}") |
| 764 |     print(f"mixed_ce_splits={mixed_ce_splits}") |
| 765 |     print(f"mixed_ce_label_types={mixed_ce_label_types}") |
| 766 |     print(f"mixed_ce_rows={len(mixed_ce_indices)}") |
| 767 |     print(f"mixed_ce_weight_scale={args.mixed_ce_anchor_weight_scale}") |
| 781 |     anchor_index_tensor = torch.tensor(anchor_indices, dtype=torch.long, device=device) |
| 782 |     mixed_ce_index_tensor = torch.tensor(mixed_ce_indices, dtype=torch.long, device=device) |
| 822 |         ce_per_row = F.nll_loss(train_log_probs, train_target_actions, reduction="none") |
| 823 |         main_ce_loss = (ce_per_row * train_weights).sum() / train_weights.sum() |
| 825 |         if len(mixed_ce_indices) > 0: |
| 826 |             mixed_ce_log_probs = log_probs[mixed_ce_index_tensor] |
| 827 |             mixed_ce_target_actions = target_actions[mixed_ce_index_tensor] |
| 828 |             mixed_ce_weights = weights[mixed_ce_index_tensor] |
| 829 |             mixed_ce_per_row = F.nll_loss( |
| 830 |                 mixed_ce_log_probs, |
| 831 |                 mixed_ce_target_actions, |
| 834 |             mixed_ce_unscaled_loss = ( |
| 835 |                 mixed_ce_per_row * mixed_ce_weights |
| 836 |             ).sum() / mixed_ce_weights.sum() |
| 837 |             mixed_ce_loss = args.mixed_ce_anchor_weight_scale * mixed_ce_unscaled_loss |
| 838 |             ce_loss = main_ce_loss + mixed_ce_loss |
| 840 |             mixed_ce_unscaled_loss = torch.zeros((), dtype=main_ce_loss.dtype, device=device) |
| 841 |             mixed_ce_loss = torch.zeros((), dtype=main_ce_loss.dtype, device=device) |
| 842 |             ce_loss = main_ce_loss |
| 847 |         anchor_kl = ( |
| 851 |         kl_loss = (anchor_kl * anchor_weights).sum() / anchor_weights.sum() |
| 853 |         loss = ce_loss + args.kl_weight * kl_loss |
| 856 |         loss.backward() |
| 858 |         optimizer.step() |
| 863 |                 f"loss={float(loss.item()):.6f} " |
| 864 |                 f"main_ce={float(main_ce_loss.item()):.6f} " |
| 865 |                 f"mixed_ce_unscaled={float(mixed_ce_unscaled_loss.item()):.6f} " |
| 866 |                 f"mixed_ce={float(mixed_ce_loss.item()):.6f} " |
| 867 |                 f"anchor_kl={float(kl_loss.item()):.6f}", |
| 890 |                     "anchor_kl_splits": list(anchor_kl_splits), |
| 891 |                     "anchor_kl_rows": len(anchor_indices), |
| 892 |                     "mixed_ce_anchor_splits": list(mixed_ce_splits), |
| 893 |                     "mixed_ce_anchor_label_types": list(mixed_ce_label_types), |
| 894 |                     "mixed_ce_anchor_weight_scale": args.mixed_ce_anchor_weight_scale, |
| 895 |                     "mixed_ce_anchor_rows": len(mixed_ce_indices), |

## Interpretation

The run1 trainer should not write a checkpoint when the training loss is non-finite. If the main CE path is empty and yields NaN, the next code fix should add explicit finite-loss guards and prevent optimizer/checkpoint side effects.

## Explicit non-actions

- No training was run.
- No optimizer step was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
