# Python MCTS vs C Terminal Safety Manual Comparison

I manually compared two play modes using the current 9x9 checkpoint.

## Modes compared

1. Python neural MCTS version

Command:

PYTHONPATH=src python -m gomoku_agent.play \
  --checkpoint checkpoints/9x9.pt \
  --board-size 9 \
  --win-length 5 \
  --mcts-sims 64

2. C CPU inference with terminal safety

Command:

cd c_inference
./play_c weights/9x9_weights.bin

## Manual test result

- Python MCTS version: human won 3/3 games.
- C policy + terminal safety version: human won 3/3 games.

## Observation

Both versions still lost to the human player in all tested games.

The C safety version sometimes appeared more defensive and sometimes lasted longer, but it was not consistently stronger. The Python MCTS version also failed to reliably stop human line-building threats.

## Interpretation

This suggests that the current checkpoint is still undertrained. Low-simulation neural MCTS does not reliably improve play when the policy/value network is weak. C terminal safety helps with some immediate tactical mistakes, but it is not enough to make the model strong in real human play.

## Conclusion

The C CPU inference migration is successful as an engineering milestone, but the current model strength is still limited by the checkpoint quality.

Next likely improvement should focus on stronger training and more systematic evaluation, then re-export the improved checkpoint to C.
