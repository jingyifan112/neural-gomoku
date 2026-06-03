# pbrain debug decision summary

Purpose:
- Diagnose why v10 and v11 have different C weights but produce identical Rapfi games.

Setup:
- v10 wrapper: run_neural_v10_15x15_mcts32_debug.sh
- v11 wrapper: run_neural_v11_15x15_mcts32_debug.sh
- opponent: Rapfi depth=1
- games: 2
- neural MCTS sims: 32
- debug variable: NEURAL_GOMOKU_DEBUG_DECISION=1

Findings:
- Debug logging works, but c-gomoku-cli displays DEBUG_DECISION as debug:_DECISION.
- v10 and v11 produce different value estimates and sometimes different direct policy moves.
- However, the final selected move is still the same in the tested Rapfi games.
- Example:
  - move_count=38:
    - v10 direct=(8,6)
    - v11 direct=(7,11)
    - both policy_safety=(3,8), mcts_safety=(3,8), final=(3,8)
  - move_count=23:
    - v10 direct=(9,9)
    - v11 direct=(6,5)
    - both policy_safety=(3,7), mcts_safety=(3,7), final=(3,7)

Conclusion:
- The v11 network is not identical to v10.
- The C final decision pipeline, especially safety / MCTS+safety, collapses v10 and v11 to the same final moves in Rapfi games.
- The Rapfi benchmark currently measures the behavior of the final safety pipeline more than the raw neural policy improvement.

Next step:
- Add a configurable pbrain move mode:
  - mcts_safe: current default
  - mcts_raw: MCTS without safety
  - policy_safe: direct policy plus safety
  - direct: raw policy only
- Use this to test whether v11 differs from v10 when safety is disabled or reduced.
