# Explicit current-best public-run provenance inputs

- branch: exp/15x15-current-best-explicit-weight-public-provenance
- commit_before_run: 64334dcc6d320e8da09fb8fd2053c46fa7f23abb
- neural_weights: weights/15x15_current_best_probe_weights.bin
- neural_weights_sha256: 72bb147ab19c8326ec13c4c2f6cf415697f3b2aa732833644fd04e60ce9a8494
- source_checkpoint_manifest: weights/15x15_current_best_probe_manifest.json
- move_mode: mcts_safe
- mcts_sims: 16
- baseline: tactical_mid
- games: 24
- scope: provenance check only; no training; no checkpoint save; no C export; no promotion
