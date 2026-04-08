#!/bin/bash
# autoresearch.sh — The main autoresearch loop.
# Usage: ./autoresearch.sh [num_experiments]

NUM_EXPERIMENTS=${1:-20}
echo "=== EVOLUTION ARENA AUTORESEARCH ==="
echo "Running $NUM_EXPERIMENTS experiments"
echo ""

# Initialize baseline if not exists
if [ ! -f baseline.json ]; then
    cp config.json baseline.json
    python3 evaluate.py > baseline_score.txt
    git add -A && git commit -m "initial baseline" --quiet
    echo "Baseline score: $(cat baseline_score.txt)"
fi

for i in $(seq 1 $NUM_EXPERIMENTS); do
    echo ""
    echo "━━━ Experiment $i/$NUM_EXPERIMENTS ━━━"

    # Read current state for the agent
    CURRENT_SCORE=$(cat baseline_score.txt)
    RECENT_LOG=$(tail -10 results.log 2>/dev/null || echo "(no history yet)")

    # Ask Claude Code to propose changes
    claude -p "You are an autonomous research agent optimizing a game creature's behavior.

CURRENT BEST SCORE: $CURRENT_SCORE

RECENT EXPERIMENT LOG:
$RECENT_LOG

Read PLAN.md for the full research directions and parameter descriptions.
Read config.json for current parameters.
Read game.py for the simulation logic.

Your task:
1. Analyze what has worked and what hasn't from the log.
2. Form a hypothesis about what change might improve the score.
3. Modify config.json (change 1-2 parameters) OR modify game.py (improve the steering logic).
4. Keep changes small and testable. One idea per experiment.
5. Write a brief comment in results.log about your hypothesis BEFORE the experiment runs.

IMPORTANT: Do NOT modify evaluate.py or run_experiment.sh.
IMPORTANT: The score is (food_collected * 10) - (damage * 2). Maximize it." --allowedTools Edit,Read,Write,Bash

    # Run the ratchet
    bash run_experiment.sh

    echo "Best so far: $(cat baseline_score.txt)"
done

echo ""
echo "=== AUTORESEARCH COMPLETE ==="
echo "Final best score: $(cat baseline_score.txt)"
echo "Total experiments: $NUM_EXPERIMENTS"
echo "Kept improvements: $(grep -c KEPT results.log 2>/dev/null || echo 0)"
echo ""
echo "View full history: cat results.log"
echo "View git log: git log --oneline"
