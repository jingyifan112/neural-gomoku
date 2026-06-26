# Top3-sensitive CE route closeout

## Scope

- Branch: `exp/15x15-top3-sensitive-ce-route-closeout`
- Consolidates the top3-sensitive legacy CE route.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed in this closeout.

## Route chain

1. `exp/15x15-top3-sensitive-nosave-supervision-audit`
2. `exp/15x15-top3-sensitive-manual-decision-audit`
3. `exp/15x15-top3-sensitive-tiny-nosave-probe-preflight`
4. `exp/15x15-top3-sensitive-tiny-nosave-probe-run1`
5. `exp/15x15-top3-sensitive-objective-target-semantics-audit`

## Findings

- Preflight ready: `True`
- Run1 decision: `FAIL_NO_SAVE_OBJECTIVE_MOVED_WRONG_DIRECTION`
- Checkpoint exists: `False`
- Rank improved/same/regressed: `0/1/2`
- Prob improved/regressed: `0/3`
- CE improved/regressed: `0/3`
- Coordinate/target semantics OK: `True`

## Decision

- Final route decision: `CLOSE_LEGACY_TINY_CE_ROUTE_NO_SAVE`
- Do not save a candidate from this route.
- Do not continue this route by increasing epochs.
- Do not run C export, public benchmark, promotion, or current-best overwrite from this route.

## Next recommended route

- Inspect objective/update direction, weighting, and train/eval aggregation.
- Prefer a dedicated rank/top-k no-save wrapper over the legacy CE trainer for the next probe.
- Keep protected top3/top5 rows as gate/anchor rows, not direct positive CE rows.

## Outputs

- `analysis/integration_eval/top3_sensitive_ce_route_closeout/route_closeout_summary.json`
