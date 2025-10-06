import numpy as np

class TrafficEnv:
    def __init__(self, config):
        self.num_lanes = 4
        self.num_actions = 2
        self.state = np.zeros(self.num_lanes + 3)
        self.config = config
        self.green_duration = self.config['phase_durations']['VERT_GREEN']
        self.yellow_duration = self.config['phase_durations']['VERT_YELLOW']
        self.red_duration = self.config['phase_durations']['VERT_RED']
        self.time_step = 0
        self.light_timer = 0
        self.current_phase = "horizontal_green"
        self.collision_count = 0
        self.phase_just_changed = False
        self.previous_action = 0
        self.cars_crossed = 0
        self.total_wait_time = 0
        self.timing_violations = 0
        self.correct_timing_count = 0
        self.consecutive_correct_timings = 0

        self.valid_transitions = {
            "horizontal_green": ["horizontal_yellow"],
            "horizontal_yellow": ["vertical_green"],
            "vertical_green": ["vertical_yellow"],
            "vertical_yellow": ["horizontal_green"]
        }
        self.phase_durations = {
            "horizontal_green": self.green_duration,
            "horizontal_yellow": self.yellow_duration,
            "vertical_green": self.green_duration,
            "vertical_yellow": self.yellow_duration
        }

    def step(self, action):
        self.time_step += 1
        self.light_timer += 1
        reward = 0
        reasons = []

        horizontal_density = (self.state[0] + self.state[2]) / 2
        vertical_density = (self.state[1] + self.state[3]) / 2

        next_phase = None
        timing_violation = False
        correct_timing = False

        phase_complete = self.light_timer >= self.phase_durations[self.current_phase]
        if action == 1:
            if phase_complete:
                if self.current_phase == "horizontal_green":
                    next_phase = "horizontal_yellow"
                elif self.current_phase == "horizontal_yellow":
                    next_phase = "vertical_green"
                elif self.current_phase == "vertical_green":
                    next_phase = "vertical_yellow"
                elif self.current_phase == "vertical_yellow":
                    next_phase = "horizontal_green"
                reward += 20
                reasons.append("Correct phase transition (+20)")
                self.consecutive_correct_timings += 1
                correct_timing = True
            else:
                timing_violation = True
                self.timing_violations += 1
                reward -= 10
                reasons.append("Timing violation (-10 for red/yellow)")
                self.consecutive_correct_timings = 0
        elif action == 0:
            if phase_complete:
                timing_violation = True
                self.timing_violations += 1
                reward -= 5
                reasons.append("Timing violation (-5 for yellow)")
                self.consecutive_correct_timings = 0
            else:
                reward += 2
                reasons.append("Correct timing (+2)")
                correct_timing = True

        # Forced transition penalty
        if self.light_timer >= 2 * self.phase_durations[self.current_phase]:
            if self.current_phase == "horizontal_green":
                next_phase = "horizontal_yellow"
            elif self.current_phase == "horizontal_yellow":
                next_phase = "vertical_green"
            elif self.current_phase == "vertical_green":
                next_phase = "vertical_yellow"
            elif self.current_phase == "vertical_yellow":
                next_phase = "horizontal_green"
            reward -= 15
            reasons.append("Incorrect phase transition (-15 forced)")
            self.consecutive_correct_timings = 0

        if next_phase and next_phase in self.valid_transitions.get(self.current_phase, []):
            self.current_phase = next_phase
            self.light_timer = 0
            self.phase_just_changed = True

        # Traffic state update
        if self.current_phase == "horizontal_green":
            self.state[0] = max(0, self.state[0] - np.random.randint(5, 15))
            self.state[2] = max(0, self.state[2] - np.random.randint(5, 15))
            self.state[1] = min(100, self.state[1] + np.random.randint(0, 5))
            self.state[3] = min(100, self.state[3] + np.random.randint(0, 5))
            if horizontal_density > 40:
                reward += 2
                reasons.append("Bonus for clearing horizontal traffic (+2)")
        elif self.current_phase == "vertical_green":
            self.state[1] = max(0, self.state[1] - np.random.randint(5, 15))
            self.state[3] = max(0, self.state[3] - np.random.randint(5, 15))
            self.state[0] = min(100, self.state[0] + np.random.randint(0, 5))
            self.state[2] = min(100, self.state[2] + np.random.randint(0, 5))
            if vertical_density > 40:
                reward += 2
                reasons.append("Bonus for clearing vertical traffic (+2)")

        self.state[4] = 1 if self.current_phase in ["horizontal_green", "horizontal_yellow"] else 0
        self.state[5] = self.light_timer
        self.state[6] = self.light_timer / self.phase_durations[self.current_phase]

        total_wait_time = np.sum(self.state[:4])
        self.total_wait_time += total_wait_time

        wait_time_penalty = -0.05 * min(total_wait_time, 100)
        reward += wait_time_penalty
        reasons.append(f"Waiting vehicles penalty ({wait_time_penalty:.1f})")

        balance_factor = 1 - abs(horizontal_density - vertical_density) / 100
        reward += balance_factor * 2
        reasons.append(f"Balance reward ({balance_factor * 2:.1f})")

        if self.consecutive_correct_timings >= 3:
            reward += 5
            reasons.append("Bonus for streak (+5)")

        self.state[:4] = np.clip(self.state[:4], 0, 100)
        reward = np.clip(reward, -50, 50)
        done = self.time_step >= self.config['environment']['max_timesteps']
        info = {
            "phase": self.current_phase,
            "timer": self.light_timer,
            "timing_violation": timing_violation,
            "correct_timing": correct_timing,
            "consecutive_correct": self.consecutive_correct_timings,
            "reasons": "; ".join(reasons)
        }
        return self.state, reward, done, info

    def reset(self):
        self.state = np.zeros(self.num_lanes + 3)
        self.state[:4] = np.random.randint(0, 20, size=(self.num_lanes,))
        self.time_step = 0
        self.light_timer = 0
        self.current_phase = "horizontal_green"
        self.collision_count = 0
        self.cars_crossed = 0
        self.total_wait_time = 0
        self.timing_violations = 0
        self.correct_timing_count = 0
        self.phase_just_changed = False
        self.consecutive_correct_timings = 0
        return self.state

    def render(self):
        print(f"Traffic State: {self.state[:4]}, Phase: {self.current_phase}, Timer: {self.light_timer}")