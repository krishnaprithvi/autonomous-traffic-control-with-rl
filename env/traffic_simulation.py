import pygame
import random
import yaml

def load_config(config_path='configs/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
config = load_config()
WIDTH, HEIGHT = config['environment']['width'], config['environment']['height']
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
ROAD_WIDTH = config['environment']['road_width']
SPEED = config['environment']['vehicle_speed']
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)

def draw_intersection(screen):
    screen.fill(BLACK)
    pygame.draw.rect(screen, GRAY, (0, HEIGHT//2 - 60, WIDTH, 120))
    pygame.draw.rect(screen, GRAY, (WIDTH//2 - 60, 0, 120, HEIGHT))
    for i in range(0, WIDTH, 20):
        pygame.draw.line(screen, WHITE, (i, HEIGHT//2), (i+10, HEIGHT//2), 2)
    for i in range(0, HEIGHT, 20):
        pygame.draw.line(screen, WHITE, (WIDTH//2, i), (WIDTH//2, i+10), 2)

def draw_stop_lines(screen):
    stop_line_distance = 65
    pygame.draw.line(screen, WHITE, (WIDTH//2 + stop_line_distance, HEIGHT//2 - 60), (WIDTH//2 + stop_line_distance, HEIGHT//2), 3)
    pygame.draw.line(screen, WHITE, (WIDTH//2 - stop_line_distance, HEIGHT//2), (WIDTH//2 - stop_line_distance, HEIGHT//2 + 60), 3)
    pygame.draw.line(screen, WHITE, (WIDTH//2 - 60, HEIGHT//2 - stop_line_distance), (WIDTH//2, HEIGHT//2 - stop_line_distance), 3)
    pygame.draw.line(screen, WHITE, (WIDTH//2, HEIGHT//2 + stop_line_distance), (WIDTH//2 + 60, HEIGHT//2 + stop_line_distance), 3)
    font = pygame.font.Font(None, 30)
    text_right = pygame.transform.rotate(font.render("STOP", True, WHITE), 90)
    text_left = pygame.transform.rotate(font.render("STOP", True, WHITE), -90)
    text_up = pygame.transform.rotate(font.render("STOP", True, WHITE), -180)
    text_down = pygame.transform.rotate(font.render("STOP", True, WHITE), 0)
    text_rect_right = text_right.get_rect(center=(WIDTH//2 + stop_line_distance + 20, HEIGHT//2 - 30))
    text_rect_left = text_left.get_rect(center=(WIDTH//2 - stop_line_distance - 20, HEIGHT//2 + 30))
    text_rect_up = text_up.get_rect(center=(WIDTH//2 - 30, HEIGHT//2 - stop_line_distance - 20))
    text_rect_down = text_down.get_rect(center=(WIDTH//2 + 30, HEIGHT//2 + stop_line_distance + 20))
    screen.blit(text_right, text_rect_right)
    screen.blit(text_left, text_rect_left)
    screen.blit(text_up, text_rect_up)
    screen.blit(text_down, text_rect_down)

def draw_traffic_lights(screen, phase, Phase):
    if phase in [Phase.VERT_GREEN, Phase.VERT_YELLOW]:
        vert_color = GREEN if phase == Phase.VERT_GREEN else YELLOW
        horz_color = RED
    else:
        vert_color = RED
        horz_color = GREEN if phase == Phase.HORZ_GREEN else YELLOW
    pygame.draw.rect(screen, BLACK, (CENTER_X - 10, CENTER_Y - ROAD_WIDTH//2 - 70, 20, 60))
    pygame.draw.circle(screen, vert_color, (CENTER_X, CENTER_Y - ROAD_WIDTH//2 - 40), 8)
    pygame.draw.rect(screen, BLACK, (CENTER_X + ROAD_WIDTH//2 + 10, CENTER_Y - 10, 60, 20))
    pygame.draw.circle(screen, horz_color, (CENTER_X + ROAD_WIDTH//2 + 40, CENTER_Y), 8)
    pygame.draw.rect(screen, BLACK, (CENTER_X - 10, CENTER_Y + ROAD_WIDTH//2 + 10, 20, 60))
    pygame.draw.circle(screen, vert_color, (CENTER_X, CENTER_Y + ROAD_WIDTH//2 + 40), 8)
    pygame.draw.rect(screen, BLACK, (CENTER_X - ROAD_WIDTH//2 - 70, CENTER_Y - 10, 60, 20))
    pygame.draw.circle(screen, horz_color, (CENTER_X - ROAD_WIDTH//2 - 40, CENTER_Y), 8)

def draw_info(screen, phase, vehicle_count):
    font = pygame.font.SysFont(None, 24)
    phase_names = ["Vertical Green", "Vertical Yellow", "Horizontal Green", "Horizontal Yellow"]
    phase_text = font.render(f"Phase: {phase_names[phase]}", True, WHITE)
    count_text = font.render(f"Vehicles: {vehicle_count}", True, WHITE)
    screen.blit(phase_text, (10, 10))
    screen.blit(count_text, (10, 40))


class Phase:
    VERT_GREEN = 0
    VERT_YELLOW = 1
    HORZ_GREEN = 2
    HORZ_YELLOW = 3

# Load phase durations from config
config = load_config()
PHASE_DURATIONS = {
    Phase.VERT_GREEN: config['phase_durations']['VERT_GREEN'],
    Phase.VERT_YELLOW: config['phase_durations']['VERT_YELLOW'],
    Phase.HORZ_GREEN: config['phase_durations']['HORZ_GREEN'],
    Phase.HORZ_YELLOW: config['phase_durations']['HORZ_YELLOW']
}

class Vehicle:
    def __init__(self, direction):
        self.direction = direction
        self.width, self.height = 30, 15
        self.speed = SPEED
        self.stopped = False
        self.crossed_stop_line = False
        self.passed = False
        if direction == "north":
            self.x = WIDTH//2 + 20
            self.y = HEIGHT
            self.height = 20
            self.width = 40
            self.orientation = "vertical"
        elif direction == "south":
            self.x = WIDTH//2 - 40
            self.y = 0
            self.height = 20
            self.width = 40
            self.orientation = "vertical"
        elif direction == "east":
            self.x = 0
            self.y = HEIGHT//2 + 20
            self.height = 40
            self.width = 20
            self.orientation = "horizontal"
        elif direction == "west":
            self.x = WIDTH
            self.y = HEIGHT//2 - 40
            self.height = 40
            self.width = 20
            self.orientation = "horizontal"

    def update(self, phase, vehicles):
        if self.passed:
            self.move()
            return
        stop_lines = {
            "north": CENTER_Y + ROAD_WIDTH // 2,
            "south": CENTER_Y - ROAD_WIDTH // 2,
            "east": CENTER_X - ROAD_WIDTH // 2,
            "west": CENTER_X + ROAD_WIDTH // 2
        }
        if not self.crossed_stop_line:
            if (self.direction == "north" and self.y <= stop_lines["north"]) or \
               (self.direction == "south" and self.y >= stop_lines["south"]) or \
               (self.direction == "east" and self.x >= stop_lines["east"]) or \
               (self.direction == "west" and self.x <= stop_lines["west"]):
                self.crossed_stop_line = True
        if self.crossed_stop_line:
            self.stopped = False
            self.move()
            if (self.direction == "north" and self.y < CENTER_Y - ROAD_WIDTH // 2) or \
               (self.direction == "south" and self.y > CENTER_Y + ROAD_WIDTH // 2) or \
               (self.direction == "east" and self.x > CENTER_X + ROAD_WIDTH // 2) or \
               (self.direction == "west" and self.x < CENTER_X - ROAD_WIDTH // 2):
                self.passed = True
            return
        should_stop = False
        if self.direction in ["north", "south"]:
            if phase in [Phase.HORZ_GREEN, Phase.HORZ_YELLOW]:
                if self.at_stop_line(stop_lines):
                    should_stop = True
        else:
            if phase in [Phase.VERT_GREEN, Phase.VERT_YELLOW]:
                if self.at_stop_line(stop_lines):
                    should_stop = True
        for v in vehicles:
            if v is self or v.passed or v.direction != self.direction:
                continue
            safe_distance = 30
            if self.direction == "north":
                if v.y < self.y and self.y - (v.y + v.height) <= safe_distance:
                    should_stop = True
                    break
            elif self.direction == "south":
                if v.y > self.y and (v.y - (self.y + self.height)) <= safe_distance:
                    should_stop = True
                    break
            elif self.direction == "east":
                if v.x > self.x and (v.x - (self.x + self.width)) <= safe_distance:
                    should_stop = True
                    break
            elif self.direction == "west":
                if v.x < self.x and self.x - (v.x + v.width) <= safe_distance:
                    should_stop = True
                    break
        if should_stop:
            self.stopped = True
        else:
            self.stopped = False
            self.move()

    def at_stop_line(self, stop_lines):
        if self.direction == "north":
            return abs(self.y + self.height - stop_lines["north"]) < 30
        elif self.direction == "south":
            return abs(self.y - stop_lines["south"]) < 50
        elif self.direction == "east":
            return abs(self.x - stop_lines["east"]) < 50
        elif self.direction == "west":
            return abs(self.x + self.width - stop_lines["west"]) < 30
        return False

    def move(self):
        if self.stopped:
            return
        if self.direction == "north":
            self.y -= self.speed
        elif self.direction == "south":
            self.y += self.speed
        elif self.direction == "east":
            self.x += self.speed
        elif self.direction == "west":
            self.x -= self.speed

    def draw(self, screen):
        color = BLUE
        if self.orientation == "vertical":
            pygame.draw.rect(screen, color, (self.x, self.y, 20, 40))
        else:
            pygame.draw.rect(screen, color, (self.x, self.y, 40, 20))

class VehicleManager:
    def __init__(self):
        self.vehicles = []
        self.spawn_timer = 0
        self.config = load_config()
        self.spawn_interval = self.config['environment']['vehicle_spawn_interval']
    
    def update(self, dt, phase):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            direction = random.choice(["north", "south", "east", "west"])
            can_spawn = True
            for v in self.vehicles:
                if v.direction == direction and not v.passed:
                    if direction == "north" and v.y > HEIGHT - 100:
                        can_spawn = False
                    elif direction == "south" and v.y < 100:
                        can_spawn = False
                    elif direction == "east" and v.x < 100:
                        can_spawn = False
                    elif direction == "west" and v.x > WIDTH - 100:
                        can_spawn = False
            if can_spawn:
                self.vehicles.append(Vehicle(direction))
        for v in self.vehicles:
            v.update(phase, self.vehicles)
        self.vehicles = [v for v in self.vehicles if not (
            (v.direction == "north" and v.y < -50) or
            (v.direction == "south" and v.y > HEIGHT + 50) or
            (v.direction == "east" and v.x > WIDTH + 50) or
            (v.direction == "west" and v.x < -50)
        )]

    def draw(self, screen):
        for v in self.vehicles:
            v.draw(screen)

    def get_wait_counts(self):
        counts = {"north": 0, "south": 0, "east": 0, "west": 0}
        for v in self.vehicles:
            if v.stopped and not v.passed:
                counts[v.direction] += 1
        return counts
        
    def reset(self):
        self.vehicles = []
        self.spawn_timer = 0