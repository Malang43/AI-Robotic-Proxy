import pygame
import heapq
import math
import time
import sys
import random

# ==========================================================
# HOSPITAL MEDICINE DELIVERY ROBOT DIGITAL TWIN
# Level-1 simulation for testing navigation, delivery workflow,
# dynamic obstacles, emergency stop, and dashboard before hardware.
# ==========================================================

WIDTH = 1180
HEIGHT = 720
MAP_W = 760
MAP_H = 720
PANEL_X = 760
CELL = 25

ROBOT_RADIUS = 11
ROBOT_SPEED = 60.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hospital Medicine Delivery Robot - Digital Twin")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 15)
tiny_font = pygame.font.SysFont("Arial", 13)
title_font = pygame.font.SysFont("Arial", 23, bold=True)
big_font = pygame.font.SysFont("Arial", 27, bold=True)

# -----------------------------
# Hospital layout points
# -----------------------------
robot_pos = [60.0, 665.0]
trail = []

mission_steps = [
    {"name": "Pharmacy: Collect Medicines", "pos": (75, 80), "label": "PHARM", "action": "pickup", "duration": 3.0},
    {"name": "Packing Station: Verify Labels", "pos": (380, 650), "label": "PACK", "action": "pack", "duration": 4.0},
    {"name": "Room 101: Deliver Medicine A", "pos": (700, 80), "label": "101", "action": "deliver", "duration": 2.0},
    {"name": "Room 203: Deliver Medicine B", "pos": (710, 430), "label": "203", "action": "deliver", "duration": 2.0},
    {"name": "ICU: Deliver Urgent Pack", "pos": (85, 360), "label": "ICU", "action": "deliver", "duration": 2.5},
    {"name": "Dock: Mission Complete", "pos": (60, 665), "label": "DOCK", "action": "dock", "duration": 1.5},
]

current_step = 0

# Static blocked areas: wards, walls, beds, counters, equipment
obstacles = [
    {"rect": pygame.Rect(185, 70, 120, 235), "name": "Ward Block A", "type": "ward"},
    {"rect": pygame.Rect(420, 65, 125, 170), "name": "Ward Block B", "type": "ward"},
    {"rect": pygame.Rect(590, 145, 95, 205), "name": "Patient Beds", "type": "ward"},
    {"rect": pygame.Rect(165, 430, 185, 85), "name": "Nurse Desk", "type": "desk"},
    {"rect": pygame.Rect(440, 400, 130, 165), "name": "Equipment Area", "type": "equipment"},
    {"rect": pygame.Rect(595, 525, 110, 90), "name": "Waiting Area", "type": "crowd"},
    {"rect": pygame.Rect(315, 260, 110, 60), "name": "Medical Trolley", "type": "equipment"},
]

# Automatic dynamic obstacle: a nurse cart appears later
auto_obstacle = {"rect": pygame.Rect(320, 350, 90, 65), "name": "Nurse Cart", "type": "dynamic"}
auto_added = False
auto_time = 10.0

# Click-added obstacles
visitor_count = 0

# Path state
path = []
path_index = 0
replan_count = 0

# Robot/system state
paused = False
mission_complete = False
replanning = False
status_message = "System starting..."
robot_mode = "AUTONOMOUS"
start_time = time.time()

# Medicine workflow state
operation_active = False
operation_start = 0.0
operation_duration = 0.0
operation_text = ""
packages_total = 3
packages_loaded = False
packages_packed = False
packages_delivered = 0

# Dashboard state
battery = 100.0
network_status = "Stable"
medicine_temp = 4.2
last_network_update = time.time()
last_temp_update = time.time()

# AI/notification mock messages
ai_messages = [
    ("System", "Prescription list received from hospital server."),
    ("Pharmacy", "Medicine A, B, and urgent ICU pack are ready."),
    ("Robot", "Route planned. Moving through safe corridor."),
    ("Nurse", "Please avoid the central corridor."),
    ("Robot", "New obstacle detected. Replanning safe route."),
    ("System", "Delivery record will be saved after mission."),
]
ai_index = 0
last_ai_update = time.time()


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

    safety = ROBOT_RADIUS + 9
    for obs in obstacles:
        inflated = obs["rect"].inflate(safety * 2, safety * 2)
        if inflated.collidepoint(pos[0], pos[1]):
            return True
    return False


def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


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

            move_cost = 1.4 if dx != 0 and dy != 0 else 1.0
            new_g = g_score[current] + move_cost

            if nxt not in g_score or new_g < g_score[nxt]:
                came_from[nxt] = current
                g_score[nxt] = new_g
                f_score = new_g + heuristic(nxt, goal)
                heapq.heappush(open_list, (f_score, nxt))

    return []


