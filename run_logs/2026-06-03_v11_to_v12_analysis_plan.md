# v11 to v12 analysis plan

Purpose:
- Prepare a focused failure-analysis package before changing training or model logic for v12.
- Keep the next work centered on positions where v11's internal improvement does not translate into Rapfi-facing play.

Current evidence:
- v11 is stronger than v10 in the internal 15x15 checkpoint tests.
  - v11 was promoted from `checkpoints/15x15_v11e_interp_truefailed_a0.05.pt`.
  - v11 beat `checkpoints/15x15_v10_frozen.pt` 20-0 in both evaluated directions.
  - v11 preserved the known v10-level behavior against greedy, random, and mixed_v5.
- Initial v10/v11 Rapfi depth=1 tests at high MCTS sims were invalid as strength comparisons because games ended by time forfeit.
- Lower-sim Rapfi tests finished normally, but both v10 and v11 lost to Rapfi depth=1.
- C weight diagnostics confirmed the exported v10 and v11 weights are different.
- Direct pbrain diagnostics showed v10 and v11 are not behaviorally identical:
  - value estimates differ throughout fixed Rapfi games.
  - direct policy moves sometimes differ, for example move_count=38 and move_count=23 in the two-game debug run.
- Despite those differences, the C pbrain final move often remains identical:
  - safety and MCTS+safety can collapse different direct policy outputs to the same `final` move.
  - normalized v10/v11 MCTS32 Rapfi logs matched after engine-name/path/speed/time normalization.

Working hypotheses:
- The v11 network did improve relative to v10, but the current C final-decision pipeline is masking that improvement in Rapfi games.
- The masking likely happens after raw network inference, in one or more of:
  - direct policy safety override,
  - MCTS visit selection,
  - MCTS safety override,
  - tactical forced-move handling.
- Rapfi depth=1 is exposing tactical failures that are not covered by the current internal opponents.
- v12 should not be designed from aggregate match score alone; it should be designed from concrete failure positions where Rapfi sees threats or wins that neural/MCTS/safety misses.

Analysis package added:
- `scripts/compare_decision_logs.py`
  - Parses pbrain `DEBUG_DECISION` / `debug:_DECISION` lines.
  - Compares two logs by `(game_index, move_count)` by default.
  - Reports value deltas and whether `direct`, `policy_safety`, `mcts_raw`, `mcts_safety`, or `final` changed.
- `scripts/extract_rapfi_failure_positions.py`
  - Parses eval logs into a CSV of neural decision positions from games where a neural engine lost to Rapfi.
  - Extracts game result, result reason, Rapfi `Bestline` context, full `DEBUG_DECISION` line, and final selected moves.

Recommended next steps before v12:
- Run the decision-log comparator on v10/v11 debug logs to isolate positions where raw policy differs but final move is the same.
- Extract Rapfi-loss decision rows from all relevant low-sim Rapfi logs.
- Rank candidate failure positions by:
  - Rapfi `Bestline` containing a forced mate or multi-move tactical line,
  - disagreement between `direct` and `final`,
  - disagreement between v10 and v11 direct policy,
  - late-game collapse where Rapfi's next bestline immediately converts.
- Reconstruct a small hand-audited position set from the top failures.
- Only after that audit, decide whether v12 should target:
  - training data / opponent curriculum,
  - tactical target augmentation,
  - C safety calibration,
  - MCTS move selection,
  - or a move-mode/evaluation change that makes neural improvements visible.

Non-goals for this package:
- No new model training.
- No training-code changes.
- No checkpoint or large binary additions.
- No model-logic changes until the failure-position analysis is reviewed.
