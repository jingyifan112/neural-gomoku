# Public benchmark summary: neural-gomoku vs Rapfi

## Goal

Run the neural-gomoku C Gomocup wrapper against a real public Gomoku engine through an external public Gomocup-protocol manager.

## Public benchmark setup

External manager:
- c-gomoku-cli

Public engine:
- Rapfi 0.43.02
- built locally on macOS from source

My engine:
- c_inference/pbrain-neural-gomoku
- weights: c_inference/weights/9x9_tactical_v2_weights.bin

Board:
- 9x9
- win length: 5
- rule: freestyle / rule 0

## Results

| Setting | Result | Notes |
|---|---:|---|
| neural sims=8 vs full Rapfi | 0W / 0D / 10L | First full public-engine benchmark run |
| neural sims=256 vs full Rapfi | 0W / 0D / 2L | Higher neural MCTS sims did not change the result |
| neural sims=256 vs Rapfi depth=1 | 0W / 0D / 4L | Attempted limited-depth Rapfi setting |
| neural sims=256 vs Rapfi depth=1, tc=1/1 | 0W / 0D / 4L | Attempted faster/weaker Rapfi setting |

## Interpretation

This is the first real public-engine benchmark for the project.

The result shows that the current 9x9 tactical v2 model is clearly below Rapfi, a mature public Gomoku engine. Even after increasing neural MCTS simulations to 256 and trying weaker Rapfi settings, the model still lost all games in these small match sets.

Current strength positioning:

- Stronger than random baseline
- Slightly more stable than the old checkpoint
- Still weaker than greedy_win_block tactical baseline
- Much weaker than public engine Rapfi

## Important limitation

This benchmark is real because it uses an external public manager and a public engine. However, it is still not a fully official Gomocup-style comparison because the current neural-gomoku model only supports 9x9, while public Gomocup engines are usually designed for 15x15 or 20x20.

## Next steps

To improve public benchmark results:

1. Train or adapt a 15x15 / 20x20 model.
2. Export matching C weights.
3. Extend pbrain-neural-gomoku to support START 15 or START 20.
4. Use public-engine losses against Rapfi to collect failure positions.
5. Continue tactical/self-play training with those failure patterns.
6. Re-run c-gomoku-cli or Piskvork matches against public engines.
