# c-gomoku-cli public manager smoke test

## Goal

Test whether the C Gomocup/Piskvork wrapper can be controlled by an external public Gomocup-protocol manager.

## External manager

Manager:
c-gomoku-cli

Downloaded manually as ZIP because git clone from GitHub was unreliable on the current network.

Local build notes on macOS:
- Patched an execvp constness issue in c-gomoku-cli/src/engine.cpp.
- Removed the Linux-only `-static` flag from c-gomoku-cli/src/Makefile.
- After these local patches, c-gomoku-cli built successfully on macOS.

These patches were made outside this repository and are not part of neural-gomoku.

## Engine under test

Executable:
c_inference/pbrain-neural-gomoku

Weights:
c_inference/weights/9x9_tactical_v2_weights.bin

Board size:
9

## Smoke test

Ran c-gomoku-cli with two copies of pbrain-neural-gomoku:

- neuralA: pbrain-neural-gomoku
- neuralB: pbrain-neural-gomoku

Result:
- neuralA vs neuralB: 1W / 0D / 1L
- score: 0.500

Observed manager output included:
- Finished game 2 (neuralB vs neuralA): 1-0 {Black win by five connection}
- Score of neuralA vs neuralB: 1 - 1 - 0 [0.500]

## Interpretation

This confirms that pbrain-neural-gomoku can be controlled by an external public Gomocup-protocol manager on macOS.

This is not yet a full public-engine benchmark because both engines were copies of my own AI. However, it completes the first real external-manager integration step.

## Remaining limitation

The current model and wrapper only support 9x9. Most public Gomocup engines are designed for 15x15 or 20x20, so a fair public-engine benchmark still requires:

1. training or adapting a 15x15 / 20x20 checkpoint,
2. exporting matching C weights,
3. extending pbrain-neural-gomoku to support START 15 or START 20,
4. running c-gomoku-cli or Piskvork against downloadable public engines.
