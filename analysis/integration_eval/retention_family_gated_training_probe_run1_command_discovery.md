# Retention family gated training probe run1 command discovery

Scope: command discovery only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Branch

```text
exp/15x15-retention-family-gated-training-probe-run1
```

## Latest commits

```text
842014a Add retention family gated training probe runner
6d16dcf Add retention family training consumer audit
c3febf6 Add retention family training input dry run
96a0d73 Add retention family split dry run closeout
b7599c6 Add retention family split application dry run
021a701 Materialize retention family split proposal
e304760 Add retention family split proposal builder
7c28fca Add retention family split design
```

## Candidate scripts

```text
scripts/accept_teacher_divergence_retention_clean_v2_dataset.py
scripts/apply_retention_family_materialized_split.py
scripts/audit_mixed_ce_heldout_regressions.py
scripts/audit_retention_family_training_consumers.py
scripts/audit_teacher_divergence_expansion_sources.py
scripts/audit_teacher_divergence_source_schema.py
scripts/build_candidate_g_teacher_policy_dataset.py
scripts/build_candidate_g_teacher_seed_manifest.py
scripts/build_retention_family_split_proposal.py
scripts/build_retention_family_training_input_dryrun.py
scripts/build_safety_block_candidate_manifest.py
scripts/build_teacher_divergence_data_inventory.py
scripts/build_teacher_divergence_retention_clean_v2_dataset.py
scripts/build_teacher_divergence_retention_dataset.py
scripts/build_teacher_divergence_retention_expanded_dataset.py
scripts/build_teacher_divergence_retention_safety_v3_dataset.py
scripts/candidate_d_teacher_disagreement_census.py
scripts/design_retention_family_splits.py
scripts/evaluate_teacher_divergence_policy_probe_gates.py
scripts/inspect_teacher_divergence_retention_sources.py
scripts/probe_teacher_divergence_retention_dataset.py
scripts/review_mixed_ce_heldout_blocker_positions.py
scripts/run_retention_family_gated_training_probe.py
scripts/run_teacher_divergence_regression_gated_policy_probe.py
scripts/train_candidate_g_policy_first_dry_run.py
scripts/train_candidate_g_teacher_policy.py
scripts/train_candidate_h_value_ranking.py
scripts/train_rapfi_teacher_policy_margin.py
scripts/train_teacher_divergence_policy_anchor_probe.py
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py
scripts/train_teacher_divergence_policy_probe.py
scripts/validate_teacher_divergence_retention_dataset.py
```

## Argument scan

