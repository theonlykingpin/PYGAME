import math
import os
import random
import pygame

# Initialize Pygame & Audio
pygame.init()
pygame.mixer.init()

# Game Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Arcade Edition")

# Colors
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (147, 112, 219)
DARK_PURPLE = (75, 0, 130)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 140)

# Clock & Fonts
clock = pygame.time.Clock()
FPS = 60

title_font = pygame.font.SysFont("Arial", 48, bold=True)
hud_font = pygame.font.SysFont("Arial", 22, bold=True)
sub_font = pygame.font.SysFont("Arial", 24)

# --- Asset Loader with Fallback ---
def load_sprite_safe(path, width, height, fallback_color):
    try:
        surf = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(surf, (width, height))
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

# Load Images (Falls back to colored blocks if images are missing)
player_img_raw = load_sprite_safe("assets/player.png", 40, 30, GREEN)
scout_img = load_sprite_safe("assets/scout.png", 24, 20, CYAN)
standard_img = load_sprite_safe("assets/standard.png", 36, 30, RED)
heavy_img = load_sprite_safe("assets/heavy.png", 52, 42, DARK_PURPLE)
boss_img = load_sprite_safe("assets/boss.png", 120, 50, PURPLE)
laser_img = load_sprite_safe("assets/laser.png", 4, 12, YELLOW)
boss_laser_img = load_sprite_safe("assets/boss_laser.png", 6, 14, ORANGE)

# --- High Score Persistence ---
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            return 0
    return 0

def save_high_score(new_high):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(new_high))

high_score = load_high_score()

# --- Parallax Starfield ---
stars = []
for _ in range(70):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(0.5, 1.2),
        "size": 1,
        "color": (120, 120, 160)
    })
for _ in range(30):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(2.0, 3.5),
        "size": 2,
        "color": (220, 230, 255)
    })

# --- Particles ---
particles = []

def create_explosion(x, y, count=20, color_palette=[RED, ORANGE, YELLOW]):
    for _ in range(count):
        angle = random.uniform(0, 6.28)
        speed = random.uniform(1.5, 5.5)
        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "radius": random.uniform(3.0, 6.0),
            "color": random.choice(color_palette),
            "life": random.randint(20, 40)
        })

def try_spawn_powerup(x, y):
    if random.random() < 0.35:
        p_type = random.choice(["HEAL", "DOUBLE", "BOMB"])
        powerups.append({"rect": pygame.Rect(x, y, 20, 20), "type": p_type})

def spawn_enemy():
    roll = random.random()
    if roll < 0.35:
        w, h = 24, 20
        return {
            "rect": pygame.Rect(random.randint(0, WIDTH - w), -h, w, h),
            "hp": 1, "max_hp": 1, "speed": 5.0, "color": CYAN,
            "score_val": 10, "type": "SCOUT", "img": scout_img
        }
    elif roll < 0.80:
        w, h = 36, 30
        return {
            "rect": pygame.Rect(random.randint(0, WIDTH - w), -h, w, h),
            "hp": 2, "max_hp": 2, "speed": 3.0, "color": RED,
            "score_val": 20, "type": "STANDARD", "img": standard_img
        }
    else:
        w, h = 52, 42
        return {
            "rect": pygame.Rect(random.randint(0, WIDTH - w), -h, w, h),
            "hp": 5, "max_hp": 5, "speed": 1.5, "color": DARK_PURPLE,
            "score_val": 50, "type": "HEAVY", "img": heavy_img
        }

# --- Game Globals & State ---
game_state = "START"
bomb_flash_timer = 0
current_angle = 0.0
MAX_TILT = 20.0
LEAN_SPEED = 0.15

def reset_game():
    global player_x, player_y, lives, bombs, double_shot_timer, score
    global lasers, boss_lasers, enemies, powerups, boss, next_boss_score, enemy_spawn_timer, bomb_flash_timer, current_angle

    player_x = WIDTH // 2 - 20
    player_y = HEIGHT - 60
    lives = 3
    bombs = 1
    double_shot_timer = 0
    score = 0
    bomb_flash_timer = 0
    current_angle = 0.0

    lasers = []
    boss_lasers = []
    enemies = []
    powerups = []

    boss = None
    next_boss_score = 500
    enemy_spawn_timer = 0

player_width, player_height = 40, 30
player_speed = 6
reset_game()