def plan_path():
    global path, path_index, replan_count, status_message, replanning, robot_mode
    if mission_complete:
        return

    replanning = True
    robot_mode = "REPLANNING"

    goal_pos = mission_steps[current_step]["pos"]
    start_cell = to_grid(robot_pos)
    goal_cell = to_grid(goal_pos)

    new_path = astar(start_cell, goal_cell)

    if not new_path:
        path = []
        robot_mode = "BLOCKED"
        status_message = "No safe path found. Remove obstacle or replan."
        replanning = False
        return

    path = new_path
    path_index = 0
    replan_count += 1
    status_message = "Path planned to {}".format(mission_steps[current_step]["name"])
    robot_mode = "AUTONOMOUS"
    replanning = False


def start_operation():
    global operation_active, operation_start, operation_duration, operation_text, robot_mode, status_message

    step = mission_steps[current_step]
    action = step["action"]
    operation_active = True
    operation_start = time.time()
    operation_duration = step["duration"]

    if action == "pickup":
        operation_text = "Picking medicines from pharmacy shelves"
    elif action == "pack":
        operation_text = "Packing medicines and verifying patient labels"
    elif action == "deliver":
        operation_text = "Delivering medicine safely to patient"
    elif action == "dock":
        operation_text = "Returning to charging dock"
    else:
        operation_text = "Processing task"

    robot_mode = "OPERATING"
    status_message = operation_text


def complete_operation():
    global operation_active, current_step, mission_complete, robot_mode, status_message
    global packages_loaded, packages_packed, packages_delivered

    step = mission_steps[current_step]
    action = step["action"]

    if action == "pickup":
        packages_loaded = True
        status_message = "Medicines collected from pharmacy."
    elif action == "pack":
        packages_packed = True
        status_message = "Medicine packs verified and sealed."
    elif action == "deliver":
        packages_delivered += 1
        status_message = "Delivery completed: {}".format(step["name"])
    elif action == "dock":
        mission_complete = True
        robot_mode = "MISSION COMPLETE"
        status_message = "Mission complete: all medicines delivered."
        operation_active = False
        return

    operation_active = False

    if current_step < len(mission_steps) - 1:
        current_step += 1
        plan_path()
    else:
        mission_complete = True
        robot_mode = "MISSION COMPLETE"


def handle_operation():
    if not operation_active:
        return
    elapsed = time.time() - operation_start
    if elapsed >= operation_duration:
        complete_operation()


def move_robot(dt):
    global path_index

    if paused or mission_complete or replanning or operation_active:
        return
    if not path or path_index >= len(path):
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
    if len(trail) > 600:
        trail.pop(0)

    goal_pos = mission_steps[current_step]["pos"]
    if distance(robot_pos, goal_pos) < 18:
        start_operation()


def add_auto_obstacle_if_needed():
    global auto_added, status_message
    if mission_complete:
        return
    elapsed = time.time() - start_time
    if elapsed > auto_time and not auto_added:
        obstacles.append(auto_obstacle)
        auto_added = True
        status_message = "Nurse cart appeared. Replanning route."
        plan_path()


def add_clicked_obstacle(mouse_pos):
    global visitor_count, status_message
    x, y = mouse_pos
    if x >= MAP_W:
        return

    if distance([x, y], robot_pos) < 55:
        status_message = "Cannot place obstacle too close to robot."
        return

    for step in mission_steps:
        if distance([x, y], step["pos"]) < 45:
            status_message = "Cannot place obstacle too close to mission point."
            return

    rect = pygame.Rect(x - 23, y - 23, 46, 46)
    for obs in obstacles:
        if obs["rect"].colliderect(rect):
            status_message = "Cannot place obstacle on existing blocked area."
            return

    visitor_count += 1
    obstacles.append({"rect": rect, "name": "Human Obstacle {}".format(visitor_count), "type": "dynamic"})
    status_message = "Human obstacle added. Replanning safe route."
    plan_path()


def update_dashboard_values(dt):
    global battery, network_status, medicine_temp, last_network_update, last_temp_update, ai_index, last_ai_update

    if not paused and not mission_complete:
        battery -= 0.0045 * dt * 60
    battery = max(0.0, battery)

    now = time.time()
    if now - last_network_update > 4.0:
        last_network_update = now
        network_status = random.choice(["Stable", "Stable", "Good", "Weak"])

    if now - last_temp_update > 2.5:
        last_temp_update = now
        medicine_temp = 4.2 + random.uniform(-0.35, 0.35)

    if now - last_ai_update > 4.5:
        last_ai_update = now
        ai_index = (ai_index + 1) % len(ai_messages)


