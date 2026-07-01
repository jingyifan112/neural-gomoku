# Neural Gomoku

Pure neural-network Gomoku baseline inspired by Arthur Chiao's tic-tac-toe reinforcement learning example, but upgraded into a larger neural Gomoku research workflow.

The project started as a clean board-game AI prototype and evolved into a 15x15 Gomoku system with:

* CNN policy-value network instead of a single-layer MLP
* neural MCTS guided by policy/value outputs
* legal-move masking
* terminal-state search safety
* CLI training and human-vs-model play
* 9x9 and 15x15 board-size support
* C inference and engine benchmark workflow
* Rapfi-based failure analysis
* teacher-divergence and retention data routes
* multi-suppress and rank/top-k repair experiments
* hard-guarded saved-candidate evaluation
* public benchmark closeout discipline

The first goal is not to immediately beat strong engines. The goal is to keep a clean research repo where model capacity, self-play quality, search, data quality, and benchmark discipline can be improved without adding hand-written Gomoku strategy rules.

---

## Current Status

The current project stage is closed out.

A final 15x15 guard-aware saved candidate was generated, exported, smoke-tested, and evaluated on the public benchmark ladder. It matched the previous current-best instead of improving over it, so it was **not promoted**.

Final decision:

```text
saved candidate completed
C export completed
smoke test completed
public benchmark completed
score table completed
benchmark same as previous current-best
no promotion
no current-best overwrite
project-stage closeout
```

Final public benchmark snapshot:

| Opponent          | Config | Score / 24 |  W-L-D | Interpretation   |
| ----------------- | -----: | ---------: | -----: | ---------------- |
| random            | MCTS32 |       24.0 | 24-0-0 | solved           |
| tactical_lite     | MCTS32 |       23.0 | 23-1-0 | near solved      |
| tactical_mid      | MCTS16 |        7.0 | 6-16-2 | weakness remains |
| tactical_plus     | MCTS16 |        3.0 | 2-20-2 | weakness remains |
| rapfi_fast_depth1 | MCTS32 |        0.0 | 0-24-0 | not competitive  |

Important clarification:

```text
Rapfi is a strong baseline, teacher-signal source, and one benchmark opponent.
The final promotion decision is not based on candidate vs Rapfi alone.
The final promotion decision compares candidate vs previous current-best on the same full benchmark ladder.
```

---

## Project Evolution

The project developed in three major stages.

### Stage 1: Tic-tac-toe-inspired prototype

The early stage focused on understanding the minimum board-game AI loop:

* board representation
* legal move generation
* win/draw detection
* current-player encoding
* model inference
* move selection
* training loop
* evaluation loop

The first model style was close to a simple policy model or MLP-style baseline. This helped verify the pipeline, but it did not capture Gomoku board geometry well.

Main lesson:

```text
A toy board-game prototype is useful for understanding the pipeline,
but Gomoku needs a model that can exploit board spatial structure.
```

### Stage 2: Model and system upgrade

The project was upgraded from a simple flattened-board model to a CNN policy-value system.

Key changes:

* flat board vector -> board tensor
* simple policy model -> CNN policy-value network
* direct policy move -> MCTS searched move
* Python-only inference -> C inference
* small-board experiments -> 15x15 Gomoku
* aggregate score checking -> position-level failure diagnosis

Main lesson:

```text
A stronger Gomoku system needs both model architecture and evaluation infrastructure.
```

### Stage 3: Rapfi and 15x15 research workflow

Rapfi was introduced as:

1. a strong baseline opponent,
2. a teacher-signal source,
3. one opponent in the public benchmark ladder.

This enabled:

* Rapfi failure extraction
* 15x15 failure corpus construction
* fixed-position evaluation
* teacher-divergence data
* retention protection
* multi-suppress objective design
* rank/top-k gates
* hard guard evaluation
* guard-aware saved-candidate closeout

Main lesson:

```text
Local repair is not the same as global strength improvement.
A candidate should only be promoted if it beats the previous current-best under the same benchmark ladder.
```

---

## Architecture Overview

The model uses a CNN policy-value design.

Conceptually:

```text
board tensor
    ↓
CNN backbone
    ↓
policy head → move logits over board positions
value head  → position value estimate
```

The policy head answers:

```text
Where should the model move?
```

The value head answers:

```text
How good is the current position for the current player?
```

MCTS uses the neural outputs to guide search:

```text
policy prior
+ value estimate
+ legal move mask
+ terminal-state safety
+ MCTS simulations
= searched move
```

