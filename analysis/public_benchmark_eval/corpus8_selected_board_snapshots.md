# Rapfi failure board snapshots

## Game 1 move_count 4

- side_to_move: black
- value: 0.319195
- direct: 7,6
- policy_safety: 7,6
- mcts_raw: 7,6
- mcts_safety: 7,6
- final: 7,6
- previous_rapfi_bestline: J6
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=7,6; direct=7,6; policy_safety=7,6; mcts_raw=7,6; final=7,6; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . O . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . O . . . . .
  . . . . . . . X X . . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 1 move_count 6

- side_to_move: black
- value: 0.293619
- direct: 9,7
- policy_safety: 9,7
- mcts_raw: 7,8
- mcts_safety: 7,8
- final: 7,8
- previous_rapfi_bestline: J7
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: first_direct_vs_mcts_divergence
- notes: neural_move=7,8; direct=9,7; policy_safety=9,7; mcts_raw=7,8; final=7,8; reason=first_direct_vs_mcts_divergence

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . O . . . . .
  . . . . . . . X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . O . . . . .
  . . . . . . . X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 1 move_count 8

- side_to_move: black
- value: 0.085446
- direct: 6,6
- policy_safety: 6,6
- mcts_raw: 6,6
- mcts_safety: 6,6
- final: 6,6
- previous_rapfi_bestline: H6
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=6,6; direct=6,6; policy_safety=6,6; mcts_raw=6,6; final=6,6; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . O . . . . .
  . . . . . . . X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . O . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 1 move_count 38

- side_to_move: black
- value: 0.31482
- direct: 12,8
- policy_safety: 12,8
- mcts_raw: 12,8
- mcts_safety: 12,8
- final: 12,8
- previous_rapfi_bestline: L8 M9
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=12,8; direct=12,8; policy_safety=12,8; mcts_raw=12,8; final=12,8; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . . O X . X . . . . .
  . . . . . X X O O O . . . . .
  . . . X O O X O O O X . . . .
  . . . . X O X X X O O . . . .
  . . . . X O X X O . X O . . .
  . . . . . . O X X . . . . . .
  . . . . . . . O . O . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . . O X . X . . . . .
  . . . . . X X O O O . . . . .
  . . . X O O X O O O X . . . .
  . . . . X O X X X O O . . . .
  . . . . X O X X O . X O . . .
  . . . . . . O X X . . . X . .
  . . . . . . . O . O . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 1 move_count 40

- side_to_move: black
- value: 0.281804
- direct: 9,7
- policy_safety: 12,6
- mcts_raw: 9,7
- mcts_safety: 12,6
- final: 12,6
- previous_rapfi_bestline: K9 M7
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=12,6; direct=9,7; policy_safety=12,6; mcts_raw=9,7; final=12,6; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . . O X . X . . . . .
  . . . . . X X O O O . . . . .
  . . . X O O X O O O X . . . .
  . . . . X O X X X O O . . . .
  . . . . X O X X O . X O . . .
  . . . . . . O X X . O . X . .
  . . . . . . . O . O . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . . O X . X . . . . .
  . . . . . X X O O O . . . . .
  . . . X O O X O O O X . . . .
  . . . . X O X X X O O . X . .
  . . . . X O X X O . X O . . .
  . . . . . . O X X . O . X . .
  . . . . . . . O . O . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 5

- side_to_move: white
- value: 0.140266
- direct: 7,8
- policy_safety: 7,8
- mcts_raw: 7,8
- mcts_safety: 7,8
- final: 7,8
- previous_rapfi_bestline: H7
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor
- notes: neural_move=7,8; direct=7,8; policy_safety=7,8; mcts_raw=7,8; final=7,8; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X X . . . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X X . . . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 7

