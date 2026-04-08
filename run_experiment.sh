#!/bin/bash
# run_experiment.sh — FIXED. Do not modify.
# Runs one experiment, compares to baseline, keeps or reverts.

set -e

# Get current score
SCORE=$(python3 evaluate.py)
if [ $? -ne 0 ]; then
    echo "EXPERIMENT FAILED — reverting"
    cp baseline.json config.json
    git checkout -- game.py 2>/dev/null || true
    exit 1
fi

# Read baseline score
BASELINE=$(cat baseline_score.txt 2>/dev/null || echo "-999999")

# Compare (using Python for float comparison)
KEEP=$(python3 -c "print('yes' if $SCORE > $BASELINE else 'no')")

TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)

if [ "$KEEP" = "yes" ]; then
    echo "$TIMESTAMP | score=$SCORE | baseline=$BASELINE | KEPT" | tee -a results.log
    # Update baseline
    cp config.json baseline.json
    echo "$SCORE" > baseline_score.txt
    git add -A && git commit -m "experiment: score=$SCORE (improvement from $BASELINE)" --quiet
else
    echo "$TIMESTAMP | score=$SCORE | baseline=$BASELINE | REVERTED" | tee -a results.log
    # Revert to baseline
    cp baseline.json config.json
    git checkout -- game.py 2>/dev/null || true
fi
