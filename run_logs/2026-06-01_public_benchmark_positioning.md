# Public benchmark / strength positioning

## Public benchmark research

The most relevant public Gomoku benchmark route is Gomocup / Piskvork.

Gomocup is a public Gomoku/Renju AI tournament platform. It provides:
- tournament results and AI strength positioning
- downloadable public AI engines
- the Piskvork manager for running AI-vs-AI games
- a standard Gomocup AI protocol based on stdin/stdout communication

However, my current model is trained for 9x9 Gomoku. Gomocup commonly uses 15x15 and 20x20 boards depending on rule category. Therefore, the current 9x9 model cannot be directly compared to Gomocup engines in the official setting yet.

## Current evaluation approach

Since the current model is 9x9, I first built a 9x9 automated evaluation harness to get an internal strength estimate.

Evaluation settings:
- board size: 9
- win length: 5
- model under test: checkpoints/9x9_tactical_v2.pt
- main MCTS simulations: 64
- evaluation games: 20 per opponent

## Results

| Evaluation | Result | Average moves | Interpretation |
|---|---:|---:|---|
| v2 vs random | 20W / 0D / 0L | 22.5 | v2 reliably beats random |
| old checkpoint vs random | 20W / 0D / 0L | 37.3 | old checkpoint also beats random, but more slowly |
| v2 vs greedy_win_block | 5W / 3D / 12L | 37.1 | v2 is not yet stronger than a simple tactical baseline |
| old checkpoint vs greedy_win_block | 5W / 0D / 15L | 31.1 | old checkpoint is slightly worse than v2 because it converts fewer losses into draws |
| v2 vs old checkpoint | 0W / 20D / 0L | 81.0 | deterministic neural-vs-neural setting lacks discrimination |

## Strength positioning

The v2 tactical checkpoint is clearly above random play. It also shows a small improvement over the old checkpoint, especially against the greedy win/block baseline, where v2 gets 3 draws while the old checkpoint loses those games.

However, v2 is still not consistently stronger than a simple tactical rule baseline. Against greedy_win_block, it scores 5W / 3D / 12L, so the current model is still below a basic tactical engine in many positions.

Current positioning:
- stronger than random
- slightly improved over the old checkpoint
- still weaker / unstable against a simple tactical greedy baseline
- not yet ready for official Gomocup-style comparison

## Limitation

The v2-vs-old checkpoint matchup produced 20 draws out of 20 games. This suggests the current deterministic neural-vs-neural setup is not discriminative enough. Future evaluation should add:
- random opening plies
- multiple seeds
- possibly different MCTS simulation settings

## Next public benchmark plan

To move toward a real public benchmark, the next steps are:

1. Implement a Gomocup / Piskvork protocol wrapper for the C AI.
2. Train or adapt the model to 15x15 or 20x20.
3. Run matches through Piskvork against downloadable Gomocup engines.
4. Report W/D/L, average moves, time per move, and possibly compare against Gomocup Elo-rated engines.

## Current conclusion

I found the relevant public benchmark route, but the current 9x9 model is not directly compatible with official Gomocup settings. As an intermediate benchmark, I added a 9x9 evaluation harness and obtained a first strength positioning:

The current v2 tactical model is above random but still below a simple tactical greedy baseline. This gives a realistic level estimate and a clear next step toward Gomocup/Piskvork evaluation.