def draw_text(text, x, y, color=(255, 255, 255), fnt=font):
    surf = fnt.render(text, True, color)
    screen.blit(surf, (x, y))


def draw_environment():
    screen.fill((18, 22, 30))
    pygame.draw.rect(screen, (29, 34, 43), (0, 0, MAP_W, MAP_H))

    for x in range(0, MAP_W, CELL):
        pygame.draw.line(screen, (42, 48, 58), (x, 0), (x, MAP_H))
    for y in range(0, MAP_H, CELL):
        pygame.draw.line(screen, (42, 48, 58), (0, y), (MAP_W, y))

    pygame.draw.rect(screen, (10, 14, 22), (0, 0, MAP_W, 40))
    draw_text("Hospital Medicine Delivery Robot - Digital Twin", 16, 8, (255, 220, 90), title_font)

    # Dock/home
    pygame.draw.rect(screen, (65, 130, 210), (20, 635, 90, 55), border_radius=8)
    draw_text("Dock", 46, 653, (255, 255, 255), small_font)

    # Obstacles and areas
    for obs in obstacles:
        rect = obs["rect"]
        t = obs["type"]
        if t == "dynamic":
            color = (220, 75, 75)
        elif t == "equipment":
            color = (95, 145, 210)
        elif t == "desk":
            color = (190, 130, 70)
        elif t == "crowd":
            color = (210, 110, 100)
        else:
            color = (125, 90, 185)

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (235, 235, 235), rect, 2, border_radius=8)
        draw_text(obs["name"][:15], rect.x + 5, rect.y + 7, (255, 255, 255), tiny_font)

    # Mission points
    for i, step in enumerate(mission_steps):
        pos = step["pos"]
        if i < current_step:
            color = (80, 205, 120)
        elif i == current_step:
            color = (255, 215, 70)
        else:
            color = (80, 135, 230)

        pygame.draw.circle(screen, color, pos, 17)
        pygame.draw.circle(screen, (255, 255, 255), pos, 17, 2)
        draw_text(step["label"], pos[0] - 22, pos[1] - 42, (255, 255, 255), small_font)

    # Planned path
    if len(path) > 1:
        pygame.draw.lines(screen, (255, 220, 70), False, path, 4)

    # Trail
    if len(trail) > 1:
        pygame.draw.lines(screen, (125, 220, 255), False, trail, 2)

    # Robot
    pygame.draw.circle(screen, (40, 230, 155), (int(robot_pos[0]), int(robot_pos[1])), ROBOT_RADIUS + 4)
    pygame.draw.circle(screen, (255, 255, 255), (int(robot_pos[0]), int(robot_pos[1])), ROBOT_RADIUS + 4, 2)
    draw_text("Robot", int(robot_pos[0]) - 23, int(robot_pos[1]) - 35, (255, 255, 255), small_font)

    # Medicine package on robot when carrying
    if packages_loaded and packages_delivered < packages_total and not mission_complete:
        pygame.draw.rect(screen, (255, 245, 120), (int(robot_pos[0]) + 9, int(robot_pos[1]) - 16, 16, 14), border_radius=3)
        pygame.draw.rect(screen, (255, 255, 255), (int(robot_pos[0]) + 9, int(robot_pos[1]) - 16, 16, 14), 1, border_radius=3)


def draw_bar(x, y, value, max_value, fill_color):
    pygame.draw.rect(screen, (80, 80, 90), (x, y, 170, 18), border_radius=5)
    fill_width = int(170 * (value / max_value))
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, 18), border_radius=5)
    pygame.draw.rect(screen, (230, 230, 230), (x, y, 170, 18), 2, border_radius=5)


