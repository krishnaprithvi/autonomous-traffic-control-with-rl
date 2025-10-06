import pygame
import random
from training.train import train
from models.reinforce_agent import TrafficControllerRL
from env.traffic_simulation import VehicleManager, Vehicle
from env.traffic_simulation import WIDTH, HEIGHT, draw_intersection, draw_stop_lines, draw_traffic_lights, draw_info

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("4-Way Intersection Traffic Control (RL)")
    clock = pygame.time.Clock()

    # Train the agent first
    print("Starting training phase...")
    train(200, save_path="models/policy.pth")
    print("Training complete. Starting simulation with trained agent...")

    # Now run the simulation with the trained agent
    controller = TrafficControllerRL(epsilon_start=0.0)  # Set epsilon to 0 for full exploitation
    controller.load("models/policy.pth")
    vehicle_manager = VehicleManager()
    for _ in range(8):
        direction = random.choice(["north", "south", "east", "west"])
        vehicle_manager.vehicles.append(Vehicle(direction))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Ending Simulation...")
            elif event.type == pygame.KEYDOWN:
                print("Trying pressing escape or closing the simulation window")
                if event.key == pygame.K_ESCAPE:
                    running = False
                    print("Ending Simulation...")

        # Update controller and vehicles (agent acts greedily)
        controller.update(dt, vehicle_manager, training=False)
        vehicle_manager.update(dt, controller.current_phase)

        # Draw everything
        draw_intersection(screen)
        draw_stop_lines(screen)
        draw_traffic_lights(screen, controller.current_phase, controller.Phase)
        vehicle_manager.draw(screen)
        draw_info(screen, controller.current_phase, len(vehicle_manager.vehicles))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()