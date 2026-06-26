# Current-best runner mismatch audit

## Scope

- Branch: `exp/15x15-current-best-runner-mismatch-audit`
- Purpose: audit/recover archived current-best runner mismatch before any additional supervision.
- This route is diagnostic only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Key provenance finding

- Archived public-score and C-diagnostic paths reference `weights/15x15_current_best_weights.bin`.
- That default weight file is currently missing locally.
- Existing manifest text for `weights/15x15_current_best_probe_weights.bin` reports `source_checkpoint: checkpoints/15x15_current_best.pt`.
- Therefore, implicit/default C runner invocation is unsafe for current-best comparisons unless the weight path is explicit.

## Explicit C diagnostic rerun

| Weight | Must-block rows | Exact target | Same match blunder | Preterminal rows | Target prevention | Zero double-threat replies |
|---|---:|---:|---:|---:|---:|---:|
| `weights/15x15_current_best_probe_weights.bin` | 16 | 0 | 16 | 2 | 0 | 0 |
| `weights/15x15_current_best_margin_g2m13_m15_3pair_b_weights.bin` | 16 | 1 | 15 | 2 | 0 | 0 |

## Archived diagnostic parity

- `must_block_archived_vs_current_best_probe`: archived rows `16`, rerun rows `16`, field checks `80`, mismatches `0`, exact field match `True`.
- `preterminal_archived_vs_current_best_probe`: archived rows `2`, rerun rows `2`, field checks `10`, mismatches `0`, exact field match `True`.

## Interpretation

- `current_best_probe_weights.bin` reproduces the archived C diagnostic behavior exactly on the audited fields.
- The missing default `15x15_current_best_weights.bin` is a provenance/reproducibility blocker for implicit benchmark commands.
- The archived `7.0/24` tactical-mid score is not explained by the small C diagnostic subset alone; the next safe step is an explicit-weight public-run provenance check only after the default-weight ambiguity is documented.
- `margin_g2m13_m15_3pair_b` does not recover the actionable preterminal failures and only changes one too-late must-block case, so it should not be treated as recovered current-best.

## Outputs

- `analysis/integration_eval/current_best_runner_mismatch_audit/archived_vs_explicit_current_best_probe_c_diagnostic_diff.csv`
- `analysis/integration_eval/current_best_runner_mismatch_audit/current_best_probe_must_block_c_mcts16.csv`
- `analysis/integration_eval/current_best_runner_mismatch_audit/current_best_probe_must_block_c_mcts16.md`
- `analysis/integration_eval/current_best_runner_mismatch_audit/current_best_probe_preterminal_c_mcts16.csv`
- `analysis/integration_eval/current_best_runner_mismatch_audit/current_best_probe_preterminal_c_mcts16.md`
- `analysis/integration_eval/current_best_runner_mismatch_audit/current_best_runner_mismatch_audit_summary.json`
- `analysis/integration_eval/current_best_runner_mismatch_audit/margin_g2m13_m15_3pair_b_must_block_c_mcts16.csv`
- `analysis/integration_eval/current_best_runner_mismatch_audit/margin_g2m13_m15_3pair_b_must_block_c_mcts16.md`
- `analysis/integration_eval/current_best_runner_mismatch_audit/margin_g2m13_m15_3pair_b_preterminal_c_mcts16.csv`
- `analysis/integration_eval/current_best_runner_mismatch_audit/margin_g2m13_m15_3pair_b_preterminal_c_mcts16.md`