- side_to_move: white
- value: -0.233914
- direct: 9,5
- policy_safety: 9,6
- mcts_raw: 9,5
- mcts_safety: 9,6
- final: 9,6
- previous_rapfi_bestline: I7
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: first_direct_vs_mcts_divergence;neighbor
- notes: neural_move=9,6; direct=9,5; policy_safety=9,6; mcts_raw=9,5; final=9,6; reason=first_direct_vs_mcts_divergence;neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X X X . . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 9

- side_to_move: white
- value: -0.555102
- direct: 9,5
- policy_safety: 9,5
- mcts_raw: 9,5
- mcts_safety: 9,5
- final: 9,5
- previous_rapfi_bestline: G10
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: first_losing_value;neighbor
- notes: neural_move=9,5; direct=9,5; policy_safety=9,5; mcts_raw=9,5; final=9,5; reason=first_losing_value;neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . O . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 11

- side_to_move: white
- value: -0.204876
- direct: 7,4
- policy_safety: 7,4
- mcts_raw: 7,4
- mcts_safety: 7,4
- final: 7,4
- previous_rapfi_bestline: H6
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor
- notes: neural_move=7,4; direct=7,4; policy_safety=7,4; mcts_raw=7,4; final=7,4; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . X . O . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . O . X . O . . . . .
  . . . . . . X X X O . . . . .
  . . . . . . . X O . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 19

- side_to_move: white
- value: -0.694868
- direct: 5,6
- policy_safety: 5,6
- mcts_raw: 5,6
- mcts_safety: 5,6
- final: 5,6
- previous_rapfi_bestline: E7 F7
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: late_loss_window
- notes: neural_move=5,6; direct=5,6; policy_safety=5,6; mcts_raw=5,6; final=5,6; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . O . X . O . . . . .
  . . . . X . X X X O . . . . .
  . . . . . X O X O X . . . . .
  . . . . O . X O . . O . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . O . X . O . . . . .
  . . . . X O X X X O . . . . .
  . . . . . X O X O X . . . . .
  . . . . O . X O . . O . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 2 move_count 21

- side_to_move: white
- value: -0.777915
- direct: 2,4
- policy_safety: 2,4
- mcts_raw: 2,4
- mcts_safety: 2,4
- final: 2,4
- previous_rapfi_bestline: D6 H10
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: late_loss_window
- notes: neural_move=2,4; direct=2,4; policy_safety=2,4; mcts_raw=2,4; final=2,4; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . X . O . X . O . . . . .
  . . . . X O X X X O . . . . .
  . . . . . X O X O X . . . . .
  . . . . O . X O . . O . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . O . . . . O . . . . . . .
  . . . X . O . X . O . . . . .
  . . . . X O X X X O . . . . .
  . . . . . X O X O X . . . . .
  . . . . O . X O . . O . . . .
  . . . . . . X . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 3 move_count 2

- side_to_move: black
- value: -0.073863
- direct: 7,6
- policy_safety: 7,6
- mcts_raw: 6,6
- mcts_safety: 6,6
- final: 6,6
- previous_rapfi_bestline:
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: first_direct_vs_mcts_divergence
- notes: neural_move=6,6; direct=7,6; policy_safety=7,6; mcts_raw=6,6; final=6,6; reason=first_direct_vs_mcts_divergence

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . O X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 3 move_count 4

- side_to_move: black
- value: 0.241949
- direct: 8,8
- policy_safety: 8,8
- mcts_raw: 8,8
- mcts_safety: 8,8
- final: 8,8
- previous_rapfi_bestline: F6
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=8,8; direct=8,8; policy_safety=8,8; mcts_raw=8,8; final=8,8; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . O X . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . O X . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 3 move_count 24

