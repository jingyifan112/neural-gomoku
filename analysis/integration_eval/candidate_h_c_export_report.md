# Candidate H C export verification

## Artifacts

- checkpoint: `checkpoints/15x15_candidate_h_value_ranking.pt`
- weights: `weights/15x15_candidate_h_value_ranking_weights.bin`
- manifest: `weights/15x15_candidate_h_value_ranking_manifest.json`

## Parity

| case | logits diff | probs diff | value diff | top agree | pass |
| --- | ---: | ---: | ---: | --- | --- |
| g2_ply15_teacher_disagreement | 2.0980835e-05 | 2.68220901e-07 | 7.74860382e-07 | True | True |
| g2_ply17_teacher_disagreement | 1.90734863e-05 | 7.15255737e-07 | 1.1920929e-07 | True | True |
| candidate_d_repair_anchor | 2.0980835e-05 | 2.68220901e-07 | 7.74860382e-07 | True | True |

## C Tactical Gate

| metric | pass count |
| --- | ---: |
| direct | 7/7 |
| policy+safety | 7/7 |
| mcts_raw | 7/7 |
| mcts+safety | 7/7 |

## C Decision Probes

| case | move | rank | prob | C top | selected |
| --- | --- | ---: | ---: | --- | --- |
| g2_ply15_teacher_disagreement teacher | 7,9 | 1 | 0.578131 | 7,9 | True |
| g2_ply15_teacher_disagreement original | 7,10 | 2 | 0.369216 | 7,9 | False |
| g2_ply15_teacher_disagreement repair | 7,10 | 2 | 0.369216 | 7,9 | False |
| g2_ply17_teacher_disagreement teacher | 9,9 | 1 | 0.818594 | 9,9 | True |
| g2_ply17_teacher_disagreement original | 9,5 | 2 | 0.052952 | 9,9 | False |
| candidate_d_repair_anchor teacher | 7,9 | 1 | 0.578131 | 7,9 | True |
| candidate_d_repair_anchor repair | 7,10 | 2 | 0.369216 | 7,9 | False |
| candidate_d_repair_anchor old_bad | 8,8 | ILLEGAL | ILLEGAL | 7,9 | False |

## Decision

C parity, C tactical, and C decision probes pass. Rapfi smoke is now unblocked by the export gates, but was not run in this step.
