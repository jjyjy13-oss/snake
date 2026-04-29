import json
import math
import random
import sys
from pathlib import Path

import pygame

pygame.init()

# ── 화면/게임 설정 ─────────────────────────────────────
WIDTH, HEIGHT = 800, 600
GRID = 20
COLS = WIDTH // GRID
ROWS = HEIGHT // GRID
BASE_SPEED = 130
MIN_SPEED = 55
HIGH_SCORE_FILE = Path(__file__).with_name("snake_high_score.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Advanced Edition")
clock = pygame.time.Clock()

# ── 색상 팔레트 ────────────────────────────────────────
BG_DARK = (10, 14, 20)
BG_GRID = (18, 24, 32)
GREEN_HEAD = (80, 220, 120)
GREEN_BODY = (50, 180, 90)
GREEN_DARK = (30, 120, 60)
APPLE_RED = (255, 60, 60)
APPLE_HIGH = (255, 160, 140)
APPLE_DARK = (180, 20, 20)
APPLE_LEAF = (60, 200, 80)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 130)
CYAN = (80, 220, 240)
VIOLET = (210, 130, 255)

# ── 폰트 ──────────────────────────────────────────────
font_big = pygame.font.SysFont("Arial", 52, bold=True)
font_mid = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 20)
font_score = pygame.font.SysFont("Arial", 24, bold=True)


class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.07)
        self.size = random.uniform(3, 7)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= self.decay

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))


def load_high_score():
    if not HIGH_SCORE_FILE.exists():
        return 0
    try:
        data = json.loads(HIGH_SCORE_FILE.read_text(encoding="utf-8"))
        return int(data.get("high_score", 0))
    except (json.JSONDecodeError, OSError, ValueError):
        return 0


def save_high_score(value):
    try:
        HIGH_SCORE_FILE.write_text(json.dumps({"high_score": value}), encoding="utf-8")
    except OSError:
        pass


