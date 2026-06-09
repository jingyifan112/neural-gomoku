# Codex fork terminal backup negative result

## Context

After Candidate D fixed game2 move15 but still failed Rapfi smoke 0-2 at mcts16/mcts32, Codex tested one minimal search-side improvement.

## Ledger summary

Candidate D mcts32 critical white moves:

| game | move | side | direct | MCTS final | value | fork score | multi-win allowed | label |
|---|---:|---|---|---|---:|---:|---|---|
| 2 | 13 | white | 8,8 | 8,8 | -0.674789 | 1 | no | SEARCH_TOO_SHALLOW |
| 2 | 15 | white | 7,10 | 7,10 | -0.114186 | 1 | no | VALUE_BLIND |
| 2 | 17 | white | 9,5 | 9,5 | -0.401256 | 1 | no | SEARCH_TOO_SHALLOW |
| 2 | 19 | white | 9,9 | 10,11 | -0.587536 | 1 | no | SEARCH_TOO_SHALLOW |
| 2 | 21 | white | 9,9 | 8,10 | -0.395404 | 1 | no | SEARCH_TOO_SHALLOW |

## Experiment

Codex tried a search-side fork terminal backup:

- MCTS treats selected children that allow an opponent forcing terminal reply as losing.
- First version ran the check at expansion time and caused a timeout regression.
- Lazy selected-child checking removed the timeout regression.

## Result

Focused tests passed during the experiment.

Valid mcts32 Rapfi smoke rerun:

- result: 0-2
- no time forfeits
- Candidate D move15 remained fixed at 7,10

Because Rapfi smoke did not improve to at least 1-1, the code change was reverted.

## Conclusion

Do not continue this exact fork terminal backup direction.

The current failure path does not look like a simple immediate fork miss:

- one-ply fork score was 1 at the inspected moves,
- multi-win allowed was no,
- search-side terminal backup did not improve smoke.

Next direction: build a Rapfi teacher ledger for these critical positions to identify better white moves before training or changing MCTS again.
