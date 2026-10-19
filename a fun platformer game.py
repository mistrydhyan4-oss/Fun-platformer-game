#.\.venv313\Scripts\python.exe "a fun platformer game.py"
import math
import json
from pathlib import Path
import random

import pygame


WIDTH = 800
HEIGHT = 450
WORLD_WIDTH = 2400
FPS = 60

SKY = (135, 206, 235)
WHITE = (255, 255, 255)
GRASS = (82, 183, 85)
PLAYER = (230, 85, 75)
DARK = (45, 52, 64)
OUTLINE = (52, 68, 86)

LEVEL_SPIKES = [
    [
        pygame.Rect(x, 360, 30, 30)
        for x in (770, 1150, 1510, 1780, 1940, 2050, 2150, 2250, 2330)
    ],
    [
        pygame.Rect(x, 360, 30, 30)
        for x in (700, 770, 960, 1130, 1200, 1470, 1540, 1740, 1810,
                  1960, 2030, 2110, 2180, 2250, 2330)
    ] + [
        pygame.Rect(x, y - 28, 28, 28)
        for x, y in (
            (205, 310), (445, 245), (680, 320), (900, 320), (1120, 255),
            (1415, 315), (1640, 255), (1885, 310), (2150, 245),
        )
    ],
    [
        pygame.Rect(x, 360, 30, 30)
        for x in (690, 760, 930, 1000, 1170, 1240, 1450, 1520, 1710, 1780,
                  1940, 2010, 2110, 2180, 2250, 2330)
    ] + [
        pygame.Rect(x, y - 28, 28, 28)
        for x, y in (
            (180, 310), (270, 310), (455, 245), (660, 320), (880, 320),
            (1100, 255), (1370, 315), (1610, 255), (1870, 310), (2180, 245),
        )
    ],
    [
        pygame.Rect(x, 360, 30, 30)
        for x in (750, 1260, 1780, 2180)
    ],
    [
        pygame.Rect(x, 360, 30, 30)
        for x in (640, 710, 780, 950, 1020, 1180, 1250, 1430, 1500, 1570,
                  1730, 1800, 1960, 2030, 2100, 2170, 2240, 2310)
    ] + [
        pygame.Rect(x, y - 28, 28, 28)
        for x, y in (
            (175, 310), (255, 310), (435, 245), (655, 320), (915, 320),
            (1125, 255), (1385, 315), (1620, 255), (1895, 310), (2170, 245),
        )
    ],
    [pygame.Rect(x, 360, 30, 30) for x in (950, 1240, 1780, 2180, 2330)],
    [pygame.Rect(x, 360, 30, 30) for x in (1030, 1510, 2010, 2330)],
    [pygame.Rect(x, 360, 30, 30) for x in (1180, 1780, 2250)],
    [pygame.Rect(x, 360, 30, 30) for x in (1510, 2180)],
    [],
]
LEVEL_STAR_POSITIONS = [
    [(235, 279), (925, 289), (1670, 224)],
    [(300, 269), (1215, 214), (1715, 214)],
    [(220, 285), (900, 295), (1640, 230)],
    [(300, 269), (1195, 214), (1720, 214)],
    [(285, 269), (1160, 214), (1690, 214)],
    [(250, 279), (1110, 224), (1690, 224)],
    [(300, 279), (1215, 224), (1900, 279)],
    [(250, 279), (1160, 224), (1715, 224)],
    [(300, 279), (1200, 224), (1880, 279)],
    [],
]
LEVEL_ENEMY_SPAWNS = [
    [],
    [],
    [],
    [],
    [(535, 354, 450, 600, 95)],
    [(535, 354, 450, 620, 100), (1400, 279, 1360, 1460, 105)],
    [(535, 354, 450, 620, 110), (900, 354, 850, 920, 115),
     (1400, 279, 1360, 1460, 120)],
    [(535, 354, 450, 620, 120), (900, 354, 850, 920, 125),
     (1400, 279, 1360, 1460, 130), (2030, 354, 1990, 2070, 135)],
    [(535, 354, 450, 620, 130), (900, 354, 850, 920, 135),
     (1400, 279, 1360, 1460, 140), (1700, 354, 1630, 1740, 145),
     (2030, 354, 1990, 2070, 150)],
    [],
]
GROUND_POUND_POWERUP = pygame.Rect(120, 352, 24, 30)
DOUBLE_JUMP_POWERUP = pygame.Rect(1728, 225, 24, 30)
DOUBLE_JUMP_STAR_REQUIREMENT = 6
BOSS_START = (1900, 210)
BOSS_HEALTH_MAX = 6
MISSILE_SPEED = 520
BOSS_SPIKE_SPEED = 210
HIGHSCORE_FILE = Path(__file__).with_name("platformer_highscores.json")
NO_TIME_TEXT = "--:--.---"


def format_time(seconds):
    total_ms = int(seconds * 1000)
    minutes, remainder = divmod(total_ms,60000)
    whole_seconds, milliseconds = divmod(remainder,1000)
    return f"{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def format_record(seconds):
    """Like format_time, but shows --:--.--- when no record exists yet."""
    return NO_TIME_TEXT if seconds is None else format_time(seconds)


def load_all_time_high_score():
    try:
        data = json.loads(HIGHSCORE_FILE.read_text(encoding="utf-8"))
        score = data.get("all_time_high_score")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            if math.isfinite(score) and score >= 0:
                return float(score)
    except (OSError, ValueError, TypeError):
        pass
    return None


def save_all_time_high_score(seconds):
    data = {"all_time_high_score": seconds}
    # indent belongs to json.dumps(), not Path.write_text().
    try:
        HIGHSCORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass

def draw_cloud(surface, x, y):
    cloud_color = (250, 253, 255)
    pygame.draw.circle(surface, cloud_color, (x, y), 22)
    pygame.draw.circle(surface, cloud_color, (x + 24, y - 10), 28)
    pygame.draw.circle(surface, cloud_color, (x + 52, y), 22)
    pygame.draw.rect(surface, cloud_color, (x - 1, y, 54, 20))


