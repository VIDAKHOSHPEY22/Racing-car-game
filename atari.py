import pygame as pg
import sys
import random
import os
import math
import json

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
RED = (220, 50, 50)
GREEN = (50, 200, 80)
BLUE = (50, 120, 220)
YELLOW = (240, 210, 40)
CYAN = (50, 210, 210)
ORANGE = (255, 140, 0)
PURPLE = (170, 60, 180)
PINK = (255, 100, 170)
ROAD_COLOR = (35, 35, 40)
SHOULDER_COLOR = (60, 62, 58)
GRASS_COLOR = (45, 75, 40)
ROAD_LEFT = 150
ROAD_RIGHT = 650

COIN_INTERVAL_BASE = 1.8
MULTIPLIER_DECAY = 3.5
NEAR_MISS_MARGIN = 12
HIGH_SCORE_FILE = "highscores.json"

CAR_SKINS = [
    {"name": "Blue Racer",       "color": BLUE,   "type": "sedan"},
    {"name": "Red Speedster",    "color": RED,     "type": "sedan"},
    {"name": "Green Machine",    "color": GREEN,   "type": "suv"},
    {"name": "Yellow Lightning", "color": YELLOW,  "type": "sedan"},
    {"name": "Purple Power",     "color": PURPLE,  "type": "suv"},
    {"name": "Orange Blaze",     "color": ORANGE,  "type": "truck"},
    {"name": "Cyan Cruiser",     "color": CYAN,    "type": "sedan"},
    {"name": "Pink Dream",       "color": PINK,    "type": "suv"},
]

DIFFICULTY = {
    "Easy":   {"base_speed": 220, "obs_interval": 2.2, "speed_inc": 4, "obs_speed": (180, 250)},
    "Medium": {"base_speed": 280, "obs_interval": 1.6, "speed_inc": 6, "obs_speed": (230, 320)},
    "Hard":   {"base_speed": 340, "obs_interval": 1.1, "speed_inc": 8, "obs_speed": (280, 400)},
}

LANE_CENTERS = [212, 325, 437, 550]

OBSTACLE_COLORS = [
    (210, 55, 55),
    (55, 170, 55),
    (210, 130, 50),
    (160, 55, 170),
    (50, 100, 200),
    (180, 170, 50),
]

POWERUP_TYPES = ["shield", "slowmo", "magnet"]
POWERUP_COLORS = {
    "shield": (80, 160, 255),
    "slowmo": (180, 80, 255),
    "magnet": (255, 180, 40),
}
POWERUP_DURATION = {
    "shield": 5.0,
    "slowmo": 4.0,
    "magnet": 6.0,
}
MAGNET_RADIUS = 120


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def load_music_playlist():
    folder = "music"
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            return []
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".mp3", ".wav", ".ogg"))
        ]
        random.shuffle(files)
        return files
    except Exception:
        return []


def load_high_scores():
    try:
        with open(HIGH_SCORE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"Easy": 0, "Medium": 0, "Hard": 0}


def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(scores, f)


class MusicPlayer:
    def __init__(self):
        self.playlist = load_music_playlist()
        self.index = 0
        self.muted = False
        self.playing = False

    def play(self):
        if not self.playlist:
            return
        track = self.playlist[self.index % len(self.playlist)]
        try:
            pg.mixer.music.load(track)
            pg.mixer.music.set_volume(0.0 if self.muted else 0.5)
            pg.mixer.music.play()
            self.playing = True
        except Exception:
            self.next_track()

    def next_track(self):
        if not self.playlist:
            return
        self.index = (self.index + 1) % len(self.playlist)
        self.play()

    def update(self):
        if self.playing and not pg.mixer.music.get_busy() and not self.muted:
            self.next_track()

    def pause(self):
        pg.mixer.music.pause()

    def unpause(self):
        if not self.muted:
            pg.mixer.music.unpause()

    def stop(self):
        pg.mixer.music.stop()
        self.playing = False

    def toggle_mute(self):
        self.muted = not self.muted
        pg.mixer.music.set_volume(0.0 if self.muted else 0.5)

    def fadeout(self, ms=1500):
        pg.mixer.music.fadeout(ms)


