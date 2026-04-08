# Research Directions for Evolution Arena

## Goal
Maximize the creature's final score: (food collected × 10) − (damage × 2), averaged across 5 seeds.

## Phase 1: Parameter Tuning (experiments 1–8)
- Find optimal speed/turn_rate balance. Too fast = overshoots food. Too slow = low coverage.
- Test whether high vision_range always helps or causes information overload.
- Determine if food_attraction or hazard_avoidance matters more.

## Phase 2: Behavioral Refinement (experiments 9–16)
- Try asymmetric configs: high food attraction when far from hazards, high avoidance when near.
- Test if exploration should be high early and low late.
- Consider if the creature should prioritize nearby food clusters over distant singles.

## Phase 3: Code-Level Improvements (experiments 17+)
The agent may also modify the steering algorithm in game.py:
- Add momentum/smoothing to steering
- Implement state machine: exploring → collecting → fleeing
- Add lookahead to avoid steering into hazards
- Weight food by distance (prefer closer)
- Add wall-avoidance to prevent corner-sticking
- Track cleared areas to avoid revisiting

## Constraints
- NEVER modify evaluate.py or run_experiment.sh
- Do NOT change arena size, food/hazard count, tick count, or scoring formula
- Keep game.py under 300 lines
- Change ONE thing per experiment
- Parameters must stay in valid ranges

## What "better" means
Only the averaged score across 5 seeds matters. A change that helps one seed but hurts the average is NOT an improvement.
