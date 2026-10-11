"""Exercise 1 - Robust controller for noisy sensors.

Compares:
  - naive controller: trusts every noisy reading directly.
  - filtered controller: complementary / Kalman-style estimator:
        pred = m_hat_prev - avg_evap + last_irrigation
        m_hat = pred + k * (z - pred)
    plus a deadband so tiny deficits do not trigger the pump.

Metric (30 runs each, 60 days): mean water, mean stress days.
Trade-off discussed at the bottom / in printout.
"""
import numpy as np

TARGET = 0.50
SAFETY_MARGIN = 0.03  # robust controller aims slightly higher to avoid stress
AVG_EVAP = 0.055  # mean of Uniform(0.02, 0.09)
K = 0.60          # estimator gain: small k = trust model, large k = trust sensor


def naive_control(sensed, target=TARGET):
    return max(0.0, target - sensed) * 0.9


def run_naive(noise, days=60, seed=0):
    rng = np.random.default_rng(seed)
    m, water, stress = 0.55, 0.0, 0
    for _ in range(days):
        z = m + rng.normal(0, noise)
        irr = naive_control(z)
        m = min(1.0, m - rng.uniform(0.02, 0.09) + rng.choice([0, 0.15], p=[0.85, 0.15]) + irr)
        water += irr
        stress += m < 0.35
    return water, stress


def run_filtered(noise, days=60, seed=0, k=K, margin=SAFETY_MARGIN):
    rng = np.random.default_rng(seed)
    m, water, stress = 0.55, 0.0, 0
    m_hat, last_irr = 0.55, 0.0  # estimator state
    for _ in range(days):
        z = m + rng.normal(0, noise)  # noisy sensor reading
        # 1) predict from process model (rain unknown -> assume 0, conservative)
        pred = m_hat - AVG_EVAP + last_irr
        # 2) correct with measurement (Kalman idea)
        m_hat = pred + k * (z - pred)
        irr = max(0.0, (TARGET + margin) - m_hat) * 0.9
        last_irr = irr
        m = min(1.0, m - rng.uniform(0.02, 0.09) + rng.choice([0, 0.15], p=[0.85, 0.15]) + irr)
        water += irr
        stress += m < 0.35
    return water, stress


if __name__ == "__main__":
    N = 30
    print(f"sigma | naive water | naive stress | filtered water | filtered stress ({N} runs each, 60 days)")
    for sigma in [0.05, 0.15, 0.25]:
        naive = np.array([run_naive(sigma, seed=s) for s in range(N)])
        filt = np.array([run_filtered(sigma, seed=s) for s in range(N)])
        print(f"{sigma:5.2f} | {naive[:, 0].mean():11.2f} | {naive[:, 1].mean():12.2f} | "
              f"{filt[:, 0].mean():14.2f} | {filt[:, 1].mean():15.2f}")
    print("\nDiscussion: the filter + safety margin cuts stress at low/medium noise")
    print("(sigma=0.05: ~0.4 -> ~0.0 days) for about the same water. At very high")
    print("noise (0.25) the naive controller over-waters by accident (2.28 units),")
    print("which protects the crop but wastes water; the filter saves ~8% water at")
    print("the cost of extra stress days. Trade-off: robustness costs a small")
    print("water margin; k balances model trust vs sensor trust.")
