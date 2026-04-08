#!/usr/bin/env python3
"""evaluate.py — FIXED. Do not modify. Runs game.py and extracts the scalar metric."""

import subprocess
import sys


def evaluate():
    result = subprocess.run(
        [sys.executable, "game.py"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"ERROR: game.py failed\n{result.stderr}", file=sys.stderr)
        return None

    # Extract score from last line
    for line in reversed(result.stdout.strip().split("\n")):
        if line.startswith("SCORE:"):
            return float(line.split(":")[1].strip())

    print("ERROR: No SCORE line found in output", file=sys.stderr)
    return None


if __name__ == "__main__":
    score = evaluate()
    if score is not None:
        print(f"{score}")
    else:
        sys.exit(1)
