# Capacity-data pairing command plan

## Branch

`exp/15x15-capacity-data-pairing-command-plan`

## Base route

Previous training-probe discovery branch:

`exp/15x15-capacity-data-pairing-training-probe`

Previous discovery commit:

`459a6b5 Add capacity-data pairing training authorization discovery`

## Purpose

This route records the concrete command plan required before a no-promotion capacity-data pairing training probe can be safely executed.

This is a command plan only.

No training is executed in this route.

## Discovery conclusion

Command discovery found that the existing implementation is split across separate components:

### Capacity initialization component

`init_capacity_candidate_b_b4c96.py`

Purpose:

- initialize a b4c96 capacity candidate from the base checkpoint
- output a b4c96 warmstart checkpoint

### Multi-suppress / rank-topk training component

`train_rapfi_teacher_policy_rank_topk_probe.py`

Purpose:

- train on rank/top-k or multi-suppress style teacher-divergence policy data
- read an init checkpoint
- read a reference checkpoint
- optionally write an output checkpoint
- supports `--dry-run` and `--no-save`

### Gate/eval component

`evaluate_policy_rank_topk_gate.py`

Purpose:

- compare model A and model B on the selected dataset
- write gate metrics/report
- does not perform public benchmark or promotion

## Key issue

The previous training authorization named only one candidate checkpoint output:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

However, the safe command chain needs an intermediate warmstart checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Without explicit authorization to write that warmstart checkpoint, the full b4c96 + increased-data training chain should not be executed.

## Required future two-stage checkpoint flow

Stage A:

Base checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Warmstart checkpoint output:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Script class:

`python scripts/init_capacity_candidate_b_b4c96.py`

Stage B:

Init checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Reference checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Train dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

Candidate checkpoint output:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Likely script class:

`python scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

Stage C:

Model A:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Model B:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Gate dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

Gate outputs:

- `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.csv`
- `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.md`

Likely script class:

`python scripts/evaluate_policy_rank_topk_gate.py`

## Retention gate note

The earlier preflight named:

`analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`

as the retention gate dataset.

However, command discovery did not confirm that `evaluate_policy_rank_topk_gate.py` can directly consume that retention-family dataset schema.

Therefore the next route should include a tiny schema compatibility check before using the retention-family gate dataset in an executable command.

## Required future authorization additions

A corrected training authorization must explicitly allow writing both:

- `checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`
- `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

It must also name exact output files for:

- warmstart init report
- training metrics/report
- rank/top-k gate metrics/report
- retention compatibility or retention gate report
- closeout

## Codex status

Codex is not required to record this command plan.

Codex may be useful in the next route if:

- existing trainer arguments do not directly support the b4c96 warmstart path,
- the retention-family eval dataset schema is incompatible with the rank/top-k gate evaluator,
- a small no-promotion wrapper is needed to run Stage A, Stage B, and Stage C with strict path guards.

## Actions not performed

Not performed:

- no checkpoint read
- no checkpoint inspection
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Decision

`CAPACITY_DATA_PAIRING_COMMAND_PLAN_COMPLETE_NEEDS_CORRECTED_TWO_STAGE_TRAINING_AUTHORIZATION`