- side_to_move: black
- value: 0.01607
- direct: 7,6
- policy_safety: 3,7
- mcts_raw: 3,7
- mcts_safety: 3,7
- final: 3,7
- previous_rapfi_bestline: C8 D8
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=3,7; direct=7,6; policy_safety=3,7; mcts_raw=3,7; final=3,7; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . X . O . X . . . . . . .
  . . . X O O O X O . . . . . .
  . . . . . O X . . . . . . . .
  . . O . O O O X . . . . . . .
  . . . . . X . O X . . . . . .
  . . . . . . . . X X . . . . .
  . . . . . . . . . . O . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . X . O . X . . . . . . .
  . . . X O O O X O . . . . . .
  . . . . . O X . . . . . . . .
  . . O X O O O X . . . . . . .
  . . . . . X . O X . . . . . .
  . . . . . . . . X X . . . . .
  . . . . . . . . . . O . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 3 move_count 26

- side_to_move: black
- value: 0.149186
- direct: 7,6
- policy_safety: 6,3
- mcts_raw: 7,6
- mcts_safety: 6,3
- final: 6,3
- previous_rapfi_bestline: D7 G4
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=6,3; direct=7,6; policy_safety=6,3; mcts_raw=7,6; final=6,3; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . X . O . X . . . . . . .
  . . . X O O O X O . . . . . .
  . . . O . O X . . . . . . . .
  . . O X O O O X . . . . . . .
  . . . . . X . O X . . . . . .
  . . . . . . . . X X . . . . .
  . . . . . . . . . . O . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . X . . . . . . . . .
  . . . . . X X . . . . . . . .
  . . . X . O . X . . . . . . .
  . . . X O O O X O . . . . . .
  . . . O . O X . . . . . . . .
  . . O X O O O X . . . . . . .
  . . . . . X . O X . . . . . .
  . . . . . . . . X X . . . . .
  . . . . . . . . . . O . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 4 move_count 13

- side_to_move: white
- value: -0.389284
- direct: 8,4
- policy_safety: 8,4
- mcts_raw: 8,4
- mcts_safety: 8,4
- final: 8,4
- previous_rapfi_bestline: H6
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor
- notes: neural_move=8,4; direct=8,4; policy_safety=8,4; mcts_raw=8,4; final=8,4; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X . . . . . .
  . . . . . . O X . . O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X . . . . . .
  . . . . . . O X . . O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 4 move_count 15

- side_to_move: white
- value: -0.149918
- direct: 9,9
- policy_safety: 6,4
- mcts_raw: 9,9
- mcts_safety: 6,4
- final: 6,4
- previous_rapfi_bestline: J8
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: first_direct_vs_mcts_divergence
- notes: neural_move=6,4; direct=9,9; policy_safety=6,4; mcts_raw=9,9; final=6,4; reason=first_direct_vs_mcts_divergence

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X . . . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X . . . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 4 move_count 17

- side_to_move: white
- value: 0.012814
- direct: 10,8
- policy_safety: 10,6
- mcts_raw: 10,6
- mcts_safety: 10,6
- final: 10,6
- previous_rapfi_bestline: J7 K7
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor
- notes: neural_move=10,6; direct=10,8; policy_safety=10,6; mcts_raw=10,6; final=10,6; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X . . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X O . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 4 move_count 21

- side_to_move: white
- value: 0.112891
- direct: 10,8
- policy_safety: 10,8
- mcts_raw: 10,8
- mcts_safety: 10,8
- final: 10,8
- previous_rapfi_bestline: L10 K9
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: late_loss_window
- notes: neural_move=10,8; direct=10,8; policy_safety=10,8; mcts_raw=10,8; final=10,8; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X O . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . X X . X . . .
  . . . . . . . . . O . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X O . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X O . . . .
  . . . . . . . . X X . X . . .
  . . . . . . . . . O . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 4 move_count 23

- side_to_move: white
- value: -0.3042
- direct: 7,4
- policy_safety: 12,9
- mcts_raw: 7,4
- mcts_safety: 12,9
- final: 12,9
- previous_rapfi_bestline: K10 M10
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: late_loss_window
- notes: neural_move=12,9; direct=7,4; policy_safety=12,9; mcts_raw=7,4; final=12,9; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X O . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X O . . . .
  . . . . . . . . X X X X . . .
  . . . . . . . . . O . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O . O . . . . . .
  . . . . . . . X . O . . . . .
  . . . . . O X X X X O . . . .
  . . . . . . O X . X O . . . .
  . . . . . . . O O X O . . . .
  . . . . . . . . X X X X O . .
  . . . . . . . . . O . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 6

