# Public engine benchmark: neural-gomoku vs Rapfi

## Goal

Run neural-gomoku against a real public Gomoku engine using an external Gomocup-protocol manager.

## Benchmark setup

External manager:
- c-gomoku-cli

Public engine:
- Rapfi 0.43.02
- built locally on macOS from source

My engine:
- c_inference/pbrain-neural-gomoku
- weights: c_inference/weights/9x9_tactical_v2_weights.bin
- MCTS sims: 8 for the public-manager benchmark run

Board:
- 9x9
- win length: 5
- rule: freestyle / rule 0

Time control:
- tc=3/1

## Result

10-game public engine benchmark:

| Matchup | Result | Score |
|---|---:|---:|
| neural vs Rapfi | 0W / 0D / 10L | 0.000 |

Observed manager summary:

Score of neural vs rapfi: 0 - 10 - 0 [0.000]

## Interpretation

This is the first successful real public-engine benchmark run for the project.

The result shows that the current 9x9 tactical v2 model is much weaker than Rapfi, a mature public Gomoku engine. This is expected because Rapfi is a strong public engine, while the current model is still a small 9x9 neural MCTS prototype.

Current strength positioning:

- Stronger than random baseline
- Slightly more stable than the old checkpoint
- Still weaker than a simple greedy win/block tactical baseline
- Much weaker than public engine Rapfi

## Limitation

This is a real public-engine benchmark run, but it is still not a fully official Gomocup-style evaluation because:

1. the current neural-gomoku model only supports 9x9,
2. most public Gomocup engines are designed for 15x15 or 20x20,
3. this run used low MCTS sims for neural-gomoku to keep the public manager run responsive.

## Next steps

To make the benchmark more official and comparable:

1. train or adapt a 15x15 / 20x20 model,
2. export matching C weights,
3. extend pbrain-neural-gomoku to support START 15 or START 20,
4. run larger match sets against public engines such as Rapfi through c-gomoku-cli or Piskvork,
5. report W/D/L, average moves, time control, and engine settings.
