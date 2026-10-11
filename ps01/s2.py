"""S2 - A generic Perceive-Decide-Act-Learn loop (smart classroom lighting)."""
import random


class IntelligentSystem:
    def __init__(self, goal_lux=400):
        self.goal, self.gain, self.memory = goal_lux, 0.5, []

    def perceive(self, env):  # noisy light sensor
        return env["daylight"] + env["lamp"] * 5 + random.gauss(0, 10)

    def decide(self, lux):  # proportional decision
        return self.gain * (self.goal - lux) / 5

    def act(self, env, delta):
        env["lamp"] = min(100, max(0, env["lamp"] + delta))

    def learn(self, error):  # adapt the gain from feedback
        self.memory.append(abs(error))
        if len(self.memory) >= 3 and self.memory[-1] > self.memory[-3]:
            self.gain *= 0.8  # oscillating -> be gentler


if __name__ == "__main__":
    random.seed(0)
    env, agent = {"daylight": 150, "lamp": 0}, IntelligentSystem()
    for t in range(12):
        if t == 6:
            env["daylight"] = 300  # clouds clear: environment changes
        lux = agent.perceive(env)
        agent.act(env, agent.decide(lux))
        agent.learn(agent.goal - lux)
        print(f"t={t:2d} daylight={env['daylight']} lux={lux:6.1f} lamp={env['lamp']:5.1f}% gain={agent.gain:.2f}")