- side_to_move: black
- value: 0.462012
- direct: 9,8
- policy_safety: 9,8
- mcts_raw: 9,8
- mcts_safety: 9,8
- final: 9,8
- previous_rapfi_bestline: I9
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=9,8; direct=9,8; policy_safety=9,8; mcts_raw=9,8; final=9,8; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . X X O . . . . . .
  . . . . . . . O O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . X . . . . .
  . . . . . . X X O . . . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 8

- side_to_move: black
- value: 0.170987
- direct: 6,6
- policy_safety: 8,5
- mcts_raw: 6,6
- mcts_safety: 8,5
- final: 8,5
- previous_rapfi_bestline: I7
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: first_direct_vs_mcts_divergence
- notes: neural_move=8,5; direct=6,6; policy_safety=8,5; mcts_raw=6,6; final=8,5; reason=first_direct_vs_mcts_divergence

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O X . . . . .
  . . . . . . X X O . . . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . O X . . . . .
  . . . . . . X X O . . . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 10

- side_to_move: black
- value: -0.113846
- direct: 10,7
- policy_safety: 10,7
- mcts_raw: 10,7
- mcts_safety: 10,7
- final: 10,7
- previous_rapfi_bestline: J8
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=10,7; direct=10,7; policy_safety=10,7; mcts_raw=10,7; final=10,7; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . O X . . . . .
  . . . . . . X X O O . . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 12

- side_to_move: black
- value: 0.002815
- direct: 7,6
- policy_safety: 7,6
- mcts_raw: 7,6
- mcts_safety: 7,6
- final: 7,6
- previous_rapfi_bestline: H5
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=7,6; direct=7,6; policy_safety=7,6; mcts_raw=7,6; final=7,6; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . . O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . X O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . . . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 14

- side_to_move: black
- value: -0.656119
- direct: 6,6
- policy_safety: 6,6
- mcts_raw: 6,6
- mcts_safety: 6,6
- final: 6,6
- previous_rapfi_bestline: F9
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: first_losing_value
- notes: neural_move=6,6; direct=6,6; policy_safety=6,6; mcts_raw=6,6; final=6,6; reason=first_losing_value

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . . X O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . X X O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 16

- side_to_move: black
- value: -0.287235
- direct: 7,5
- policy_safety: 7,5
- mcts_raw: 7,5
- mcts_safety: 7,5
- final: 7,5
- previous_rapfi_bestline: G5
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: neighbor
- notes: neural_move=7,5; direct=7,5; policy_safety=7,5; mcts_raw=7,5; final=7,5; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . . . . X . . . . . .
  . . . . . . X X O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . . . X X . . . . . .
  . . . . . . X X O X . . . . .
  . . . . . . X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 28

- side_to_move: black
- value: -0.78911
- direct: 7,3
- policy_safety: 5,11
- mcts_raw: 5,11
- mcts_safety: 5,11
- final: 5,11
- previous_rapfi_bestline: F10 F12
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=5,11; direct=7,3; policy_safety=5,11; mcts_raw=5,11; final=5,11; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . O X X X . . . . . .
  . . . . . X X X O X . . . . .
  . . . . X O X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . O O . O . . . . . .
  . . . . . O . . X . . . . . .
  . . . . X . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . O X X X . . . . . .
  . . . . . X X X O X . . . . .
  . . . . X O X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . O O . O . . . . . .
  . . . . . O . . X . . . . . .
  . . . . X X . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 5 move_count 30

