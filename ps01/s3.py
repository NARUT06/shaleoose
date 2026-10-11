"""S3 - Evaluating an intelligent system: effectiveness, efficiency, robustness."""
import numpy as np


def feedback(moisture, target=0.50):
    return max(0.0, target - moisture) * 0.9


def run(noise, days=60, seed=0):
    rng = np.random.default_rng(seed)
    m, water, stress = 0.55, 0.0, 0
    for _ in range(days):
        sensed = m + rng.normal(0, noise)  # sensor noise
        irr = feedback(sensed)
        m = min(1.0, m - rng.uniform(0.02, 0.09) + irr)
        water += irr
        stress += m < 0.35
    return water, stress


if __name__ == "__main__":
    print("noise | mean water | mean stress days (20 runs each)")
    for noise in [0.0, 0.05, 0.10, 0.20]:
        res = np.array([run(noise, seed=s) for s in range(20)])
        print(f"{noise:5.2f} | {res[:, 0].mean():10.2f} | {res[:, 1].mean():6.2f}")
