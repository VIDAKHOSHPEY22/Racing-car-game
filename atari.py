import pygame as pg
import sys
import random
import math
import os

pg.init()
pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 800, 600
FPS = 60

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Note: Install numpy for sound effects (pip install numpy)")

def generate_beep_sound(frequency, duration, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = np.sin(2 * np.pi * frequency * np.arange(n_samples) / sample_rate)
    sound = np.array(buf * 32767 * volume, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_explosion_sound():
    sample_rate = 22050
    duration = 0.5
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    noise = np.random.normal(0, 1, n_samples) * np.exp(-t * 15)
    sound = np.array(noise * 8000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_coin_sound():
    sample_rate = 22050
    duration = 0.15
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    freq = 800 * np.exp(-t * 8)
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 15)
    sound = np.array(wave * 20000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_boost_sound():
    sample_rate = 22050
    duration = 0.8
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    freq = 300 + 400 * t / duration
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 3)
    sound = np.array(wave * 25000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_levelup_sound():
    sample_rate = 22050
    duration = 0.6
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    wave = (np.sin(2 * np.pi * 440 * t) * np.exp(-t * 2) +
            np.sin(2 * np.pi * 880 * t) * np.exp(-t * 3))
    sound = np.array(wave * 20000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_hit_sound():
    sample_rate = 22050
    duration = 0.2
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    noise = np.random.normal(0, 1, n_samples) * np.exp(-t * 20)
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 15)
    wave = (noise * 0.6 + tone * 0.4) * np.exp(-t * 10)
    sound = np.array(wave * 15000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

def generate_powerup_sound():
    sample_rate = 22050
    duration = 0.5
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    freq = 500 + 700 * t / duration
    wave = (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)) * np.exp(-t * 4)
    sound = np.array(wave * 22000, dtype=np.int16)
    sound = np.repeat(sound.reshape(n_samples, 1), 2, axis=1)
    return pg.sndarray.make_sound(sound)

if not HAS_NUMPY:
    class DummySound:
        def play(self): pass
    generate_beep_sound = lambda *args: DummySound()
    generate_explosion_sound = lambda: DummySound()
    generate_coin_sound = lambda: DummySound()
    generate_boost_sound = lambda: DummySound()
    generate_levelup_sound = lambda: DummySound()
    generate_hit_sound = lambda: DummySound()
    generate_powerup_sound = lambda: DummySound()

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

ROAD_LEFT, ROAD_RIGHT = 150, 650

CAR_SKINS = [
    {"name": "Blue Racer",       "color": BLUE,              "type": "sedan", "speed_bonus": 1.0},
    {"name": "Red Speedster",    "color": RED,               "type": "sedan", "speed_bonus": 1.1},
    {"name": "Green Machine",    "color": GREEN,             "type": "suv",   "speed_bonus": 0.95},
    {"name": "Yellow Lightning", "color": YELLOW,            "type": "sedan", "speed_bonus": 1.15},
    {"name": "Purple Power",     "color": PURPLE,            "type": "suv",   "speed_bonus": 1.0},
    {"name": "Orange Blaze",     "color": ORANGE,            "type": "truck", "speed_bonus": 0.9},
    {"name": "Cyan Cruiser",     "color": CYAN,              "type": "sedan", "speed_bonus": 1.05},
    {"name": "Pink Dream",       "color": PINK,              "type": "suv",   "speed_bonus": 1.0},
    {"name": "Ghost White",      "color": (230, 230, 235),   "type": "sedan", "speed_bonus": 1.08},
    {"name": "Midnight Black",   "color": (25, 25, 30),      "type": "sedan", "speed_bonus": 1.12},
    {"name": "Lime Rocket",      "color": (160, 230, 30),    "type": "sedan", "speed_bonus": 1.18},
    {"name": "Crimson Truck",    "color": (180, 20, 40),     "type": "truck", "speed_bonus": 0.88},
    {"name": "Steel SUV",        "color": (140, 160, 175),   "type": "suv",   "speed_bonus": 0.97},
    {"name": "Gold Rush",        "color": (212, 175, 55),    "type": "sedan", "speed_bonus": 1.13},
    {"name": "Neon Violet",      "color": (138, 43, 226),    "type": "suv",   "speed_bonus": 1.02},
]

DIFFICULTY = {
    "Easy":   {"base_speed": 280, "obs_interval": 1.8, "speed_inc": 6,  "obs_speed": (220, 320)},
    "Medium": {"base_speed": 380, "obs_interval": 1.3, "speed_inc": 9,  "obs_speed": (280, 400)},
    "Hard":   {"base_speed": 500, "obs_interval": 0.9, "speed_inc": 12, "obs_speed": (350, 500)},
}

LANE_CENTERS = [212, 325, 437, 550]
OBSTACLE_COLORS = [
    (255, 80, 80), (80, 255, 80), (255, 180, 60),
    (200, 80, 255), (80, 150, 255), (255, 220, 60),
]

POWERUP_SHIELD     = "shield"
POWERUP_MAGNET     = "magnet"
POWERUP_TIMEFREEZE = "timefreeze"

_POWERUP_COLORS = {
    POWERUP_SHIELD:     (80, 180, 255),
    POWERUP_MAGNET:     (255, 80, 200),
    POWERUP_TIMEFREEZE: (80, 230, 200),
}

_POWERUP_LABELS = {
    POWERUP_SHIELD:     "SHIELD",
    POWERUP_MAGNET:     "MAGNET",
    POWERUP_TIMEFREEZE: "FREEZE",
}

_PARTICLE_POOL_SIZE = 300


class ParticlePool:
    __slots__ = ("_pool", "_active")

    def __init__(self, size):
        self._pool = [_PooledParticle() for _ in range(size)]
        self._active = []

    def spawn(self, x, y, vx, vy, color, lifetime):
        for p in self._pool:
            if not p.alive:
                p.reset(x, y, vx, vy, color, lifetime)
                self._active.append(p)
                return
        p = _PooledParticle()
        p.reset(x, y, vx, vy, color, lifetime)
        self._active.append(p)

    def update_and_draw(self, surface, dt):
        keep = []
        for p in self._active:
            if p.update(dt):
                p.draw(surface)
                keep.append(p)
            else:
                p.alive = False
        self._active = keep


class _PooledParticle:
    __slots__ = ("x", "y", "vx", "vy", "color", "lifetime", "max_lifetime", "alive", "_surf_cache")

    def __init__(self):
        self.alive = False
        self._surf_cache = {}

    def reset(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface):
        ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * ratio)
        size = max(2, int(4 * ratio))
        key = (size, self.color, alpha)
        if key not in self._surf_cache:
            s = pg.Surface((size * 2, size * 2), pg.SRCALPHA)
            pg.draw.circle(s, (*self.color, alpha), (size, size), size)
            self._surf_cache[key] = s
        surface.blit(self._surf_cache[key], (int(self.x - size), int(self.y - size)))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def draw_heart(surface, cx, cy, size, color):
    r = size // 2
    pg.draw.circle(surface, color, (cx - r // 2, cy), r // 2)
    pg.draw.circle(surface, color, (cx + r // 2, cy), r // 2)
    pg.draw.polygon(surface, color, [(cx - r, cy), (cx + r, cy), (cx, cy + int(r * 1.2))])


def draw_arrow(surface, cx, cy, size, color, direction):
    h = size // 2
    if direction == "left":
        pts = [(cx + h, cy - h), (cx + h, cy + h), (cx - h, cy)]
    else:
        pts = [(cx - h, cy - h), (cx - h, cy + h), (cx + h, cy)]
    pg.draw.polygon(surface, color, pts)


def draw_car(surface, x, y, w, h, body_color, window_color, car_type, player=False):
    shadow = pg.Surface((w + 6, h // 3), pg.SRCALPHA)
    pg.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
    surface.blit(shadow, (x - 3, y + h - h // 6))

    r, g, b = body_color
    hi = (clamp(r + 50, 0, 255), clamp(g + 50, 0, 255), clamp(b + 50, 0, 255))
    sh = (clamp(r - 40, 0, 255), clamp(g - 40, 0, 255), clamp(b - 40, 0, 255))

    pg.draw.rect(surface, sh, (x + 2, y + 4, w - 4, h - 4), border_radius=5)
    pg.draw.rect(surface, body_color, (x, y, w, h), border_radius=5)
    pg.draw.rect(surface, hi, (x + 3, y + 3, w - 6, 8), border_radius=3)

    if car_type == "sedan":
        pg.draw.rect(surface, window_color, (x + 6, y + 12, w - 12, 20), border_radius=3)
        pg.draw.rect(surface, window_color, (x + 6, y + 38, w - 12, 18), border_radius=3)
        pg.draw.line(surface, (0, 0, 0), (x + 6, y + 23), (x + w - 6, y + 23), 1)
    elif car_type == "truck":
        pg.draw.rect(surface, window_color, (x + 8, y + 8, w - 16, 18), border_radius=3)
        pg.draw.rect(surface, sh, (x + 4, y + 35, w - 8, h - 42), border_radius=2)
        pg.draw.line(surface, hi, (x + 4, y + 34), (x + w - 4, y + 34), 1)
    else:
        pg.draw.rect(surface, window_color, (x + 6, y + 10, w - 12, 30), border_radius=3)
        pg.draw.line(surface, (0, 0, 0), (x + w // 2, y + 10), (x + w // 2, y + 40), 1)

    wheel_col, rim_col = (30, 30, 35), (120, 120, 130)
    for wx, wy in [(x - 4, y + 8), (x + w - 9, y + 8), (x - 4, y + h - 20), (x + w - 9, y + h - 20)]:
        pg.draw.rect(surface, wheel_col, (wx, wy, 13, 13), border_radius=3)
        pg.draw.rect(surface, rim_col, (wx + 3, wy + 3, 7, 7), border_radius=2)

    if player:
        for lx in [x + 4, x + w - 12]:
            pg.draw.ellipse(surface, (255, 255, 100), (lx, y - 5, 8, 6))
        pg.draw.rect(surface, RED, (x + 4, y + h - 4, w - 8, 4), border_radius=2)


class Cone:
    WIDTH, HEIGHT = 18, 26
    _surf = None

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed
        if Cone._surf is None:
            s = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
            cx = self.WIDTH // 2
            pg.draw.polygon(s, ORANGE, [(cx, 0), (0, self.HEIGHT), (self.WIDTH, self.HEIGHT)])
            pg.draw.rect(s, (255, 200, 100), (2, self.HEIGHT - 6, self.WIDTH - 4, 4))
            Cone._surf = s

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        surface.blit(Cone._surf, (self.x, int(self.y)))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Barrier:
    WIDTH, HEIGHT = 60, 20
    _surf = None

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed
        if Barrier._surf is None:
            s = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
            pg.draw.rect(s, (200, 200, 210), (0, 0, self.WIDTH, self.HEIGHT), border_radius=3)
            for i in range(3):
                pg.draw.rect(s, ORANGE, (i * 20 + 2, 2, 14, self.HEIGHT - 4), border_radius=2)
            Barrier._surf = s

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        surface.blit(Barrier._surf, (self.x, int(self.y)))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class OilSlick:
    WIDTH, HEIGHT = 54, 28

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed
        self.angle = 0.0
        self._s0 = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        self._s1 = pg.Surface((self.WIDTH - 10, self.HEIGHT - 6), pg.SRCALPHA)

    def update(self, dt):
        self.y += self.speed * dt
        self.angle += dt * 2.0
        return self.y > HEIGHT

    def draw(self, surface):
        t = self.angle
        c0 = (
            clamp(int(100 + 80 * math.sin(t)), 0, 255),
            clamp(int(50 + 80 * math.sin(t + 2.1)), 0, 255),
            clamp(int(150 + 80 * math.sin(t + 4.2)), 0, 255),
            200,
        )
        c1 = (
            clamp(int(200 + 80 * math.sin(t + 1.0)), 0, 255),
            clamp(int(100 + 80 * math.sin(t + 3.1)), 0, 255),
            clamp(int(50 + 80 * math.sin(t + 5.2)), 0, 255),
            180,
        )
        self._s0.fill((0, 0, 0, 0))
        pg.draw.ellipse(self._s0, c0, self._s0.get_rect())
        surface.blit(self._s0, (self.x, self.y))
        self._s1.fill((0, 0, 0, 0))
        pg.draw.ellipse(self._s1, c1, self._s1.get_rect())
        surface.blit(self._s1, (self.x + 5, self.y + 3))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class SpeedBump:
    WIDTH, HEIGHT = 70, 12
    _surf = None

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.HEIGHT)
        self.speed = speed
        if SpeedBump._surf is None:
            s = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
            pg.draw.rect(s, (180, 100, 50), (0, 0, self.WIDTH, self.HEIGHT), border_radius=5)
            sw = 10
            for i in range(self.WIDTH // (sw * 2) + 1):
                sx = i * sw * 2
                cw = min(sw, self.WIDTH - sx)
                if cw > 0:
                    pg.draw.rect(s, (255, 220, 80), (sx, 0, cw, self.HEIGHT), border_radius=3)
            SpeedBump._surf = s

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        surface.blit(SpeedBump._surf, (self.x, int(self.y)))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Coin:
    RADIUS = 11
    _cache = {}

    def __init__(self, x, speed):
        self.x = x
        self.y = float(-self.RADIUS * 2)
        self.speed = speed
        self.angle = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.y += self.speed * dt
        self.angle += 8.0 * dt
        return self.y > HEIGHT

    def draw(self, surface):
        w = max(4, int(self.RADIUS * 2 * abs(math.cos(self.angle))))
        key = w
        if key not in Coin._cache:
            h = self.RADIUS * 2
            s = pg.Surface((w, h), pg.SRCALPHA)
            pg.draw.ellipse(s, (220, 180, 30), (0, 0, w, h))
            pg.draw.ellipse(s, (255, 220, 70), (1, 1, w - 2, h - 2))
            pg.draw.ellipse(s, (255, 250, 150), (w // 4, 2, w // 2, h // 4))
            Coin._cache[key] = s
        surface.blit(Coin._cache[key], (self.x - w // 2, self.y - self.RADIUS))

    def get_rect(self):
        return pg.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)


class PowerUp:
    RADIUS = 14
    _cache = {}

    def __init__(self, x, speed, kind):
        self.x = x
        self.y = float(-self.RADIUS * 2)
        self.speed = speed
        self.kind = kind
        self.angle = 0.0

    def update(self, dt):
        self.y += self.speed * dt
        self.angle += 3.0 * dt
        return self.y > HEIGHT

    def draw(self, surface):
        col = _POWERUP_COLORS[self.kind]
        pulse = abs(math.sin(self.angle))
        r = int(self.RADIUS + 4 * pulse)
        glow = pg.Surface((r * 2 + 8, r * 2 + 8), pg.SRCALPHA)
        pg.draw.circle(glow, (*col, 80), (r + 4, r + 4), r + 4)
        surface.blit(glow, (int(self.x) - r - 4, int(self.y) - r - 4))
        pg.draw.circle(surface, col, (int(self.x), int(self.y)), r)
        pg.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r, 2)
        label = _POWERUP_LABELS[self.kind]
        key = (label, r)
        if key not in PowerUp._cache:
            f = pg.font.Font(None, 16)
            PowerUp._cache[key] = f.render(label[0], True, WHITE)
        surf = PowerUp._cache[key]
        surface.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))

    def get_rect(self):
        return pg.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)


class ObstacleCar:
    _cache = {}

    def __init__(self, lane, speed):
        self.width = 48
        self.height = random.choice([82, 88, 94])
        self.x = float(LANE_CENTERS[lane] - self.width // 2)
        self.y = float(-self.height - 10)
        self.speed = speed
        self.color = random.choice(OBSTACLE_COLORS)
        self.car_type = random.choice(["sedan", "suv", "truck"])
        self.lane = lane
        key = (self.color, self.car_type, self.width, self.height)
        if key not in ObstacleCar._cache:
            s = pg.Surface((self.width + 8, self.height + 8), pg.SRCALPHA)
            draw_car(s, 4, 4, self.width, self.height, self.color, (100, 100, 120), self.car_type)
            ObstacleCar._cache[key] = s
        self._surf = ObstacleCar._cache[key]

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        surface.blit(self._surf, (int(self.x) - 4, int(self.y) - 4))

    def get_rect(self):
        return pg.Rect(int(self.x) + 4, int(self.y) + 4, self.width - 8, self.height - 8)


class Road:
    STRIPE_W = 10
    STRIPE_H = 60
    STRIPE_GAP = 100
    LANE_DIVIDERS = [LANE_CENTERS[1] - 8, LANE_CENTERS[2] - 8, LANE_CENTERS[3] - 8]
    RUMBLE_W = 18
    RUMBLE_PERIOD = 50

    def __init__(self, scroll_speed):
        self.scroll = 0.0
        self.scroll_speed = scroll_speed
        self._base = self._build_base()
        self._stripe_surf = self._build_stripe_surf()

    def _build_base(self):
        grass = pg.Surface((ROAD_LEFT, HEIGHT))
        grass.fill(GRASS_COLOR)
        rng = random.Random(42)
        for _ in range(300):
            gx = rng.randint(0, ROAD_LEFT - 4)
            gy = rng.randint(0, HEIGHT - 6)
            shade = rng.randint(-20, 20)
            col = tuple(clamp(GRASS_COLOR[i] + shade, 0, 255) for i in range(3))
            pg.draw.rect(grass, col, (gx, gy, rng.randint(2, 6), rng.randint(3, 8)))

        s = pg.Surface((WIDTH, HEIGHT))
        s.blit(grass, (0, 0))
        s.blit(pg.transform.flip(grass, True, False), (ROAD_RIGHT, 0))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_LEFT - 22, 0, 22, HEIGHT))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_RIGHT, 0, 22, HEIGHT))

        road_w = ROAD_RIGHT - ROAD_LEFT
        road_surface = pg.Surface((road_w, HEIGHT))
        base_intensity = 35
        stripe_count = 10
        stripe_h = HEIGHT // stripe_count
        for i in range(stripe_count + 1):
            intensity = base_intensity + int(10 * math.sin(i / stripe_count * math.pi * 2))
            y0 = i * stripe_h
            y1 = min(y0 + stripe_h, HEIGHT)
            pg.draw.rect(road_surface, (intensity, intensity, intensity + 5), (0, y0, road_w, y1 - y0))

        s.blit(road_surface, (ROAD_LEFT, 0))
        pg.draw.line(s, (255, 255, 100), (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
        pg.draw.line(s, (255, 255, 100), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)
        return s

    def _build_stripe_surf(self):
        period = self.STRIPE_H + self.STRIPE_GAP
        s = pg.Surface((WIDTH, period), pg.SRCALPHA)
        for lx in self.LANE_DIVIDERS:
            glow = pg.Surface((self.STRIPE_W + 4, self.STRIPE_H), pg.SRCALPHA)
            pg.draw.rect(glow, (100, 100, 150, 80), (0, 0, self.STRIPE_W + 4, self.STRIPE_H), border_radius=3)
            s.blit(glow, (lx - 2, 0))
            pg.draw.rect(s, (180, 180, 200), (lx, 0, self.STRIPE_W, self.STRIPE_H), border_radius=2)
        return s

    def update(self, dt):
        period = self.STRIPE_H + self.STRIPE_GAP
        self.scroll = (self.scroll + self.scroll_speed * dt) % period

    def draw(self, surface):
        surface.blit(self._base, (0, 0))

        period = self.RUMBLE_PERIOD
        offset = self.scroll % period
        time = pg.time.get_ticks() / 1000
        pulse = abs(math.sin(time * 10))

        for i in range(HEIGHT // period + 2):
            ry = int(i * period - offset)
            col = RED if i % 2 == 0 else (255, 200, 100)
            bright_col = tuple(clamp(c + int(50 * pulse), 0, 255) for c in col)
            pg.draw.rect(surface, bright_col, (ROAD_LEFT - self.RUMBLE_W - 22, ry, self.RUMBLE_W, period // 2))
            pg.draw.rect(surface, bright_col, (ROAD_RIGHT + 22, ry, self.RUMBLE_W, period // 2))

        sp = self.STRIPE_H + self.STRIPE_GAP
        so = int(self.scroll % sp)
        y = -sp + so
        while y < HEIGHT:
            surface.blit(self._stripe_surf, (0, y))
            y += sp


class Player:
    WIDTH = 48
    HEIGHT = 88
    SPEED = 400

    def __init__(self, color, car_type, speed_bonus=1.0):
        self.x = float(WIDTH // 2 - self.WIDTH // 2)
        self.y = float(HEIGHT - self.HEIGHT - 30)
        self.color = color
        self.car_type = car_type
        self.speed_bonus = speed_bonus
        self.vel_x = 0.0
        self.tilt = 0.0
        self.slide_vel = 0.0
        self.slide_timer = 0.0
        self.slowdown_timer = 0.0
        self.boost_timer = 0.0
        self.boost_multiplier = 1.0
        self.shield_timer = 0.0
        self.magnet_timer = 0.0
        self.freeze_timer = 0.0
        self._surf = pg.Surface((self.WIDTH + 12, self.HEIGHT + 12), pg.SRCALPHA)
        self._cached_surf = None
        self._cache_key = None
        self._prerender()

    def _prerender(self):
        key = (self.color, self.car_type)
        if self._cache_key != key:
            self._cached_surf = pg.Surface((self.WIDTH + 12, self.HEIGHT + 12), pg.SRCALPHA)
            draw_car(self._cached_surf, 6, 6, self.WIDTH, self.HEIGHT, self.color, CYAN, self.car_type, player=True)
            self._cache_key = key

    def apply_oil(self):
        self.slide_vel = random.choice([-1, 1]) * self.SPEED * 1.2
        self.slide_timer = 1.0

    def apply_speedbump(self):
        self.slowdown_timer = 1.2

    def apply_boost(self):
        self.boost_timer = 1.5
        self.boost_multiplier = 1.8

    def apply_shield(self):
        self.shield_timer = 6.0

    def apply_magnet(self):
        self.magnet_timer = 6.0

    def apply_freeze(self):
        self.freeze_timer = 5.0

    def has_shield(self):
        return self.shield_timer > 0

    def has_magnet(self):
        return self.magnet_timer > 0

    def has_freeze(self):
        return self.freeze_timer > 0

    def update(self, dt, keys):
        if self.boost_timer > 0:
            self.boost_timer -= dt
        else:
            self.boost_multiplier = 1.0
        if self.shield_timer > 0:
            self.shield_timer -= dt
        if self.magnet_timer > 0:
            self.magnet_timer -= dt
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
        if self.slide_timer > 0:
            self.slide_timer -= dt
            self.x += self.slide_vel * dt
            self.slide_vel *= (1 - dt * 3.0)
        else:
            if keys[pg.K_LEFT]:
                self.vel_x = max(self.vel_x - 1200 * dt, -self.SPEED)
            elif keys[pg.K_RIGHT]:
                self.vel_x = min(self.vel_x + 1200 * dt, self.SPEED)
            else:
                if self.vel_x:
                    self.vel_x = clamp(
                        self.vel_x - math.copysign(min(800 * dt, abs(self.vel_x)), self.vel_x),
                        -self.SPEED, self.SPEED,
                    )
                else:
                    self.vel_x = 0.0
            self.x += self.vel_x * dt
        if self.slowdown_timer > 0:
            self.slowdown_timer -= dt
        self.x = clamp(self.x, ROAD_LEFT + 2, ROAD_RIGHT - self.WIDTH - 2)
        target_tilt = (self.vel_x + self.slide_vel) / self.SPEED * 8
        self.tilt += (target_tilt - self.tilt) * 10 * dt

    def get_speed_factor(self):
        factor = self.speed_bonus
        if self.slowdown_timer > 0:
            factor *= 0.5
        if self.boost_timer > 0:
            factor *= self.boost_multiplier
        return factor

    def draw(self, surface, invincible, ticks):
        if invincible and not self.has_shield() and (ticks // 60) % 2 == 0:
            return
        cx = int(self.x + self.WIDTH // 2)
        cy = int(self.y + self.HEIGHT // 2)
        if self.has_shield():
            glow = pg.Surface((self.WIDTH + 28, self.HEIGHT + 28), pg.SRCALPHA)
            pg.draw.ellipse(glow, (80, 180, 255, 120), glow.get_rect())
            surface.blit(glow, (int(self.x) - 14, int(self.y) - 14))
            pg.draw.ellipse(surface, (80, 180, 255), (int(self.x) - 10, int(self.y) - 10, self.WIDTH + 20, self.HEIGHT + 20), 3)
        if self.boost_timer > 0:
            glow = pg.Surface((self.WIDTH + 20, self.HEIGHT + 20), pg.SRCALPHA)
            pg.draw.ellipse(glow, (255, 100, 0, 100), glow.get_rect())
            surface.blit(glow, (int(self.x) - 10, int(self.y) - 10))
        if self.has_magnet():
            pg.draw.circle(surface, (255, 80, 200), (cx, cy), self.WIDTH, 2)
        if abs(self.tilt) > 0.3:
            self._surf.fill((0, 0, 0, 0))
            self._surf.blit(self._cached_surf, (0, 0))
            rot = pg.transform.rotate(self._surf, -self.tilt)
            surface.blit(rot, rot.get_rect(center=(cx, cy)))
        else:
            surface.blit(self._cached_surf, (int(self.x) - 6, int(self.y) - 6))

    def get_rect(self):
        m = 6
        return pg.Rect(int(self.x) + m, int(self.y) + m, self.WIDTH - m * 2, self.HEIGHT - m * 2)


class HUD:
    def __init__(self, fonts):
        self.small = fonts[1]
        self.tiny = fonts[2]
        self.surf = pg.Surface((240, 185), pg.SRCALPHA)

    def draw(self, surface, score, level, speed_pct, difficulty, multiplier, lives, boost_timer, player):
        self.surf.fill((0, 0, 0, 180))
        pg.draw.rect(self.surf, (255, 255, 255, 40), (0, 0, 240, 185), 3, border_radius=10)
        pulse = int(8 * abs(math.sin(pg.time.get_ticks() / 300)))
        self._blit(f"SCORE: {score}", (255, 220, 50 + pulse), 12, 10)
        self._blit(f"LEVEL: {level}", CYAN, 12, 40)
        self._blit(f"SPEED: {speed_pct}%", GREEN, 12, 65)
        bar_width = 100
        bar_height = 8
        fill = int(bar_width * min(1.0, speed_pct / 150))
        pg.draw.rect(self.surf, (50, 50, 50), (12, 88, bar_width, bar_height), border_radius=4)
        pg.draw.rect(self.surf, GREEN, (12, 88, fill, bar_height), border_radius=4)
        self._blit(f"MODE: {difficulty}", YELLOW, 12, 100, tiny=True)
        if boost_timer > 0:
            boost_width = int(100 * (boost_timer / 1.5))
            pg.draw.rect(self.surf, ORANGE, (12, 115, boost_width, 6), border_radius=3)
            self._blit("BOOST!", (255, 105, 0), 12, 120, tiny=True)
        y_icons = 138
        for i in range(3):
            draw_heart(self.surf, 22 + i * 20, y_icons, 14, RED if i < lives else GRAY)
        if multiplier > 1.0:
            col = YELLOW if multiplier >= 2.0 else (150, 220, 150)
            glow = int(50 * abs(math.sin(pg.time.get_ticks() / 100)))
            r = clamp(col[0] + glow, 0, 255)
            g = clamp(col[1] + glow, 0, 255)
            b = clamp(col[2], 0, 255)
            self._blit(f"x{multiplier:.1f} COMBO!", (r, g, b), 130, 126, tiny=True)
        active_icons = []
        if player.has_shield():
            active_icons.append((POWERUP_SHIELD, player.shield_timer, 6.0))
        if player.has_magnet():
            active_icons.append((POWERUP_MAGNET, player.magnet_timer, 6.0))
        if player.has_freeze():
            active_icons.append((POWERUP_TIMEFREEZE, player.freeze_timer, 5.0))
        for idx, (kind, timer, max_t) in enumerate(active_icons):
            col = _POWERUP_COLORS[kind]
            bw = int(70 * (timer / max_t))
            pg.draw.rect(self.surf, (40, 40, 40), (12 + idx * 80, 158, 70, 8), border_radius=3)
            pg.draw.rect(self.surf, col, (12 + idx * 80, 158, bw, 8), border_radius=3)
            self._blit(_POWERUP_LABELS[kind], col, 12 + idx * 80, 166, tiny=True)
        surface.blit(self.surf, (10, 10))

    def _blit(self, text, color, x, y, tiny=False):
        if isinstance(color, tuple):
            color = tuple(int(clamp(c, 0, 255)) for c in color)
        self.surf.blit((self.tiny if tiny else self.small).render(text, True, color), (x, y))


class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.base_color = color or (45, 165, 75)
        self.hover_color = tuple(clamp(c + 40, 0, 255) for c in self.base_color)

    def draw(self, surface, font):
        col = self.hover_color if self.rect.collidepoint(pg.mouse.get_pos()) else self.base_color
        if self.rect.collidepoint(pg.mouse.get_pos()):
            glow = pg.Surface((self.rect.w + 10, self.rect.h + 10), pg.SRCALPHA)
            pg.draw.rect(glow, (*col, 80), (0, 0, self.rect.w + 10, self.rect.h + 10), border_radius=10)
            surface.blit(glow, (self.rect.x - 5, self.rect.y - 5))
        pg.draw.rect(surface, (0, 0, 0), (self.rect.x + 3, self.rect.y + 4, self.rect.w, self.rect.h), border_radius=8)
        pg.draw.rect(surface, col, self.rect, border_radius=8)
        pg.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        t = font.render(self.text, True, WHITE)
        surface.blit(t, t.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("HIGH SPEED RACER - Extreme Edition")
        self.clock = pg.time.Clock()
        self.fonts = (pg.font.Font(None, 48), pg.font.Font(None, 32), pg.font.Font(None, 24))
        self.selected_skin = 0
        self.selected_diff = "Medium"
        self.state = "menu"
        self.hud = HUD(self.fonts)

        self.btn_play    = Button(WIDTH // 2 - 100, 490, 200, 52, "START RACE")
        self.btn_pause   = Button(WIDTH - 115, 10, 100, 36, "PAUSE", (60, 60, 80))
        self.btn_restart = Button(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 46, "RESTART")
        self.btn_menu    = Button(WIDTH // 2 - 90, HEIGHT // 2 + 96, 180, 46, "MAIN MENU", (60, 80, 160))
        self.btn_quit    = Button(WIDTH // 2 - 90, HEIGHT // 2 + 152, 180, 46, "QUIT", (160, 50, 50))

        self._blur_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self._particle_pool = ParticlePool(_PARTICLE_POOL_SIZE)
        self._prerender_blur_lines()

        self.sounds = {}
        if HAS_NUMPY:
            self.sounds = {
                "coin":       generate_coin_sound(),
                "boost":      generate_boost_sound(),
                "levelup":    generate_levelup_sound(),
                "hit":        generate_hit_sound(),
                "explosion":  generate_explosion_sound(),
                "powerup":    generate_powerup_sound(),
            }

        self._reset_state()

    def _prerender_blur_lines(self):
        self._blur_lines = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for i in range(30):
            lx = ROAD_LEFT + (ROAD_RIGHT - ROAD_LEFT) * i // 30
            pg.draw.line(self._blur_lines, (255, 255, 255, 8), (lx, 0), (lx, HEIGHT), 2)

    def _play_sound(self, name):
        if HAS_NUMPY and name in self.sounds:
            self.sounds[name].play()

    def _reset_state(self):
        diff = DIFFICULTY[self.selected_diff]
        skin = CAR_SKINS[self.selected_skin]
        self.player           = Player(skin["color"], skin["type"], skin.get("speed_bonus", 1.0))
        self.road             = Road(diff["base_speed"])
        self.obs_cars         = []
        self.obs_misc         = []
        self.coins            = []
        self.powerups         = []
        self._particle_pool._active.clear()
        self.score            = 0
        self.level            = 1
        self.speed_pct        = 100
        self.scroll_speed     = diff["base_speed"]
        self.obs_timer        = 0.0
        self.obs_interval     = diff["obs_interval"]
        self.coin_timer       = 0.0
        self.powerup_timer    = 0.0
        self.combo            = 0
        self.multiplier       = 1.0
        self.combo_timer      = 0.0
        self.fb_text          = ""
        self.fb_pos           = (WIDTH // 2, HEIGHT // 2)
        self.fb_timer         = 0.0
        self.lives            = 3
        self.invincibility_timer  = 0.0
        self.level_flash_timer    = 0.0
        self.speed_blur_alpha     = 0.0
        self.screen_shake         = 0.0

    def _get_high_score(self):
        try:
            with open("highscore.txt") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self._get_high_score())))

    def _add_particles(self, x, y, count, color):
        for _ in range(count):
            vx = random.uniform(-200, 200)
            vy = random.uniform(-300, -100)
            lifetime = random.uniform(0.3, 0.8)
            self._particle_pool.spawn(x, y, vx, vy, color, lifetime)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                pos = ev.pos
                if self.state == "menu":
                    self._handle_menu_click(pos)
                elif self.state == "playing":
                    if self.btn_pause.rect.collidepoint(pos):
                        self.state = "paused"
                elif self.state == "paused":
                    if self.btn_pause.rect.collidepoint(pos):
                        self.state = "playing"
                    elif self.btn_restart.rect.collidepoint(pos):
                        self._reset_state()
                        self.state = "playing"
                    elif self.btn_menu.rect.collidepoint(pos):
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                elif self.state == "gameover":
                    if self.btn_restart.rect.collidepoint(pos):
                        self._reset_state()
                        self.state = "playing"
                    elif self.btn_menu.rect.collidepoint(pos):
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                    elif self.btn_quit.rect.collidepoint(pos):
                        self._save_high_score()
                        pg.quit()
                        sys.exit()
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_SPACE and self.state == "playing":
                    if self.score >= 50 and self.player.boost_timer <= 0:
                        self.score -= 50
                        self.player.apply_boost()
                        self._set_fb("BOOST!", 0.8)
                        self._add_particles(
                            self.player.x + Player.WIDTH // 2,
                            self.player.y + Player.HEIGHT,
                            20, ORANGE,
                        )
                        self._play_sound("boost")
                if ev.key in (pg.K_p, pg.K_ESCAPE):
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                    elif self.state == "gameover":
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                if ev.key == pg.K_r and self.state in ("gameover", "paused"):
                    self._reset_state()
                    self.state = "playing"

    def _handle_menu_click(self, pos):
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            if pg.Rect(WIDTH // 2 - 90, 148 + i * 46, 180, 36).collidepoint(pos):
                self.selected_diff = d
        if pg.Rect(WIDTH // 2 - 145, 365, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
        if pg.Rect(WIDTH // 2 + 105, 365, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
        if self.btn_play.rect.collidepoint(pos):
            self._reset_state()
            self.state = "playing"

    def _update(self, dt):
        if self.state != "playing":
            self.screen_shake = 0
            return

        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 6)

        self.invincibility_timer = max(0.0, self.invincibility_timer - dt)
        self.level_flash_timer   = max(0.0, self.level_flash_timer - dt)

        self.player.update(dt, pg.key.get_pressed())

        freeze_factor = 0.3 if self.player.has_freeze() else 1.0
        self.road.scroll_speed = self.scroll_speed * self.player.get_speed_factor()
        self.road.update(dt)

        self._particle_pool.update_and_draw.__func__

        target_blur = clamp((self.scroll_speed - 250) / 350 * 180, 0, 180)
        self.speed_blur_alpha += (target_blur - self.speed_blur_alpha) * dt * 6

        diff = DIFFICULTY[self.selected_diff]

        self.obs_timer += dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0.0
            self._spawn_obstacle(diff)

        self.coin_timer += dt
        if self.coin_timer >= 1.2:
            self.coin_timer = 0.0
            if random.random() < 0.3:
                for _ in range(random.randint(2, 4)):
                    self.coins.append(Coin(LANE_CENTERS[random.randint(0, 3)], self.scroll_speed * 0.95))
            else:
                self.coins.append(Coin(LANE_CENTERS[random.randint(0, 3)], self.scroll_speed * 0.95))

        self.powerup_timer += dt
        if self.powerup_timer >= 8.0:
            self.powerup_timer = 0.0
            if random.random() < 0.55:
                kind = random.choice([POWERUP_SHIELD, POWERUP_MAGNET, POWERUP_TIMEFREEZE])
                lane = random.randint(0, 3)
                self.powerups.append(PowerUp(LANE_CENTERS[lane], self.scroll_speed * 0.85, kind))

        invincible  = self.invincibility_timer > 0
        player_rect = self.player.get_rect()

        effective_dt = dt * freeze_factor
        for car in self.obs_cars[:]:
            if car.update(effective_dt):
                self.obs_cars.remove(car)
                self._on_car_passed()
                continue
            if not invincible and not self.player.has_shield() and car.get_rect().colliderect(player_rect):
                self._on_hit()
                return

        for obj in self.obs_misc[:]:
            if obj.update(effective_dt):
                self.obs_misc.remove(obj)
                self._on_misc_passed()
                continue
            if obj.get_rect().colliderect(player_rect):
                if isinstance(obj, OilSlick):
                    self.obs_misc.remove(obj)
                    if not self.player.has_shield():
                        self.player.apply_oil()
                        self._set_fb("SLIPPING!", 0.8)
                elif isinstance(obj, SpeedBump):
                    self.obs_misc.remove(obj)
                    if not self.player.has_shield():
                        self.player.apply_speedbump()
                        self._set_fb("BUMP!", 0.8)
                        self.screen_shake = 0.3
                elif not invincible and not self.player.has_shield():
                    self._on_hit()
                    return

        for coin in self.coins[:]:
            if coin.update(effective_dt):
                self.coins.remove(coin)
                continue
            collected = coin.get_rect().colliderect(player_rect)
            if not collected and self.player.has_magnet():
                dx = self.player.x + Player.WIDTH // 2 - coin.x
                dy = self.player.y + Player.HEIGHT // 2 - coin.y
                dist = math.hypot(dx, dy)
                if dist < 120:
                    coin.x += dx / dist * 300 * dt
                    coin.y += dy / dist * 300 * dt
                    collected = coin.get_rect().colliderect(player_rect)
            if collected:
                self.coins.remove(coin)
                self._on_coin(int(coin.x), int(coin.y))

        for pu in self.powerups[:]:
            if pu.update(effective_dt):
                self.powerups.remove(pu)
                continue
            if pu.get_rect().colliderect(player_rect):
                self.powerups.remove(pu)
                self._on_powerup(pu.kind, int(pu.x), int(pu.y))

        self.combo_timer += dt
        if self.combo_timer >= 2.5:
            self.combo_timer = 0.0
            if self.combo > 0:
                self.combo = max(0, self.combo - 1)
                self._recalc_multiplier()

        if self.fb_timer > 0:
            self.fb_timer -= dt

        if self.score >= (8 + self.level * 4) * self.level:
            self.level += 1
            self.scroll_speed = min(self.scroll_speed + diff["speed_inc"], diff["base_speed"] * 2.5)
            self.obs_interval = max(0.6, self.obs_interval - 0.05)
            self.speed_pct    = int(self.scroll_speed / diff["base_speed"] * 100)
            self.level_flash_timer = 1.0
            self._set_fb(f"LEVEL {self.level}!", 1.0)
            self._play_sound("levelup")
            for _ in range(5):
                self.coins.append(Coin(LANE_CENTERS[random.randint(0, 3)], self.scroll_speed * 0.9))

    def _set_fb(self, text, duration):
        self.fb_text  = text
        self.fb_pos   = (int(self.player.x + Player.WIDTH // 2), int(self.player.y))
        self.fb_timer = duration

    def _spawn_obstacle(self, diff):
        spd  = random.uniform(*diff["obs_speed"])
        occ  = {c.lane for c in self.obs_cars}
        available_lanes = [i for i in range(4) if i not in occ]
        if not available_lanes:
            available_lanes = list(range(4))
        lane = random.choice(available_lanes)
        lc   = LANE_CENTERS[lane]
        roll = random.random()

        if roll < 0.55:
            self.obs_cars.append(ObstacleCar(lane, spd))
        elif roll < 0.70:
            self.obs_misc.append(Cone(lc - Cone.WIDTH // 2, spd))
        elif roll < 0.82:
            self.obs_misc.append(Barrier(lc - Barrier.WIDTH // 2, spd))
        elif roll < 0.91:
            self.obs_misc.append(OilSlick(lc - OilSlick.WIDTH // 2, spd * 0.8))
        else:
            self.obs_misc.append(SpeedBump(lc - SpeedBump.WIDTH // 2, spd * 0.9))

    def _on_hit(self):
        self.lives -= 1
        self.combo = 0
        self._recalc_multiplier()
        self._set_fb("-1 LIFE!", 1.0)
        self.screen_shake = 0.5
        self._add_particles(
            self.player.x + Player.WIDTH // 2,
            self.player.y + Player.HEIGHT // 2,
            30, RED,
        )
        self._play_sound("hit")
        if self.lives <= 0:
            self._trigger_gameover()
            self._play_sound("explosion")
        else:
            self.invincibility_timer = 2.0

    def _on_car_passed(self):
        self.score += 2
        self.combo += 1
        self._recalc_multiplier()

    def _on_misc_passed(self):
        self.combo += 1
        self._recalc_multiplier()
        self.score += int(1 * self.multiplier)

    def _on_coin(self, x, y):
        self.combo += 1
        self._recalc_multiplier()
        gain = int(8 * self.multiplier)
        self.score += gain
        self.fb_text  = f"+{gain}"
        self.fb_pos   = (x, y)
        self.fb_timer = 0.7
        self._add_particles(x, y, 10, YELLOW)
        self._play_sound("coin")
        if random.random() < 0.1 and self.player.boost_timer <= 0:
            self.player.apply_boost()
            self._set_fb("BOOST!", 0.8)
            self._play_sound("boost")

    def _on_powerup(self, kind, x, y):
        col = _POWERUP_COLORS[kind]
        self._add_particles(x, y, 20, col)
        self._play_sound("powerup")
        if kind == POWERUP_SHIELD:
            self.player.apply_shield()
            self._set_fb("SHIELD ON!", 1.0)
        elif kind == POWERUP_MAGNET:
            self.player.apply_magnet()
            self._set_fb("MAGNET!", 1.0)
        elif kind == POWERUP_TIMEFREEZE:
            self.player.apply_freeze()
            self._set_fb("TIME FREEZE!", 1.0)

    def _recalc_multiplier(self):
        self.multiplier = (
            4.0 if self.combo >= 25 else
            3.0 if self.combo >= 18 else
            2.5 if self.combo >= 12 else
            2.0 if self.combo >= 7  else
            1.5 if self.combo >= 3  else 1.0
        )

    def _trigger_gameover(self):
        self.state = "gameover"
        self.screen_shake = 0
        self._save_high_score()

    def _draw(self):
        shake_x, shake_y = 0, 0
        if self.screen_shake > 0 and self.state == "playing":
            intensity = self.screen_shake * 15
            shake_x = random.randint(-int(intensity), int(intensity))
            shake_y = random.randint(-int(intensity // 2), int(intensity // 2))

        self.screen.fill(BLACK)

        if self.state == "menu":
            self._draw_menu()
        else:
            self.road.draw(self.screen)
            for obj in (*self.obs_cars, *self.obs_misc, *self.coins, *self.powerups):
                obj.draw(self.screen)
            self.player.draw(self.screen, self.invincibility_timer > 0, pg.time.get_ticks())

            self._particle_pool.update_and_draw(self.screen, 0)

            if self.speed_blur_alpha > 4:
                alpha = int(self.speed_blur_alpha)
                self._blur_surf.fill((0, 0, 0, 0))
                self._blur_surf.blit(self._blur_lines, (0, 0))
                self._blur_surf.set_alpha(alpha)
                self.screen.blit(self._blur_surf, (shake_x, shake_y))

            self.hud.draw(
                self.screen, self.score, self.level, self.speed_pct,
                self.selected_diff, self.multiplier, self.lives,
                self.player.boost_timer, self.player,
            )
            self.btn_pause.draw(self.screen, self.fonts[2])
            self._draw_feedback()

            if self.state == "playing" and self.score >= 50 and self.player.boost_timer <= 0:
                hint = self.fonts[2].render("SPACE = BOOST (50 pts)", True, (255, 200, 0))
                hint.set_alpha(128 + int(64 * abs(math.sin(pg.time.get_ticks() / 200))))
                self.screen.blit(hint, (WIDTH - 180, HEIGHT - 30))

            if self.level_flash_timer > 0:
                self._draw_level_flash()
            if self.state == "paused":
                self._draw_pause()
            elif self.state == "gameover":
                self._draw_gameover()

        if shake_x != 0 or shake_y != 0:
            temp_surf = self.screen.copy()
            self.screen.fill(BLACK)
            self.screen.blit(temp_surf, (shake_x, shake_y))

        pg.display.flip()

    def _draw_level_flash(self):
        alpha = int(clamp(self.level_flash_timer / 1.0 * 200, 0, 200))
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        s.fill((255, 255, 100, min(alpha // 4, 40)))
        self.screen.blit(s, (0, 0))
        t = self.fonts[0].render(f"LEVEL {self.level}!", True, YELLOW)
        t.set_alpha(alpha)
        y_offset = int(20 * math.sin(pg.time.get_ticks() / 100))
        self.screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40 + y_offset)))

    def _draw_feedback(self):
        if self.fb_timer <= 0 or not self.fb_text:
            return
        alpha = int(255 * (self.fb_timer / 0.8))
        y = self.fb_pos[1] - int((0.8 - self.fb_timer) * 80)
        surf = self.fonts[1].render(self.fb_text, True, YELLOW)
        surf.set_alpha(clamp(alpha, 0, 255))
        shadow = self.fonts[1].render(self.fb_text, True, BLACK)
        shadow.set_alpha(alpha // 2)
        self.screen.blit(shadow, (self.fb_pos[0] - surf.get_width() // 2 + 2, y + 2))
        self.screen.blit(surf, surf.get_rect(center=(self.fb_pos[0], y)))

    def _draw_menu(self):
        f_main, f_small, f_tiny = self.fonts

        time = pg.time.get_ticks() / 1000
        for y in range(HEIGHT):
            shade = 10 + int(25 * math.sin(y / 30 + time))
            shade_clamped = clamp(shade, 0, 255)
            pg.draw.line(self.screen, (shade_clamped, shade_clamped, min(shade_clamped + 10, 255)), (0, y), (WIDTH, y))

        title = f_main.render("HIGH SPEED RACER", True, YELLOW)
        tx = WIDTH // 2 - title.get_width() // 2
        for offset in range(3):
            glow = f_main.render("HIGH SPEED RACER", True, (100, 70 + offset * 20, 0))
            self.screen.blit(glow, (tx - offset, 38 - offset))
        self.screen.blit(title, (tx, 35))

        sub = f_tiny.render("EXTREME EDITION", True, ORANGE)
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 85))

        bg = pg.Surface((460, 480), pg.SRCALPHA)
        bg.fill((0, 0, 0, 190))
        pg.draw.rect(bg, (255, 255, 255, 40), (0, 0, 460, 480), 2, border_radius=15)
        self.screen.blit(bg, (WIDTH // 2 - 230, 115))

        lbl = f_small.render("DIFFICULTY", True, WHITE)
        self.screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 122))
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            r = pg.Rect(WIDTH // 2 - 90, 148 + i * 46, 180, 36)
            sel = d == self.selected_diff
            col = GREEN if sel else (70, 70, 75)
            if sel:
                pg.draw.rect(self.screen, (0, 200, 0, 80), r.inflate(10, 10), border_radius=8)
            pg.draw.rect(self.screen, col, r, border_radius=7)
            pg.draw.rect(self.screen, WHITE, r, 2 if sel else 1, border_radius=7)
            t = f_small.render(d, True, WHITE)
            self.screen.blit(t, t.get_rect(center=r.center))

        lbl2 = f_small.render("CAR SKIN", True, WHITE)
        self.screen.blit(lbl2, (WIDTH // 2 - lbl2.get_width() // 2, 310))
        skin = CAR_SKINS[self.selected_skin]
        px, py = WIDTH // 2 - 24, 345
        pbg = pg.Surface((100, 110), pg.SRCALPHA)
        pbg.fill((25, 25, 35, 220))
        pg.draw.rect(pbg, (255, 255, 255, 40), (0, 0, 100, 110), 1, border_radius=8)
        self.screen.blit(pbg, (px - 26, py - 5))
        draw_car(self.screen, px, py, 48, 88, skin["color"], CYAN, skin["type"], player=True)

        mouse = pg.mouse.get_pos()
        for rect, direction in [
            (pg.Rect(WIDTH // 2 - 145, 365, 40, 40), "left"),
            (pg.Rect(WIDTH // 2 + 105, 365, 40, 40), "right"),
        ]:
            col = GREEN if rect.collidepoint(mouse) else (70, 70, 75)
            if rect.collidepoint(mouse):
                pg.draw.rect(self.screen, (0, 200, 0, 80), rect.inflate(10, 10), border_radius=8)
            pg.draw.rect(self.screen, col, rect, border_radius=6)
            pg.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
            draw_arrow(self.screen, rect.centerx, rect.centery, 18, WHITE, direction)

        bonus_val = skin.get("speed_bonus", 1)
        bonus_text = f_tiny.render(
            f"{skin['name']} - {'+' if bonus_val > 1 else ''}{int((bonus_val - 1) * 100)}% SPEED",
            True, GREEN if bonus_val >= 1 else ORANGE,
        )
        self.screen.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, 445))

        hs_text = f"HIGH SCORE: {self._get_high_score()}"
        self.screen.blit(f_tiny.render(hs_text, True, YELLOW), (WIDTH // 2 - f_tiny.size(hs_text)[0] // 2, 465))

        self.btn_play.draw(self.screen, f_small)

        hint = f_tiny.render("   Move  |  SPACE to boost  |  P - Pause  |  R - Restart", True, GRAY)
        text_x = WIDTH // 2 - hint.get_width() // 2
        MARGIN = 20
        arrow_left_x  = text_x - 22
        arrow_right_x = text_x - 4
        if arrow_left_x < MARGIN:
            shift = MARGIN - arrow_left_x
            arrow_left_x  += shift
            arrow_right_x += shift
            text_x        += shift
        self.screen.blit(hint, (text_x, 555))
        draw_arrow(self.screen, arrow_left_x,  560, 14, GRAY, "left")
        draw_arrow(self.screen, arrow_right_x, 560, 14, GRAY, "right")

    def _draw_overlay(self, title_text, title_color, box_h, box_border_color):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))
        bx, by = WIDTH // 2 - 200, HEIGHT // 2 - box_h // 2
        box = pg.Surface((400, box_h), pg.SRCALPHA)
        box.fill((20, 20, 30, 250))
        pg.draw.rect(box, box_border_color, (0, 0, 400, box_h), 3, border_radius=15)
        self.screen.blit(box, (bx, by))
        t = self.fonts[0].render(title_text, True, title_color)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 18))
        return by

    def _draw_pause(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        by = self._draw_overlay("PAUSED", YELLOW, 260, (255, 255, 255, 60))
        center_x = WIDTH // 2
        t_score = f_small.render(f"SCORE: {self.score}", True, WHITE)
        t_level = f_small.render(f"LEVEL: {self.level}", True, CYAN)
        self.screen.blit(t_score, (center_x - t_score.get_width() // 2, by + 62))
        self.screen.blit(t_level, (center_x - t_level.get_width() // 2, by + 90))
        resume_text  = f_tiny.render("P / ESC to resume", True, GRAY)
        restart_text = f_tiny.render("R to restart", True, GRAY)
        self.screen.blit(resume_text,  (center_x - resume_text.get_width()  // 2, by + 125))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, by + 143))
        btn_width  = min(200, max(160, WIDTH // 5))
        btn_height = 46
        btn_x = center_x - btn_width // 2
        self.btn_restart.rect = pg.Rect(btn_x, by + 161, btn_width, btn_height)
        self.btn_menu.rect    = pg.Rect(btn_x, by + 209, btn_width, btn_height)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)

    def _draw_gameover(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        hs = self._get_high_score()
        by = self._draw_overlay("GAME OVER", RED, 340, (200, 30, 30, 100))
        center_x = WIDTH // 2
        t_score = f_small.render(f"SCORE: {self.score}", True, WHITE)
        t_level = f_small.render(f"LEVEL: {self.level}", True, CYAN)
        self.screen.blit(t_score, (center_x - t_score.get_width() // 2, by + 62))
        self.screen.blit(t_level, (center_x - t_level.get_width() // 2, by + 90))
        if self.score >= hs:
            hs_text = f_small.render("NEW HIGH SCORE!", True, YELLOW)
        else:
            hs_text = f_tiny.render(f"BEST: {hs}", True, GRAY)
        self.screen.blit(hs_text, (center_x - hs_text.get_width() // 2, by + 118))
        btn_width  = min(200, max(160, WIDTH // 5))
        btn_height = 46
        btn_x = center_x - btn_width // 2
        self.btn_restart.rect = pg.Rect(btn_x, by + 148, btn_width, btn_height)
        self.btn_menu.rect    = pg.Rect(btn_x, by + 200, btn_width, btn_height)
        self.btn_quit.rect    = pg.Rect(btn_x, by + 252, btn_width, btn_height)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)
        self.btn_quit.draw(self.screen, f_small)
        hint = f_tiny.render("R restart  |  ESC menu", True, GRAY)
        self.screen.blit(hint, (center_x - hint.get_width() // 2, by + 308))


if __name__ == "__main__":
    Game().run()
