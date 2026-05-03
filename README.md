# Evolution Arena

> **Writeup:** [Evolution Arena: a game-based autoresearch testbed](https://jthomas.site/blog/evolution-arena.html)

A game-based autoresearch testbed implementing [Karpathy's autoresearch pattern](https://github.com/karpathy/autoresearch). An AI agent (Claude Code) iteratively optimizes a game creature's behavior parameters and steering logic to maximize score.

## How it works

1. A creature navigates a 2D arena collecting food and avoiding hazards
2. Claude Code proposes parameter or code changes each cycle
3. A ratchet script keeps improvements and reverts regressions
4. Score monotonically increases over experiments

## Quick start

```bash
# Requirements: Python 3.8+, Claude Code CLI, Git

# Run the baseline
python3 evaluate.py

# Start autoresearch (default 20 experiments)
./autoresearch.sh 20
```

## Files

| File | Role | Editable by agent? |
|------|------|-------------------|
| `game.py` | Arena simulation engine | Yes |
| `config.json` | Creature behavior parameters | Yes |
| `evaluate.py` | Score extraction wrapper | No |
| `run_experiment.sh` | Ratchet (keep/revert) logic | No |
| `autoresearch.sh` | Outer loop calling Claude Code | No |
| `PLAN.md` | Research directions & constraints | Reference |

## Scoring

```
score = (food_collected × 10) − (total_damage × 2)
```

Averaged across 5 deterministic seeds for robustness.
