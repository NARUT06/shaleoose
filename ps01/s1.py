"""S1 - Automation vs. intelligence: fixed-timer vs. feedback irrigation."""
import numpy as np


def simulate(controller, days=30, seed=1):
    rng = np.random.default_rng(seed)
    moisture, water, stress = 0.55, 0.0, 0
    for day in range(days):
        heat = rng.uniform(0.02, 0.09)  # daily evaporation (weather)
        rain = rng.choice([0, 0.15], p=[0.85, 0.15])
        irrigation = controller(day, moisture)  # decision
        moisture = min(1.0, moisture - heat + rain + irrigation)
        water += irrigation
        stress += moisture < 0.35  # crop stress if soil too dry
    return water, stress


def fixed_timer(day, moisture):  # automation: blind schedule
    return 0.12 if day % 2 == 0 else 0.0


def feedback(day, moisture, target=0.50):  # intelligence: sense -> decide
    return max(0.0, target - moisture) * 0.9


if __name__ == "__main__":
    for name, ctrl in [("Fixed timer", fixed_timer), ("Feedback", feedback)]:
        w, s = simulate(ctrl)
        print(f"{name:12s} water used = {w:5.2f} stress days = {s}")
