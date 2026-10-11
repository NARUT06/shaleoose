"""Mini-project: Smart Irrigation System (ps01/irrigation.py).

Environment: Field (weather, soil dynamics).
Agent: SmartIrrigator with perceive / decide / act / learn.
Knowledge: weather forecast (80% accurate) -> skip irrigation if rain expected.
Noise handling: complementary filter m_hat = pred + k*(z - pred).
Adaptation: moisture target rises after stress days, decays when safe.

Comparison: fixed timer (0.12 every 2nd day) vs smart, 90 days, >=20 seeds.
Metrics: total water, stress days (moisture<0.35), pump-on days.
"""
import numpy as np

STRESS_T = 0.35
AVG_EVAP = 0.055
RAIN_AMOUNT = 0.15


class Field:
    """Environment: soil moisture changes with weather and irrigation."""

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.moisture = 0.55
        self.day = 0

    def weather(self):
        return {"heat": self.rng.uniform(0.02, 0.09),
                "rain": self.rng.choice([0, RAIN_AMOUNT], p=[0.85, 0.15])}

    def step(self, irrigation, w):
        self.moisture = min(1.0, self.moisture - w["heat"] + w["rain"] + irrigation)
        self.day += 1
        return self.moisture


def make_forecast(actual_rain, rng, accuracy=0.8):
    """80%-accurate binary rain forecast: with prob. `accuracy` report truth,
    otherwise report the opposite. Returns 0 or RAIN_AMOUNT (expected)."""
    rain_today = actual_rain > 0
    if rng.random() < accuracy:
        return RAIN_AMOUNT if rain_today else 0.0
    return 0.0 if rain_today else RAIN_AMOUNT


class SmartIrrigator:
    """Agent with perceive-decide-act-learn loop."""

    def __init__(self, target=0.55, k=0.5, sigma=0.10, deadband=0.01):
        self.target = target      # adaptive moisture target
        self.k = k                # filter gain
        self.sigma = sigma        # assumed sensor noise std
        self.deadband = deadband
        self.m_hat = 0.55         # moisture estimate
        self.last_irr = 0.0
        self.stress_streak = 0
        self.safe_streak = 0

    def perceive(self, field, forecast, rng):
        """Noisy soil sensor + forecast as knowledge."""
        z = field.moisture + rng.normal(0, self.sigma)
        pred = self.m_hat - AVG_EVAP + self.last_irr  # rain unknown in prediction
        self.m_hat = pred + self.k * (z - pred)
        return {"m_hat": self.m_hat, "forecast_rain": forecast}

    def decide(self, percept):
        """Rule: fill deficit to target; discount expected rain (conservative)."""
        deficit = self.target - percept["m_hat"]
        if percept["forecast_rain"] > 0:
            deficit -= 0.05  # expected rain 0.15 * 0.8 accuracy, minus safety margin
        if deficit < self.deadband:
            return 0.0
        return max(0.0, deficit) * 0.9

    def act(self, field, weather, irrigation):
        self.last_irr = irrigation
        return field.step(irrigation, weather)

    def learn(self, true_moisture):
        """Adapt target from feedback: stress -> raise target; long safe run -> lower."""
        if true_moisture < STRESS_T:
            self.stress_streak += 1
            self.safe_streak = 0
            self.target = min(0.60, self.target + 0.02)
        else:
            self.safe_streak += 1
            self.stress_streak = 0
            if self.safe_streak >= 15:
                self.target = max(0.45, self.target - 0.01)
                self.safe_streak = 0


def run_episode(seed=0, days=90, sigma=0.10, controller="smart"):
    rng = np.random.default_rng(seed + 10_000)
    field = Field(seed=seed)
    agent = SmartIrrigator(sigma=sigma)
    water, stress, pump_days = 0.0, 0, 0
    for day in range(days):
        w = field.weather()
        forecast = make_forecast(w["rain"], rng, accuracy=0.8)
        if controller == "smart":
            percept = agent.perceive(field, forecast, rng)
            irr = agent.decide(percept)
            agent.act(field, w, irr)
            agent.learn(field.moisture)
        else:  # fixed timer baseline
            irr = 0.12 if day % 2 == 0 else 0.0
            field.step(irr, w)
        water += irr
        stress += field.moisture < STRESS_T
        pump_days += irr > 1e-9
    return water, stress, pump_days


def compare(n_seeds=20, days=90, sigma=0.10):
    base = np.array([run_episode(s, days, sigma, "fixed") for s in range(n_seeds)])
    smart = np.array([run_episode(s, days, sigma, "smart") for s in range(n_seeds)])
    print(f"90 days, {n_seeds} seeds, sensor sigma={sigma}, forecast accuracy=80%")
    print(f"{'controller':<12} | {'mean water':>10} | {'mean stress':>11} | {'mean pump-days':>14}")
    for name, res in [("fixed timer", base), ("smart", smart)]:
        print(f"{name:<12} | {res[:, 0].mean():10.2f} | {res[:, 1].mean():11.2f} | {res[:, 2].mean():14.2f}")
    print(f"\nWater saved: {(base[:,0].mean()-smart[:,0].mean())/base[:,0].mean():.1%} | "
          f"stress change: {smart[:,1].mean()-base[:,1].mean():+.2f} days | "
          f"pump-days change: {smart[:,2].mean()-base[:,2].mean():+.1f}")
    return base, smart


if __name__ == "__main__":
    compare(20, 90, 0.10)