def draw_platform(surface, rect):
    pygame.draw.rect(surface, (102, 65, 54), rect, border_radius=7)
    pygame.draw.rect(
        surface, (119, 78, 57), (rect.x, rect.y + 8, rect.width, rect.height - 8),
        border_radius=5,
    )
    pygame.draw.rect(
        surface, (105, 204, 104), (rect.x, rect.y, rect.width, 12),
        border_radius=6,
    )
    pygame.draw.line(
        surface, (174, 231, 129), (rect.x + 8, rect.y + 3),
        (rect.right - 8, rect.y + 3), 2,
    )
    for pebble_x in range(rect.x + 18, rect.right - 8, 42):
        pygame.draw.circle(surface, (151, 103, 73), (pebble_x, rect.y + 18), 2)


def draw_spike(surface, rect):
    points = [
        (rect.left, rect.bottom),
        (rect.centerx, rect.top),
        (rect.right, rect.bottom),
    ]
    pygame.draw.polygon(surface, (190, 53, 66), points)
    pygame.draw.polygon(surface, (255, 133, 111), points, 2)


def draw_star(surface, center, radius=12, color=(255, 198, 57)):
    points = []
    for point_index in range(10):
        point_radius = radius if point_index % 2 == 0 else radius * 0.48
        angle = -math.pi / 2 + point_index * math.pi / 5
        points.append((
            round(center[0] + math.cos(angle) * point_radius),
            round(center[1] + math.sin(angle) * point_radius),
        ))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 239, 155), points, 2)


def draw_enemy(surface, rect):
    pygame.draw.ellipse(surface, (74, 49, 112), rect)
    pygame.draw.ellipse(surface, (139, 91, 190), rect.inflate(-6, -8))
    pygame.draw.circle(surface, WHITE, (rect.x + 11, rect.y + 13), 4)
    pygame.draw.circle(surface, WHITE, (rect.x + 22, rect.y + 13), 4)
    pygame.draw.circle(surface, DARK, (rect.x + 12, rect.y + 14), 2)
    pygame.draw.circle(surface, DARK, (rect.x + 23, rect.y + 14), 2)


def draw_powerup(surface, rect, locked=False):
    background = (112, 121, 134) if locked else (77, 165, 231)
    outline = (190, 197, 207) if locked else (195, 238, 255)
    bolt_color = (215, 219, 224) if locked else WHITE
    pygame.draw.rect(surface, background, rect, border_radius=8)
    pygame.draw.rect(surface, outline, rect, 2, border_radius=8)
    pygame.draw.polygon(
        surface, bolt_color,
        [(rect.centerx, rect.y + 5), (rect.x + 7, rect.y + 16),
         (rect.centerx - 2, rect.y + 16), (rect.centerx - 5, rect.bottom - 5),
         (rect.right - 6, rect.y + 13), (rect.centerx + 3, rect.y + 13)],
    )


def draw_boss(surface, rect):
    pygame.draw.polygon(
        surface, (248, 155, 78),
        [(rect.x + 18, rect.y + 16), (rect.x + 5, rect.y - 3),
         (rect.x + 36, rect.y + 9)],
    )
    pygame.draw.polygon(
        surface, (248, 155, 78),
        [(rect.right - 18, rect.y + 16), (rect.right - 5, rect.y - 3),
         (rect.right - 36, rect.y + 9)],
    )
    pygame.draw.ellipse(surface, (91, 49, 105), rect)
    pygame.draw.ellipse(surface, (155, 76, 147), rect.inflate(-12, -12))
    pygame.draw.circle(surface, WHITE, (rect.x + 34, rect.y + 34), 9)
    pygame.draw.circle(surface, WHITE, (rect.right - 34, rect.y + 34), 9)
    pygame.draw.circle(surface, DARK, (rect.x + 36, rect.y + 35), 4)
    pygame.draw.circle(surface, DARK, (rect.right - 32, rect.y + 35), 4)
    pygame.draw.arc(
        surface, DARK, (rect.x + 30, rect.y + 43, rect.width - 60, 23),
        0, math.pi, 3,
    )


def draw_missile(surface, position, target):
    direction = target - position
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    direction = direction.normalize()
    side = pygame.Vector2(-direction.y, direction.x)
    nose = position + direction * 16
    tail = position - direction * 12
    points = [
        nose,
        tail + side * 6,
        tail + side * 3,
        tail - side * 3,
        tail - side * 6,
    ]
    pixel_points = [(round(point.x), round(point.y)) for point in points]
    pygame.draw.polygon(surface, (255, 207, 80), pixel_points)
    pygame.draw.polygon(surface, (110, 71, 44), pixel_points, 2)
    pygame.draw.line(
        surface, (255, 112, 68),
        (round((tail - direction * 5).x), round((tail - direction * 5).y)),
        (round((tail - direction * 11).x), round((tail - direction * 11).y)), 3,
    )


def draw_homing_spike(surface, position, velocity):
    direction = velocity.normalize() if velocity.length_squared() else pygame.Vector2(1, 0)
    side = pygame.Vector2(-direction.y, direction.x)
    points = [
        position + direction * 13,
        position + side * 6 - direction * 7,
        position - side * 6 - direction * 7,
    ]
    pixel_points = [(round(point.x), round(point.y)) for point in points]
    pygame.draw.polygon(surface, (210, 54, 76), pixel_points)
    pygame.draw.polygon(surface, (255, 178, 138), pixel_points, 2)