```text
scripts/init_capacity_candidate_a_b6c64.py:18:        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
scripts/init_capacity_candidate_a_b6c64.py:23:        default=Path("checkpoints/15x15_capacity_a_b6c64_warmstart.pt"),
scripts/init_capacity_candidate_a_b6c64.py:53:        raise ValueError(f"source checkpoint meta mismatch: expected={expected}, found={source_meta}")
scripts/init_capacity_candidate_a_b6c64.py:92:            "source_checkpoint": str(args.source),
scripts/probe_teacher_divergence_retention_dataset.py:27:    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
scripts/probe_teacher_divergence_retention_dataset.py:203:    lines.append(f"- Checkpoint: `{args.checkpoint}`")
scripts/probe_teacher_divergence_retention_dataset.py:246:    for r in [x for x in rows if x["split"] == "heldout_retention"]:
scripts/probe_teacher_divergence_retention_dataset.py:269:    model = load_model(args.checkpoint, args, device)
scripts/probe_teacher_divergence_retention_dataset.py:284:            if row.get("split") == "heldout_retention"
scripts/probe_teacher_divergence_retention_dataset.py:307:                "heldout": str(bool(row.get("heldout"))),
scripts/probe_teacher_divergence_retention_dataset.py:330:            "heldout",
scripts/review_mixed_ce_heldout_blocker_positions.py:23:        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv"),
scripts/review_mixed_ce_heldout_blocker_positions.py:28:        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv"),
scripts/review_mixed_ce_heldout_blocker_positions.py:33:        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv"),
scripts/review_mixed_ce_heldout_blocker_positions.py:40:AUDIT_SUMMARY = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv")
scripts/review_mixed_ce_heldout_blocker_positions.py:42:OUT_DETAIL = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv")
scripts/review_mixed_ce_heldout_blocker_positions.py:43:OUT_REPORT = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md")
scripts/review_mixed_ce_heldout_blocker_positions.py:186:    lines.append("# Mixed-CE heldout blocker position review")
scripts/review_mixed_ce_heldout_blocker_positions.py:190:    lines.append("- read-only review of six repeated heldout blockers")
scripts/review_mixed_ce_heldout_blocker_positions.py:192:    lines.append("- no checkpoint")
scripts/review_mixed_ce_heldout_blocker_positions.py:205:    lines.append("All six are heldout `policy_target` rows. Filtering only by label_type is therefore not enough.")
scripts/review_mixed_ce_heldout_blocker_positions.py:269:    lines.append("The candidate D move15 rows are especially important because one nearby heldout row gained top-1 under all mixed-CE scales, while two sibling targets regressed. This suggests a local target conflict rather than a global inability to retain the position family.")
scripts/review_mixed_ce_heldout_blocker_positions.py:271:    lines.append("The candidate E move17 rows have extremely low target probability. One row improves rank while still losing probability, so row-level probability gates are catching a real mass-allocation issue that rank-only metrics would miss.")
scripts/review_mixed_ce_heldout_blocker_positions.py:280:    lines.append("- add explicit retention anchors for these blocker families outside the heldout split, or")
scripts/review_mixed_ce_heldout_blocker_positions.py:283:    lines.append("Any such variant must still run through the regression-gated runner before saving a checkpoint.")
scripts/train_teacher_divergence_policy_probe.py:17:from gomoku_agent.checkpoint import load_compatible_checkpoint
scripts/train_teacher_divergence_policy_probe.py:53:        "--base-checkpoint",
scripts/train_teacher_divergence_policy_probe.py:55:        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
scripts/train_teacher_divergence_policy_probe.py:58:        "--out-checkpoint",
scripts/train_teacher_divergence_policy_probe.py:60:        default=Path("checkpoints/15x15_teacher_divergence_policy_probe.pt"),
scripts/train_teacher_divergence_policy_probe.py:336:            "heldout_retention": 11,
scripts/train_teacher_divergence_policy_probe.py:376:def load_model(args: argparse.Namespace, checkpoint: Path, device: torch.device) -> PolicyValueNet:
scripts/train_teacher_divergence_policy_probe.py:378:    loaded = load_compatible_checkpoint(
scripts/train_teacher_divergence_policy_probe.py:380:        checkpoint,
scripts/train_teacher_divergence_policy_probe.py:387:        raise RuntimeError(f"could not load compatible checkpoint: {checkpoint}")
scripts/train_teacher_divergence_policy_probe.py:570:    saved_checkpoint: bool,
scripts/train_teacher_divergence_policy_probe.py:597:    lines.append(f"- base_checkpoint: `{args.base_checkpoint}`")
scripts/train_teacher_divergence_policy_probe.py:598:    lines.append(f"- out_checkpoint: `{args.out_checkpoint}`")
scripts/train_teacher_divergence_policy_probe.py:613:    lines.append(f"- saved_checkpoint: {saved_checkpoint}")
scripts/train_teacher_divergence_policy_probe.py:620:        for split in ("train_candidate", "train_teacher_divergence", "heldout_retention", "ALL"):
scripts/train_teacher_divergence_policy_probe.py:634:    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
scripts/train_teacher_divergence_policy_probe.py:687:    print(f"base_checkpoint={args.base_checkpoint}")
scripts/train_teacher_divergence_policy_probe.py:688:    print(f"out_checkpoint={args.out_checkpoint}")
scripts/train_teacher_divergence_policy_probe.py:704:    model = load_model(args, args.base_checkpoint, device)
scripts/train_teacher_divergence_policy_probe.py:705:    reference = load_model(args, args.base_checkpoint, device)
scripts/train_teacher_divergence_policy_probe.py:713:        print("dry-run: no training, no checkpoint, no eval/report writes")
scripts/train_teacher_divergence_policy_probe.py:771:    saved_checkpoint = False
scripts/train_teacher_divergence_policy_probe.py:773:        args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
scripts/train_teacher_divergence_policy_probe.py:784:                    "base_checkpoint": str(args.base_checkpoint),
scripts/train_teacher_divergence_policy_probe.py:796:            args.out_checkpoint,
scripts/train_teacher_divergence_policy_probe.py:798:        saved_checkpoint = True
scripts/train_teacher_divergence_policy_probe.py:801:    write_report(args.report, args, dataset_meta, rows, before, after, saved_checkpoint)
scripts/train_teacher_divergence_policy_probe.py:805:    if saved_checkpoint:
scripts/train_teacher_divergence_policy_probe.py:806:        print(f"wrote checkpoint: {args.out_checkpoint}")
scripts/train_teacher_divergence_policy_probe.py:808:        print("no checkpoint saved due to --no-save")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:39:        description="Evaluate pass/fail gates for teacher-divergence policy probe CSVs."
scripts/evaluate_teacher_divergence_policy_probe_gates.py:44:        default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_summary.csv"),
scripts/evaluate_teacher_divergence_policy_probe_gates.py:49:        default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_report.md"),
scripts/evaluate_teacher_divergence_policy_probe_gates.py:56:    parser.add_argument("--max-heldout-prob-regressed", type=int, default=4)
scripts/evaluate_teacher_divergence_policy_probe_gates.py:57:    parser.add_argument("--max-heldout-rank-regressed", type=int, default=3)
scripts/evaluate_teacher_divergence_policy_probe_gates.py:58:    parser.add_argument("--allow-heldout-top1-loss", action="store_true")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:136:def gate_probe(name: str, stats: dict[str, dict[str, Any]], args: argparse.Namespace) -> tuple[str, list[str]]:
scripts/evaluate_teacher_divergence_policy_probe_gates.py:141:    held = stats["heldout_retention"]
scripts/evaluate_teacher_divergence_policy_probe_gates.py:165:    if held["prob_regressed"] > args.max_heldout_prob_regressed:
scripts/evaluate_teacher_divergence_policy_probe_gates.py:167:            f"heldout_retention prob_regressed {held['prob_regressed']} > {args.max_heldout_prob_regressed}"
scripts/evaluate_teacher_divergence_policy_probe_gates.py:169:    if held["rank_regressed"] > args.max_heldout_rank_regressed:
scripts/evaluate_teacher_divergence_policy_probe_gates.py:171:            f"heldout_retention rank_regressed {held['rank_regressed']} > {args.max_heldout_rank_regressed}"
scripts/evaluate_teacher_divergence_policy_probe_gates.py:173:    if not args.allow_heldout_top1_loss and held["after_top1"] < held["before_top1"]:
scripts/evaluate_teacher_divergence_policy_probe_gates.py:175:            f"heldout_retention top1 decreased {held['before_top1']} -> {held['after_top1']}"
scripts/evaluate_teacher_divergence_policy_probe_gates.py:188:    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
scripts/evaluate_teacher_divergence_policy_probe_gates.py:256:    lines.append("# Teacher-divergence policy probe gate report")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:260:    lines.append("This report applies fixed regression gates to existing teacher-divergence policy probe CSVs.")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:262:    lines.append("It does not train, save checkpoints, export C weights, run benchmarks, promote a model, or make a capacity conclusion.")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:271:    lines.append(f"- max heldout_retention probability regressed: {args.max_heldout_prob_regressed}")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:272:    lines.append(f"- max heldout_retention rank regressed: {args.max_heldout_rank_regressed}")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:273:    lines.append(f"- allow heldout top-1 loss: {args.allow_heldout_top1_loss}")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:291:        for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
scripts/evaluate_teacher_divergence_policy_probe_gates.py:305:    lines.append("All evaluated probes fail the regression gates.")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:313:    lines.append("Do not continue blindly sweeping KL weight and epoch count. The next probe should add explicit regression gates before checkpoint saving and should explore mixed low-weight CE anchors on selected train_teacher_divergence rows while keeping heldout_retention evaluation-only.")
scripts/evaluate_teacher_divergence_policy_probe_gates.py:328:        decision, failures = gate_probe(probe.name, stats, args)
scripts/build_safety_block_candidate_manifest.py:233:                    suggested_split = "heldout_retention_candidate"
scripts/build_safety_block_candidate_manifest.py:415:    md.append("- `heldout_retention_candidate`: candidate row where logged final already matches the block; likely better as retention/probe unless policy target is separately justified.")
scripts/train_greedy_sparring_v9.py:13:from gomoku_agent.checkpoint import load_compatible_checkpoint
scripts/train_greedy_sparring_v9.py:20:    p.add_argument("--init-checkpoint", type=Path, required=True)
scripts/train_greedy_sparring_v9.py:21:    p.add_argument("--out-checkpoint", type=Path, required=True)
scripts/train_greedy_sparring_v9.py:184:    load_compatible_checkpoint(
scripts/train_greedy_sparring_v9.py:186:        args.init_checkpoint,
scripts/train_greedy_sparring_v9.py:238:    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
scripts/train_greedy_sparring_v9.py:247:        args.out_checkpoint,
scripts/train_greedy_sparring_v9.py:249:    print(f"saved {args.out_checkpoint}", flush=True)
scripts/train_greedy_sparring_v10.py:12:from gomoku_agent.checkpoint import load_compatible_checkpoint
scripts/train_greedy_sparring_v10.py:19:    p.add_argument("--init-checkpoint", type=Path, required=True)
scripts/train_greedy_sparring_v10.py:20:    p.add_argument("--out-checkpoint", type=Path, required=True)
scripts/train_greedy_sparring_v10.py:505:    load_compatible_checkpoint(
scripts/train_greedy_sparring_v10.py:507:        args.init_checkpoint,
scripts/train_greedy_sparring_v10.py:569:    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
scripts/train_greedy_sparring_v10.py:578:        args.out_checkpoint,
scripts/train_greedy_sparring_v10.py:580:    print(f"saved {args.out_checkpoint}", flush=True)
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:17:from gomoku_agent.checkpoint import load_compatible_checkpoint
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:53:        "--base-checkpoint",
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:55:        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:58:        "--out-checkpoint",
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:60:        default=Path("checkpoints/15x15_teacher_divergence_policy_mixed_ce_anchor_probe.pt"),
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:84:            "heldout_retention should normally stay evaluation-only."
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:367:            "heldout_retention": 11,
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:407:def load_model(args: argparse.Namespace, checkpoint: Path, device: torch.device) -> PolicyValueNet:
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:409:    loaded = load_compatible_checkpoint(
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:411:        checkpoint,
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:418:        raise RuntimeError(f"could not load compatible checkpoint: {checkpoint}")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:601:    saved_checkpoint: bool,
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:621:    lines.append("- `heldout_retention` is evaluation-only and is not used in the loss.")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:631:    lines.append(f"- base_checkpoint: `{args.base_checkpoint}`")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:632:    lines.append(f"- out_checkpoint: `{args.out_checkpoint}`")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:652:    lines.append(f"- saved_checkpoint: {saved_checkpoint}")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:659:        for split in ("train_candidate", "train_teacher_divergence", "heldout_retention", "ALL"):
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:673:    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:730:    if "heldout_retention" in anchor_kl_splits and not args.no_strict_splits:
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:731:        raise ValueError("heldout_retention must remain evaluation-only in strict mode")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:746:    if "heldout_retention" in mixed_ce_splits and not args.no_strict_splits:
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:747:        raise ValueError("heldout_retention must remain evaluation-only in strict mode")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:759:    print(f"base_checkpoint={args.base_checkpoint}")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:760:    print(f"out_checkpoint={args.out_checkpoint}")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:784:    model = load_model(args, args.base_checkpoint, device)
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:785:    reference = load_model(args, args.base_checkpoint, device)
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:793:        print("dry-run: no training, no checkpoint, no eval/report writes")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:874:    saved_checkpoint = False
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:876:        args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:887:                    "base_checkpoint": str(args.base_checkpoint),
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:905:            args.out_checkpoint,
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:907:        saved_checkpoint = True
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:910:    write_report(args.report, args, dataset_meta, rows, before, after, saved_checkpoint)
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:914:    if saved_checkpoint:
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:915:        print(f"wrote checkpoint: {args.out_checkpoint}")
scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py:917:        print("no checkpoint saved due to --no-save")
scripts/run_retention_family_gated_training_probe.py:3:Run or preflight a retention-family gated training probe.
scripts/run_retention_family_gated_training_probe.py:8:- Enforce the critical family gate_scope rule.
scripts/run_retention_family_gated_training_probe.py:9:- Save/promote checkpoint only when all gates PASS.
scripts/run_retention_family_gated_training_probe.py:10:- If train/gate fails, do not create/promote final checkpoint.
scripts/run_retention_family_gated_training_probe.py:36:DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.json")
scripts/run_retention_family_gated_training_probe.py:37:DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.md")
scripts/run_retention_family_gated_training_probe.py:38:DEFAULT_LOG_DIR = Path("eval_logs/integration_eval/retention_family_gated_training_probe")
scripts/run_retention_family_gated_training_probe.py:83:        if clean(r.get("train_use_policy")) != "include_as_nonheldout_retention_anchor_candidate":
scripts/run_retention_family_gated_training_probe.py:96:            "normal_heldout_gate_candidate",
scripts/run_retention_family_gated_training_probe.py:97:            "restricted_family_level_gate_candidate",
scripts/run_retention_family_gated_training_probe.py:98:            "review_before_eval_gate_use",
scripts/run_retention_family_gated_training_probe.py:99:            "heldout_gate_candidate_review_scope",
scripts/run_retention_family_gated_training_probe.py:106:            if clean(r.get("gate_scope")) != "external_or_family_level_only_not_sibling_only":
scripts/run_retention_family_gated_training_probe.py:107:                errors.append("critical target 7,9 has wrong gate_scope")
scripts/run_retention_family_gated_training_probe.py:108:            if clean(r.get("allowed_as_only_sibling_family_gate")) == "yes":
scripts/run_retention_family_gated_training_probe.py:109:                errors.append("critical target 7,9 incorrectly allowed as only sibling-family gate")
scripts/run_retention_family_gated_training_probe.py:154:def safe_checkpoint_action(
scripts/run_retention_family_gated_training_probe.py:155:    candidate_checkpoint: Path,
scripts/run_retention_family_gated_training_probe.py:156:    final_checkpoint: Optional[Path],
scripts/run_retention_family_gated_training_probe.py:157:    gates_passed: bool,
scripts/run_retention_family_gated_training_probe.py:163:        "candidate_checkpoint": str(candidate_checkpoint),
scripts/run_retention_family_gated_training_probe.py:164:        "candidate_exists": candidate_checkpoint.exists(),
scripts/run_retention_family_gated_training_probe.py:165:        "final_checkpoint": str(final_checkpoint) if final_checkpoint else "",
scripts/run_retention_family_gated_training_probe.py:166:        "final_exists_before": final_checkpoint.exists() if final_checkpoint else False,
scripts/run_retention_family_gated_training_probe.py:173:    if gates_passed:
scripts/run_retention_family_gated_training_probe.py:175:            action["action"] = "gates_passed_no_promotion_requested"
scripts/run_retention_family_gated_training_probe.py:178:        if final_checkpoint is None:
scripts/run_retention_family_gated_training_probe.py:179:            action["action"] = "gates_passed_no_final_checkpoint_path"
scripts/run_retention_family_gated_training_probe.py:180:            action["error"] = "final checkpoint path is required for promotion"
scripts/run_retention_family_gated_training_probe.py:183:        if not candidate_checkpoint.exists():
scripts/run_retention_family_gated_training_probe.py:184:            action["action"] = "gates_passed_candidate_missing"
scripts/run_retention_family_gated_training_probe.py:185:            action["error"] = "candidate checkpoint does not exist, cannot promote"
scripts/run_retention_family_gated_training_probe.py:188:        final_checkpoint.parent.mkdir(parents=True, exist_ok=True)
scripts/run_retention_family_gated_training_probe.py:189:        if final_checkpoint.exists():
scripts/run_retention_family_gated_training_probe.py:190:            action["action"] = "blocked_final_checkpoint_exists"
scripts/run_retention_family_gated_training_probe.py:191:            action["error"] = "final checkpoint already exists; refusing to overwrite"
scripts/run_retention_family_gated_training_probe.py:194:        shutil.copy2(candidate_checkpoint, final_checkpoint)
scripts/run_retention_family_gated_training_probe.py:195:        action["action"] = "promoted_candidate_to_final_checkpoint"
scripts/run_retention_family_gated_training_probe.py:196:        action["final_exists_after"] = final_checkpoint.exists()
scripts/run_retention_family_gated_training_probe.py:199:    if not gates_passed and quarantine_on_fail and candidate_checkpoint.exists():
scripts/run_retention_family_gated_training_probe.py:201:        dest = quarantine_dir / candidate_checkpoint.name
scripts/run_retention_family_gated_training_probe.py:204:            dest = quarantine_dir / f"{candidate_checkpoint.stem}.{suffix}{candidate_checkpoint.suffix}"
scripts/run_retention_family_gated_training_probe.py:205:        shutil.move(str(candidate_checkpoint), str(dest))
scripts/run_retention_family_gated_training_probe.py:206:        action["action"] = "quarantined_failed_candidate_checkpoint"
scripts/run_retention_family_gated_training_probe.py:210:    if not gates_passed:
scripts/run_retention_family_gated_training_probe.py:211:        action["action"] = "gates_failed_no_promotion"
scripts/run_retention_family_gated_training_probe.py:239:    md.append("# Retention family gated training probe runner")
scripts/run_retention_family_gated_training_probe.py:241:    md.append("Scope: gated training probe wrapper/report. No C export, benchmark, or promotion was run by this wrapper.")
scripts/run_retention_family_gated_training_probe.py:247:    md.append(f"- gates_passed: `{payload['gates_passed']}`")
scripts/run_retention_family_gated_training_probe.py:250:    md.append(f"- candidate_checkpoint: `{payload['inputs']['candidate_checkpoint']}`")
scripts/run_retention_family_gated_training_probe.py:251:    md.append(f"- final_checkpoint: `{payload['inputs'].get('final_checkpoint', '')}`")
scripts/run_retention_family_gated_training_probe.py:284:        ["target", "source", "eval_policy", "gate_scope", "only_sibling_gate_ok", "risk_flags"],
scripts/run_retention_family_gated_training_probe.py:290:                r.get("gate_scope", ""),
scripts/run_retention_family_gated_training_probe.py:291:                r.get("allowed_as_only_sibling_family_gate", ""),
scripts/run_retention_family_gated_training_probe.py:316:        md.append("No train/gate commands were run.")
scripts/run_retention_family_gated_training_probe.py:321:    ck = payload.get("checkpoint_action", {})
scripts/run_retention_family_gated_training_probe.py:327:    md.append("- This wrapper requires manifest validation before running training or gates.")
scripts/run_retention_family_gated_training_probe.py:328:    md.append("- Candidate checkpoints should be written only to the candidate checkpoint path.")
scripts/run_retention_family_gated_training_probe.py:329:    md.append("- Final checkpoint promotion happens only when all gates pass and `--promote-on-pass` is set.")
scripts/run_retention_family_gated_training_probe.py:330:    md.append("- On gate failure, the wrapper does not promote the candidate checkpoint.")
scripts/run_retention_family_gated_training_probe.py:340:    ap.add_argument("--mode", choices=["preflight", "train-and-gate", "gates-only"], default="preflight")
scripts/run_retention_family_gated_training_probe.py:341:    ap.add_argument("--train-manifest", type=Path, default=DEFAULT_TRAIN_MANIFEST)
scripts/run_retention_family_gated_training_probe.py:342:    ap.add_argument("--eval-manifest", type=Path, default=DEFAULT_EVAL_MANIFEST)
scripts/run_retention_family_gated_training_probe.py:343:    ap.add_argument("--candidate-checkpoint", type=Path, required=True)
scripts/run_retention_family_gated_training_probe.py:344:    ap.add_argument("--final-checkpoint", type=Path, default=None)
scripts/run_retention_family_gated_training_probe.py:346:    ap.add_argument("--gate-cmd", action="append", default=[])
scripts/run_retention_family_gated_training_probe.py:349:    ap.add_argument("--quarantine-dir", type=Path, default=Path("checkpoints/failed_retention_family_probe"))
scripts/run_retention_family_gated_training_probe.py:372:    if args.mode == "train-and-gate" and not clean(args.train_cmd):
scripts/run_retention_family_gated_training_probe.py:373:        setup_errors.append("train-and-gate mode requires --train-cmd")
scripts/run_retention_family_gated_training_probe.py:374:    if args.mode in {"train-and-gate", "gates-only"} and not args.gate_cmd:
scripts/run_retention_family_gated_training_probe.py:375:        setup_errors.append(f"{args.mode} mode requires at least one --gate-cmd")
scripts/run_retention_family_gated_training_probe.py:376:    if args.promote_on_pass and args.final_checkpoint is None:
scripts/run_retention_family_gated_training_probe.py:377:        setup_errors.append("--promote-on-pass requires --final-checkpoint")
scripts/run_retention_family_gated_training_probe.py:378:    if args.final_checkpoint and args.final_checkpoint.exists() and args.promote_on_pass:
scripts/run_retention_family_gated_training_probe.py:379:        setup_errors.append(f"final checkpoint already exists: {args.final_checkpoint}")
scripts/run_retention_family_gated_training_probe.py:382:    gates_passed = False
scripts/run_retention_family_gated_training_probe.py:388:        "RETENTION_FAMILY_CANDIDATE_CHECKPOINT": str(args.candidate_checkpoint),
scripts/run_retention_family_gated_training_probe.py:389:        "RETENTION_FAMILY_FINAL_CHECKPOINT": str(args.final_checkpoint or ""),
scripts/run_retention_family_gated_training_probe.py:397:        if args.mode == "train-and-gate":
scripts/run_retention_family_gated_training_probe.py:405:        if overall_status in {"train_passed"} or args.mode == "gates-only":
scripts/run_retention_family_gated_training_probe.py:406:            gate_passes = []
scripts/run_retention_family_gated_training_probe.py:407:            for i, cmd in enumerate(args.gate_cmd, 1):
scripts/run_retention_family_gated_training_probe.py:408:                res = run_shell_command(f"gate_{i}", cmd, args.log_dir, env_extra)
scripts/run_retention_family_gated_training_probe.py:410:                gate_passes.append(res["passed"])
scripts/run_retention_family_gated_training_probe.py:411:            gates_passed = bool(gate_passes) and all(gate_passes)
scripts/run_retention_family_gated_training_probe.py:412:            overall_status = "gates_passed" if gates_passed else "gates_failed"
scripts/run_retention_family_gated_training_probe.py:415:        checkpoint_action = {
scripts/run_retention_family_gated_training_probe.py:416:            "candidate_checkpoint": str(args.candidate_checkpoint),
scripts/run_retention_family_gated_training_probe.py:417:            "candidate_exists": args.candidate_checkpoint.exists(),
scripts/run_retention_family_gated_training_probe.py:418:            "final_checkpoint": str(args.final_checkpoint or ""),
scripts/run_retention_family_gated_training_probe.py:419:            "action": "preflight_only_no_checkpoint_action",
scripts/run_retention_family_gated_training_probe.py:422:        checkpoint_action = safe_checkpoint_action(
scripts/run_retention_family_gated_training_probe.py:423:            candidate_checkpoint=args.candidate_checkpoint,
scripts/run_retention_family_gated_training_probe.py:424:            final_checkpoint=args.final_checkpoint,
scripts/run_retention_family_gated_training_probe.py:425:            gates_passed=gates_passed,
scripts/run_retention_family_gated_training_probe.py:430:        if checkpoint_action.get("error"):
scripts/run_retention_family_gated_training_probe.py:431:            overall_status = f"{overall_status}_checkpoint_action_error"
scripts/run_retention_family_gated_training_probe.py:439:            "candidate_checkpoint": str(args.candidate_checkpoint),
scripts/run_retention_family_gated_training_probe.py:440:            "final_checkpoint": str(args.final_checkpoint or ""),
scripts/run_retention_family_gated_training_probe.py:442:            "gate_cmd": args.gate_cmd,
scripts/run_retention_family_gated_training_probe.py:457:        "gates_passed": gates_passed,
scripts/run_retention_family_gated_training_probe.py:459:        "checkpoint_action": checkpoint_action,
scripts/run_retention_family_gated_training_probe.py:474:    print("gates_passed:", gates_passed)
scripts/run_retention_family_gated_training_probe.py:475:    print("checkpoint_action:", checkpoint_action.get("action"))
scripts/run_retention_family_gated_training_probe.py:477:    if overall_status.startswith("blocked") or checkpoint_action.get("error"):
scripts/run_retention_family_gated_training_probe.py:479:    if overall_status in {"train_failed", "gates_failed"}:
scripts/apply_retention_family_materialized_split.py:12:- no checkpoint save
scripts/apply_retention_family_materialized_split.py:169:def is_heldout_retention(row: Dict[str, Any]) -> bool:
scripts/apply_retention_family_materialized_split.py:173:    return "heldout_retention" in hay or "heldout retention" in hay
scripts/apply_retention_family_materialized_split.py:252:    if role == "nonheldout_retention_anchor":
scripts/apply_retention_family_materialized_split.py:254:    if role == "heldout_retention_gate":
scripts/apply_retention_family_materialized_split.py:255:        return "heldout_retention_gate"
scripts/apply_retention_family_materialized_split.py:256:    if role == "heldout_retention_gate_family_conflict_review":
scripts/apply_retention_family_materialized_split.py:257:        return "heldout_retention_gate_review"
scripts/apply_retention_family_materialized_split.py:258:    if role == "heldout_retention_gate_review":
scripts/apply_retention_family_materialized_split.py:259:        return "heldout_retention_gate_review"
scripts/apply_retention_family_materialized_split.py:264:    if role == "nonheldout_retention_anchor":
scripts/apply_retention_family_materialized_split.py:265:        return "nonheldout_retention_anchor"
scripts/apply_retention_family_materialized_split.py:266:    if role == "heldout_retention_gate":
scripts/apply_retention_family_materialized_split.py:267:        return "heldout_retention_gate"
scripts/apply_retention_family_materialized_split.py:268:    if role.startswith("heldout_retention_gate"):
scripts/apply_retention_family_materialized_split.py:287:        gate_scope = ""
scripts/apply_retention_family_materialized_split.py:291:        only_sibling_gate_ok = ""
scripts/apply_retention_family_materialized_split.py:296:        gate_scope = clean(manifest.get("gate_scope"))
scripts/apply_retention_family_materialized_split.py:300:        only_sibling_gate_ok = clean(manifest.get("allowed_as_only_sibling_family_gate"))
scripts/apply_retention_family_materialized_split.py:313:        "is_heldout_retention": yn(is_heldout_retention(row)),
```