- side_to_move: black
- value: -0.393157
- direct: 7,3
- policy_safety: 4,9
- mcts_raw: 7,3
- mcts_safety: 4,9
- final: 4,9
- previous_rapfi_bestline: H10 J10
- next_rapfi_bestline:
- loss_reason: White win by five connection
- failure_type: late_loss_window
- notes: neural_move=4,9; direct=7,3; policy_safety=4,9; mcts_raw=7,3; final=4,9; reason=late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . O X X X . . . . . .
  . . . . . X X X O X . . . . .
  . . . . X O X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . . O O O O . . . . . .
  . . . . . O . . X . . . . . .
  . . . . X X . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . O O . . . . . . .
  . . . . . O X X X . . . . . .
  . . . . . X X X O X . . . . .
  . . . . X O X X O O X . . . .
  . . . . . O . O O X . . . . .
  . . . . X O O O O . . . . . .
  . . . . . O . . X . . . . . .
  . . . . X X . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 6 move_count 5

- side_to_move: white
- value: -0.553274
- direct: 8,8
- policy_safety: 8,8
- mcts_raw: 8,8
- mcts_safety: 8,8
- final: 8,8
- previous_rapfi_bestline: G8
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: first_losing_value
- notes: neural_move=8,8; direct=8,8; policy_safety=8,8; mcts_raw=8,8; final=8,8; reason=first_losing_value

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . X X . . . . . . .
  . . . . . . . O . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . O . . . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . . . X X . . . . . . .
  . . . . . . . O O . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 6 move_count 15

- side_to_move: white
- value: -0.134725
- direct: 4,8
- policy_safety: 4,8
- mcts_raw: 4,8
- mcts_safety: 4,8
- final: 4,8
- previous_rapfi_bestline: D10 E9
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor
- notes: neural_move=4,8; direct=4,8; policy_safety=4,8; mcts_raw=4,8; final=4,8; reason=neighbor

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . O X X X . . . . . . .
  . . . . . . X O O . . . . . .
  . . . X . . X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . O X X X . . . . . . .
  . . . . O . X O O . . . . . .
  . . . X . . X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 6 move_count 17

- side_to_move: white
- value: -0.079101
- direct: 7,9
- policy_safety: 4,9
- mcts_raw: 7,9
- mcts_safety: 4,9
- final: 4,9
- previous_rapfi_bestline: F10
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: first_direct_vs_mcts_divergence;late_loss_window
- notes: neural_move=4,9; direct=7,9; policy_safety=4,9; mcts_raw=7,9; final=4,9; reason=first_direct_vs_mcts_divergence;late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . O X X X . . . . . . .
  . . . . O . X O O . . . . . .
  . . . X . X X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . . . . . . .
  . . . . . . X . . . . . . . .
  . . . . O X X X . . . . . . .
  . . . . O . X O O . . . . . .
  . . . X O X X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

## Game 6 move_count 19

- side_to_move: white
- value: 0.147963
- direct: 9,7
- policy_safety: 9,5
- mcts_raw: 9,7
- mcts_safety: 9,5
- final: 9,5
- previous_rapfi_bestline: I7 J6
- next_rapfi_bestline:
- loss_reason: Black win by five connection
- failure_type: neighbor;late_loss_window
- notes: neural_move=9,5; direct=9,7; policy_safety=9,5; mcts_raw=9,7; final=9,5; reason=neighbor;late_loss_window

Before decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . . . . . . .
  . . . . . . X . X . . . . . .
  . . . . O X X X . . . . . . .
  . . . . O . X O O . . . . . .
  . . . X O X X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```

After decision:

```text
  ------------------------------
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . O . . . . . .
  . . . . . O O X . O . . . . .
  . . . . . . X . X . . . . . .
  . . . . O X X X . . . . . . .
  . . . . O . X O O . . . . . .
  . . . X O X X . . . . . . . .
  . . . . . . O . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  . . . . . . . . . . . . . . .
  ------------------------------
```
