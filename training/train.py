import yaml
from models.reinforce_agent import TrafficControllerRL
from env.traffic_env import TrafficEnv
from env.traffic_simulation import Vehicle, VehicleManager
from visualization.console_output import print_episode_summary, print_training_summary
from visualization.performance_visualization import plot_metrics
import os

def load_config(config_path='configs/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def train(num_episodes=100, save_path="models/policy.pth"):
    config = load_config()
    env = TrafficEnv(config)
    epsilon_start = config['exploration']['epsilon_start']
    epsilon_min = config['exploration']['epsilon_min']
    epsilon_decay = config['exploration']['epsilon_decay']
    controller = TrafficControllerRL(epsilon_start=epsilon_start, epsilon_min=epsilon_min, epsilon_decay=epsilon_decay)
    rewards = []
    epsilons = []
    timing_violations_list = []
    correct_timings_list = []
    prev_total_reward = None

    for episode in range(num_episodes):
        state = env.reset()
        done = False
        total_reward = 0
        timing_violations = 0
        correct_timings = 0
        reasons = []

        while not done:
            action, _ = controller.select_action(state, training=True)
            state, reward, done, info = env.step(action)
            total_reward += reward
            timing_violations += info.get('timing_violation', 0)
            correct_timings += info.get('correct_timing', 0)
            if 'reasons' in info and info['reasons']:
                reasons = info['reasons']
        controller.decay_epsilon_after_episode(total_reward)
        rewards.append(total_reward)
        epsilons.append(controller.epsilon)
        timing_violations_list.append(timing_violations)
        correct_timings_list.append(correct_timings)

        if prev_total_reward is None or total_reward > 0 and total_reward < prev_total_reward + 50:
            performance = "NEUTRAL"
        elif total_reward > prev_total_reward + 50 and total_reward > 0:
            performance = "GOOD"
        elif total_reward < 0:
            performance = "BAD"
        else:
            performance = "NEUTRAL"
        prev_total_reward = total_reward
        total_timings = timing_violations + correct_timings
        timing_accuracy = 100.0 * correct_timings / total_timings if total_timings else 0.0

        print_episode_summary(
            episode, total_reward, performance,
            timing_violations, correct_timings, timing_accuracy,
            controller.epsilon, reasons
        )

    print_training_summary(
        num_episodes, sum(rewards), sum(timing_violations_list), sum(correct_timings_list)
    )

    plot_metrics(rewards, epsilons)

    # Save the trained policy
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    controller.save(save_path)