# v11d interpolation invalidation note

The first interpolation experiment used checkpoints/15x15_mixed_v11_failed_selfplay_stage1.pt as the candidate source.

Later checks showed:
- alpha=1.00 was exactly equal to checkpoints/15x15_mixed_v11_failed_selfplay_stage1.pt
- alpha=1.00 evaluated as 10-10 vs v10_frozen and 10-10 vs greedy
- this contradicted the original failed v11 stage1 behavior, which was 0-20 vs greedy and 0-20 vs v10_frozen

Conclusion:
- checkpoints/15x15_mixed_v11_failed_selfplay_stage1.pt was likely copied after candidate had already been restored to v10.
- The earlier v11d interpolation results are invalid/inconclusive.
- The true failed self-play source is now checkpoints/15x15_v11_true_failed_selfplay.pt.