def draw_panel():
    pygame.draw.rect(screen, (14, 17, 25), (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
    pygame.draw.line(screen, (100, 105, 120), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    x = PANEL_X + 22
    y = 18

    draw_text("HOSPITAL ROBOT", x, y, (255, 255, 255), title_font)
    y += 28
    draw_text("MEDICINE DELIVERY TWIN", x, y, (255, 220, 80), title_font)
    y += 45

    if mission_complete:
        mode = "MISSION COMPLETE"
        mode_color = (80, 230, 150)
    elif paused:
        mode = "EMERGENCY STOP"
        mode_color = (255, 90, 90)
    elif operation_active:
        mode = "OPERATING"
        mode_color = (255, 215, 80)
    else:
        mode = robot_mode
        mode_color = (80, 230, 150)

    draw_text("Robot Mode:", x, y, (180, 180, 185)); y += 24
    draw_text(mode, x, y, mode_color, title_font); y += 40

    step = mission_steps[current_step]
    draw_text("Current Task:", x, y, (180, 180, 185)); y += 24
    draw_text(step["name"][:36], x, y, (255, 255, 255), small_font); y += 36

    if operation_active:
        progress = min(1.0, (time.time() - operation_start) / operation_duration)
        draw_text("Operation:", x, y, (180, 180, 185)); y += 22
        draw_text(operation_text[:38], x, y, (255, 220, 80), tiny_font); y += 22
        draw_bar(x, y, progress, 1.0, (255, 215, 80)); y += 35

    dist = distance(robot_pos, step["pos"])
    draw_text("Distance to Task: {:.1f} px".format(dist), x, y, (220, 220, 220), small_font); y += 24

    draw_text("Battery: {:.1f}%".format(battery), x, y, (220, 220, 220), small_font); y += 22
    battery_color = (70, 220, 120) if battery > 50 else (255, 190, 70)
    draw_bar(x, y, battery, 100.0, battery_color); y += 34

    temp_color = (120, 230, 255) if 2.0 <= medicine_temp <= 8.0 else (255, 80, 80)
    draw_text("Medicine Temp: {:.1f} C".format(medicine_temp), x, y, temp_color, small_font); y += 24
    draw_text("Network: {}".format(network_status), x, y, (220, 220, 220), small_font); y += 24
    draw_text("Hospital Server: Connected", x, y, (120, 230, 160), small_font); y += 34

    draw_text("Delivery Data", x, y, (255, 255, 255), title_font); y += 28
    draw_text("Packages Loaded: {}".format("Yes" if packages_loaded else "No"), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Packed/Verified: {}".format("Yes" if packages_packed else "No"), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Delivered: {}/{}".format(packages_delivered, packages_total), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Path Replans: {}".format(replan_count), x, y, (220, 220, 220), small_font); y += 22
    draw_text("Dynamic Obstacles: {}".format(visitor_count + (1 if auto_added else 0)), x, y, (220, 220, 220), small_font); y += 32

    draw_text("Status:", x, y, (180, 180, 185)); y += 22
    draw_text(status_message[:42], x, y, (255, 220, 80), tiny_font); y += 40

    pygame.draw.rect(screen, (28, 34, 45), (x - 5, y, 365, 92), border_radius=8)
    pygame.draw.rect(screen, (100, 110, 130), (x - 5, y, 365, 92), 2, border_radius=8)
    draw_text("Hospital AI / Notification Panel", x + 10, y + 10, (255, 220, 80), small_font)
    speaker, msg = ai_messages[ai_index]
    draw_text("{}:".format(speaker), x + 10, y + 38, (120, 220, 255), small_font)
    draw_text(msg[:44], x + 10, y + 62, (255, 255, 255), tiny_font)
    y += 112

    draw_text("Controls", x, y, (255, 255, 255), title_font); y += 27
    draw_text("Mouse Click = Add human obstacle", x, y, (220, 220, 220), tiny_font); y += 20
    draw_text("S = Emergency Stop", x, y, (220, 220, 220), tiny_font); y += 20
    draw_text("R = Resume", x, y, (220, 220, 220), tiny_font); y += 20
    draw_text("P = Replan", x, y, (220, 220, 220), tiny_font); y += 20
    draw_text("ESC = Quit", x, y, (220, 220, 220), tiny_font); y += 28

    draw_text("Legend", x, y, (255, 255, 255), title_font); y += 26
    draw_text("Green circle = Delivery robot", x, y, (180, 255, 220), tiny_font); y += 18
    draw_text("Purple = Wards/rooms", x, y, (220, 205, 255), tiny_font); y += 18
    draw_text("Red = Nurse/human obstacle", x, y, (255, 180, 180), tiny_font); y += 18
    draw_text("Yellow = Planned route", x, y, (255, 235, 120), tiny_font); y += 18
    draw_text("Blue = Robot travel history", x, y, (180, 235, 255), tiny_font)


# Initial path
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
                status_message = "Emergency stop activated. Robot holding position."
            elif event.key == pygame.K_r:
                paused = False
                robot_mode = "AUTONOMOUS"
                status_message = "Robot resumed. Continuing delivery mission."
            elif event.key == pygame.K_p:
                status_message = "Manual replan requested."
                plan_path()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                add_clicked_obstacle(event.pos)

    add_auto_obstacle_if_needed()
    update_dashboard_values(dt)
    handle_operation()
    move_robot(dt)

    draw_environment()
    draw_panel()
    pygame.display.flip()

pygame.quit()
sys.exit()
