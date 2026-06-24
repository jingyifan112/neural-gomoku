# Capacity-data pairing command plan closeout

## Branch

`exp/15x15-capacity-data-pairing-command-plan`

## Purpose

This closeout records that the capacity-data pairing command plan route completed as a documentation-only route.

The route identified the safe command structure needed before executing a no-promotion data-supported capacity training probe.

## Key conclusion

The training chain cannot be safely executed under the previous authorization because the previous authorization named only one candidate checkpoint output:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Command planning showed that the safe b4c96 capacity-data pairing chain requires an additional intermediate warmstart checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Therefore a corrected two-stage training authorization is required before any executable training command may run.

## Required corrected stage structure

### Stage A: capacity warmstart

Script class:

`python scripts/init_capacity_candidate_b_b4c96.py`

Input checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Output checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

### Stage B: increased-data training probe

Likely script class:

`python scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

Train dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

Init checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Reference checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Output checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

### Stage C: gate/eval

Likely script class:

`python scripts/evaluate_policy_rank_topk_gate.py`

Model A:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Model B:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Gate dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

## Retention gate caveat

The retention-family eval dataset remains selected as a gate-side artifact, but command planning did not prove that the rank/top-k gate evaluator can directly consume the retention-family schema.

A later executable route must either:

- run a separate schema compatibility check, or
- produce a separate retention gate/report using a compatible evaluator.

## Actions performed

Performed:

- recorded command plan
- identified the two-stage checkpoint requirement
- identified likely Stage A, Stage B, and Stage C script classes
- recorded that corrected authorization is required

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

## Final status

`CAPACITY_DATA_PAIRING_COMMAND_PLAN_CLOSEOUT_COMPLETE_CORRECTED_TWO_STAGE_AUTHORIZATION_REQUIRED_NO_TRAINING`

## Final decision

`NONE__COMMAND_PLAN_ROUTE_CLOSED_CORRECTED_TWO_STAGE_TRAINING_AUTHORIZATION_REQUIRED`
