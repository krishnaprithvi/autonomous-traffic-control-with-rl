# 4-Way Intersection Traffic Control with Reinforcement Learning
A Python project that uses reinforcement learning to optimize traffic light phases at a four-way intersection, aiming to reduce congestion and waiting times through adaptive signal control.


# Overview
This project simulates a four-way traffic intersection and trains a reinforcement learning (RL) agent to control the traffic lights. The agent learns to minimize vehicle waiting times and improve the flow of traffic by dynamically adjusting signal phases based on real-time vehicle queue data.


# Features
1. Custom Traffic Environment: Simulates realistic vehicle movements and traffic light phases.
2. Reinforcement Learning Agent: Uses a policy-gradient (REINFORCE) algorithm with a neural network to learn optimal phase transitions.
3. Training and Evaluation: Trains the RL agent and evaluates its performance in a live simulation.
4. Visualization: Real-time intersection visualization and training metrics plotting.
5. Configurable: Easily adjust environment and RL parameters via YAML config files.


# Install dependencies
pip install -r requirements.txt


# Run the main script
python main.py

The script will first train the RL agent and then launch the simulation using the trained model.


# How It Works
## Training:
The RL agent observes the current traffic state (vehicle queues, light phase, timers) and selects actions to change the traffic light phase. It receives rewards based on traffic efficiency and timing accuracy, updating its policy to maximize long-term performance.

## Simulation:
After training, the agent's learned policy is used to control the intersection in real time, adapting to changing traffic conditions for optimal flow.


# Visualization
## Real-Time Simulation:
The intersection and vehicles are rendered using Pygame.

## Training Metrics:
Training reward and exploration rate curves are plotted and saved as training_metrics.png.


# Requirements
1. Python 3.7+
2. See requirements.txt for all dependencies:
    numpy, torch, matplotlib, pygame, pyyaml, random, os, time etc.