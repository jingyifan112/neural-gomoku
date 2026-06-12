# Tactical-mid Failure Category Report

- source: `analysis/public_benchmark_eval/tactical_mid_failure_summary.csv`
- total games: `24`

## Category counts

| Category | Count |
|---|---:|
| `fast_diagonal_loss` | 8 |
| `fast_straight_loss` | 6 |
| `win` | 6 |
| `draw_full_board` | 2 |
| `long_diagonal_loss` | 1 |
| `mid_diagonal_loss` | 1 |

## Loss direction counts

| Direction | Count |
|---|---:|
| `diagonal` | 10 |
| `vertical` | 3 |
| `horizontal` | 3 |

## Loss phase counts

| Phase | Count |
|---|---:|
| `fast` | 14 |
| `long` | 1 |
| `mid` | 1 |

## Loss details

| Game | Neural color | Category | Ply | Direction | Winner line | Final move |
|---:|---|---|---:|---|---|---|
| 1 | W | `long_diagonal_loss` | 175 | `diagonal` | `0,8 1,9 2,10 3,11 4,12` | `B@0,8` |
| 3 | W | `fast_straight_loss` | 27 | `vertical` | `4,5 4,6 4,7 4,8 4,9` | `B@4,9` |
| 4 | B | `fast_diagonal_loss` | 32 | `diagonal` | `1,6 2,7 3,8 4,9 5,10` | `W@1,6` |
| 6 | B | `fast_diagonal_loss` | 42 | `diagonal` | `4,8 5,7 6,6 7,5 8,4` | `W@8,4` |
| 10 | B | `fast_straight_loss` | 54 | `vertical` | `10,1 10,2 10,3 10,4 10,5` | `W@10,5` |
| 11 | W | `mid_diagonal_loss` | 89 | `diagonal` | `7,14 8,13 9,12 10,11 11,10` | `B@7,14` |
| 13 | W | `fast_straight_loss` | 25 | `horizontal` | `8,10 9,10 10,10 11,10 12,10` | `B@8,10` |
| 14 | B | `fast_straight_loss` | 26 | `vertical` | `11,8 11,9 11,10 11,11 11,12` | `W@11,12` |
| 15 | W | `fast_diagonal_loss` | 37 | `diagonal` | `5,3 6,4 7,5 8,6 9,7` | `B@5,3` |
| 17 | W | `fast_diagonal_loss` | 45 | `diagonal` | `10,11 11,10 12,9 13,8 14,7` | `B@14,7` |
| 19 | W | `fast_diagonal_loss` | 25 | `diagonal` | `6,9 7,8 8,7 9,6 10,5` | `B@6,9` |
| 20 | B | `fast_diagonal_loss` | 28 | `diagonal` | `9,5 10,6 11,7 12,8 13,9` | `W@13,9` |
| 21 | W | `fast_straight_loss` | 35 | `horizontal` | `6,10 7,10 8,10 9,10 10,10` | `B@6,10` |
| 22 | B | `fast_diagonal_loss` | 46 | `diagonal` | `7,9 8,8 9,7 10,6 11,5` | `W@7,9` |
| 23 | W | `fast_diagonal_loss` | 55 | `diagonal` | `5,9 6,10 7,11 8,12 9,13` | `B@9,13` |
| 24 | B | `fast_straight_loss` | 52 | `horizontal` | `7,11 8,11 9,11 10,11 11,11` | `W@11,11` |

## Recommendation

Prioritize tactical defense data where the opponent has a direct line threat, especially diagonal threats in early and midgame positions. Use this report as a fixed diagnostic target before promoting any new model.
