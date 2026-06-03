# pbrain move-mode ablation summary

Purpose:
- Test whether v10/v11 differences are hidden by the C final decision pipeline.
- Compare mcts_raw and direct modes against Rapfi depth=1.

Setup:
- board size: 15
- opponent: Rapfi fast
- Rapfi setting: tc=1/1, depth=1
- games: 2 per mode
- neural MCTS sims: 32
- debug variable: NEURAL_GOMOKU_DEBUG_DECISION=1
- move mode variable: NEURAL_GOMOKU_MOVE_MODE

Results:
- v11_mcts_raw vs Rapfi: 0-2
- v10_mcts_raw vs Rapfi: 0-2
- v11_direct vs Rapfi: 0-2
- v10_direct vs Rapfi: 0-2

Findings:
- In mcts_raw mode, v10 and v11 still produce very similar final moves. Values differ, but final MCTS moves are mostly identical.
- In direct mode, v10 and v11 begin to produce clearly different final moves.
- Example direct-mode divergence:
  - move_count=13:
    - v10 final=(8,9)
    - v11 final=(8,8)
  - move_count=15:
    - v10 final=(8,6)
    - v11 final=(7,10)
  - v11 direct continued to later move_count=17 and move_count=19 in the shown diff.

Conclusion:
- v11's raw policy differs from v10.
- C MCTS, even without safety, tends to collapse v10 and v11 into similar final decisions.
- The next v12 direction should not be plain self-play.
- The next useful step is to extract Rapfi failure positions and train/evaluate against those positions directly.