The project intentionally avoids hand-written Gomoku shape rules. Terminal-state safety only checks immediate game-ending conditions using the game rule, not expert shape knowledge.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
```

If editable install fails because pip cannot reach PyPI, run commands with `PYTHONPATH=src` from the repo root instead.

---

## Run Tests

```bash
python -m pytest
```

---

## Train

Start tiny to verify the loop:

```bash
python -m gomoku_agent.train --iterations 1 --games 5 --epochs 1 --board-size 9 --win-length 5
```

For normal Gomoku:

```bash
python -m gomoku_agent.train --iterations 3 --games 30 --epochs 2 --board-size 15 --win-length 5
```

Checkpoints are written to:

```text
checkpoints/latest.pt
```

A checkpoint is tied to its board size, so use separate files when switching between 9x9 and 15x15:

```bash
python -m gomoku_agent.train --board-size 9 --checkpoint checkpoints/9x9.pt
python -m gomoku_agent.play --board-size 9 --checkpoint checkpoints/9x9.pt
```

MCTS is expensive on CPU. Increase `--games`, `--iterations`, and `--mcts-sims` gradually only after the quick command works.

---

## Colab GPU

For faster 9x9 or 15x15 experiments, enable a GPU runtime in Google Colab, clone the repo, and keep checkpoints in Google Drive so runtime disconnects do not erase the trained model.

```python
from google.colab import drive
drive.mount("/content/drive")
```

```bash
git clone https://github.com/jingyifan112/neural-gomoku.git
cd /content/neural-gomoku
pip install -r requirements.txt
mkdir -p /content/drive/MyDrive/gomoku_checkpoints
```

Example 9x9 Colab training run:

```bash
PYTHONPATH=src python -m gomoku_agent.train \
  --iterations 3 \
  --games 20 \
  --epochs 1 \
  --board-size 9 \
  --win-length 5 \
  --mcts-sims 16 \
  --allow-immediate-loss \
  --checkpoint /content/drive/MyDrive/gomoku_checkpoints/9x9.pt
