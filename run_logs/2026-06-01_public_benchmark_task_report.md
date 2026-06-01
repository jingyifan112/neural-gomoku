# Public benchmark positioning and Gomocup/Piskvork integration report

## Goal

The goal was to find a public benchmark route for the Gomoku model and use it to position the current model's strength.

## Public benchmark route

The most relevant public benchmark route is Gomocup / Piskvork.

Gomocup is a public Gomoku/Renju AI tournament platform. It provides:
- public AI tournament results
- downloadable Gomoku AI engines
- the Piskvork manager for AI-vs-AI games
- a Gomocup protocol based on stdin/stdout communication

The protocol supports commands such as START, BEGIN, TURN, BOARD, INFO, ABOUT, and END.

## Current limitation

The current best model is trained for 9x9 Gomoku:

- Python checkpoint: checkpoints/9x9_tactical_v2.pt
- C weights: c_inference/weights/9x9_tactical_v2_weights.bin

Most public Gomocup/Piskvork engines are intended for larger official settings such as 15x15 or 20x20. Therefore, the current 9x9 model cannot yet be fairly compared against official Gomocup engines.

## Internal 9x9 benchmark results

I added a 9x9 automated evaluation harness and evaluated the current v2 tactical checkpoint.

Evaluation settings:
- board size: 9
- win length: 5
- MCTS simulations: 64
- games per matchup: 20

| Evaluation | Result | Average moves | Interpretation |
|---|---:|---:|---|
| v2 vs random | 20W / 0D / 0L | 22.5 | v2 reliably beats random |
| old checkpoint vs random | 20W / 0D / 0L | 37.3 | old checkpoint also beats random, but slower |
| v2 vs greedy_win_block | 5W / 3D / 12L | 37.1 | v2 is not yet stronger than a simple tactical baseline |
| old checkpoint vs greedy_win_block | 5W / 0D / 15L | 31.1 | v2 is slightly more stable than old because it converts some losses into draws |
| v2 vs old checkpoint | 0W / 20D / 0L | 81.0 | deterministic neural-vs-neural setup lacks discrimination |

## Strength positioning

The current v2 tactical checkpoint is clearly above random play.

Compared with the old checkpoint, v2 shows a small stability improvement, especially against greedy_win_block, where v2 gets 3 draws while the old checkpoint gets 0 draws.

However, v2 is still not consistently stronger than a simple tactical greedy baseline. This means the model is not yet at the level of a robust tactical engine.

Current positioning:
- stronger than random
- slightly improved over the old checkpoint
- still weaker / unstable against a simple greedy win/block baseline
- not yet ready for official Gomocup engine comparison

## Gomocup protocol wrapper

I added a C-side Gomocup/Piskvork protocol wrapper:

- executable: c_inference/pbrain-neural-gomoku
- default weights: c_inference/weights/9x9_tactical_v2_weights.bin
- default MCTS sims: 256
- supported board size for now: 9x9 only

Smoke tests passed:

START 9 + BEGIN:
- returns OK
- returns a legal move

START 9 + TURN 4,4:
- returns OK
- returns a legal response move

START 15:
- returns ERROR unsupported board size

This confirms that the project has started connecting to the public Gomocup/Piskvork benchmark interface, even though the current model is only 9x9.

## Next steps for full public benchmark

To run a real public Gomocup/Piskvork benchmark, the next steps are:

1. Train or adapt a 15x15 or 20x20 model.
2. Export the new checkpoint to C weights.
3. Extend pbrain-neural-gomoku to support START 15 or START 20.
4. Run Piskvork manager against downloadable public Gomocup engines.
5. Report W/D/L, average moves, time per move, and matchup settings.

## Conclusion

The public benchmark route has been identified and the first integration step is complete.

The current 9x9 v2 tactical model is above random, slightly more stable than the old checkpoint, but still below a simple tactical greedy baseline. The project now has a clear path toward official Gomocup/Piskvork evaluation.
