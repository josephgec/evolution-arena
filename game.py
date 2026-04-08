#!/usr/bin/env python3
"""game.py — Arena simulation engine. Agent may modify creature behavior logic."""

import json
import random
import math
import sys


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def run_game(config, seed=42):
    random.seed(seed)

    # Arena dimensions
    WIDTH, HEIGHT = 600, 400
    TICKS = 600

    # Creature state
    cx, cy = WIDTH / 2, HEIGHT / 2
    heading = random.uniform(0, 2 * math.pi)

    # Parameters from config
    speed = max(0.5, min(6.0, config["speed"]))
    turn_rate = max(0.5, min(8.0, config["turn_rate"]))
    vision_range = max(30, min(250, config["vision_range"]))
    food_attraction = max(0.0, min(10.0, config["food_attraction"]))
    hazard_avoidance = max(0.0, min(10.0, config["hazard_avoidance"]))
    exploration_bias = max(0.0, min(10.0, config["exploration_bias"]))

    # Spawn 12 food items
    food = []
    for _ in range(12):
        food.append({
            "x": random.uniform(20, WIDTH - 20),
            "y": random.uniform(20, HEIGHT - 20),
            "alive": True,
        })

    # Spawn 6 hazard zones
    hazards = []
    for _ in range(6):
        hazards.append({
            "x": random.uniform(40, WIDTH - 40),
            "y": random.uniform(40, HEIGHT - 40),
            "radius": random.uniform(18, 32),
        })

    food_collected = 0
    total_damage = 0.0
    eaten_food = []  # (index, tick_eaten) for respawn tracking

    for tick in range(TICKS):
        # --- Food respawn every 120 ticks ---
        if tick > 0 and tick % 120 == 0:
            for idx, tick_eaten in list(eaten_food):
                if random.random() < 0.6:
                    food[idx]["x"] = random.uniform(20, WIDTH - 20)
                    food[idx]["y"] = random.uniform(20, HEIGHT - 20)
                    food[idx]["alive"] = True
                    eaten_food.remove((idx, tick_eaten))

        # --- Find nearest visible food ---
        nearest_food = None
        nearest_food_dist = float("inf")
        for f in food:
            if not f["alive"]:
                continue
            dx = f["x"] - cx
            dy = f["y"] - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < vision_range and dist < nearest_food_dist:
                nearest_food = f
                nearest_food_dist = dist

        # --- Find nearest visible hazard (vision_range * 0.8) ---
        nearest_hazard = None
        nearest_hazard_dist = float("inf")
        hazard_vision = vision_range * 0.8
        for h in hazards:
            dx = h["x"] - cx
            dy = h["y"] - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < hazard_vision and dist < nearest_hazard_dist:
                nearest_hazard = h
                nearest_hazard_dist = dist

        # --- Steering logic ---
        # Base: wander
        target_heading = heading + random.gauss(0, 0.3) * (exploration_bias / 5.0)

        # Blend toward food (using angular difference to handle wrapping)
        if nearest_food is not None:
            food_angle = math.atan2(nearest_food["y"] - cy, nearest_food["x"] - cx)
            weight = food_attraction / 10.0
            diff = math.atan2(math.sin(food_angle - target_heading), math.cos(food_angle - target_heading))
            target_heading += weight * diff

        # Blend away from hazard (using angular difference to handle wrapping)
        if nearest_hazard is not None:
            hazard_angle = math.atan2(nearest_hazard["y"] - cy, nearest_hazard["x"] - cx)
            away_angle = hazard_angle + math.pi  # opposite direction
            weight = hazard_avoidance / 10.0
            diff = math.atan2(math.sin(away_angle - target_heading), math.cos(away_angle - target_heading))
            target_heading += weight * diff

        # --- Wall avoidance ---
        wall_margin = 40
        wall_dx = 0.0
        wall_dy = 0.0
        if cx < wall_margin:
            wall_dx += (wall_margin - cx) / wall_margin
        if cx > WIDTH - wall_margin:
            wall_dx -= (cx - (WIDTH - wall_margin)) / wall_margin
        if cy < wall_margin:
            wall_dy += (wall_margin - cy) / wall_margin
        if cy > HEIGHT - wall_margin:
            wall_dy -= (cy - (HEIGHT - wall_margin)) / wall_margin

        if wall_dx != 0 or wall_dy != 0:
            wall_angle = math.atan2(wall_dy, wall_dx)
            wall_weight = min(1.0, math.sqrt(wall_dx**2 + wall_dy**2)) * 0.6
            diff = math.atan2(math.sin(wall_angle - target_heading), math.cos(wall_angle - target_heading))
            target_heading += wall_weight * diff

        # Clamp angular change by turn_rate (in degrees, convert to radians)
        turn_rate_rad = math.radians(turn_rate)
        delta = target_heading - heading
        # Normalize to [-pi, pi]
        delta = math.atan2(math.sin(delta), math.cos(delta))
        delta = max(-turn_rate_rad, min(turn_rate_rad, delta))
        heading += delta

        # --- Move ---
        cx += math.cos(heading) * speed
        cy += math.sin(heading) * speed

        # Bounce off walls
        if cx < 0:
            cx = -cx
            heading = math.pi - heading
        elif cx > WIDTH:
            cx = 2 * WIDTH - cx
            heading = math.pi - heading
        if cy < 0:
            cy = -cy
            heading = -heading
        elif cy > HEIGHT:
            cy = 2 * HEIGHT - cy
            heading = -heading

        # Clamp position
        cx = max(0, min(WIDTH, cx))
        cy = max(0, min(HEIGHT, cy))

        # --- Collect food (radius 14) ---
        for i, f in enumerate(food):
            if not f["alive"]:
                continue
            dx = f["x"] - cx
            dy = f["y"] - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 14:
                f["alive"] = False
                food_collected += 1
                eaten_food.append((i, tick))

        # --- Hazard damage ---
        for h in hazards:
            dx = h["x"] - cx
            dy = h["y"] - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < h["radius"]:
                total_damage += 0.5

    final_score = (food_collected * 10) - (total_damage * 2)
    return final_score


def main():
    config = load_config()
    seeds = [42, 123, 456, 789, 1024]
    scores = [run_game(config, s) for s in seeds]
    avg = sum(scores) / len(scores)
    # Print individual scores for debugging
    for i, s in enumerate(scores):
        print(f"  seed {seeds[i]}: score={s}", file=sys.stderr)
    # Final metric on stdout — this is what the ratchet reads
    print(f"SCORE: {avg:.1f}")


if __name__ == "__main__":
    main()
