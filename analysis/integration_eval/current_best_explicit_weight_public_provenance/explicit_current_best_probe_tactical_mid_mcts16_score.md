# Tactical-mid Failure Summary

- run prefix: `/Users/jing1fan/neural-gomoku/analysis/public_benchmark_eval/local_runs/neural_mcts16_vs_tactical_mid_20260626_105738`
- neural engine: `neural_current_best_mcts16`
- total games: `24`
- wins: `6`
- losses: `16`
- draws: `2`

## Loss games

| Game | Neural color | Reason | Ply count | Winner line | Final move |
|---:|---|---|---:|---|---|
| 1 | W | Black win by five connection | 175 | `0,8 1,9 2,10 3,11 4,12` | `B@0,8` |
| 3 | W | Black win by five connection | 27 | `4,5 4,6 4,7 4,8 4,9` | `B@4,9` |
| 4 | B | White win by five connection | 32 | `1,6 2,7 3,8 4,9 5,10` | `W@1,6` |
| 6 | B | White win by five connection | 42 | `4,8 5,7 6,6 7,5 8,4` | `W@8,4` |
| 10 | B | White win by five connection | 54 | `10,1 10,2 10,3 10,4 10,5` | `W@10,5` |
| 11 | W | Black win by five connection | 89 | `7,14 8,13 9,12 10,11 11,10` | `B@7,14` |
| 13 | W | Black win by five connection | 25 | `8,10 9,10 10,10 11,10 12,10` | `B@8,10` |
| 14 | B | White win by five connection | 26 | `11,8 11,9 11,10 11,11 11,12` | `W@11,12` |
| 15 | W | Black win by five connection | 37 | `5,3 6,4 7,5 8,6 9,7` | `B@5,3` |
| 17 | W | Black win by five connection | 45 | `10,11 11,10 12,9 13,8 14,7` | `B@14,7` |
| 19 | W | Black win by five connection | 25 | `6,9 7,8 8,7 9,6 10,5` | `B@6,9` |
| 20 | B | White win by five connection | 28 | `9,5 10,6 11,7 12,8 13,9` | `W@13,9` |
| 21 | W | Black win by five connection | 35 | `6,10 7,10 8,10 9,10 10,10` | `B@6,10` |
| 22 | B | White win by five connection | 46 | `7,9 8,8 9,7 10,6 11,5` | `W@7,9` |
| 23 | W | Black win by five connection | 55 | `5,9 6,10 7,11 8,12 9,13` | `B@9,13` |
| 24 | B | White win by five connection | 52 | `7,11 8,11 9,11 10,11 11,11` | `W@11,11` |

## Draw games

| Game | Neural color | Reason | Ply count | Final move |
|---:|---|---|---:|---|
| 2 | B | Draw by fullfilled board | 225 | `B@14,14` |
| 12 | B | Draw by fullfilled board | 225 | `B@14,0` |

## Win games

| Game | Neural color | Reason | Ply count | Winner line | Final move |
|---:|---|---|---:|---|---|
| 5 | W | White win by five connection | 118 | `6,6 7,5 8,4 9,3 10,2` | `W@8,4` |
| 7 | W | White win by five connection | 112 | `8,0 9,1 10,2 11,3 12,4` | `W@10,2` |
| 8 | B | Black win by five connection | 27 | `6,6 7,5 8,4 9,3 10,2` | `B@10,2` |
| 9 | W | White win by five connection | 44 | `9,7 10,7 11,7 12,7 13,7` | `W@13,7` |
| 16 | B | Black win by five connection | 79 | `3,8 4,7 5,6 6,5 7,4` | `B@7,4` |
| 18 | B | Black win by five connection | 55 | `6,4 6,5 6,6 6,7 6,8` | `B@6,4` |
