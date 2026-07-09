import pygame
import heapq
import math
import time
import sys
import random

# ==========================================================
# EXPO ROBOT DIGITAL TWIN - FINAL INTERACTIVE VERSION
# Features:
# - Custom expo environment
# - Multi-booth navigation
# - A* path planning
# - Click-to-add visitor obstacle
# - Automatic replanning
# - Battery/network/mode dashboard
# - AI assistant mock panel
# - Emergency stop/resume
# ==========================================================

# -----------------------------
# Window settings
# -----------------------------
WIDTH = 1100
HEIGHT = 700

MAP_W = 700
MAP_H = 700
PANEL_X = 700

CELL = 25

ROBOT_RADIUS = 10
ROBOT_SPEED = 58.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Expo Robot Digital Twin - AI Robotic Proxy")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 15)
tiny_font = pygame.font.SysFont("Arial", 13)
title_font = pygame.font.SysFont("Arial", 23, bold=True)
big_font = pygame.font.SysFont("Arial", 27, bold=True)


# -----------------------------
# Environment setup
# -----------------------------
start_pos = [60.0, 630.0]
robot_pos = start_pos[:]

goals = [
    {"name": "Booth A: Product Demo", "pos": (620, 80), "label": "A"},
    {"name": "Booth B: Client Meeting", "pos": (90, 270), "label": "B"},
    {"name": "Booth C: Info Desk", "pos": (610, 560), "label": "C"},
    {"name": "Exit: Mission Complete", "pos": (70, 80), "label": "EXIT"},
]

current_goal_index = 0

# Static expo booths / blocked regions
obstacles = [
    {"rect": pygame.Rect(210, 70, 90, 190), "name": "Booth Block 1", "type": "booth"},
    {"rect": pygame.Rect(380, 80, 95, 130), "name": "Booth Block 2", "type": "booth"},
    {"rect": pygame.Rect(530, 130, 80, 160), "name": "Product Booth", "type": "booth"},

    {"rect": pygame.Rect(170, 330, 130, 75), "name": "Display Table", "type": "table"},
    {"rect": pygame.Rect(390, 325, 150, 80), "name": "Crowd Area", "type": "crowd"},

    {"rect": pygame.Rect(85, 500, 185, 80), "name": "Blocked Booth", "type": "booth"},
    {"rect": pygame.Rect(440, 510, 90, 110), "name": "Info Counter", "type": "table"},
]

# Dynamic visitor that appears automatically
auto_visitor = {"rect": pygame.Rect(315, 235, 90, 65), "name": "Auto Visitor", "type": "visitor"}
auto_visitor_added = False
auto_visitor_time = 9.0

# Click-added visitors
visitor_count = 0

# Robot path/trail
path = []
path_index = 0
trail = []

# State variables
paused = False
mission_complete = False
replanning = False
status_message = "System starting..."
robot_mode = "AUTONOMOUS"

start_time = time.time()
last_network_update = time.time()
battery = 100.0
network_status = "Stable"
replan_count = 0

# AI mock messages
ai_messages = [
    ("Visitor", "Can you tell me about Product A?"),
    ("AI Robot", "Product A is designed for smart business automation."),
    ("Visitor", "Can I meet your company representative?"),
    ("AI Robot", "Yes, I can guide you to the client meeting booth."),
    ("Visitor", "Is the robot safe around people?"),
    ("AI Robot", "Yes, navigation uses obstacle avoidance and emergency stop."),
]
ai_index = 0
last_ai_update = time.time()


