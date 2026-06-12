# Candidate G teacher-distillation plan

## Goal

Prepare a small teacher-distillation experiment for 15x15 Candidate G.

This is a planning step only:
- no training
- no export
- no promotion
- no smoke match

## Motivation

Recent public benchmark and Rapfi diagnostics show that neural_current_best / Candidate D remain far below rapfi_full on the 15x15 Gomocup public-opening ladder.

Single-position margin repair is no longer the preferred next step. The main observed failure mode is missing policy knowledge: strong Rapfi teacher moves are often outside the model's top policy mass.

## Seed teacher targets

Initial high-priority teacher divergence targets:

| Source | Position | Teacher target | Reason |
|---|---:|---|---|
| Candidate D teacher disagreement census | game1 ply22 | 4,8 | strong teacher continuation divergence |
| Candidate D teacher disagreement census | game2 ply17 | 9,10 | same-position Rapfi teacher correction; previous 9,9 target was continuation reply, not same-position teacher move |

## Retention anchors

Candidate G should include retention anchors around positions that Candidate D or earlier margin repair already fixed:

- game2 move15 repair anchor
- teacher-aligned later blocks
- current_best / Candidate D agreement positions
- tactical benchmark anchors that must not regress

## Proposed dataset structure

Each training row should include:

- board
- side to move
- last move
- teacher move
- model original move
- teacher rank under current model
- teacher probability
- model probability
- optional Rapfi continuation label
- anchor/replay group id
- weight

## Training recommendation

Do not start with value tuning.

First experiment should be policy-first distillation:

- small number of teacher divergence rows
- nearby non-divergent anchors
- conservative learning rate
- frozen or partially frozen backbone if needed
- strict regression gates

## Gates before promotion

Candidate G must pass:

1. teacher target rank/probability improves on seed divergences
2. game2 move15 repair does not regress
3. 15x15 tactical benchmark does not regress
4. Rapfi smoke does not get worse
5. public benchmark score table is not rerun unless the above gates pass

## Current decision

Proceed to dataset construction only after this plan is reviewed.
