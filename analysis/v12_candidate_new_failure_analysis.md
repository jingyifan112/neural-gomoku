# v12 candidate new Rapfi failure analysis

## Context

v12_candidate was created by interpolating v11 current_best with the v12_stage2 Rapfi repair specialist checkpoint using alpha=0.30.

It passed internal robustness checks and improved the original Rapfi failure-set direct block accuracy from 0/5 to 4/5.

A Rapfi depth=1 smoke test still resulted in 0-2, so new failure positions were extracted from the v12 debug log.

## Main finding

v12_candidate changed actual C pbrain gameplay and repaired some old immediate-block failures, but it still loses to Rapfi through new forcing lines.

## Game 1: severe value over-optimism

Selected positions:
- move_count 12: value = 0.680296
- move_count 14: value = 0.478734
- move_count 16: value = 0.757017
- move_count 18: value = 0.695656

Threat analysis:
- move_count 16:
  - opponent immediate winning move = 5,2
  - direct = 3,7, does not block
  - final = 5,2, blocks via MCTS/safety
  - preliminary type: value_miscalibration

- move_count 18:
  - opponent immediate winning moves = 7,1 and 2,6
  - direct/final = 7,1, blocks only one
  - preliminary type: forced_loss_or_double_threat

Interpretation:
- v12_candidate still fails to value Rapfi forcing lines correctly.
- The model can sometimes block immediate threats, but it enters positions where blocking one threat is no longer enough.
- The biggest issue in Game 1 is not final-move blocking; it is earlier forced-line / double-threat value miscalibration.

## Game 2: immediate blocking improved, pre-double-threat issue remains

Selected positions:
- move_count 27: direct/final = 5,8, blocks opponent immediate win
- move_count 29: direct/final = 4,5, blocks opponent immediate win
- move_count 33: direct/final = 9,6, blocks one of the immediate winning moves

Important remaining position:
- move_count 31:
  - no opponent immediate winning move detected
  - next Rapfi bestline = J8 J12
  - direct = 10,7
  - final = 10,9
  - preliminary type: pre_double_threat_setup_review

Interpretation:
- v12 repaired the old direct-policy block issue in this game.
- The remaining problem is earlier prevention of Rapfi's forcing line, not immediate blocking.

## Decision

Do not promote v12_candidate yet.

v12_candidate is a meaningful improvement over v11 in failure-set behavior, but it still has unresolved Rapfi-specific failure modes.

## Next direction

The next training direction should not focus only on immediate-block examples.

It should add:
1. value targets for early forcing-line positions
2. double-threat / forced-loss value samples
3. pre-double-threat prevention examples
4. training positions where there is no immediate win yet, but Rapfi's next bestline creates a forcing sequence

The next candidate should be evaluated on:
- original v11 failure set
- new v12 failure set
- internal gates
- only then Rapfi smoke
