# 🚦 4-Way Intersection Traffic Control with Reinforcement Learning
A Python-based project that applies Reinforcement Learning (RL) to manage a four-way traffic intersection, optimizing traffic light phases to minimize congestion and vehicle waiting time through adaptive signal control.


# 🧭 Overview
This project simulates a realistic four-way intersection and trains an RL agent to control the traffic lights dynamically.

The goal is to improve traffic flow by learning when to switch lights based on real-time vehicle queue data.

The agent is trained using a policy-gradient (REINFORCE) approach and continuously improves by interacting with the simulation environment.


# ✨ Features
1. 🏙️ Custom Traffic Environment — Simulates realistic vehicle arrivals, departures, and light changes.
2. 🧠 Reinforcement Learning Agent — Uses a neural network with the REINFORCE algorithm to learn optimal signal phase transitions.
3. 📈 Training & Evaluation — Trains the agent and evaluates its policy using live simulations and metrics tracking.
4. 🎮 Visualization — Includes real-time traffic visualization using Pygame.
5. ⚙️ Configurable Setup — All environment and RL parameters can be adjusted easily through YAML configuration files.


# ⚙️ Installation
Make sure you have Python 3.7+ installed.

Install all required dependencies using: pip install -r requirements.txt


# 🚀 Running the Project
To train the agent and start the simulation, run: python main.py

The script first trains the RL agent and then launches a live simulation using the trained model.


# 🧩 How It Works
## 🏋️ Training Phase
1. The RL agent observes the current traffic state — including queue lengths, signal phase, and time.
2. Based on this state, it decides whether to switch or hold the current signal phase.
3. Rewards are assigned depending on traffic efficiency, such as minimizing waiting times and avoiding long queues.
4. The agent updates its policy network to maximize long-term performance.

## 🚗 Simulation Phase
After training, the learned policy is used to control the intersection in real time.
The system continuously adapts to varying traffic conditions, switching lights intelligently to maintain smooth traffic flow.


# 📊 Visualization
## 🕹️ Real-Time Simulation
The traffic intersection and moving vehicles are rendered using Pygame, allowing live observation of how the agent manages signals.

## 📈 Training Metrics
During training, the following graphs are generated and saved as training_metrics.png:
1. Average episode rewards
2. Exploration rate (if applicable)
3. Traffic performance over time


# 🧾 Requirements
1. Python 3.7+
2. Dependencies (see requirements.txt):
numpy
torch
matplotlib
pygame
pyyaml
random
os
time


# 🧠 Project Summary
This project demonstrates how reinforcement learning can be applied to real-world control problems such as traffic management.

By learning from simulated traffic behavior, the system adapts to reduce congestion and improve throughput — paving the way for smarter cities.