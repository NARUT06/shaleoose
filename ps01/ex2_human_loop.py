"""Exercise 2 - Human-in-the-loop approval gate.

Smart pump proposes (volume, confidence). Risk score in [0,1]:
    risk = w_v * (volume / max_volume) + w_c * (1 - confidence)
Low risk -> auto-execute. High risk -> escalate to simulated farmer.
"""
import numpy as np

W_V = 0.6          # weight of volume term
W_C = 0.4          # weight of uncertainty term
THRESHOLD = 0.5    # escalation threshold (design parameter)
MAX_VOL = 0.20     # max plausible irrigation volume per proposal


def risk_score(volume, confidence):
    """Both terms in [0,1]; convex combination stays in [0,1]."""
    v_term = min(1.0, max(0.0, volume / MAX_VOL))
    c_term = 1.0 - min(1.0, max(0.0, confidence))
    return W_V * v_term + W_C * c_term


def simulated_farmer(volume, confidence, rng):
    """Farmer is cautious: rejects big low-confidence requests more often."""
    r = risk_score(volume, confidence)
    # approval probability drops with risk: e.g. 0.95 at r=0 -> 0.25 at r=1
    p_approve = 0.95 - 0.70 * r
    return rng.random() < p_approve


def make_proposals(n=20, seed=0):
    """Fixed proposal set so threshold comparison is fair."""
    rng = np.random.default_rng(seed)
    return [(float(rng.uniform(0.0, 0.20)), float(rng.uniform(0.5, 1.0))) for _ in range(n)]


def run(n=20, seed=0, threshold=THRESHOLD, proposals=None, farmer_seed=99):
    rng = np.random.default_rng(farmer_seed)
    if proposals is None:
        proposals = make_proposals(n, seed)
    auto, escalated, approved, rejected = 0, 0, 0, 0
    for i, (volume, confidence) in enumerate(proposals):
        r = risk_score(volume, confidence)
        if r < threshold:
            auto += 1
            decision = "AUTO"
        else:
            escalated += 1
            ok = simulated_farmer(volume, confidence, rng)
            approved += ok
            rejected += (not ok)
            decision = "APPROVED" if ok else "REJECTED"
        print(f"proposal {i:2d}: vol={volume:.3f} conf={confidence:.2f} risk={r:.2f} -> {decision}")
    print(f"\nTotal={n} auto={auto} escalated={escalated} "
          f"approved={approved} rejected={rejected} escalation_rate={escalated/n:.1%}")
    return escalated / n


if __name__ == "__main__":
    props = make_proposals(20, seed=1)
    print(f"--- threshold = {THRESHOLD} ---")
    run(20, seed=1, proposals=props)
    print("\n--- threshold sensitivity (same 20 proposals) ---")
    for th in [0.3, 0.5, 0.7]:
        rate = run(20, seed=1, threshold=th, proposals=props)
        print(f"threshold={th:.1f} -> escalation {rate:.1%}\n")
    print("Discussion: raising the threshold lowers escalation (less farmer load, more autonomy)")
    print("but risky actions execute blindly. Lowering it is safer but causes alert fatigue.")