def draw_background(surface, elapsed, camera_x):
    sky_colors = ((115, 190, 235), (154, 215, 239), (207, 235, 237))
    for band in range(15):
        color = sky_colors[min(band // 5, len(sky_colors) - 1)]
        pygame.draw.rect(surface, color, (0, band * 30, WIDTH, 30))

    pygame.draw.circle(surface, (255, 232, 151), (710, 82), 49)
    pygame.draw.circle(surface, (255, 218, 105), (710, 82), 35)
    pygame.draw.circle(surface, (255, 241, 181), (700, 71), 9)

    distant_hills = [
        (0, 300), (110, 190), (225, 300), (355, 175), (510, 310),
        (650, 205), (800, 300), (800, HEIGHT), (0, HEIGHT),
    ]
    close_hills = [
        (0, 330), (135, 245), (280, 335), (445, 230), (620, 340),
        (750, 260), (800, 300), (800, HEIGHT), (0, HEIGHT),
    ]
    for shift in (-WIDTH, 0, WIDTH):
        distant_shift = shift - int(camera_x * 0.2) % WIDTH
        close_shift = shift - int(camera_x * 0.4) % WIDTH
        pygame.draw.polygon(
            surface, (159, 207, 190),
            [(x + distant_shift, y) for x, y in distant_hills],
        )
        pygame.draw.polygon(
            surface, (116, 190, 151),
            [(x + close_shift, y) for x, y in close_hills],
        )

    cloud_one_x = int((90 + elapsed * 14) % (WIDTH + 100)) - 50
    cloud_two_x = int((475 + elapsed * 9) % (WIDTH + 100)) - 50
    draw_cloud(surface, cloud_one_x, 105)
    draw_cloud(surface, cloud_two_x, 145)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("A Fun Platformer Game")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 32)
    controls_font = pygame.font.Font(None, 23)
    menu_button = pygame.Rect(WIDTH - 134, 60, 116, 38)

    # ---- Level menu layout (everything fits inside the 800x450 window) ----
    # Left column : speedrun card, Resume button.
    # Right column: beaten-level buttons (2 x 5 grid).
    # Bottom      : Close button.
    # The same rects are used for drawing AND for mouse hit-testing.
    menu_panel = pygame.Rect(40, 30, 720, 390)
    menu_speedrun_card = pygame.Rect(70, 86, 280, 188)
    menu_continue_button = pygame.Rect(70, 292, 280, 50)
    menu_close_button = pygame.Rect(WIDTH // 2 - 60, 366, 120, 40)
    menu_levels_header_center = (556, 102)
    menu_level_buttons = {
        index: pygame.Rect(
            386 + (index % 2) * 176,
            120 + (index // 2) * 46,
            164,
            38,
        )
        for index in range(len(LEVEL_SPIKES))
    }

    platforms = [
        pygame.Rect(0, 390, WORLD_WIDTH, 60),
        pygame.Rect(145, 310, 180, 24),
        pygame.Rect(405, 245, 160, 24),
        pygame.Rect(615, 320, 135, 24),
        pygame.Rect(850, 320, 150, 24),
        pygame.Rect(1080, 255, 170, 24),
        pygame.Rect(1340, 315, 155, 24),
        pygame.Rect(1580, 255, 180, 24),
        pygame.Rect(1850, 310, 150, 24),
        pygame.Rect(2100, 245, 180, 24),
    ]
    level_index = 0
    campaign_level_index = 0
    beaten_levels = set()
    replaying_level = False
    menu_open = False
    checkpoint = (65, 338)
    collected_stars = set()
    collected_star_indices_by_level = [
        set() for _ in LEVEL_STAR_POSITIONS
    ]
    level_start_collected_star_indices = [
        stars.copy() for stars in collected_star_indices_by_level
    ]
    spent_star_ids_this_level = set()
    total_stars = 0
    total_enemies_stomped = 0
    level_start_total_enemies_stomped = 0
    player = pygame.Rect(65, 338, 38, 52)
    vertical_speed = 0
    on_ground = True
    coyote_timer = 0.12
    jump_buffer_timer = 0
    facing_direction = 1
    elapsed = 0
    speedrun_timer = 0.0
    timer_running = True
    current_game_high_score = None
    all_time_high_score = load_all_time_high_score()
    level_complete = False
    has_ground_pound = False
    ground_pounding = False
    has_double_jump = False
    double_jump_unlocked = False
    double_jump_available = False
    health = 3
    invulnerability_timer = 0
    enemy_spawns = LEVEL_ENEMY_SPAWNS[level_index].copy()
    enemies = [
        pygame.Rect(spawn[0], spawn[1], 32, 36) for spawn in enemy_spawns
    ]
    enemy_directions = [1] * len(enemies)
    boss = pygame.Rect(*BOSS_START, 110, 100)
    boss_health = BOSS_HEALTH_MAX
    boss_direction = 1
    boss_vertical_speed = 0
    boss_shot_timer = random.uniform(1.5, 2.5)
    homing_spikes = []
    missile_position = None
    missile_target = None
    def finish_speedrun():
        nonlocal timer_running, current_game_high_score
        nonlocal all_time_high_score

        if replaying_level or not timer_running:
            return

        timer_running = False

        if(current_game_high_score is None or speedrun_timer < current_game_high_score):
            current_game_high_score = speedrun_timer

        if(all_time_high_score is None or speedrun_timer < all_time_high_score):
            all_time_high_score = speedrun_timer
            save_all_time_high_score(all_time_high_score)

    def start_level(index):
        nonlocal level_index, vertical_speed, on_ground, coyote_timer
        nonlocal jump_buffer_timer, level_complete, health, invulnerability_timer
        nonlocal double_jump_available, ground_pounding, total_stars
        nonlocal level_start_total_enemies_stomped
        nonlocal boss, boss_health, boss_direction
        nonlocal boss_vertical_speed, boss_shot_timer, missile_position
        nonlocal missile_target, enemy_spawns, enemies, enemy_directions
        nonlocal level_start_collected_star_indices, spent_star_ids_this_level

        level_index = index
        player.topleft = (65, 338)
        vertical_speed = 0
        on_ground = True
        coyote_timer = 0.12
        jump_buffer_timer = 0
        double_jump_available = False
        level_complete = False
        health = 3
        invulnerability_timer = 0
        ground_pounding = False
        collected_stars.clear()
        collected_stars.update(collected_star_indices_by_level[level_index])
        level_start_collected_star_indices = [
            stars.copy() for stars in collected_star_indices_by_level
        ]
        spent_star_ids_this_level = set()
        total_stars = sum(
            len(stars) for stars in collected_star_indices_by_level
        )
        level_start_total_enemies_stomped = total_enemies_stomped
        enemy_spawns = LEVEL_ENEMY_SPAWNS[level_index].copy()
        enemies = [
            pygame.Rect(spawn[0], spawn[1], 32, 36) for spawn in enemy_spawns
        ]
        enemy_directions = [1] * len(enemies)
        missile_position = None
        missile_target = None
        homing_spikes.clear()
        boss = pygame.Rect(*BOSS_START, 110, 100)
        boss_health = BOSS_HEALTH_MAX
        boss_direction = 1
        boss_vertical_speed = 0
        boss_shot_timer = random.uniform(1.5, 2.5)

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000
        elapsed += delta_time
        camera_x = max(0, min(player.centerx - WIDTH // 2, WORLD_WIDTH - WIDTH))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not menu_open:
                if not level_complete:
                    if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        jump_buffer_timer = 0.15
                    elif (
                        event.key in (pygame.K_s, pygame.K_DOWN)
                        and has_ground_pound
                        and level_index != 9
                        and not on_ground
                    ):
                        ground_pounding = True
                        vertical_speed = 1100
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_open:
                    if menu_close_button.collidepoint(event.pos):
                        menu_open = False
                    elif menu_continue_button.collidepoint(event.pos):
                        if replaying_level:
                            replaying_level = False
                            start_level(campaign_level_index)
                        menu_open = False
                    else:
                        for selected_level, button_rect in menu_level_buttons.items():
                            if (
                                selected_level in beaten_levels
                                and button_rect.collidepoint(event.pos)
                            ):
                                replaying_level = True
                                start_level(selected_level)
                                menu_open = False
                                break
                elif menu_button.collidepoint(event.pos):
                    menu_open = True
                elif (
                    level_index == 9
                    and not level_complete
                    and missile_position is None
                    and boss_health > 0
                ):
                    mouse_x, mouse_y = event.pos
                    missile_position = pygame.Vector2(
                        player.centerx, player.centery
                    )
                    missile_target = pygame.Vector2(mouse_x + camera_x, mouse_y)

        spikes = LEVEL_SPIKES[level_index]
        star_positions = LEVEL_STAR_POSITIONS[level_index]
        star_rects = [
            pygame.Rect(x - 12, y - 12, 24, 24) for x, y in star_positions
        ]

        if not level_complete and not menu_open:
            if timer_running:
                speedrun_timer += delta_time
            invulnerability_timer = max(0, invulnerability_timer - delta_time)
            if on_ground:
                coyote_timer = 0.12
            else:
                coyote_timer = max(0, coyote_timer - delta_time)
            jump_buffer_timer = max(0, jump_buffer_timer - delta_time)
            if jump_buffer_timer > 0:
                if coyote_timer > 0:
                    vertical_speed = -620
                    on_ground = False
                    coyote_timer = 0
                    jump_buffer_timer = 0
                    double_jump_available = has_double_jump
                elif (
                    has_double_jump
                    and double_jump_available
                    and total_stars > 0
                ):
                    star_to_spend = None
                    level_search_order = [level_index] + [
                        index
                        for index in range(len(collected_star_indices_by_level))
                        if index != level_index
                    ]
                    for star_level in level_search_order:
                        if collected_star_indices_by_level[star_level]:
                            star_index = next(
                                iter(collected_star_indices_by_level[star_level])
                            )
                            star_to_spend = (star_level, star_index)
                            break
                    if star_to_spend is None:
                        raise RuntimeError(
                            "Star inventory is inconsistent with its total."
                        )
                    star_level, star_index = star_to_spend
                    collected_star_indices_by_level[star_level].remove(
                        star_index
                    )
                    spent_star_ids_this_level.add(star_to_spend)
                    total_stars -= 1
                    vertical_speed = -620
                    jump_buffer_timer = 0
                    double_jump_available = False
                    ground_pounding = False

            keys = pygame.key.get_pressed()
            horizontal_direction = int(
                keys[pygame.K_d] or keys[pygame.K_RIGHT]
            ) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
            if horizontal_direction:
                facing_direction = horizontal_direction
            player.x += round(horizontal_direction * 300 * delta_time)
            player.left = max(0, player.left)
            player.right = min(WORLD_WIDTH, player.right)

            for platform in platforms:
                if player.colliderect(platform):
                    if horizontal_direction > 0:
                        player.right = platform.left
                    elif horizontal_direction < 0:
                        player.left = platform.right

            vertical_speed += 1800 * delta_time
            previous_top = player.top
            previous_bottom = player.bottom
            player.y += round(vertical_speed * delta_time)
            hit_spike = any(player.colliderect(spike) for spike in spikes)

            for enemy_index, (enemy, spawn) in enumerate(zip(enemies, enemy_spawns)):
                enemy.x += round(
                    enemy_directions[enemy_index] * spawn[4] * delta_time
                )
                if enemy.left <= spawn[2]:
                    enemy.left = spawn[2]
                    enemy_directions[enemy_index] = 1
                elif enemy.right >= spawn[3]:
                    enemy.right = spawn[3]
                    enemy_directions[enemy_index] = -1

            if level_index == 9 and boss_health > 0:
                previous_boss_top = boss.top
                previous_boss_bottom = boss.bottom
                boss.x += round(boss_direction * 90 * delta_time)
                for platform in platforms:
                    if boss.colliderect(platform):
                        if boss_direction > 0:
                            boss.right = platform.left
                        else:
                            boss.left = platform.right
                        boss_direction *= -1
                if boss.left <= 0:
                    boss.left = 0
                    boss_direction = 1
                elif boss.right >= WORLD_WIDTH:
                    boss.right = WORLD_WIDTH
                    boss_direction = -1

                boss_vertical_speed += 1400 * delta_time
                boss.y += round(boss_vertical_speed * delta_time)
                for platform in platforms:
                    overlaps_horizontally = (
                        boss.left < platform.right and boss.right > platform.left
                    )
                    if not overlaps_horizontally:
                        continue
                    if (
                        boss_vertical_speed > 0
                        and previous_boss_bottom <= platform.top
                        and boss.bottom >= platform.top
                    ):
                        boss.bottom = platform.top
                        boss_vertical_speed = 0
                    elif (
                        boss_vertical_speed < 0
                        and previous_boss_top >= platform.bottom
                        and boss.top <= platform.bottom
                    ):
                        boss.top = platform.bottom
                        boss_vertical_speed = 0

                boss_shot_timer -= delta_time
                if boss_shot_timer <= 0:
                    shot_direction = pygame.Vector2(
                        player.centerx - boss.centerx,
                        player.centery - boss.centery,
                    )
                    if shot_direction.length_squared() == 0:
                        shot_direction = pygame.Vector2(-1, 0)
                    shot_velocity = shot_direction.normalize() * BOSS_SPIKE_SPEED
                    homing_spikes.append(
                        [pygame.Vector2(boss.center), shot_velocity]
                    )
                    boss_shot_timer = random.uniform(1.5, 2.5)

                for spike_index in range(len(homing_spikes) - 1, -1, -1):
                    spike_position, spike_velocity = homing_spikes[spike_index]
                    target_direction = pygame.Vector2(
                        player.centerx - spike_position.x,
                        player.centery - spike_position.y,
                    )
                    if target_direction.length_squared() > 0:
                        desired_velocity = (
                            target_direction.normalize() * BOSS_SPIKE_SPEED
                        )
                        spike_velocity = spike_velocity.lerp(
                            desired_velocity, min(delta_time * 1.8, 1)
                        )
                    spike_position += spike_velocity * delta_time
                    homing_spikes[spike_index] = [
                        spike_position, spike_velocity
                    ]
                    spike_rect = pygame.Rect(
                        round(spike_position.x - 7),
                        round(spike_position.y - 7),
                        14,
                        14,
                    )
                    hits_block = any(
                        spike_rect.colliderect(platform)
                        for platform in platforms
                    )
                    hits_player = spike_rect.colliderect(player)
                    if hits_player and invulnerability_timer == 0:
                        health -= 1
                        invulnerability_timer = 1
                        vertical_speed = -300
                    if (
                        hits_block
                        or hits_player
                        or not (0 <= spike_position.x <= WORLD_WIDTH)
                        or spike_position.y < -100
                        or spike_position.y > HEIGHT + 100
                    ):
                        del homing_spikes[spike_index]

                camera_x = max(
                    0, min(player.centerx - WIDTH // 2, WORLD_WIDTH - WIDTH)
                )
                mouse_x, mouse_y = pygame.mouse.get_pos()
                missile_target = pygame.Vector2(mouse_x + camera_x, mouse_y)
                if missile_position is not None:
                    to_target = missile_target - missile_position
                    reached_target = to_target.length_squared() == 0
                    if to_target.length_squared() > 0:
                        distance = to_target.length()
                        travel = MISSILE_SPEED * delta_time
                        if distance <= travel:
                            missile_position = missile_target.copy()
                            reached_target = True
                        else:
                            missile_position += to_target.normalize() * travel
                    missile_rect = pygame.Rect(
                        round(missile_position.x - 12),
                        round(missile_position.y - 6),
                        24,
                        12,
                    )
                    if missile_rect.colliderect(boss):
                        boss_health = max(0, boss_health - 1)
                        missile_position = None
                        missile_target = None
                        if boss_health == 0:
                            finish_speedrun()
                            level_complete = True
                            homing_spikes.clear()
                    elif reached_target:
                        missile_position = None
                        missile_target = None

            on_ground = False
            if not hit_spike:
                for enemy_index, enemy in enumerate(enemies):
                    stomp_contact = (
                        ground_pounding
                        and vertical_speed > 0
                        and player.inflate(16, 6).colliderect(enemy)
                    )
                    if stomp_contact:
                        del enemies[enemy_index]
                        del enemy_spawns[enemy_index]
                        del enemy_directions[enemy_index]
                        total_enemies_stomped += 1
                        ground_pounding = False
                        vertical_speed = -360
                        break
                    if player.colliderect(enemy) and invulnerability_timer == 0:
                        health -= 1
                        invulnerability_timer = 1
                        if player.centerx < enemy.centerx:
                            player.right = enemy.left
                        else:
                            player.left = enemy.right
                        vertical_speed = -350
                        ground_pounding = False
                        break

            if (
                level_index == 9
                and boss_health > 0
                and player.colliderect(boss)
                and invulnerability_timer == 0
            ):
                health -= 1
                invulnerability_timer = 1
                if player.centerx < boss.centerx:
                    player.right = boss.left
                else:
                    player.left = boss.right
                vertical_speed = -350

            landed = False
            for platform in platforms:
                overlaps_horizontally = (
                    player.left < platform.right and player.right > platform.left
                )
                if not overlaps_horizontally:
                    continue

                if (
                    vertical_speed > 0
                    and previous_bottom <= platform.top
                    and player.bottom >= platform.top
                ):
                    player.bottom = platform.top
                    vertical_speed = 0
                    on_ground = True
                    landed = True
                elif (
                    vertical_speed < 0
                    and previous_top >= platform.bottom
                    and player.top <= platform.bottom
                ):
                    player.top = platform.bottom
                    vertical_speed = 0
                    ground_pounding = False
            if landed:
                ground_pounding = False

            died = health <= 0 or hit_spike
            if died:
                player.topleft = checkpoint
                vertical_speed = 0
                on_ground = True
                coyote_timer = 0.12
                jump_buffer_timer = 0
                double_jump_available = False
                collected_star_indices_by_level = [
                    stars.copy()
                    for stars in level_start_collected_star_indices
                ]
                total_stars = sum(
                    len(stars) for stars in collected_star_indices_by_level
                )
                collected_stars.clear()
                collected_stars.update(
                    collected_star_indices_by_level[level_index]
                )
                total_enemies_stomped = level_start_total_enemies_stomped
                health = 3
                invulnerability_timer = 0
                ground_pounding = False
                enemy_spawns = LEVEL_ENEMY_SPAWNS[level_index].copy()
                enemies = [
                    pygame.Rect(spawn[0], spawn[1], 32, 36)
                    for spawn in enemy_spawns
                ]
                enemy_directions = [1] * len(enemies)
                missile_position = None
                missile_target = None
                spent_star_ids_this_level = set()
                level_start_collected_star_indices = [
                    stars.copy()
                    for stars in collected_star_indices_by_level
                ]
                if level_index == 9:
                    boss = pygame.Rect(*BOSS_START, 110, 100)
                    boss_health = BOSS_HEALTH_MAX
                    boss_direction = 1
                    boss_vertical_speed = 0
                    boss_shot_timer = random.uniform(1.5, 2.5)
                    homing_spikes.clear()
            else:
                if (
                    level_index == 4
                    and not has_ground_pound
                    and player.colliderect(GROUND_POUND_POWERUP)
                ):
                    has_ground_pound = True
                for star_index, star_rect in enumerate(star_rects):
                    if (
                        star_index not in collected_stars
                        and player.colliderect(star_rect)
                    ):
                        collected_stars.add(star_index)
                        collected_star_indices_by_level[level_index].add(star_index)
                        total_stars += 1
                        if total_stars >= DOUBLE_JUMP_STAR_REQUIREMENT:
                            double_jump_unlocked = True
                if (
                    level_index == 1
                    and double_jump_unlocked
                    and not has_double_jump
                    and player.colliderect(DOUBLE_JUMP_POWERUP)
                ):
                    has_double_jump = True
                    double_jump_available = not on_ground

            if player.right >= WORLD_WIDTH:
                if replaying_level:
                    replaying_level = False
                    start_level(campaign_level_index)
                elif level_index + 1 < len(LEVEL_SPIKES):
                    beaten_levels.add(level_index)
                    level_index += 1
                    campaign_level_index = level_index
                    checkpoint = (65, 338)
                    level_start_total_enemies_stomped = total_enemies_stomped
                    player.topleft = checkpoint
                    vertical_speed = 0
                    on_ground = True
                    coyote_timer = 0.12
                    jump_buffer_timer = 0
                    double_jump_available = False
                    collected_stars.clear()
                    collected_stars.update(
                        collected_star_indices_by_level[level_index]
                    )
                    level_start_collected_star_indices = [
                        stars.copy()
                        for stars in collected_star_indices_by_level
                    ]
                    spent_star_ids_this_level = set()
                    health = 3
                    invulnerability_timer = 0
                    ground_pounding = False
                    enemy_spawns = LEVEL_ENEMY_SPAWNS[level_index].copy()
                    enemies = [
                        pygame.Rect(spawn[0], spawn[1], 32, 36)
                        for spawn in enemy_spawns
                    ]
                    enemy_directions = [1] * len(enemies)
                    missile_position = None
                    missile_target = None
                    if level_index == 9:
                        boss = pygame.Rect(*BOSS_START, 110, 100)
                        boss_health = BOSS_HEALTH_MAX
                        boss_direction = 1
                        boss_vertical_speed = 0
                        boss_shot_timer = random.uniform(1.5, 2.5)
                        homing_spikes.clear()
                else:
                    if boss_health <= 0:
                        beaten_levels.add(level_index)
                        level_complete = True

        spikes = LEVEL_SPIKES[level_index]
        star_positions = LEVEL_STAR_POSITIONS[level_index]
        camera_x = max(0, min(player.centerx - WIDTH // 2, WORLD_WIDTH - WIDTH))
        draw_background(screen, elapsed, camera_x)

        for platform in platforms:
            screen_platform = platform.move(-camera_x, 0)
            if screen_platform.right >= 0 and screen_platform.left <= WIDTH:
                draw_platform(screen, screen_platform)

        if level_index == 4 and not has_ground_pound:
            screen_powerup = GROUND_POUND_POWERUP.move(-camera_x, 0)
            if -screen_powerup.width <= screen_powerup.x <= WIDTH:
                draw_powerup(screen, screen_powerup)
        if level_index == 1 and not has_double_jump:
            screen_powerup = DOUBLE_JUMP_POWERUP.move(-camera_x, 0)
            if -screen_powerup.width <= screen_powerup.x <= WIDTH:
                draw_powerup(
                    screen, screen_powerup, locked=not double_jump_unlocked
                )

        for spike in spikes:
            screen_spike = spike.move(-camera_x, 0)
            if screen_spike.right >= 0 and screen_spike.left <= WIDTH:
                draw_spike(screen, screen_spike)

        for enemy in enemies:
            screen_enemy = enemy.move(-camera_x, 0)
            if -screen_enemy.width <= screen_enemy.x <= WIDTH:
                draw_enemy(screen, screen_enemy)

        if level_index == 9 and boss_health > 0:
            screen_boss = boss.move(-camera_x, 0)
            if -screen_boss.width <= screen_boss.x <= WIDTH:
                draw_boss(screen, screen_boss)
            pygame.draw.rect(screen, (65, 47, 66), (WIDTH - 224, 20, 204, 24), border_radius=8)
            pygame.draw.rect(screen, WHITE, (WIDTH - 224, 20, 204, 24), 2, border_radius=8)
            health_width = round(196 * boss_health / BOSS_HEALTH_MAX)
            pygame.draw.rect(
                screen, (221, 73, 100),
                (WIDTH - 220, 24, health_width, 16), border_radius=6,
            )
            screen.blit(
                controls_font.render("BOSS", True, WHITE), (WIDTH - 278, 23)
            )

        if level_index == 9:
            camera_offset = pygame.Vector2(camera_x, 0)
            for spike_position, spike_velocity in homing_spikes:
                draw_homing_spike(
                    screen, spike_position - camera_offset, spike_velocity
                )

        if missile_position is not None and missile_target is not None:
            camera_offset = pygame.Vector2(camera_x, 0)
            draw_missile(
                screen, missile_position - camera_offset,
                missile_target - camera_offset,
            )

        for star_index, (star_x, star_y) in enumerate(star_positions):
            if star_index not in collected_stars:
                screen_star = (round(star_x - camera_x), star_y)
                if -12 <= screen_star[0] <= WIDTH + 12:
                    draw_star(screen, screen_star)

        screen_player = player.move(-camera_x, 0)
        pygame.draw.ellipse(
            screen, (75, 106, 105),
            (screen_player.x + 2, screen_player.bottom - 3, screen_player.width - 4, 9),
        )
        player_outline = (
            (255, 238, 110) if invulnerability_timer > 0 else OUTLINE
        )
        pygame.draw.rect(
            screen, player_outline, screen_player.inflate(4, 4), border_radius=11
        )
        pygame.draw.rect(screen, PLAYER, screen_player, border_radius=9)
        pygame.draw.line(
            screen, (255, 151, 125),
            (screen_player.x + 8, screen_player.y + 7),
            (screen_player.x + 8, screen_player.bottom - 8), 3,
        )
        pygame.draw.ellipse(
            screen, (180, 65, 65),
            (screen_player.x + 4, screen_player.bottom - 9, 15, 9),
        )
        pygame.draw.ellipse(
            screen, (180, 65, 65),
            (screen_player.right - 19, screen_player.bottom - 9, 15, 9),
        )
        eye_x = screen_player.centerx + facing_direction * 6
        eye_y = screen_player.y + 16
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 5)
        pygame.draw.circle(
            screen, DARK, (eye_x + facing_direction * 2, eye_y), 2
        )
        if ground_pounding:
            pygame.draw.ellipse(
                screen, (94, 204, 255), screen_player.inflate(12, 8), 3
            )

        # HUD panel. Kept to 480px wide so it no longer covers the boss
        # health bar / "BOSS" label (x >= 522) or the speedrun timer stack.
        hud = pygame.Surface((480, 184), pygame.SRCALPHA)
        pygame.draw.rect(hud, (255, 255, 255, 215), hud.get_rect(), border_radius=16)
        pygame.draw.rect(hud, (255, 255, 255, 255), hud.get_rect(), 2, border_radius=16)
        hud.blit(
            title_font.render(f"LEVEL {level_index + 1}", True, OUTLINE), (14, 8)
        )
        hud.blit(
            controls_font.render(
                (
                    f"HP {health}/3"
                    if level_index == 9
                    else (
                        f"STARS {len(collected_star_indices_by_level[level_index])}/"
                        f"{len(star_positions)}   HP {health}/3   "
                    f"POUND {'READY' if has_ground_pound else 'LOCKED'}"
                    )
                ),
                True, OUTLINE
            ),
            (160, 13)
        )
        hud.blit(
            controls_font.render(
                f"TOTAL STARS {total_stars}   ENEMIES STOMPED {total_enemies_stomped}",
                True, OUTLINE,
            ),
            (14, 42),
        )
        hud.blit(
            controls_font.render(
                (
                    "Aim with mouse; click to fire missile"
                    if level_index == 9
                    else "Move: A/D or arrows   Jump: Space/W/Up   Pound: S/Down"
                ),
                True, DARK,
            ),
            (14, 68),
        )
        if level_index == 1 and not double_jump_unlocked:
            double_jump_message = (
                f"Collect {DOUBLE_JUMP_STAR_REQUIREMENT} total stars "
                "to unlock Double Jump"
            )
        elif level_index == 1 and not has_double_jump:
            double_jump_message = "Double Jump unlocked! Collect the blue power-up"
        elif has_double_jump:
            double_jump_message = (
                "Double Jump: press jump again in air (costs 1 star)"
            )
        else:
            double_jump_message = ""
        if double_jump_message:
            hud.blit(
                controls_font.render(double_jump_message, True, DARK), (14, 92)
            )
        screen.blit(hud, (18, 16))

        # Speedrun timer stack (top-right, under the LEVEL MENU button, so it
        # never overlaps the HUD panel or the boss health bar).
        timer_text = controls_font.render(
            f"TIME {format_time(speedrun_timer)}",
            True,
            OUTLINE,
        )
        timer_box = pygame.Rect(WIDTH - 218, 106, 200, 38)
        pygame.draw.rect(screen, WHITE, timer_box, border_radius=10)
        pygame.draw.rect(screen, OUTLINE, timer_box, 2, border_radius=10)
        screen.blit(
            timer_text,
            timer_text.get_rect(center=timer_box.center),
        )

        # Current game best time
        if current_game_high_score is not None:
            game_best_text = controls_font.render(
                f"GAME BEST {format_time(current_game_high_score)}",
                True,
                OUTLINE,
            )
            screen.blit(
                game_best_text,
                game_best_text.get_rect(topright=(WIDTH - 18, 152)),
            )

        # Persistent all-time best time
        if all_time_high_score is not None:
            all_time_text = controls_font.render(
                f"ALL-TIME BEST {format_time(all_time_high_score)}",
                True,
                OUTLINE,
            )
            screen.blit(
                all_time_text,
                all_time_text.get_rect(topright=(WIDTH - 18, 174)),
            )

        # Level-complete message
        if level_complete:
            message = title_font.render(
                "BOSS DEFEATED! ALL 10 LEVELS COMPLETE!",
                True,
                WHITE,
            )
            message_box = message.get_rect(
                center=(WIDTH // 2, HEIGHT // 2)
            )
            pygame.draw.rect(
                screen,
                OUTLINE,
                message_box.inflate(36, 24),
                border_radius=14,
            )
            screen.blit(message, message_box)

        # Level menu button
        pygame.draw.rect(
            screen,
            (255, 255, 255, 225),
            menu_button,
            border_radius=10,
        )
        pygame.draw.rect(
            screen, OUTLINE, menu_button, 2, border_radius=10
        )
        menu_label = controls_font.render(
            "LEVEL MENU", True, OUTLINE
        )
        screen.blit(
            menu_label,
            menu_label.get_rect(center=menu_button.center),
        )

        # Level menu overlay (always drawn last so nothing can cover it)
        if menu_open:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((24, 34, 47, 170))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(
                screen,
                (248, 250, 252),
                menu_panel,
                border_radius=18,
            )
            pygame.draw.rect(
                screen, OUTLINE, menu_panel, 3, border_radius=18
            )

            menu_title = title_font.render("LEVEL MENU", True, OUTLINE)
            screen.blit(
                menu_title,
                menu_title.get_rect(center=(WIDTH // 2, menu_panel.y + 26)),
            )

            # Vertical divider between the two columns
            pygame.draw.line(
                screen, (200, 208, 216),
                (368, menu_speedrun_card.y + 4),
                (368, menu_continue_button.bottom), 2,
            )

            # ---- Speedrun times card (left column) ----
            pygame.draw.rect(
                screen,
                (232, 244, 250),
                menu_speedrun_card,
                border_radius=12,
            )
            pygame.draw.rect(
                screen, OUTLINE, menu_speedrun_card, 2, border_radius=12
            )
            speedrun_title = title_font.render(
                "SPEEDRUN TIMES", True, OUTLINE
            )
            screen.blit(
                speedrun_title,
                speedrun_title.get_rect(
                    center=(
                        menu_speedrun_card.centerx,
                        menu_speedrun_card.y + 22,
                    )
                ),
            )
            pygame.draw.line(
                screen, (135, 153, 168),
                (menu_speedrun_card.x + 16, menu_speedrun_card.y + 42),
                (menu_speedrun_card.right - 16, menu_speedrun_card.y + 42),
                2,
            )

            speedrun_rows = (
                ("Current Run", format_time(speedrun_timer), True),
                (
                    "Session Best",
                    format_record(current_game_high_score),
                    current_game_high_score is not None,
                ),
                (
                    "All-Time Best",
                    format_record(all_time_high_score),
                    all_time_high_score is not None,
                ),
            )
            for row_index, (row_label, row_value, has_value) in enumerate(
                speedrun_rows
            ):
                row_y = menu_speedrun_card.y + 70 + row_index * 42
                label_surface = controls_font.render(
                    f"{row_label}:", True, DARK
                )
                value_surface = controls_font.render(
                    row_value,
                    True,
                    OUTLINE if has_value else (120, 130, 140),
                )
                screen.blit(
                    label_surface,
                    label_surface.get_rect(
                        midleft=(menu_speedrun_card.x + 16, row_y)
                    ),
                )
                screen.blit(
                    value_surface,
                    value_surface.get_rect(
                        midright=(menu_speedrun_card.right - 16, row_y)
                    ),
                )

            # ---- Resume / Return button (left column) ----
            pygame.draw.rect(
                screen,
                (204, 232, 245),
                menu_continue_button,
                border_radius=9,
            )
            pygame.draw.rect(
                screen,
                OUTLINE,
                menu_continue_button,
                2,
                border_radius=9,
            )

            continue_label = controls_font.render(
                (
                    f"Return to Level {campaign_level_index + 1}"
                    if replaying_level
                    else f"Resume Level {level_index + 1}"
                ),
                True,
                OUTLINE,
            )
            screen.blit(
                continue_label,
                continue_label.get_rect(
                    center=menu_continue_button.center
                ),
            )

            # ---- Beaten levels (right column) ----
            levels_header = title_font.render(
                "BEATEN LEVELS", True, OUTLINE
            )
            screen.blit(
                levels_header,
                levels_header.get_rect(center=menu_levels_header_center),
            )
            if not beaten_levels:
                empty_hint = controls_font.render(
                    "Beat a level to replay it here", True, DARK
                )
                screen.blit(
                    empty_hint,
                    empty_hint.get_rect(
                        center=(menu_levels_header_center[0], 231)
                    ),
                )

            for selected_level in sorted(beaten_levels):
                button_rect = menu_level_buttons[selected_level]

                pygame.draw.rect(
                    screen,
                    WHITE,
                    button_rect,
                    border_radius=8,
                )
                pygame.draw.rect(
                    screen,
                    (135, 153, 168),
                    button_rect,
                    2,
                    border_radius=8,
                )

                level_label = controls_font.render(
                    f"Level {selected_level + 1}",
                    True,
                    OUTLINE,
                )
                screen.blit(
                    level_label,
                    level_label.get_rect(
                        midleft=(button_rect.x + 10, button_rect.centery)
                    ),
                )

                for star_index in range(
                    len(LEVEL_STAR_POSITIONS[selected_level])
                ):
                    star_color = (
                        (255, 198, 57)
                        if star_index
                        in collected_star_indices_by_level[selected_level]
                        else (173, 183, 192)
                    )

                    draw_star(
                        screen,
                        (
                            button_rect.right - 68 + star_index * 20,
                            button_rect.centery,
                        ),
                        radius=7,
                        color=star_color,
                    )

            # ---- Close button (bottom centre) ----
            pygame.draw.rect(
                screen,
                (230, 232, 235),
                menu_close_button,
                border_radius=9,
            )
            pygame.draw.rect(
                screen,
                OUTLINE,
                menu_close_button,
                2,
                border_radius=9,
            )

            close_label = controls_font.render(
                "Close", True, OUTLINE
            )
            screen.blit(
                close_label,
                close_label.get_rect(
                    center=menu_close_button.center
                ),
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()