def draw_apple(surf, x, y, anim, special=False):
    cx = x * GRID + GRID // 2
    cy = y * GRID + GRID // 2
    bob = math.sin(anim * 3) * 2
    shadow_surf = pygame.Surface((GRID, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (2, 2, GRID - 4, 4))
    surf.blit(shadow_surf, (x * GRID, y * GRID + GRID - 4 + int(bob)))

    r = GRID // 2 - 1
    body_color = VIOLET if special else APPLE_RED
    deep_color = (130, 70, 190) if special else APPLE_DARK
    high_color = (240, 200, 255) if special else APPLE_HIGH
    pygame.draw.circle(surf, deep_color, (cx, int(cy + bob) + 1), r)
    pygame.draw.circle(surf, body_color, (cx, int(cy + bob)), r)
    pygame.draw.circle(surf, high_color, (cx - 3, int(cy + bob) - 3), r // 3)

    stem_x, stem_y = cx + 1, int(cy + bob) - r
    pygame.draw.line(surf, (100, 60, 20), (stem_x, stem_y), (stem_x + 3, stem_y - 5), 2)
    leaf_pts = [(stem_x + 3, stem_y - 4), (stem_x + 9, stem_y - 8), (stem_x + 5, stem_y - 2)]
    pygame.draw.polygon(surf, APPLE_LEAF, leaf_pts)


def draw_snake(surf, body, anim):
    n = len(body)
    for i, (bx, by) in enumerate(reversed(body)):
        idx = n - 1 - i
        is_head = idx == 0
        cx = bx * GRID + GRID // 2
        cy = by * GRID + GRID // 2
        t = idx / max(n - 1, 1)
        color = (
            int(GREEN_DARK[0] + (GREEN_BODY[0] - GREEN_DARK[0]) * (1 - t)),
            int(GREEN_DARK[1] + (GREEN_BODY[1] - GREEN_DARK[1]) * (1 - t)),
            int(GREEN_DARK[2] + (GREEN_BODY[2] - GREEN_DARK[2]) * (1 - t)),
        )
        if is_head:
            color = GREEN_HEAD
        rad = GRID // 2 - 1 if not is_head else GRID // 2
        pygame.draw.circle(surf, color, (cx, cy), rad)

        if not is_head and rad > 4:
            sc = tuple(max(0, c - 30) for c in color)
            pygame.draw.circle(surf, sc, (cx, cy), rad - 3, 1)

        if is_head:
            pygame.draw.circle(surf, (180, 255, 200), (cx - 3, cy - 3), 3)
            ex, ey = cx + 4, cy - 3
            pygame.draw.circle(surf, WHITE, (ex, ey), 3)
            pygame.draw.circle(surf, (10, 10, 10), (ex + 1, ey + 1), 2)
            ex2 = cx - 4
            pygame.draw.circle(surf, WHITE, (ex2, ey), 3)
            pygame.draw.circle(surf, (10, 10, 10), (ex2 - 1, ey + 1), 2)
            if math.sin(anim * 8) > 0.3:
                tx, ty = cx, cy + rad
                pygame.draw.line(surf, (220, 50, 80), (tx, ty), (tx, ty + 5), 2)
                pygame.draw.line(surf, (220, 50, 80), (tx, ty + 5), (tx - 3, ty + 8), 2)
                pygame.draw.line(surf, (220, 50, 80), (tx, ty + 5), (tx + 3, ty + 8), 2)


def draw_background(surf):
    surf.fill(BG_DARK)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 0:
                pygame.draw.rect(surf, BG_GRID, (col * GRID, row * GRID, GRID, GRID))


def draw_hud(surf, score, high_score, length, level, paused):
    pygame.draw.rect(surf, (15, 20, 28), (0, 0, WIDTH, 38))
    pygame.draw.line(surf, (40, 60, 80), (0, 38), (WIDTH, 38), 1)
    texts = [
        font_score.render(f"SCORE {score:04d}", True, CYAN),
        font_score.render(f"BEST {high_score:04d}", True, GOLD),
        font_score.render(f"LEN {length:02d}", True, GREEN_HEAD),
        font_score.render(f"LV {level:02d}", True, WHITE),
    ]
    surf.blit(texts[0], (12, 7))
    surf.blit(texts[1], (WIDTH // 2 - texts[1].get_width() // 2, 7))
    surf.blit(texts[2], (WIDTH - texts[2].get_width() - 120, 7))
    surf.blit(texts[3], (WIDTH - texts[3].get_width() - 16, 7))
    if paused:
        pause_text = font_small.render("PAUSED (P)", True, VIOLET)
        surf.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT - 28))


def draw_overlay(surf, title, sub, score=None):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))
    t = font_big.render(title, True, WHITE)
    surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 90))
    if score is not None:
        s = font_mid.render(f"Score: {score}", True, GOLD)
        surf.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 16))
    s2 = font_small.render(sub, True, GRAY)
    surf.blit(s2, (WIDTH // 2 - s2.get_width() // 2, HEIGHT // 2 + 54))


def new_apple(body, blocked=None):
    blocked = blocked or set()
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(2, ROWS - 1))
        if pos not in body and pos not in blocked:
            return pos


def toggle_fullscreen(is_fullscreen):
    if is_fullscreen:
        return pygame.display.set_mode((WIDTH, HEIGHT)), False
    return pygame.display.set_mode((0, 0), pygame.FULLSCREEN), True


def main():
    high_score = load_high_score()
    is_fullscreen = False
    game_screen = screen

    while True:
        body = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]
        direction = (1, 0)
        next_dir = (1, 0)
        apple = new_apple(body)
        special_apple = None
        special_until = 0
        score = 0
        particles = []
        anim = 0.0
        move_timer = 0
        speed = BASE_SPEED
        growth_buffer = 0
        apples_eaten = 0
        game_state = "start"  # start | playing | paused | dead
        running = True

        while running:
            dt = clock.tick(60)
            anim += 0.016
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_high_score(high_score)
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        game_screen, is_fullscreen = toggle_fullscreen(is_fullscreen)
                    elif event.key == pygame.K_p and game_state in ("playing", "paused"):
                        game_state = "paused" if game_state == "playing" else "playing"
                    elif game_state == "start":
                        game_state = "playing"
                    elif game_state == "playing":
                        if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                            next_dir = (0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                            next_dir = (0, 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                            next_dir = (-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                            next_dir = (1, 0)
                    elif game_state == "dead":
                        running = False

            if special_apple and now > special_until:
                special_apple = None

            if game_state == "playing":
                move_timer += dt
                if move_timer >= speed:
                    move_timer = 0
                    direction = next_dir
                    hx, hy = body[0]
                    nx, ny = hx + direction[0], hy + direction[1]

                    if not (0 <= nx < COLS and 2 <= ny < ROWS) or (nx, ny) in body:
                        game_state = "dead"
                        high_score = max(high_score, score)
                        save_high_score(high_score)
                        for _ in range(30):
                            particles.append(Particle(hx * GRID + GRID // 2, hy * GRID + GRID // 2, (255, 100, 50)))
                        continue

                    body.insert(0, (nx, ny))
                    ate = False

                    if (nx, ny) == apple:
                        ate = True
                        apples_eaten += 1
                        score += 10
                        growth_buffer += 1
                        high_score = max(high_score, score)
                        apple = new_apple(body, {special_apple} if special_apple else None)
                        speed = max(MIN_SPEED, speed - 3)
                        for _ in range(20):
                            particles.append(Particle(nx * GRID + GRID // 2, ny * GRID + GRID // 2, APPLE_RED))
                        if apples_eaten % 5 == 0 and special_apple is None:
                            special_apple = new_apple(body, {apple})
                            special_until = now + 6000

                    if special_apple and (nx, ny) == special_apple:
                        ate = True
                        score += 50
                        growth_buffer += 3
                        high_score = max(high_score, score)
                        special_apple = None
                        for _ in range(35):
                            particles.append(Particle(nx * GRID + GRID // 2, ny * GRID + GRID // 2, VIOLET))

                    if growth_buffer > 0:
                        growth_buffer -= 1
                    elif not ate:
                        body.pop()

            particles = [p for p in particles if p.life > 0]
            for p in particles:
                p.update()

            draw_background(game_screen)
            for p in particles:
                p.draw(game_screen)
            draw_apple(game_screen, *apple, anim, special=False)
            if special_apple:
                draw_apple(game_screen, *special_apple, anim * 1.6, special=True)
            if body:
                draw_snake(game_screen, body, anim)

            level = 1 + max(0, (BASE_SPEED - speed) // 10)
            draw_hud(game_screen, score, high_score, len(body), level, game_state == "paused")

            if game_state == "start":
                draw_overlay(
                    game_screen,
                    "SNAKE",
                    "Any key: Start | Arrows/WASD: Move | P: Pause | F11: Fullscreen",
                )
            elif game_state == "paused":
                draw_overlay(game_screen, "PAUSED", "Press P to continue")
            elif game_state == "dead":
                draw_overlay(game_screen, "GAME OVER", "Any key to restart", score)

            pygame.display.flip()


if __name__ == "__main__":
    main()