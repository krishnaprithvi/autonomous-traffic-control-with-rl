import matplotlib.pyplot as plt

def plot_metrics(rewards, epsilons):
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2,2,1)
    plt.plot(rewards)
    plt.title("Rewards vs Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("Reward")
    plt.grid(True)
    
    plt.subplot(2,2,2)
    plt.plot(epsilons)
    plt.title("Exploration Rate (epsilon) vs Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("Epsilon")
    plt.grid(True)
    
    # Calculate moving average of rewards
    window_size = 5
    if len(rewards) >= window_size:
        moving_avg = [sum(rewards[i:i+window_size])/window_size 
                     for i in range(len(rewards)-window_size+1)]
        plt.subplot(2,2,3)
        plt.plot(range(window_size-1, len(rewards)), moving_avg)
        plt.title(f"Moving Average Reward")
        plt.xlabel("Epoch")
        plt.ylabel("Average Reward")
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_metrics.png')
    plt.show()