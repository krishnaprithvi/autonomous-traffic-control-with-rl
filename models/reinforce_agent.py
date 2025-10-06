import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import yaml
from env.traffic_simulation import Phase

def load_config(config_path='configs/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class PolicyNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(7, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 4),
            nn.Softmax(dim=-1)
        )
    def forward(self, x):
        return self.net(x)

class TrafficControllerRL:
    def __init__(self, epsilon_start=1.0, epsilon_min=0.05, epsilon_decay=0.95, reward_based_decay=False):
        config = load_config()
        self.Phase = Phase
        self.PHASE_DURATIONS = {
            0: config['phase_durations']['VERT_GREEN'],
            1: config['phase_durations']['VERT_YELLOW'],
            2: config['phase_durations']['HORZ_GREEN'],
            3: config['phase_durations']['HORZ_YELLOW']
        }
        self.phase_timer = 0
        self.current_phase = 0
        self.consecutive_correct_timings = 0
        self.policy = PolicyNetwork()
        self.optimizer = optim.Adam(self.policy.parameters(), lr=config['rl']['learning_rate'])
        self.gamma = config['rl']['gamma']
        self.rewards_history = []
        self.log_probs = []
        self.state_history = []
        self.last_phase = None
        self.epsilon_start = epsilon_start
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.episode_count = 0
        self.reward_based_decay = reward_based_decay
        self.reward_threshold = 100
        self.reward_increment = 50

    def get_state(self, vehicle_manager):
        wait_counts = vehicle_manager.get_wait_counts()
        normalized_counts = [
            min(wait_counts["north"], 100) / 100.0,
            min(wait_counts["south"], 100) / 100.0,
            min(wait_counts["east"], 100) / 100.0,
            min(wait_counts["west"], 100) / 100.0
        ]
        # Phase as integer (0-3)
        phase_feature = float(self.current_phase)
        # Timer as raw value (or normalized)
        timer_feature = float(self.phase_timer)
        # Streak feature (normalized)
        streak_feature = float(self.consecutive_correct_timings)
        # Compose state vector: 4 lanes + phase + timer + streak
        state = np.array(normalized_counts + [phase_feature, timer_feature, streak_feature], dtype=np.float32)
        return torch.from_numpy(state)

    def select_action(self, state, training=True):
        if isinstance(state, np.ndarray):
            state = torch.from_numpy(state).float()
        action_probs = self.policy(state)
        action_probs = torch.clamp(action_probs, min=1e-6)
        if training and random.random() < self.epsilon:
            action = random.randint(0, 3)
            log_prob = torch.log(action_probs[action])
        else:
            m = torch.distributions.Categorical(action_probs)
            action = m.sample()
            log_prob = m.log_prob(action)
            action = action.item()
        return action, log_prob

    def is_valid_phase_transition(self, new_phase):
        if self.current_phase == self.Phase.VERT_GREEN:
            return new_phase == self.Phase.VERT_YELLOW
        elif self.current_phase == self.Phase.VERT_YELLOW:
            return new_phase == self.Phase.HORZ_GREEN
        elif self.current_phase == self.Phase.HORZ_GREEN:
            return new_phase == self.Phase.HORZ_YELLOW
        elif self.current_phase == self.Phase.HORZ_YELLOW:
            return new_phase == self.Phase.VERT_GREEN
        return False

    def update(self, dt, vehicle_manager, training=True):
        self.phase_timer += dt
        if self.phase_timer >= self.PHASE_DURATIONS[self.current_phase]:
            state = self.get_state(vehicle_manager)
            action, log_prob = self.select_action(state, training=training)
            original_action = action
            if not self.is_valid_phase_transition(action):
                if self.current_phase == self.Phase.VERT_GREEN:
                    action = self.Phase.VERT_YELLOW
                elif self.current_phase == self.Phase.VERT_YELLOW:
                    action = self.Phase.HORZ_GREEN
                elif self.current_phase == self.Phase.HORZ_GREEN:
                    action = self.Phase.HORZ_YELLOW
                elif self.current_phase == self.Phase.HORZ_YELLOW:
                    action = self.Phase.VERT_GREEN
                action_probs = self.policy(state)
                action_probs = torch.clamp(action_probs, min=1e-6)
                log_prob = torch.log(action_probs[action])
            self.state_history.append(state)
            self.log_probs.append(log_prob)
            wait_counts = vehicle_manager.get_wait_counts()
            total_waiting = sum(wait_counts.values())
            base_reward = -min(total_waiting, 100) / 10.0
            transition_reward = 20 if self.is_valid_phase_transition(original_action) else -20
            total_reward = base_reward + transition_reward
            self.rewards_history.append(total_reward)
            self.last_phase = self.current_phase
            self.current_phase = action
            self.phase_timer = 0
            if training and len(self.rewards_history) >= 5:
                self.update_policy()

    def update_policy(self):
        R = 0
        returns = []
        for r in self.rewards_history[::-1]:
            R = r + self.gamma * R
            returns.insert(0, R)
        returns = torch.tensor(returns)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        policy_loss = []
        for log_prob, R in zip(self.log_probs, returns):
            policy_loss.append(-log_prob * R)
        self.optimizer.zero_grad()
        policy_loss = torch.stack(policy_loss).sum()
        policy_loss.backward()
        self.optimizer.step()
        self.rewards_history = []
        self.log_probs = []
        self.state_history = []
        if not self.reward_based_decay:
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def decay_epsilon_after_episode(self, last_reward=None):
        self.episode_count += 1
        if self.reward_based_decay and last_reward is not None:
            if self.epsilon > self.epsilon_min and last_reward >= self.reward_threshold:
                self.epsilon = max(self.epsilon - 0.05, self.epsilon_min)
                self.reward_threshold += self.reward_increment
        else:
            self.epsilon = max(self.epsilon_min, self.epsilon_start * (self.epsilon_decay ** self.episode_count))

    def reset(self):
        self.phase_timer = 0
        self.current_phase = self.Phase.VERT_GREEN
        self.last_phase = None

    def save(self, path="models/policy.pth"):
        torch.save(self.policy.state_dict(), path)

    def load(self, path="models/policy.pth"):
        self.policy.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
        self.policy.eval()