```

`--allow-immediate-loss` disables the expensive terminal safety checks during self-play training. Human play still uses safety checks by default.

---

## Play

```bash
python -m gomoku_agent.play --checkpoint checkpoints/latest.pt --board-size 15 --win-length 5
```

Enter moves as:

```text
row col
```

using zero-based coordinates.

By default, human play uses deterministic neural MCTS. Use `--mcts-sims 0` to test the raw policy network without search. Add `--sample` only when you intentionally want a more exploratory, weaker raw-policy opponent.

MCTS also filters moves that allow the opponent to win immediately using only the game's terminal-state rule. This is search safety, not hand-written Gomoku shape knowledge. Pass `--allow-immediate-loss` to disable that filter.

---

## C Inference and Engine Workflow

The project includes a C inference path so that trained neural checkpoints can be evaluated outside Python.

The C workflow is used for:

* Python/C inference consistency checks
* CPU inference
* engine wrapper integration
* benchmark workflow support
* candidate smoke tests
* public benchmark runs

Important C inference concerns:

* checkpoint architecture metadata
* board size
* channel count
* residual block count
* BatchNorm eval-mode behavior
* tensor layout
* legal move masking
* top-move parity between Python and C
* engine startup and benchmark parsing

For details, see:

```text
c_inference/README.md
```

---

## Public Benchmark Workflow

The public benchmark ladder compares candidate models against the previous current-best under the same opponent set.

Benchmark opponents:

```text
random
tactical_lite
tactical_mid
tactical_plus
rapfi_fast_depth1
```

The benchmark is not only a strength test. It is also a promotion gate.

Core rules:

```text
local improvement != public benchmark improvement
teacher-divergence repair != full-game strength improvement
saved candidate != promotion
rapfi_fast_depth1 is one ladder opponent, not the only comparison target
promotion requires candidate > old current-best on the full benchmark ladder
```

Final public benchmark result:

```text
candidate ladder score:     24, 23, 7, 3, 0
old current-best ladder:    24, 23, 7, 3, 0
comparison result:          same as current-best
final decision:             no promotion
```

---

## Rapfi, Teacher Divergence, and Failure Analysis

Rapfi was used in three roles.

### 1. Strong baseline

Rapfi exposed the gap between neural-gomoku and a stronger Gomoku engine.

### 2. Teacher-signal source

Rapfi recommendations were used to identify teacher moves in fixed positions.

### 3. Benchmark opponent

`rapfi_fast_depth1` is one opponent in the public benchmark ladder.

The failure-analysis workflow is:

```text
Rapfi game / failure position
→ fixed-position evaluation
→ model move vs Rapfi teacher move
→ teacher rank / teacher probability / gap
→ teacher-divergence row
→ repair objective
```

This turns game-level failure into structured position-level data.

Representative evidence categories include:

* Rapfi failure set
* 15x15 failure corpus
* selected hard positions
* MCTS32 debug failures
* margin-repair target/suppress pairs
* hard-guard legacy rows
* tactical_mid preterminal cases

---

## Repair and Safety Routes

Several repair routes were explored.

### Policy repair

* policy-only repair
* single-suppress margin repair
* mixed CE + anchor KL

### Multi-suppress objective

The teacher target may be below several high-probability wrong moves, not just one. Multi-suppress training tries to make the target beat multiple suppress candidates.

### Rank/top-k objective

The project moved from pairwise gap repair toward teacher-move visibility in the model's ranking.

Important buckets:

```text
protected_top10
trainable_rank_11_50
tail_rank_gt50
```

### Safety routes

To avoid damaging existing behavior, the project added:

* retention anchors
* heldout retention rows
* retention family split
* regression audits
* no-save wrapper
* hard guard
* save-on-pass-only candidate policy

Important distinction:

```text
training pass
!= gate pass
!= candidate saved
!= C export pass
!= public benchmark improvement
!= promotion
```

---

## Final Candidate and Closeout

The final saved-candidate route was:

```text
exp/15x15-rank-topk-b4c64-guardaware-v2-modefix-saved-candidate-run1
```

The final candidate was a 15x15 b4c64 guard-aware v2 modefix candidate.

Candidate lifecycle:

```text
train
→ gate
→ save
→ verify current-best unchanged
→ C export
→ smoke test
→ public benchmark
→ score table
→ closeout decision
```

Final result:

```text
candidate saved
hard guard preservation passed
current-best unchanged
C export completed
smoke test completed
public benchmark completed
score table completed
benchmark same as previous current-best
no promotion
no current-best overwrite
project-stage closeout
```

---

## Repository Structure

High-level repository structure:

```text
neural-gomoku/
│
├── src/gomoku_agent/
│   ├── model.py
│   ├── train.py
│   ├── play.py
│   ├── mcts.py
│   └── self_play.py
│
├── c_inference/
│   ├── README.md
│   ├── cnn_infer.c
│   ├── mcts_c.c
│   └── test_infer.c
│
├── scripts/
│   ├── benchmark helpers
│   ├── teacher-divergence builders
│   ├── policy repair scripts
│   ├── rank/top-k gate scripts
│   └── public score table builders
│
├── analysis/
│   ├── integration_eval/
│   ├── public_benchmark_eval/
│   └── project_summary/
│
├── checkpoints/
│   └── model checkpoints
│
├── run_logs/
│   └── experiment logs
│
└── README.md
```

---

## Experiment Logs and Evidence

Early logs:

* `run_logs/2026-05-21-human-test.md`
* `run_logs/2026-05-22-colab-gpu.md`

Later project evidence is mainly under:

```text
analysis/integration_eval/
analysis/public_benchmark_eval/
analysis/project_summary/
```

Important evidence categories:

* teacher-divergence reports
* retention reports
* policy-only repair reports
* multi-suppress reports
* rank/top-k reports
* guard-aware reports
* benchmark score tables
* final closeout files

Project summary evidence pack:

```text
analysis/project_summary/neural_gomoku_project_summary_evidence_pack/
```

---

## Roadmap

Completed:

1. Build initial neural Gomoku training and play loop.
2. Upgrade from simple MLP-style baseline to CNN policy-value network.
3. Add neural MCTS guided by policy/value outputs.
4. Add legal-move masking and terminal-state safety.
5. Add 9x9 and 15x15 support.
6. Add C inference path.
7. Add public benchmark workflow.
8. Add Rapfi-based failure analysis.
9. Add teacher-divergence and retention routes.
10. Add multi-suppress and rank/top-k objective experiments.
11. Add hard-guard and guard-aware saved-candidate route.
12. Complete final public benchmark closeout.

Future directions:

1. Expand the Rapfi teacher dataset.
2. Build a more diverse 15x15 failure corpus.
3. Improve value training.
4. Add stronger tactical curriculum data.
5. Improve MCTS diagnostics.
6. Expand public benchmark coverage.
7. Revisit 15x15 self-play data quality.
8. Explore stronger candidate architectures after data quality improves.

---

## Limitations

Current limitations:

* The model remains weak against Rapfi.
* `tactical_mid` and `tactical_plus` remain difficult.
* Local teacher-divergence repair did not translate into public benchmark improvement.
* The teacher dataset is still limited.
* Rank/top-k repair needs broader and more diverse training data.
* C inference and benchmark workflows require careful architecture/checkpoint consistency.

---

## Design Philosophy

This project intentionally avoids adding hand-written Gomoku strategy rules. The goal is to improve model capacity, training data, search, and evaluation discipline while keeping the core system neural-network based.

The final project lesson is:

```text
A candidate is not promoted because it was saved.
A candidate is promoted only if it beats the previous current-best under the same public benchmark ladder.
```
