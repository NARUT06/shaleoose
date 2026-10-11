# PS01 Report — Smart Irrigation System (2-page summary)

## 1. Architecture (perceive–decide–act–learn)

```
[Field: weather(heat,rain) + soil] --true moisture--> [Sensor: +N(0,sigma)] --z--> |
[Forecast 80%] -------------------------------------------------------------------> | PERCEIVE: pred = m_hat - 0.055 + last_irr; m_hat = pred + k(z-pred)
                                                                                      DECIDE: deficit = target - m_hat - (0.05 if rain expected); irr = 0.9*deficit
[Pump] <-- ACT: field.step(irr) <-- LEARN: stress -> target+=0.02 (max 0.60); 15 safe days -> target-=0.01
```

Files: `ps01/s1.py, s2.py, s3.py` (solved), `ex1_robust.py, ex2_human_loop.py, ex3_autonomy.py`, `irrigation.py` (mini-project).

## 2. Twelve-element case study

1. **Problem:** replace fixed timer (wastes water) with controller using less water and ~0 stress over 90 days.
2. **Environment:** simulated field; moisture -= heat(0.02–0.09) + rain(0/0.15, p=0.15) + irrigation; partially observable, stochastic.
3. **Sensors:** noisy soil-moisture probe `z = m + N(0,0.10)`; binary rain forecast (80% accurate).
4. **Actuators:** pump, continuous volume 0–~0.2/day; pump-on day counted for energy.
5. **Perception:** complementary/Kalman-style filter `m_hat = pred + k(z-pred)`, k=0.5; forecast as second percept.
6. **Decision:** proportional refill `0.9*(target-m_hat)`, minus 0.05 if rain expected; deadband 0.01 saves pump cycles.
7. **Action:** `Field.step(irr, weather)`; clipped to [0,1] moisture.
8. **Learning:** parameter adaptation — target 0.55 rises +0.02 on any stress day, decays −0.01 after 15 safe days.
9. **Knowledge:** `P(rain)=0.15`, mean evap 0.055, forecast reliability 0.8 encoded in 0.05 discount (not full 0.15).
10. **Autonomy:** L2–L3: acts alone when safe; farmer/failsafe analogue is Ex2 approval gate and Ex3 safe-mode pattern.
11. **Evaluation:** 20 seeds, 90 days: effectiveness (stress days), efficiency (water, pump-days), robustness (sigma sweep in Ex1).
12. **Ethics:** water is shared in Assiut; under-irrigation risks farmer livelihood, over-irrigation wastes aquifer + energy; forecast/sensor failures must fail-safe (slight over-water bias), logs must be auditable, farmer keeps override.

## 3. Results

| controller | mean water (90d) | mean stress days | mean pump-days |
|---|---|---|---|
| fixed timer (0.12 every 2nd day) | 5.40 | 0.00 | 45.0 |
| smart (filter + forecast + adapt) | 2.82 | 1.10 | 44.2 |
| saving | **−47.8% water** | +1.1 d stress | −0.8 d pump |

Supporting: Ex1 (30 runs, 60 d): sigma=0.05 naive 1.92/0.43 vs filtered 1.94/0.03; sigma=0.25 naive 2.28/0.27 vs filtered 2.09/0.80 — filter wins at low noise, saves water at high noise for small stress cost. Ex2: risk=`0.6*vol/0.2+0.4*(1-conf)`, threshold 0.5 → 25% escalation (0.3→60%, 0.7→0%). Ex3: L0–L2 suggest/confirm; L3 at 38 °C requests takeover, safe-mode if no human.

## 4. Limitations

- Forecast is binary and memoryless; 20% false alarms still cause skipped irrigation → residual ~1 stress day.
- Estimator assumes constant evap 0.055; heat waves bias it; k fixed instead of variance-adaptive (full Kalman).
- No rain sensor fusion (rain added directly to soil but predictor assumes 0).
- Evaluation is simulation-only; real soil, pump delays, and forecast bias differ.
- Ethics: needs real farmer override + water-quota guard before deployment.
