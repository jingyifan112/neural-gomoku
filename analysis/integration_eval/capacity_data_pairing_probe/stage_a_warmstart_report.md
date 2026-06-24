# Capacity-data pairing Stage A warmstart report

## Route

`exp/15x15-capacity-data-pairing-two-stage-training-probe`

## Stage

Stage A: b4c96 warmstart initialization

## Command

```bash
PYTHONPATH=src python scripts/init_capacity_candidate_b_b4c96.py --source checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt --output checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt
```

## Input checkpoint

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

## Output checkpoint

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

## Output status

`CREATED`

## Scope guard

This stage created only the authorized warmstart checkpoint.

No C export, no public benchmark, no promotion, no current_best overwrite, and no manifest overwrite were performed.