# --- Main Engine Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # 1. Background Starfield
    for star in stars:
        star["y"] += star["speed"]
        if star["y"] >= HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, star["color"], (int(star["x"]), int(star["y"])), star["size"])

    # 2. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "START":
                if event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = "PLAYING"

            elif game_state == "PLAYING":
                if event.key == pygame.K_SPACE:
                    if double_shot_timer > 0:
                        lasers.append(pygame.Rect(player_x + 6, player_y, 4, 12))
                        lasers.append(pygame.Rect(player_x + player_width - 10, player_y, 4, 12))
                    else:
                        lasers.append(pygame.Rect(player_x + player_width // 2 - 2, player_y, 4, 12))

                if (event.key == pygame.K_b or event.key == pygame.K_LSHIFT) and bombs > 0:
                    bombs -= 1
                    bomb_flash_timer = 10
                    boss_lasers.clear()
                    for enemy in enemies:
                        score += enemy["score_val"]
                        create_explosion(enemy["rect"].centerx, enemy["rect"].centery, count=25, color_palette=[YELLOW, ORANGE, WHITE])
                    enemies.clear()

                    if boss:
                        boss["hp"] -= 10
                        create_explosion(boss["rect"].centerx, boss["rect"].centery, count=40, color_palette=[PURPLE, YELLOW, WHITE])
                        if boss["hp"] <= 0:
                            score += 150
                            try_spawn_powerup(boss["rect"].centerx, boss["rect"].centery)
                            boss = None

            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_m:
                    game_state = "START"

    # ==========================================
    # STATE: START MENU
    # ==========================================
    if game_state == "START":
        t_text = title_font.render("SPACE SHOOTER", True, CYAN)
        start_text = sub_font.render("Press SPACE to Start", True, WHITE)
        controls_text = hud_font.render("Controls: SPACE = Shoot  |  B / SHIFT = Screen Bomb", True, GRAY)
        hs_text = hud_font.render(f"HIGH SCORE: {high_score}", True, YELLOW)

        screen.blit(t_text, (WIDTH // 2 - t_text.get_width() // 2, 160))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 280))
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 330))
        screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 380))

    # ==========================================
    # STATE: PLAYING
    # ==========================================
    elif game_state == "PLAYING":
        if double_shot_timer > 0:
            double_shot_timer -= 1

        target_angle = 0.0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if player_x > 0:
                player_x -= player_speed
            target_angle = MAX_TILT

        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if player_x < WIDTH - player_width:
                player_x += player_speed
            target_angle = -MAX_TILT

        current_angle += (target_angle - current_angle) * LEAN_SPEED
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        if score >= next_boss_score and boss is None:
            boss = {
                "rect": pygame.Rect(WIDTH // 2 - 60, 50, 120, 50),
                "hp": 30, "max_hp": 30, "dir": 1, "shoot_timer": 0
            }
            next_boss_score += 500

        if boss is None:
            enemy_spawn_timer += 1
            if enemy_spawn_timer > 35:
                enemies.append(spawn_enemy())
                enemy_spawn_timer = 0

        for laser in lasers[:]:
            laser.y -= 10
            if laser.bottom < 0:
                lasers.remove(laser)

        if boss:
            boss["rect"].x += 4 * boss["dir"]
            if boss["rect"].right >= WIDTH - 10 or boss["rect"].left <= 10:
                boss["dir"] *= -1

            boss["shoot_timer"] += 1
            if boss["shoot_timer"] >= 45:
                boss["shoot_timer"] = 0
                cx, cy = boss["rect"].centerx, boss["rect"].bottom
                boss_lasers.append({"rect": pygame.Rect(cx - 3, cy, 6, 14), "vx": 0, "vy": 6})
                boss_lasers.append({"rect": pygame.Rect(cx - 15, cy, 6, 14), "vx": -2, "vy": 6})
                boss_lasers.append({"rect": pygame.Rect(cx + 10, cy, 6, 14), "vx": 2, "vy": 6})

            for laser in lasers[:]:
                if boss["rect"].colliderect(laser):
                    lasers.remove(laser)
                    boss["hp"] -= 1
                    create_explosion(laser.centerx, laser.top, count=4, color_palette=[YELLOW, WHITE])
                    if boss["hp"] <= 0:
                        score += 150
                        create_explosion(boss["rect"].centerx, boss["rect"].centery, count=60, color_palette=[PURPLE, RED, ORANGE, YELLOW, WHITE])
                        try_spawn_powerup(boss["rect"].centerx - 20, boss["rect"].centery)
                        try_spawn_powerup(boss["rect"].centerx + 20, boss["rect"].centery)
                        boss = None
                        break

        for b_laser in boss_lasers[:]:
            b_laser["rect"].x += b_laser["vx"]
            b_laser["rect"].y += b_laser["vy"]

            if b_laser["rect"].colliderect(player_rect):
                lives -= 1
                create_explosion(player_rect.centerx, player_rect.centery, count=15, color_palette=[RED, ORANGE])
                boss_lasers.remove(b_laser)
                if lives <= 0:
                    game_state = "GAME_OVER"
                continue

            if b_laser["rect"].top > HEIGHT or b_laser["rect"].right < 0 or b_laser["rect"].left > WIDTH:
                boss_lasers.remove(b_laser)

        for p in powerups[:]:
            p["rect"].y += 3
            if p["rect"].colliderect(player_rect):
                if p["type"] == "HEAL" and lives < 3:
                    lives += 1
                elif p["type"] == "DOUBLE":
                    double_shot_timer = 300
                elif p["type"] == "BOMB" and bombs < 3:
                    bombs += 1

                p_color = CYAN if p["type"] == "HEAL" else MAGENTA if p["type"] == "DOUBLE" else YELLOW
                create_explosion(p["rect"].centerx, p["rect"].centery, count=12, color_palette=[p_color, WHITE])
                powerups.remove(p)
            elif p["rect"].top > HEIGHT:
                powerups.remove(p)

        for enemy in enemies[:]:
            enemy["rect"].y += enemy["speed"]

            if enemy["rect"].colliderect(player_rect):
                lives -= 1
                create_explosion(enemy["rect"].centerx, enemy["rect"].centery, count=25, color_palette=[RED, ORANGE, YELLOW])
                enemies.remove(enemy)
                if lives <= 0:
                    game_state = "GAME_OVER"
                continue

            for laser in lasers[:]:
                if enemy["rect"].colliderect(laser):
                    lasers.remove(laser)
                    enemy["hp"] -= 1

                    if enemy["hp"] <= 0:
                        score += enemy["score_val"]
                        p_count = 35 if enemy["type"] == "HEAVY" else 20
                        create_explosion(enemy["rect"].centerx, enemy["rect"].centery, count=p_count, color_palette=[enemy["color"], ORANGE, YELLOW])
                        try_spawn_powerup(enemy["rect"].centerx, enemy["rect"].centery)
                        enemies.remove(enemy)
                    else:
                        create_explosion(laser.centerx, laser.top, count=3, color_palette=[YELLOW, WHITE])
                    break

            if enemy["rect"].top > HEIGHT:
                enemies.remove(enemy)

        if score > high_score:
            high_score = score
            save_high_score(high_score)

        # Draw Player with Smooth Tilting
        rotated_player_img = pygame.transform.rotate(player_img_raw, current_angle)
        rotated_rect = rotated_player_img.get_rect(center=player_rect.center)
        screen.blit(rotated_player_img, rotated_rect)

        for laser in lasers:
            screen.blit(laser_img, laser)
        for b_laser in boss_lasers:
            screen.blit(boss_laser_img, b_laser["rect"])

        for enemy in enemies:
            e_rect = enemy["rect"]
            screen.blit(enemy["img"], e_rect)
            if enemy["max_hp"] > 1:
                bar_w, bar_h = e_rect.width, 4
                bar_x, bar_y = e_rect.x, e_rect.y - 8
                pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h))
                fill_w = int(bar_w * (enemy["hp"] / enemy["max_hp"]))
                if fill_w > 0:
                    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, bar_h))

        if boss:
            screen.blit(boss_img, boss["rect"])
            hp_bar_width, hp_bar_height = 400, 18
            hp_bar_x, hp_bar_y = (WIDTH - hp_bar_width) // 2, 15
            pygame.draw.rect(screen, (50, 50, 50), (hp_bar_x - 2, hp_bar_y - 2, hp_bar_width + 4, hp_bar_height + 4), border_radius=4)
            pygame.draw.rect(screen, (100, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            fill_width = int(hp_bar_width * (boss["hp"] / boss["max_hp"]))
            if fill_width > 0:
                pygame.draw.rect(screen, RED, (hp_bar_x, hp_bar_y, fill_width, hp_bar_height))

        for p in powerups:
            color = CYAN if p["type"] == "HEAL" else MAGENTA if p["type"] == "DOUBLE" else YELLOW
            pygame.draw.rect(screen, color, p["rect"], border_radius=3)

        # HUD
        score_txt = hud_font.render(f"Score: {score}", True, WHITE)
        lives_txt = hud_font.render(f"Lives: {'♥ ' * lives}", True, RED)
        bombs_txt = hud_font.render(f"Bombs: {'💣 ' * bombs}", True, YELLOW)
        hs_hud_txt = hud_font.render(f"High: {high_score}", True, YELLOW)

        screen.blit(score_txt, (10, 10))
        screen.blit(lives_txt, (10, 35))
        screen.blit(bombs_txt, (10, 60))
        screen.blit(hs_hud_txt, (WIDTH - hs_hud_txt.get_width() - 10, 10))

        if double_shot_timer > 0:
            buff_txt = hud_font.render(f"DOUBLE SHOT: {double_shot_timer // 60 + 1}s", True, MAGENTA)
            screen.blit(buff_txt, (10, 85))

        if bomb_flash_timer > 0:
            bomb_flash_timer -= 1
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(150)
            screen.blit(flash_surface, (0, 0))

    # ==========================================
    # STATE: GAME OVER
    # ==========================================
    elif game_state == "GAME_OVER":
        go_title = title_font.render("GAME OVER", True, RED)
        score_msg = sub_font.render(f"Final Score: {score}", True, WHITE)
        hs_msg = sub_font.render(f"Best Score: {high_score}", True, YELLOW)
        restart_msg = hud_font.render("Press [R] to Restart  |  [M] for Main Menu", True, GRAY)

        screen.blit(go_title, (WIDTH // 2 - go_title.get_width() // 2, 180))
        screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, 260))
        screen.blit(hs_msg, (WIDTH // 2 - hs_msg.get_width() // 2, 300))
        screen.blit(restart_msg, (WIDTH // 2 - restart_msg.get_width() // 2, 370))

    # Render Particles
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        p["radius"] *= 0.95
        if p["life"] <= 0 or p["radius"] <= 0.5:
            particles.remove(p)
        else:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), int(p["radius"]))

    pygame.display.flip()

pygame.quit()
