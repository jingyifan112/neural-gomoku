# v12b forced-line repair plan

## Current conclusion

v12 stage1 appears to have repaired the first, narrow problem found in the v11 Rapfi failure set: direct policy was missing immediate defensive blocks. The repair data made those original direct immediate-block failures improve, and C pbrain debug runs showed that decisions changed on Rapfi positions. Internal robustness also passed, so the repair did not obviously break the existing greedy/random/mixed/v10-style gates.

However, Rapfi still exposes earlier forcing-line failures. The next target should not be another broad training run or a model/search rewrite. v12b should add a second small repair set focused on early value calibration and pre-double-threat avoidance.

Rapfi win rate should remain a downstream metric. The v12b goal is to improve decisions and value estimates on the failure positions that precede Rapfi's forcing lines.

## What v12 fixed

- Original direct immediate-block failures improved.
- C pbrain decisions changed in Rapfi debug positions, showing that the repair reached the exported/runtime path.
- Internal robustness passed, so the targeted repair did not visibly regress the basic internal opponents.

## What v12 still fails

- Rapfi smoke is still `0-2`, so the tactical repair did not yet translate into external wins.
- Game 1 shows value over-optimism at move_count `12`, `14`, `16`, and `18`, before the later immediate-block sequence. These are earlier positions where Rapfi appears to be building a forcing line while the model value remains too comfortable.
- Game 2 still has the pre-double-threat setup at move_count `31`, where no immediate win is detected yet but Rapfi's bestline points into a forcing sequence.

## Proposed v12b data

### Old immediate-block repair samples

Keep the original v11 Rapfi failure repair samples in the mix. They are now regression tests as much as training data: v12b should preserve the direct-policy block improvements from v12.

### New v12 early forcing-line negative value samples

Add game 1 move_count `12`, `14`, `16`, and `18` from the v12 Rapfi failure analysis as negative value examples. These should teach the value head that the position is already dangerous before an immediate one-ply block appears.

These should be value-focused first. Policy targets should be added only after manual review identifies a safer move, because blindly targeting one move from a lost or unclear forcing-line position can teach the wrong lesson.

### Double-threat value=-1 samples

Keep double-threat examples as hard negative value targets:
- positions where the opponent has multiple immediate winning moves,
- positions where final blocks one threat but another remains.

These positions should remain `value=-1` or close to it for the side to move. A model that thinks these are neutral or positive is likely to keep entering doomed lines.

### Pre-double-threat samples with moderate negative value

Add pre-double-threat positions such as game 2 move_count `31` with a moderate negative value target rather than always `-1`. These are not necessarily immediate forced losses by the detector, but they should be treated as danger states.

A reasonable first target is a moderate negative value such as `-0.5`, pending manual review. The goal is to reduce overconfidence while avoiding a model that becomes pessimistic in every sharp position.

## Proposed evaluation gates

### Original v11 failure set

v12b must preserve v12's gains on the original labeled failure set:
- direct policy blocks single immediate wins,
- value is negative on value-miscalibration and double-threat positions,
- double-threat positions remain recognized as losing or near-losing.

### New v12 failure set

Add a new v12 failure set covering:
- game 1 move_count `12`, `14`, `16`, `18`,
- game 2 move_count `31`,
- any additional early forcing-line positions from the same Rapfi smoke logs.

v12b should improve value calibration on these positions and, where audited policy targets exist, choose safer moves.

### Internal gates

Before any Rapfi smoke rerun, v12b should pass:
- preserve vs greedy,
- preserve vs random,
- preserve vs mixed_v5,
- preserve or improve vs v10,
- preserve or improve vs v11/v12 on the internal robustness checks.

### Rapfi smoke

Run Rapfi smoke only after the original v11 failure set, new v12 failure set, and internal gates pass. Rapfi smoke should be used as an external sanity check, not as the first training objective.

## Risks

- Overfitting to tiny failure sets: seven original positions plus a few v12 positions are not enough to define general strength. Use symmetry and mined near-neighbors, and keep previous self-play/greedy-sparring data mixed in.
- Harming the v10/v11 matchup: targeted tactical repair may shift policy priors in ways that reduce internal head-to-head strength. Preserve-vs-v10/v11 gates are mandatory.
- Value becoming too pessimistic: adding negative value targets for forcing-line positions can make the model avoid playable sharp positions. Use moderate negative targets for pre-threat samples and reserve `-1` for verified forced-loss/double-threat states.
