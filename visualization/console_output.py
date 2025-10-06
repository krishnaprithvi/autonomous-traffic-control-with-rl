def print_episode_summary(
    epoch, reward, performance, timing_violations, correct_timings,
    timing_accuracy, epsilon, reasons
):

    if reasons:
        reason_str = reasons
    else:
        reason_str = "Normal step"

    print(f"\nEpoch: {epoch+1}")
    print(f"\nEpisode Reward: {reward:.2f}")
    print(f"Agent Performance: {performance}")
    print("----------------------------------------")
    print(f"Timing Violations: {timing_violations}, Correct Timings: {correct_timings}")
    print(f"Timing Accuracy: {timing_accuracy:.2f}%, Exploration Rate (ε): {epsilon:.4f}")
    print(f"Reasons: {reason_str}")
    print("----------------------------------------")

def print_training_summary(
    total_episodes, total_reward, total_violations, total_correct
):
    print("\n======= Training Summary =======")
    print(f"Total Episodes: {total_episodes}")
    print(f"Total Cumulative Reward: {total_reward:.2f}")
    print(f"Total Timing Violations: {total_violations}")
    print(f"Total Correct Timings: {total_correct}")
    print("===============================")