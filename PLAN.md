# PLAN.md — Evolution Arena: Game-Based Autoresearch Testbed

## Overview

Build a self-contained game environment that implements Karpathy's autoresearch pattern. Instead of optimizing LLM training on a GPU, an AI agent optimizes a game-playing creature's behavior parameters. The three autoresearch primitives map directly:

- **Editable asset** → Creature behavior parameters (a JSON config)
- **Scalar metric** → Game score (food collected minus damage)
- **Time-boxed cycle** → Fixed-length simulation (600 ticks per run)

The system uses Claude Code itself as the AI agent in the loop, just like autoresearch uses an AI coding agent.

---

## Architecture

```
evolution-arena/
├── PLAN.md              # This file — research directions for the agent
├── game.py              # The game simulation engine (EDITABLE by agent)
├── evaluate.py          # Runs the simulation and prints the scalar metric (FIXED)
├── config.json          # Current best parameters (EDITABLE by agent)
├── baseline.json        # Locked copy of last-known-best config (managed by loop)
├── run_experiment.sh    # Single experiment runner with ratchet logic (FIXED)
├── autoresearch.sh      # The outer loop that calls Claude Code (FIXED)
├── results.log          # Append-only log of all experiments
└── README.md            # Setup instructions
```

### Fixed vs Editable (critical separation)
- **FIXED** (agent must not modify): `evaluate.py`, `run_experiment.sh`, `autoresearch.sh`
- **EDITABLE** (agent can modify): `game.py`, `config.json`

This mirrors autoresearch's separation of `prepare.py` (fixed) from `train.py` (editable).

---

## Research Directions for the Agent

### Phase 1: Parameter sweep (experiments 1-8)
- Find a good speed/turn_rate balance. Too fast = overshooting. Too slow = not enough coverage.
- Test whether high vision_range is always better or if it causes information overload.
- Establish whether food_attraction or hazard_avoidance contributes more to score.

### Phase 2: Behavioral refinement (experiments 9-16)
- Try asymmetric strategies: high food attraction when far from hazards, high avoidance when near.
- Test if exploration_bias should decrease over time (explore early, exploit late).
- Consider whether the creature should sometimes ignore distant food in favor of nearby clusters.

### Phase 3: Code-level improvements (experiments 17+)
The agent may also modify `game.py` to improve the creature's steering algorithm:
- Add momentum or smoothing to the steering
- Implement a simple state machine (exploring vs. collecting vs. fleeing)
- Add lookahead: predict if current heading leads into a hazard
- Weight food by distance (prefer closer food over farther food)
- Add wall-avoidance behavior to prevent getting stuck in corners
- Implement path memory: avoid revisiting areas already cleared of food

### Constraints
- Do not modify evaluate.py or run_experiment.sh
- Do not change the arena size, food count, hazard count, or tick count
- Do not change the scoring formula
- Keep game.py under 300 lines
- Each experiment should change ONE thing so we can attribute improvements

### What "better" means
The ONLY metric is the averaged score across 5 seeds. Higher is better. A change that improves one seed but hurts the average is NOT an improvement.
