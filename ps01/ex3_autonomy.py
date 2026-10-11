"""Exercise 3 - Levels of autonomy (thermostat L0-L3)."""
SAFE_MIN, SAFE_MAX = 10.0, 35.0


def thermostat(level, temp, target=22.0, human_available=True):
    """One function, behaviour depends on autonomy level L0-L3.

    L0 manual:     only report, never act.
    L1 assisted:   suggest an action, human executes.
    L2 partial:    act autonomously only if safe, else ask confirmation.
    L3 conditional:act autonomously if safe; if unsafe request takeover,
                   or enter safe mode if no human is available.
    """
    safe = SAFE_MIN <= temp <= SAFE_MAX
    if abs(temp - target) < 0.5:
        action = "OFF (already comfortable)"
    elif temp > target:
        action = "COOL"
    else:
        action = "HEAT"

    if level == 0:
        return f"L0 MANUAL: temp={temp}C. No action taken. Suggestion for human: {action}."
    if level == 1:
        return f"L1 ASSISTED: temp={temp}C. Suggested action: {action}. Waiting for human to execute."
    if level == 2:
        if safe:
            return f"L2 PARTIAL: temp={temp}C (safe). Acting autonomously (pending confirmation): {action}."
        return (f"L2 PARTIAL: temp={temp}C (OUT OF SAFE RANGE [{SAFE_MIN},{SAFE_MAX}]). "
                f"Action {action} requires explicit human confirmation.")
    if level == 3:
        if safe:
            return f"L3 CONDITIONAL: temp={temp}C (safe). Full autonomy: {action}."
        if human_available:
            return (f"L3 CONDITIONAL: temp={temp}C UNSAFE! Requesting HUMAN TAKEOVER "
                    f"(outside [{SAFE_MIN},{SAFE_MAX}]C). Holding last safe action.")
        return (f"L3 CONDITIONAL: temp={temp}C UNSAFE and NO HUMAN available. "
                f"Entering SAFE MODE (system OFF + alarm).")
    raise ValueError("level must be 0-3")


if __name__ == "__main__":
    for temp in [22, 27, 38]:
        print(f"=== temp = {temp} C ===")
        for lvl in [0, 1, 2, 3]:
            print(" ", thermostat(lvl, temp, human_available=True))
        print()
    print("=== L3 with no human available, temp=38 ===")
    print(" ", thermostat(3, 38, human_available=False))