def draw_car(surface, x, y, w, h, body_color, window_color, car_type, player=False):
    shadow = pg.Surface((w + 6, h // 3), pg.SRCALPHA)
    pg.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
    surface.blit(shadow, (x - 3, y + h - h // 6))

    r, g, b = body_color
    highlight = (clamp(r + 40, 0, 255), clamp(g + 40, 0, 255), clamp(b + 40, 0, 255))
    shadow_col = (clamp(r - 40, 0, 255), clamp(g - 40, 0, 255), clamp(b - 40, 0, 255))

    pg.draw.rect(surface, shadow_col, (x + 2, y + 4, w - 4, h - 4), border_radius=5)
    pg.draw.rect(surface, body_color, (x, y, w, h), border_radius=5)
    pg.draw.rect(surface, highlight, (x + 3, y + 3, w - 6, 8), border_radius=3)

    if car_type == "sedan":
        pg.draw.rect(surface, window_color, (x + 6, y + 12, w - 12, 20), border_radius=3)
        pg.draw.rect(surface, window_color, (x + 6, y + 38, w - 12, 18), border_radius=3)
        pg.draw.line(surface, (0, 0, 0), (x + 6, y + 23), (x + w - 6, y + 23), 1)
    elif car_type == "truck":
        pg.draw.rect(surface, window_color, (x + 8, y + 8, w - 16, 18), border_radius=3)
        pg.draw.rect(surface, shadow_col, (x + 4, y + 35, w - 8, h - 42), border_radius=2)
        pg.draw.line(surface, highlight, (x + 4, y + 34), (x + w - 4, y + 34), 1)
    else:
        pg.draw.rect(surface, window_color, (x + 6, y + 10, w - 12, 30), border_radius=3)
        pg.draw.line(surface, (0, 0, 0), (x + w // 2, y + 10), (x + w // 2, y + 40), 1)

    wheel_col = (18, 18, 18)
    rim_col = (90, 90, 95)
    for wx, wy in [(x - 4, y + 8), (x + w - 9, y + 8), (x - 4, y + h - 20), (x + w - 9, y + h - 20)]:
        pg.draw.rect(surface, wheel_col, (wx, wy, 13, 13), border_radius=3)
        pg.draw.rect(surface, rim_col, (wx + 3, wy + 3, 7, 7), border_radius=2)

    if player:
        for lx in [x + 4, x + w - 12]:
            pg.draw.ellipse(surface, (255, 255, 180), (lx, y - 5, 8, 6))
        pg.draw.rect(surface, RED, (x + 4, y + h - 4, w - 8, 4), border_radius=2)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "radius")

    def __init__(self, x, y, color, speed=120, radius=4):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed * 0.4, speed)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.life = random.uniform(0.4, 0.9)
        self.max_life = self.life
        self.color = color
        self.radius = radius

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 60 * dt
        self.life -= dt
        return self.life <= 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.radius * (self.life / self.max_life)))
        surf = pg.Surface((r * 2, r * 2), pg.SRCALPHA)
        pg.draw.circle(surf, (*self.color, alpha), (r, r), r)
        surface.blit(surf, (int(self.x) - r, int(self.y) - r))


class Obstacle:
    __slots__ = ("x", "y", "speed")

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def get_rect(self):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError


class Cone(Obstacle):
    __slots__ = ("x", "y", "speed")
    WIDTH = 18
    HEIGHT = 26

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed

    def draw(self, surface):
        cx = self.x + self.WIDTH // 2
        pg.draw.polygon(surface, ORANGE, [
            (cx, self.y),
            (self.x, self.y + self.HEIGHT),
            (self.x + self.WIDTH, self.y + self.HEIGHT),
        ])
        pg.draw.rect(surface, WHITE, (self.x + 2, self.y + self.HEIGHT - 6, self.WIDTH - 4, 4))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Barrier(Obstacle):
    __slots__ = ("x", "y", "speed")
    WIDTH = 60
    HEIGHT = 20

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed

    def draw(self, surface):
        pg.draw.rect(surface, (220, 220, 220), (self.x, self.y, self.WIDTH, self.HEIGHT), border_radius=3)
        for i in range(3):
            pg.draw.rect(surface, ORANGE, (self.x + i * 20 + 2, self.y + 2, 14, self.HEIGHT - 4), border_radius=2)

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Pothole(Obstacle):
    __slots__ = ("x", "y", "speed")
    RADIUS = 14

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.RADIUS * 2)
        self.speed = speed

    def draw(self, surface):
        pg.draw.ellipse(surface, (20, 18, 15),
                        (self.x - self.RADIUS, self.y - self.RADIUS // 2,
                         self.RADIUS * 2, self.RADIUS))
        pg.draw.ellipse(surface, (50, 45, 40),
                        (self.x - self.RADIUS + 3, self.y - self.RADIUS // 2 + 2,
                         self.RADIUS * 2 - 6, self.RADIUS - 4))

    def get_rect(self):
        return pg.Rect(
            self.x - self.RADIUS, self.y - self.RADIUS // 2,
            self.RADIUS * 2, self.RADIUS
        )


class ObstacleCar(Obstacle):
    __slots__ = ("x", "y", "speed", "width", "height", "color", "car_type", "lane")

    def __init__(self, lane, speed):
        self.width = 48
        self.height = random.choice([82, 88, 94])
        self.x = float(LANE_CENTERS[lane] - self.width // 2)
        self.y = float(-self.height - 10)
        self.speed = speed
        self.color = random.choice(OBSTACLE_COLORS)
        self.car_type = random.choice(["sedan", "suv", "truck"])
        self.lane = lane

    def draw(self, surface):
        draw_car(surface, int(self.x), int(self.y), self.width, self.height,
                 self.color, WHITE, self.car_type)

    def get_rect(self):
        return pg.Rect(int(self.x) + 4, int(self.y) + 4, self.width - 8, self.height - 8)


class Coin:
    __slots__ = ("x", "y", "speed", "angle")
    RADIUS = 11

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.RADIUS * 2)
        self.speed = speed
        self.angle = 0.0

    def update(self, dt):
        self.y += self.speed * dt
        self.angle += 3.0 * dt
        return self.y > HEIGHT

    def draw(self, surface):
        scale = abs(math.cos(self.angle))
        w = max(4, int(self.RADIUS * 2 * scale))
        h = self.RADIUS * 2
        coin_surf = pg.Surface((w, h), pg.SRCALPHA)
        pg.draw.ellipse(coin_surf, (200, 170, 20), (0, 0, w, h))
        pg.draw.ellipse(coin_surf, (240, 210, 60), (1, 1, w - 2, h - 2))
        pg.draw.ellipse(coin_surf, (255, 235, 100), (w // 4, 2, w // 2, h // 4))
        surface.blit(coin_surf, (self.x - w // 2, self.y - self.RADIUS))

    def get_rect(self):
        return pg.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)


class Powerup:
    __slots__ = ("x", "y", "speed", "kind", "angle")
    RADIUS = 14

    def __init__(self, x, speed, kind):
        self.x = x
        self.y = float(-self.RADIUS * 2)
        self.speed = speed
        self.kind = kind
        self.angle = 0.0

    def update(self, dt):
        self.y += self.speed * dt
        self.angle += 2.0 * dt
        return self.y > HEIGHT

    def draw(self, surface):
        col = POWERUP_COLORS[self.kind]
        pulse = abs(math.sin(self.angle)) * 4
        r = int(self.RADIUS + pulse)
        glow = pg.Surface((r * 4, r * 4), pg.SRCALPHA)
        pg.draw.circle(glow, (*col, 40), (r * 2, r * 2), r * 2)
        surface.blit(glow, (int(self.x) - r * 2, int(self.y) - r * 2))
        pg.draw.circle(surface, col, (int(self.x), int(self.y)), r)
        pg.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r, 2)
        label = {
            "shield": "S",
            "slowmo": "T",
            "magnet": "M",
        }[self.kind]
        font = pg.font.Font(None, 22)
        t = font.render(label, True, WHITE)
        surface.blit(t, t.get_rect(center=(int(self.x), int(self.y))))

    def get_rect(self):
        return pg.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)


class Road:
    STRIPE_W = 8
    STRIPE_H = 50
    STRIPE_GAP = 80
    LANE_DIVIDERS = [LANE_CENTERS[1] - 6, LANE_CENTERS[2] - 6, LANE_CENTERS[3] - 6]

    def __init__(self, scroll_speed):
        self.scroll = 0.0
        self.scroll_speed = scroll_speed

    def update(self, dt):
        self.scroll += self.scroll_speed * dt
        period = self.STRIPE_H + self.STRIPE_GAP
        if self.scroll >= period:
            self.scroll -= period

    def draw(self, surface):
        pg.draw.rect(surface, GRASS_COLOR, (0, 0, ROAD_LEFT, HEIGHT))
        pg.draw.rect(surface, GRASS_COLOR, (ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT))
        pg.draw.rect(surface, SHOULDER_COLOR, (ROAD_LEFT - 18, 0, 18, HEIGHT))
        pg.draw.rect(surface, SHOULDER_COLOR, (ROAD_RIGHT, 0, 18, HEIGHT))
        pg.draw.rect(surface, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))

        period = self.STRIPE_H + self.STRIPE_GAP
        num = (HEIGHT // period) + 2
        for i in range(num):
            y = int(i * period - self.scroll % period)
            for lx in self.LANE_DIVIDERS:
                pg.draw.rect(surface, (90, 90, 95), (lx, y, self.STRIPE_W, self.STRIPE_H))

        pg.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
        pg.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)


class RoadsideObject:
    __slots__ = ("x", "y", "speed", "kind")
    KINDS = ["tree", "sign", "post"]

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-60)
        self.speed = speed
        self.kind = random.choice(self.KINDS)

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT + 60

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        if self.kind == "tree":
            pg.draw.rect(surface, (80, 50, 20), (ix - 4, iy + 20, 8, 20))
            pg.draw.circle(surface, (30, 100, 35), (ix, iy + 15), 18)
            pg.draw.circle(surface, (40, 130, 45), (ix, iy + 10), 13)
        elif self.kind == "sign":
            pg.draw.rect(surface, (160, 140, 60), (ix - 2, iy, 4, 36))
            pg.draw.rect(surface, (220, 200, 60), (ix - 14, iy, 28, 18), border_radius=3)
            pg.draw.rect(surface, (80, 70, 20), (ix - 14, iy, 28, 18), 2, border_radius=3)
        else:
            pg.draw.rect(surface, (120, 120, 130), (ix - 3, iy, 6, 32))
            pg.draw.circle(surface, (240, 200, 50), (ix, iy), 7)