# ==========================================================
# Helper functions
# ==========================================================
def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def to_grid(pos):
    return int(pos[0] // CELL), int(pos[1] // CELL)


def to_world(cell):
    return [cell[0] * CELL + CELL / 2, cell[1] * CELL + CELL / 2]


def inside_map(pos):
    x, y = pos
    return ROBOT_RADIUS < x < MAP_W - ROBOT_RADIUS and ROBOT_RADIUS < y < MAP_H - ROBOT_RADIUS


def is_blocked(cell):
    pos = to_world(cell)

    if not inside_map(pos):
        return True

    safety = ROBOT_RADIUS + 8

    for obs in obstacles:
        inflated = obs["rect"].inflate(safety * 2, safety * 2)
        if inflated.collidepoint(pos[0], pos[1]):
            return True

    return False


def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# ==========================================================
# A* path planning
# ==========================================================
def astar(start, goal):
    open_list = []
    heapq.heappush(open_list, (0, start))

    came_from = {}
    g_score = {start: 0}

    neighbors = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            final_path = []

            while current in came_from:
                final_path.append(current)
                current = came_from[current]

            final_path.append(start)
            final_path.reverse()

            return [to_world(c) for c in final_path]

        for dx, dy in neighbors:
            nxt = (current[0] + dx, current[1] + dy)

            if nxt[0] < 0 or nxt[1] < 0:
                continue

            if nxt[0] >= MAP_W // CELL or nxt[1] >= MAP_H // CELL:
                continue

            if is_blocked(nxt):
                continue

            cost = 1.4 if dx != 0 and dy != 0 else 1.0
            new_g = g_score[current] + cost

            if nxt not in g_score or new_g < g_score[nxt]:
                came_from[nxt] = current
                g_score[nxt] = new_g
                f_score = new_g + heuristic(nxt, goal)
                heapq.heappush(open_list, (f_score, nxt))

    return []


def plan_path():
    global path, path_index, status_message, replan_count, replanning, robot_mode

    if mission_complete:
        return

    replanning = True
    robot_mode = "REPLANNING"

    goal_pos = goals[current_goal_index]["pos"]

    start_cell = to_grid(robot_pos)
    goal_cell = to_grid(goal_pos)

    new_path = astar(start_cell, goal_cell)

    if not new_path:
        path = []
        status_message = "No path found. Remove/move obstacles."
        robot_mode = "BLOCKED"
        replanning = False
        return

    path = new_path
    path_index = 0
    replan_count += 1

    status_message = "Path planned to {}".format(goals[current_goal_index]["name"])
    robot_mode = "AUTONOMOUS"
    replanning = False


# ==========================================================
# Robot movement and state update
# ==========================================================
def move_robot(dt):
    global path_index, current_goal_index, mission_complete, status_message, robot_mode

    if paused or mission_complete or replanning:
        return

    if not path:
        return

    if path_index >= len(path):
        return

    target = path[path_index]

    dx = target[0] - robot_pos[0]
    dy = target[1] - robot_pos[1]
    d = math.sqrt(dx * dx + dy * dy)

    if d < 5:
        path_index += 1
        return

    vx = dx / d
    vy = dy / d

    robot_pos[0] += vx * ROBOT_SPEED * dt
    robot_pos[1] += vy * ROBOT_SPEED * dt

    trail.append((int(robot_pos[0]), int(robot_pos[1])))

    if len(trail) > 500:
        trail.pop(0)

    goal_pos = goals[current_goal_index]["pos"]

    if distance(robot_pos, goal_pos) < 18:
        if current_goal_index < len(goals) - 1:
            current_goal_index += 1
            status_message = "Checkpoint reached. Planning next goal..."
            plan_path()
        else:
            mission_complete = True
            robot_mode = "MISSION COMPLETE"
            status_message = "Mission complete: all expo points visited."


def add_auto_visitor_if_needed():
    global auto_visitor_added, status_message

    elapsed = time.time() - start_time

    if elapsed > auto_visitor_time and not auto_visitor_added and not mission_complete:
        obstacles.append(auto_visitor)
        auto_visitor_added = True
        status_message = "New visitor appeared. Auto replanning..."
        plan_path()


def add_clicked_visitor(mouse_pos):
    global visitor_count, status_message

    x, y = mouse_pos

    if x >= MAP_W:
        return

    if distance([x, y], robot_pos) < 55:
        status_message = "Cannot place visitor too close to robot."
        return

    for g in goals:
        if distance([x, y], g["pos"]) < 45:
            status_message = "Cannot place visitor too close to goal."
            return

    visitor_rect = pygame.Rect(x - 23, y - 23, 46, 46)

    for obs in obstacles:
        if obs["rect"].colliderect(visitor_rect):
            status_message = "Cannot place visitor on existing booth."
            return

    visitor_count += 1

    obstacles.append({
        "rect": visitor_rect,
        "name": "Clicked Visitor {}".format(visitor_count),
        "type": "visitor"
    })

    status_message = "Visitor added by click. Replanning path..."
    plan_path()


def update_battery_and_network(dt):
    global battery, network_status, last_network_update

    if not paused and not mission_complete:
        battery -= 0.006 * dt * 60

    if battery < 0:
        battery = 0

    now = time.time()

    if now - last_network_update > 4.0:
        last_network_update = now
        network_status = random.choice(["Stable", "Stable", "Stable", "Good", "Weak"])


def update_ai_panel():
    global ai_index, last_ai_update

    now = time.time()

    if now - last_ai_update > 4.5:
        last_ai_update = now
        ai_index = (ai_index + 1) % len(ai_messages)


# ==========================================================
# Drawing
# ==========================================================
def draw_text(text, x, y, color=(255, 255, 255), fnt=font):
    surface = fnt.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_environment():
    screen.fill((18, 22, 30))

    # Map background
    pygame.draw.rect(screen, (30, 35, 45), (0, 0, MAP_W, MAP_H))

    # Grid
    for x in range(0, MAP_W, CELL):
        pygame.draw.line(screen, (43, 48, 58), (x, 0), (x, MAP_H))

    for y in range(0, MAP_H, CELL):
        pygame.draw.line(screen, (43, 48, 58), (0, y), (MAP_W, y))

    # Header inside map
    pygame.draw.rect(screen, (10, 14, 22), (0, 0, MAP_W, 38))
    draw_text("AI Robotic Proxy - Expo Hall Digital Twin", 16, 8, (255, 220, 90), title_font)

    # Entrance
    pygame.draw.rect(screen, (70, 130, 210), (20, 615, 95, 55), border_radius=8)
    draw_text("Entrance", 31, 632, (255, 255, 255), small_font)

    # Obstacles
    for obs in obstacles:
        rect = obs["rect"]
        obs_type = obs["type"]

        if obs_type == "visitor":
            color = (220, 75, 75)
        elif obs_type == "crowd":
            color = (190, 120, 80)
        elif obs_type == "table":
            color = (100, 145, 210)
        else:
            color = (125, 90, 185)

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (235, 235, 235), rect, 2, border_radius=8)

        label = obs["name"][:13]
        draw_text(label, rect.x + 5, rect.y + 7, (255, 255, 255), tiny_font)

    # Goals
    for i, g in enumerate(goals):
        pos = g["pos"]

        if i < current_goal_index:
            color = (80, 205, 120)
        elif i == current_goal_index:
            color = (255, 215, 70)
        else:
            color = (80, 135, 230)

        pygame.draw.circle(screen, color, pos, 16)
        pygame.draw.circle(screen, (255, 255, 255), pos, 16, 2)

        draw_text(g["label"], pos[0] - 18, pos[1] - 40, (255, 255, 255), small_font)

    # Planned path
    if len(path) > 1:
        pygame.draw.lines(screen, (255, 220, 70), False, path, 4)

    # Trail
    if len(trail) > 1:
        pygame.draw.lines(screen, (125, 220, 255), False, trail, 2)

    # Robot
    pygame.draw.circle(screen, (40, 230, 155), (int(robot_pos[0]), int(robot_pos[1])), ROBOT_RADIUS + 3)
    pygame.draw.circle(screen, (255, 255, 255), (int(robot_pos[0]), int(robot_pos[1])), ROBOT_RADIUS + 3, 2)
    draw_text("Robot", int(robot_pos[0]) - 23, int(robot_pos[1]) - 34, (255, 255, 255), small_font)


