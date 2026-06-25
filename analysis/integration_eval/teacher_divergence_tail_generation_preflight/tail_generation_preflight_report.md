# Teacher-divergence tail generation preflight

## Scope

- Preflight only.
- No source generation run.
- No dataset build.
- No training.
- No checkpoint read or write beyond file existence checks.
- No C export, no public benchmark, no promotion.

## Upstream decisions

- tail_schema_recovery_decision: `TAIL_SCHEMA_RECOVERY_NO_TAIL_FOUND`
- tail_plan_decision: `TAIL_SOURCE_GENERATION_PLAN_REQUIRED`
- source_audit_decision: `EXPANSION_SOURCE_AUDIT_HAS_PARTIAL_CANDIDATES`
- expansion_targets_decision: `TEACHER_DIVERGENCE_EXPANSION_TARGETS_READY`

## Prerequisite status

| prereq | value |
|---|---:|
| has_board_snapshots | `True` |
| has_current_b4c64_checkpoint | `True` |
| has_b4c96_probe_checkpoint | `True` |
| has_nosave_wrapper | `True` |
| has_external_rapfi_candidate | `True` |
| generation_script_candidates | `68` |
| multisuppress_schema_artifacts | `28` |
| tail_gap | `12` |
| unique_tail_recovered_from_old_sources | `0` |
| unique_materializable_tail_from_old_sources | `0` |

## Decision

`TAIL_GENERATION_PREFLIGHT_READY_WITH_LOCAL_TEACHER_ENGINE`

Local prerequisites appear sufficient to design a guarded tail candidate generator with local teacher labeling.

## Next actions

| order | action | requires | training |
|---:|---|---|---|
| 1 | Build a tail candidate source generator that enumerates additional positions and scores model policy rank. | board snapshots or expanded failure positions plus b4c64/b4c96 scoring path | no |
| 2 | Attach or call Rapfi teacher only if a local teacher executable/script is available. | run_rapfi.sh or equivalent local Rapfi command | no |
| 3 | Materialize tail candidates as heldout tail_guard rows only after >=12 valid rank>50 or near-tail candidates exist. | candidate manifest with board/side/target/suppress_rcs/rank fields | no |

## Final note

This preflight does not authorize source generation into a train dataset, training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