class Player:
    WIDTH = 48
    HEIGHT = 88
    SPEED = 320

    def __init__(self, color, car_type):
        self.x = float(WIDTH // 2 - self.WIDTH // 2)
        self.y = float(HEIGHT - self.HEIGHT - 30)
        self.color = color
        self.car_type = car_type
        self.vel_x = 0.0
        self.tilt = 0.0
        self.shield_active = False
        self.slowmo_active = False
        self.magnet_active = False
        self.powerup_timers = {"shield": 0.0, "slowmo": 0.0, "magnet": 0.0}

    def update(self, dt, keys):
        accel = 900
        friction = 600
        if keys[pg.K_LEFT]:
            self.vel_x = max(self.vel_x - accel * dt, -self.SPEED)
        elif keys[pg.K_RIGHT]:
            self.vel_x = min(self.vel_x + accel * dt, self.SPEED)
        else:
            if self.vel_x > 0:
                self.vel_x = max(0.0, self.vel_x - friction * dt)
            else:
                self.vel_x = min(0.0, self.vel_x + friction * dt)

        self.x += self.vel_x * dt
        self.x = clamp(self.x, ROAD_LEFT + 2, ROAD_RIGHT - self.WIDTH - 2)

        target_tilt = self.vel_x / self.SPEED * 6
        self.tilt += (target_tilt - self.tilt) * 8 * dt

        for kind in POWERUP_TYPES:
            if self.powerup_timers[kind] > 0:
                self.powerup_timers[kind] -= dt
                if self.powerup_timers[kind] <= 0:
                    self.powerup_timers[kind] = 0.0

        self.shield_active = self.powerup_timers["shield"] > 0
        self.slowmo_active = self.powerup_timers["slowmo"] > 0
        self.magnet_active = self.powerup_timers["magnet"] > 0

    def activate_powerup(self, kind):
        self.powerup_timers[kind] = POWERUP_DURATION[kind]

    def draw(self, surface):
        if abs(self.tilt) > 0.3:
            temp = pg.Surface((self.WIDTH + 12, self.HEIGHT + 12), pg.SRCALPHA)
            draw_car(temp, 6, 6, self.WIDTH, self.HEIGHT, self.color, CYAN, self.car_type, player=True)
            rotated = pg.transform.rotate(temp, -self.tilt)
            surface.blit(rotated, rotated.get_rect(center=(int(self.x + self.WIDTH // 2),
                                                            int(self.y + self.HEIGHT // 2))))
        else:
            draw_car(surface, int(self.x), int(self.y), self.WIDTH, self.HEIGHT,
                     self.color, CYAN, self.car_type, player=True)

            if self.shield_active:
    alpha = int(80 + 60 * abs(math.sin(pg.time.get_ticks() / 200)))
    r = self.WIDTH // 2 + 10
    shield_surf = pg.Surface((r * 2 + 4, r * 2 + 4), pg.SRCALPHA)
    pg.draw.ellipse(shield_surf, (80, 160, 255, alpha),
                    (0, 0, r * 2 + 4, r * 2 + 4), 3)
    surface.blit(shield_surf, (int(self.x + self.WIDTH // 2) - r - 2,
                               int(self.y + self.HEIGHT // 2) - r - 2))

        if self.magnet_active:
            angle = pg.time.get_ticks() / 300
            for i in range(6):
                a = angle + i * math.tau / 6
                rx = int(self.x + self.WIDTH // 2 + math.cos(a) * (MAGNET_RADIUS * 0.15))
                ry = int(self.y + self.HEIGHT // 2 + math.sin(a) * (MAGNET_RADIUS * 0.15))
                pg.draw.circle(surface, (255, 200, 60), (rx, ry), 2)

    def get_rect(self):
        margin = 6
        return pg.Rect(int(self.x) + margin, int(self.y) + margin,
                       self.WIDTH - margin * 2, self.HEIGHT - margin * 2)

    def center(self):
        return (self.x + self.WIDTH / 2, self.y + self.HEIGHT / 2)


class ScoreDisplay:
    def __init__(self):
        self.displayed = 0.0
        self.target = 0

    def set_target(self, score):
        self.target = score

    def update(self, dt):
        diff = self.target - self.displayed
        if abs(diff) < 1:
            self.displayed = float(self.target)
        else:
            self.displayed += diff * min(1.0, 10 * dt)

    def value(self):
        return int(self.displayed)


class HUD:
    def __init__(self, fonts):
        self.small, self.tiny = fonts[1], fonts[2]
        self.surf = pg.Surface((210, 150), pg.SRCALPHA)

    def draw(self, surface, score_display, level, speed_pct, difficulty, multiplier, player):
        self.surf.fill((10, 10, 18, 170))
        pg.draw.rect(self.surf, (255, 255, 255, 30), (0, 0, 210, 150), 2, border_radius=8)

        pulse = int(4 * abs(math.sin(pg.time.get_ticks() / 400)))
        self._blit(f"Score  {score_display.value()}", (255, 255, 90 + pulse), 14, 10)
        self._blit(f"Level  {level}", CYAN, 14, 36)
        self._blit(f"Speed  {speed_pct}%", GREEN, 14, 60)
        self._blit(f"Mode: {difficulty}", YELLOW, 14, 86, tiny=True)
        if multiplier > 1.0:
            mc = YELLOW if multiplier >= 2.0 else (150, 220, 150)
            self._blit(f"x{multiplier:.1f} combo!", mc, 14, 100, tiny=True)

        active = [k for k in POWERUP_TYPES if player.powerup_timers[k] > 0]
        for i, kind in enumerate(active):
            t = player.powerup_timers[kind]
            col = POWERUP_COLORS[kind]
            self._blit(f"{kind.upper()} {t:.1f}s", col, 14, 116 + i * 14, tiny=True)

        surface.blit(self.surf, (10, 10))

    def _blit(self, text, color, x, y, tiny=False):
        font = self.tiny if tiny else self.small
        self.surf.blit(font.render(text, True, color), (x, y))


class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.base_color = color or (45, 165, 75)
        self.hover_color = tuple(clamp(c + 35, 0, 255) for c in self.base_color)

    def draw(self, surface, font):
        col = self.hover_color if self.rect.collidepoint(pg.mouse.get_pos()) else self.base_color
        pg.draw.rect(surface, (0, 0, 0), (self.rect.x + 3, self.rect.y + 4, self.rect.w, self.rect.h), border_radius=8)
        pg.draw.rect(surface, col, self.rect, border_radius=8)
        pg.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    POWERUP_INTERVAL = 12.0
    ROADSIDE_INTERVAL = 1.4

    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Sleek Street Racer")
        self.clock = pg.time.Clock()

        f_main = pg.font.Font(None, 44)
        f_small = pg.font.Font(None, 30)
        f_tiny = pg.font.Font(None, 22)
        self.fonts = (f_main, f_small, f_tiny)

        self.music = MusicPlayer()
        self.selected_skin = 0
        self.selected_diff = "Medium"
        self.state = "menu"
        self.high_scores = load_high_scores()

        self.hud = HUD(self.fonts)
        self.btn_play = Button(WIDTH // 2 - 100, 0, 200, 52, "START RACE")
        self.btn_pause = Button(WIDTH - 115, 10, 100, 36, "PAUSE", (60, 60, 80))
        self.btn_sound = Button(WIDTH - 115, 52, 100, 32, "SFX: ON", (60, 60, 80))
        self.btn_restart = Button(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 46, "RESTART")
        self.btn_menu = Button(WIDTH // 2 - 90, HEIGHT // 2 + 96, 180, 46, "MAIN MENU", (60, 80, 160))
        self.btn_quit = Button(WIDTH // 2 - 90, HEIGHT // 2 + 152, 180, 46, "QUIT", (160, 50, 50))

        self._reset_state()

    def _reset_state(self):
        diff = DIFFICULTY[self.selected_diff]
        skin = CAR_SKINS[self.selected_skin]
        self.player = Player(skin["color"], skin["type"])
        self.road = Road(diff["base_speed"])
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.particles = []
        self.roadside = []
        self.score = 0
        self.score_display = ScoreDisplay()
        self.level = 1
        self.speed_pct = 100
        self.scroll_speed = diff["base_speed"]
        self.obs_timer = 0.0
        self.obs_interval = diff["obs_interval"]
        self.coin_timer = 0.0
        self.coin_interval = COIN_INTERVAL_BASE
        self.powerup_timer = 0.0
        self.roadside_timer = 0.0
        self.combo = 0
        self.multiplier = 1.0
        self.combo_timer = 0.0
        self.fb_entries = []
        self.level_up_timer = 0.0

    def _get_high_score(self):
        return self.high_scores.get(self.selected_diff, 0)

    def _save_high_scores(self):
        hs = self._get_high_score()
        if self.score > hs:
            self.high_scores[self.selected_diff] = self.score
        save_high_scores(self.high_scores)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.music.stop()
                pg.quit()
                sys.exit()

            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                pos = ev.pos
                if self.state == "menu":
                    self._handle_menu_click(pos)
                elif self.state == "playing":
                    if self.btn_pause.clicked(pos):
                        self.state = "paused"
                        self.music.pause()
                    if self.btn_sound.clicked(pos):
                        self.music.toggle_mute()
                        self.btn_sound.text = "SFX: OFF" if self.music.muted else "SFX: ON"
                elif self.state == "paused":
                    if self.btn_pause.clicked(pos):
                        self.state = "playing"
                        self.music.unpause()
                    if self.btn_restart.clicked(pos):
                        self._reset_state()
                        self.state = "playing"
                        self.music.play()
                    if self.btn_menu.clicked(pos):
                        self._save_high_scores()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                elif self.state == "gameover":
                    if self.btn_restart.clicked(pos):
                        self._reset_state()
                        self.state = "playing"
                        self.music.play()
                    if self.btn_menu.clicked(pos):
                        self._save_high_scores()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                    if self.btn_quit.clicked(pos):
                        self._save_high_scores()
                        self.music.stop()
                        pg.quit()
                        sys.exit()

            if ev.type == pg.KEYDOWN:
                if ev.key in (pg.K_p, pg.K_ESCAPE):
                    if self.state == "playing":
                        self.state = "paused"
                        self.music.pause()
                    elif self.state == "paused":
                        self.state = "playing"
                        self.music.unpause()
                    elif self.state == "gameover":
                        self._save_high_scores()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                if ev.key == pg.K_r and self.state in ("gameover", "paused"):
                    self._reset_state()
                    self.state = "playing"
                    self.music.play()

    def _handle_menu_click(self, pos):
        for i, diff in enumerate(["Easy", "Medium", "Hard"]):
            if pg.Rect(WIDTH // 2 - 90, 138 + i * 46, 180, 36).collidepoint(pos):
                self.selected_diff = diff

        if pg.Rect(WIDTH // 2 - 145, 345, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
        if pg.Rect(WIDTH // 2 + 105, 345, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)

        self.btn_play.rect.y = 470
        if self.btn_play.clicked(pos):
            self._reset_state()
            self.state = "playing"
            self.music.play()

    def _spawn_particles(self, x, y, color, count=14):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def _award(self, base, x, y, label=None):
        self.combo += 1
        self._recalc_multiplier()
        gain = int(base * self.multiplier)
        self.score += gain
        self.score_display.set_target(self.score)
        self.fb_entries.append({
            "text": label or f"+{gain}",
            "x": float(x),
            "y": float(y),
            "timer": 0.9,
            "max": 0.9,
        })

    def _update(self, dt):
        self.music.update()
        if self.state != "playing":
            return

        slowmo_dt = dt * 0.4 if self.player.slowmo_active else dt

        keys = pg.key.get_pressed()
        self.player.update(dt, keys)
        self.road.scroll_speed = self.scroll_speed * (0.4 if self.player.slowmo_active else 1.0)
        self.road.update(dt)
        self.score_display.update(dt)

        diff = DIFFICULTY[self.selected_diff]
        px, py = self.player.center()

        self.obs_timer += slowmo_dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0.0
            self._spawn_obstacle(diff)

        self.coin_timer += slowmo_dt
        if self.coin_timer >= self.coin_interval:
            self.coin_timer = 0.0
            self.coins.append(Coin(LANE_CENTERS[random.randint(0, 3)], self.scroll_speed * 0.9))

        self.powerup_timer += slowmo_dt
        if self.powerup_timer >= self.POWERUP_INTERVAL:
            self.powerup_timer = 0.0
            kind = random.choice(POWERUP_TYPES)
            self.powerups.append(Powerup(LANE_CENTERS[random.randint(0, 3)],
                                         self.scroll_speed * 0.85, kind))

        self.roadside_timer += dt
        if self.roadside_timer >= self.ROADSIDE_INTERVAL:
            self.roadside_timer = 0.0
            for side_x in [random.randint(20, ROAD_LEFT - 30),
                            random.randint(ROAD_RIGHT + 12, WIDTH - 20)]:
                self.roadside.append(RoadsideObject(side_x, self.scroll_speed * 1.1))

        player_rect = self.player.get_rect()

        for obs in self.obstacles[:]:
            if obs.update(slowmo_dt):
                self.obstacles.remove(obs)
                self._award(1, obs.x if hasattr(obs, "x") else px, py)
                continue
            obs_rect = obs.get_rect()
            if obs_rect.colliderect(player_rect):
                if self.player.shield_active:
                    self.player.powerup_timers["shield"] = 0.0
                    self._spawn_particles(px, py, (80, 160, 255), 20)
                    self.obstacles.remove(obs)
                else:
                    self._trigger_gameover(px, py)
                    return
            else:
                exp = obs_rect.inflate(NEAR_MISS_MARGIN * 2, NEAR_MISS_MARGIN * 2)
                if exp.colliderect(player_rect) and not obs_rect.colliderect(player_rect):
                    self._award(3, int(px), int(py), "NEAR MISS!")

        for coin in self.coins[:]:
            if self.player.magnet_active:
                cx, cy = coin.x, coin.y
                dx, dy = px - cx, py - cy
                dist = math.hypot(dx, dy)
                if dist < MAGNET_RADIUS and dist > 1:
                    coin.x += dx / dist * 200 * dt
                    coin.y += dy / dist * 200 * dt
            if coin.update(slowmo_dt):
                self.coins.remove(coin)
                continue
            if coin.get_rect().colliderect(player_rect):
                self.coins.remove(coin)
                self._spawn_particles(int(coin.x), int(coin.y), (240, 200, 30), 10)
                self._award(5, int(coin.x), int(coin.y))

        for pu in self.powerups[:]:
            if pu.update(slowmo_dt):
                self.powerups.remove(pu)
                continue
            if pu.get_rect().colliderect(player_rect):
                self.powerups.remove(pu)
                self.player.activate_powerup(pu.kind)
                self._spawn_particles(int(pu.x), int(pu.y), POWERUP_COLORS[pu.kind], 16)
                self.fb_entries.append({
                    "text": pu.kind.upper() + "!",
                    "x": float(pu.x),
                    "y": float(pu.y),
                    "timer": 1.2,
                    "max": 1.2,
                })

        for obj in self.roadside[:]:
            if obj.update(dt):
                self.roadside.remove(obj)

        self.particles = [p for p in self.particles if not p.update(dt)]

        for fb in self.fb_entries[:]:
            fb["timer"] -= dt
            if fb["timer"] <= 0:
                self.fb_entries.remove(fb)

        if self.level_up_timer > 0:
            self.level_up_timer -= dt

        self.combo_timer += dt
        if self.combo_timer >= MULTIPLIER_DECAY:
            self.combo_timer = 0.0
            if self.combo > 0:
                self.combo = max(0, self.combo - 1)
                self._recalc_multiplier()

        level_threshold = 5 + self.level * 3
        if self.score >= level_threshold * self.level:
            self.level += 1
            self.scroll_speed = min(self.scroll_speed + diff["speed_inc"], diff["base_speed"] * 2.5)
            self.obs_interval = max(0.55, self.obs_interval - 0.05)
            self.coin_interval = max(0.8, self.coin_interval - 0.05)
            self.speed_pct = int(self.scroll_speed / diff["base_speed"] * 100)
            self.level_up_timer = 2.0
            self._spawn_particles(int(px), int(py), YELLOW, 24)

    def _spawn_obstacle(self, diff):
        min_spd, max_spd = diff["obs_speed"]
        spd = random.uniform(min_spd, max_spd)
        occupied = {c.lane for c in self.obs_cars}
        lanes = [i for i in range(4) if i not in occupied] or list(range(4))
        lane = random.choice(lanes)
        roll = random.random()
        if roll < 0.55:
            self.obstacles.append(ObstacleCar(lane, spd))
        elif roll < 0.75:
            self.obstacles.append(Cone(LANE_CENTERS[lane] - Cone.WIDTH // 2, spd))
        elif roll < 0.88:
            self.obstacles.append(Barrier(LANE_CENTERS[lane] - Barrier.WIDTH // 2, spd))
        else:
            self.obstacles.append(Pothole(LANE_CENTERS[lane], spd))

    def _recalc_multiplier(self):
        if self.combo >= 20:
            self.multiplier = 3.0
        elif self.combo >= 15:
            self.multiplier = 2.5
        elif self.combo >= 10:
            self.multiplier = 2.0
        elif self.combo >= 5:
            self.multiplier = 1.5
        else:
            self.multiplier = 1.0

    def _trigger_gameover(self, px, py):
        self._spawn_particles(int(px), int(py), RED, 30)
        self.state = "gameover"
        self._save_high_scores()
        self.music.fadeout(1500)

    def _draw(self):
        self.screen.fill(BLACK)
        if self.state == "menu":
            self._draw_menu()
        else:
            self.road.draw(self.screen)
            for obj in self.roadside:
                obj.draw(self.screen)
            for obs in self.obstacles:
                obs.draw(self.screen)
            for coin in self.coins:
                coin.draw(self.screen)
            for pu in self.powerups:
                pu.draw(self.screen)
            self.player.draw(self.screen)
            for p in self.particles:
                p.draw(self.screen)
            self.hud.draw(self.screen, self.score_display, self.level,
                          self.speed_pct, self.selected_diff, self.multiplier, self.player)
            self.btn_pause.draw(self.screen, self.fonts[2])
            self.btn_sound.draw(self.screen, self.fonts[2])
            self._draw_feedback()
            if self.level_up_timer > 0:
                self._draw_level_up()
            if self.state == "paused":
                self._draw_overlay_screen("PAUSED", YELLOW, 280, (255, 255, 255, 40), self._draw_pause_content)
            elif self.state == "gameover":
                self._draw_overlay_screen("GAME OVER", RED, 360, (200, 30, 30, 80), self._draw_gameover_content)
        pg.display.flip()

    def _draw_feedback(self):
        for fb in self.fb_entries:
            alpha = int(255 * (fb["timer"] / fb["max"]))
            y = fb["y"] - int((fb["max"] - fb["timer"]) * 60)
            col = YELLOW if "MISS" in fb["text"] or "!" in fb["text"] else GREEN
            surf = self.fonts[1].render(fb["text"], True, col)
            surf.set_alpha(alpha)
            self.screen.blit(surf, surf.get_rect(center=(int(fb["x"]), int(y))))

    def _draw_level_up(self):
        t = self.level_up_timer / 2.0
        alpha = int(255 * min(1.0, t * 4) * min(1.0, (1 - t) * 4 + 0.2))
        surf = self.fonts[0].render(f"LEVEL {self.level}!", True, YELLOW)
        surf.set_alpha(alpha)
        self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

    def _draw_menu(self):
        f_main, f_small, f_tiny = self.fonts
        for y in range(HEIGHT):
            shade = 8 + int(18 * y / HEIGHT)
            pg.draw.line(self.screen, (shade, shade, shade + 6), (0, y), (WIDTH, y))

        title = f_main.render("SLEEK STREET RACER", True, YELLOW)
        sh = f_main.render("SLEEK STREET RACER", True, (70, 70, 0))
        self.screen.blit(sh, (WIDTH // 2 - title.get_width() // 2 + 3, 38))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 35))

        bg = pg.Surface((440, 460), pg.SRCALPHA)
        bg.fill((0, 0, 0, 170))
        pg.draw.rect(bg, (255, 255, 255, 30), (0, 0, 440, 460), 2, border_radius=12)
        self.screen.blit(bg, (WIDTH // 2 - 220, 115))

        diff_lbl = f_small.render("Difficulty", True, WHITE)
        self.screen.blit(diff_lbl, (WIDTH // 2 - diff_lbl.get_width() // 2, 122))
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            r = pg.Rect(WIDTH // 2 - 90, 138 + i * 46, 180, 36)
            sel = d == self.selected_diff
            hs = self.high_scores.get(d, 0)
            pg.draw.rect(self.screen, GREEN if sel else (70, 70, 75), r, border_radius=7)
            pg.draw.rect(self.screen, WHITE, r, 1 if not sel else 2, border_radius=7)
            t = f_small.render(d, True, WHITE)
            self.screen.blit(t, t.get_rect(center=r.center))
            hs_t = f_tiny.render(f"Best: {hs}", True, YELLOW if sel else GRAY)
            self.screen.blit(hs_t, (r.right + 8, r.centery - hs_t.get_height() // 2))

        skin_lbl = f_small.render("Car Skin", True, WHITE)
        self.screen.blit(skin_lbl, (WIDTH // 2 - skin_lbl.get_width() // 2, 296))

        skin = CAR_SKINS[self.selected_skin]
        px, py = WIDTH // 2 - 24, 315
        pbg = pg.Surface((96, 108), pg.SRCALPHA)
        pbg.fill((25, 25, 35, 200))
        pg.draw.rect(pbg, (255, 255, 255, 30), (0, 0, 96, 108), 1, border_radius=6)
        self.screen.blit(pbg, (px - 24, py - 5))
        draw_car(self.screen, px, py, 48, 88, skin["color"], CYAN, skin["type"], player=True)

        mouse = pg.mouse.get_pos()
        for rect, sym in [
            (pg.Rect(WIDTH // 2 - 145, 345, 40, 40), "<"),
            (pg.Rect(WIDTH // 2 + 105, 345, 40, 40), ">"),
        ]:
            col = GREEN if rect.collidepoint(mouse) else (70, 70, 75)
            pg.draw.rect(self.screen, col, rect, border_radius=6)
            pg.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
            t = f_small.render(sym, True, WHITE)
            self.screen.blit(t, t.get_rect(center=rect.center))

        name_t = f_tiny.render(skin["name"], True, YELLOW)
        self.screen.blit(name_t, (WIDTH // 2 - name_t.get_width() // 2, 425))

        self.btn_play.rect.y = 470
        self.btn_play.draw(self.screen, f_small)

        hint = f_tiny.render("Use arrow keys to steer  |  P - Pause  |  R - Restart", True, GRAY)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 530))

    def _draw_overlay_screen(self, title_text, title_color, box_h, border_col, content_fn):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))
        bx, by = WIDTH // 2 - 200, HEIGHT // 2 - box_h // 2
        box = pg.Surface((400, box_h), pg.SRCALPHA)
        box.fill((18, 18, 28, 245))
        pg.draw.rect(box, border_col, (0, 0, 400, box_h), 3, border_radius=14)
        self.screen.blit(box, (bx, by))
        t = self.fonts[0].render(title_text, True, title_color)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 18))
        content_fn(by)

    def _draw_pause_content(self, by):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        for text, col, dy in [
            (f"Score: {self.score}", WHITE, 62),
            (f"Level:  {self.level}", CYAN, 90),
        ]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        for text, dy in [("P / ESC to resume", 125), ("R to restart", 143)]:
            t = f_tiny.render(text, True, GRAY)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        self.btn_restart.rect.topleft = (WIDTH // 2 - 90, by + 168)
        self.btn_menu.rect.topleft = (WIDTH // 2 - 90, by + 220)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)

    def _draw_gameover_content(self, by):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        hs = self._get_high_score()
        for text, col, dy in [
            (f"Score: {self.score}", WHITE, 62),
            (f"Level: {self.level}", CYAN, 90),
        ]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        t = (f_small.render("NEW HIGH SCORE!", True, YELLOW) if self.score >= hs
             else f_tiny.render(f"Best: {hs}", True, GRAY))
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 118))
        self.btn_restart.rect.topleft = (WIDTH // 2 - 90, by + 148)
        self.btn_menu.rect.topleft = (WIDTH // 2 - 90, by + 200)
        self.btn_quit.rect.topleft = (WIDTH // 2 - 90, by + 252)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)
        self.btn_quit.draw(self.screen, f_small)
        hint = f_tiny.render("R restart  |  ESC menu", True, GRAY)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, by + 318))

if __name__ == "__main__":
    game = Game()
    game.run()