def draw_battery_bar(x, y, value):
    pygame.draw.rect(screen, (80, 80, 90), (x, y, 160, 18), border_radius=5)

    fill_width = int(160 * (value / 100.0))

    if value > 60:
        color = (70, 220, 120)
    elif value > 30:
        color = (255, 190, 70)
    else:
        color = (230, 70, 70)

    pygame.draw.rect(screen, color, (x, y, fill_width, 18), border_radius=5)
    pygame.draw.rect(screen, (230, 230, 230), (x, y, 160, 18), 2, border_radius=5)


def draw_panel():
    pygame.draw.rect(screen, (14, 17, 25), (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
    pygame.draw.line(screen, (100, 105, 120), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    x = PANEL_X + 22
    y = 20

    draw_text("REMOTE OPERATOR", x, y, (255, 255, 255), title_font)
    y += 28
    draw_text("DIGITAL TWIN DASHBOARD", x, y, (255, 220, 80), title_font)
    y += 45

    # Robot mode
    if mission_complete:
        mode = "MISSION COMPLETE"
    elif paused:
        mode = "EMERGENCY STOP"
    else:
        mode = robot_mode

    draw_text("Robot Mode:", x, y, (180, 180, 185)); y += 24
    draw_text(mode, x, y, (80, 230, 150) if not paused else (255, 90, 90), title_font)
    y += 42

    # Goal
    current_goal = goals[current_goal_index]
    draw_text("Current Goal:", x, y, (180, 180, 185)); y += 24
    draw_text(current_goal["name"][:31], x, y, (255, 255, 255), small_font)
    y += 38

    # Distance
    dist = distance(robot_pos, current_goal["pos"])
    draw_text("Distance to Goal: {:.1f} px".format(dist), x, y, (220, 220, 220), small_font)
    y += 28

    draw_text("Battery: {:.1f}%".format(battery), x, y, (220, 220, 220), small_font)
    y += 24
    draw_battery_bar(x, y, battery)
    y += 38

    draw_text("Network: {}".format(network_status), x, y, (220, 220, 220), small_font)
    y += 25
    draw_text("Remote Operator: Connected", x, y, (120, 230, 160), small_font)
    y += 25
    draw_text("AI Assistant: Ready", x, y, (120, 230, 160), small_font)
    y += 35

    draw_text("Mission Data", x, y, (255, 255, 255), title_font)
    y += 30
    draw_text("Obstacles: {}".format(len(obstacles)), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Path Replans: {}".format(replan_count), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Visitors Added: {}".format(visitor_count), x, y, (220, 220, 220), small_font); y += 32

    draw_text("Status:", x, y, (180, 180, 185)); y += 24
    draw_text(status_message[:35], x, y, (255, 220, 80), small_font)
    y += 45

    # AI Assistant mock panel
    pygame.draw.rect(screen, (28, 34, 45), (x - 5, y, 350, 100), border_radius=8)
    pygame.draw.rect(screen, (100, 110, 130), (x - 5, y, 350, 100), 2, border_radius=8)
    draw_text("AI Assistant Mock Panel", x + 10, y + 10, (255, 220, 80), small_font)

    speaker, msg = ai_messages[ai_index]
    draw_text("{}:".format(speaker), x + 10, y + 38, (120, 220, 255), small_font)
    draw_text(msg[:38], x + 10, y + 62, (255, 255, 255), tiny_font)

    y += 125

    draw_text("Controls", x, y, (255, 255, 255), title_font)
    y += 28
    draw_text("Mouse Click = Add visitor", x, y, (220, 220, 220), small_font); y += 22
    draw_text("S = Emergency Stop", x, y, (220, 220, 220), small_font); y += 22
    draw_text("R = Resume", x, y, (220, 220, 220), small_font); y += 22
    draw_text("P = Replan Path", x, y, (220, 220, 220), small_font); y += 22
    draw_text("ESC = Quit", x, y, (220, 220, 220), small_font)

    y += 35

    draw_text("Legend", x, y, (255, 255, 255), title_font)
    y += 28
    draw_text("Green circle = Robot", x, y, (180, 255, 220), tiny_font); y += 20
    draw_text("Purple blocks = Booths", x, y, (220, 205, 255), tiny_font); y += 20
    draw_text("Red blocks = Visitors", x, y, (255, 180, 180), tiny_font); y += 20
    draw_text("Yellow line = Planned path", x, y, (255, 235, 120), tiny_font); y += 20
    draw_text("Blue line = Robot trail", x, y, (180, 235, 255), tiny_font)


# ==========================================================
# Main loop
# ==========================================================
plan_path()

running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_s:
                paused = True
                robot_mode = "EMERGENCY STOP"
                status_message = "Emergency stop activated."

            elif event.key == pygame.K_r:
                paused = False
                robot_mode = "AUTONOMOUS"
                status_message = "Robot resumed."

            elif event.key == pygame.K_p:
                status_message = "Manual replanning requested."
                plan_path()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                add_clicked_visitor(event.pos)

    add_auto_visitor_if_needed()
    update_battery_and_network(dt)
    update_ai_panel()
    move_robot(dt)

    draw_environment()
    draw_panel()

    pygame.display.flip()

pygame.quit()
sys.exit()
