import pygame as pg
import sys
import random
import math
import os
from collections import namedtuple
from bisect import bisect_left

pg.init()
pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 800, 600
FPS = 60

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

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

Skin = namedtuple("Skin", "name color type speed_bonus")
CAR_SKINS = [
    Skin("Blue Racer",       BLUE,             "sedan", 1.0),
    Skin("Red Speedster",    RED,              "sedan", 1.1),
    Skin("Green Machine",    GREEN,            "suv",   0.95),
    Skin("Yellow Lightning", YELLOW,           "sedan", 1.15),
    Skin("Purple Power",     PURPLE,           "suv",   1.0),
    Skin("Orange Blaze",     ORANGE,           "truck", 0.9),
    Skin("Cyan Cruiser",     CYAN,             "sedan", 1.05),
    Skin("Pink Dream",       PINK,             "suv",   1.0),
    Skin("Ghost White",      (230, 230, 235),  "sedan", 1.08),
    Skin("Midnight Black",   (25, 25, 30),     "sedan", 1.12),
    Skin("Lime Rocket",      (160, 230, 30),   "sedan", 1.18),
    Skin("Crimson Truck",    (180, 20, 40),    "truck", 0.88),
    Skin("Steel SUV",        (140, 160, 175),  "suv",   0.97),
    Skin("Gold Rush",        (212, 175, 55),   "sedan", 1.13),
    Skin("Neon Violet",      (138, 43, 226),   "suv",   1.02),
]

DiffSettings = namedtuple("DiffSettings", "base_speed obs_interval speed_inc obs_speed")
DIFFICULTY = {
    "Easy":   DiffSettings(280, 1.8, 6,  (220, 320)),
    "Medium": DiffSettings(380, 1.3, 9,  (280, 400)),
    "Hard":   DiffSettings(500, 0.9, 12, (350, 500)),
}

LANE_CENTERS = [212, 325, 437, 550]
OBSTACLE_COLORS = [
    (255, 80, 80), (80, 255, 80), (255, 180, 60),
    (200, 80, 255), (80, 150, 255), (255, 220, 60),
]

POWERUP_SHIELD     = "shield"
POWERUP_MAGNET     = "magnet"
POWERUP_TIMEFREEZE = "timefreeze"

POWERUP_META = {
    POWERUP_SHIELD:     ((80, 180, 255), "SHIELD",  6.0),
    POWERUP_MAGNET:     ((255, 80, 200), "MAGNET",  6.0),
    POWERUP_TIMEFREEZE: ((80, 230, 200), "FREEZE",  5.0),
}

_COMBO_THRESHOLDS  = (3, 7, 12, 18, 25)
_COMBO_MULTIPLIERS = (1.5, 2.0, 2.5, 3.0, 4.0)
_COMBO_MAP = {t: m for t, m in zip(_COMBO_THRESHOLDS, _COMBO_MULTIPLIERS)}

_PARTICLE_POOL_SIZE = 300

_ROAD_BASE_SURF = None

DAY_NIGHT_PERIOD = 60.0
WEATHER_CLEAR = "clear"
WEATHER_RAIN  = "rain"
WEATHER_FOG   = "fog"

POLICE_CHASE_DURATION  = 4.0
POLICE_ESCAPE_BONUS    = 40
POLICE_MIN_LEVEL       = 3
POLICE_SPAWN_INTERVAL  = (15.0, 25.0)

COIN_BASE_VALUE = 5

_RAIN_POOL_SIZE = 120


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def clamp_color(r, g, b):
    return (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))


def lerp_color(c0, c1, t):
    return (
        int(c0[0] + (c1[0] - c0[0]) * t),
        int(c0[1] + (c1[1] - c0[1]) * t),
        int(c0[2] + (c1[2] - c0[2]) * t),
    )


def level_threshold(level):
    return (20 + level * 6) * level


def _make_sound(wave):
    n = len(wave)
    arr = np.array(wave * 32767, dtype=np.int16)
    return pg.sndarray.make_sound(np.repeat(arr.reshape(n, 1), 2, axis=1))


class _DummySound:
    def play(self): pass


def _build_sounds():
    if not HAS_NUMPY:
        dummy = _DummySound()
        return {k: dummy for k in ("coin", "boost", "levelup", "hit", "explosion", "powerup", "siren")}
    sr = 22050

    def _buf(duration):
        n = int(sr * duration)
        return n, np.arange(n) / sr

    n, t = _buf(0.15)
    freq = 800 * np.exp(-t * 8)
    coin = _make_sound(np.sin(2 * np.pi * freq * t) * np.exp(-t * 15) * 0.6)

    n, t = _buf(0.8)
    freq = 300 + 400 * t / 0.8
    boost = _make_sound(np.sin(2 * np.pi * freq * t) * np.exp(-t * 3) * 0.76)

    n, t = _buf(0.6)
    levelup = _make_sound(
        (np.sin(2 * np.pi * 440 * t) * np.exp(-t * 2) +
         np.sin(2 * np.pi * 880 * t) * np.exp(-t * 3)) * 0.61
    )

    n, t = _buf(0.2)
    noise = np.random.normal(0, 1, n) * np.exp(-t * 20)
    tone  = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 15)
    hit   = _make_sound((noise * 0.6 + tone * 0.4) * np.exp(-t * 10) * 0.46)

    n, t = _buf(0.5)
    noise = np.random.normal(0, 1, n) * np.exp(-t * 15)
    explosion = _make_sound(noise * 0.24)

    n, t = _buf(0.5)
    freq = 500 + 700 * t / 0.5
    powerup = _make_sound(
        (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)) * np.exp(-t * 4) * 0.67
    )

    n, t = _buf(0.5)
    freq = 600 + 300 * np.sin(2 * np.pi * 4 * t)
    siren = _make_sound(np.sin(2 * np.pi * freq * t) * 0.5)

    return dict(coin=coin, boost=boost, levelup=levelup, hit=hit, explosion=explosion, powerup=powerup, siren=siren)


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
    hi = clamp_color(r + 50, g + 50, b + 50)
    sh = clamp_color(r - 40, g - 40, b - 40)

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
    elif car_type == "police":
        pg.draw.rect(surface, window_color, (x + 6, y + 12, w - 12, 20), border_radius=3)
        pg.draw.rect(surface, window_color, (x + 6, y + 38, w - 12, 18), border_radius=3)
        pg.draw.line(surface, (0, 0, 0), (x + 6, y + 23), (x + w - 6, y + 23), 1)
        pg.draw.rect(surface, WHITE, (x + 4, y + 30, w - 8, 6))
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


class ParticlePool:
    __slots__ = ("_pool", "_active")

    def __init__(self, size):
        self._pool   = [_PooledParticle() for _ in range(size)]
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
    _global_cache = {}
    _MAX_CACHE    = 128

    def __init__(self):
        self.alive       = False
        self._surf_cache = self.__class__._global_cache

    def reset(self, x, y, vx, vy, color, lifetime):
        self.x            = x
        self.y            = y
        self.vx           = vx
        self.vy           = vy
        self.color        = color
        self.lifetime     = lifetime
        self.max_lifetime = lifetime
        self.alive        = True

    def update(self, dt):
        self.x        += self.vx * dt
        self.y        += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface):
        ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * ratio)
        size  = max(2, int(4 * ratio))
        key   = (size, self.color, alpha)
        if key not in self._surf_cache:
            if len(self._surf_cache) >= self.__class__._MAX_CACHE:
                self._surf_cache.pop(next(iter(self._surf_cache)))
            s = pg.Surface((size * 2, size * 2), pg.SRCALPHA)
            pg.draw.circle(s, (*self.color, alpha), (size, size), size)
            self._surf_cache[key] = s
        surface.blit(self._surf_cache[key], (int(self.x - size), int(self.y - size)))


class RainPool:
    __slots__ = ("_drops", "_active_count")

    def __init__(self, size):
        self._drops = [[0.0, 0.0, 0.0] for _ in range(size)]
        self._active_count = 0

    def set_active(self, count):
        self._active_count = clamp(count, 0, len(self._drops))

    def reset_drop(self, idx):
        d = self._drops[idx]
        d[0] = random.uniform(0, WIDTH)
        d[1] = random.uniform(-HEIGHT, 0)
        d[2] = random.uniform(600, 900)

    def update_and_draw(self, surface, dt, intensity):
        if self._active_count <= 0:
            return
        col = (180, 200, 220, int(140 * intensity))
        for i in range(self._active_count):
            d = self._drops[i]
            if d[2] == 0.0:
                self.reset_drop(i)
                d = self._drops[i]
            d[1] += d[2] * dt
            if d[1] > HEIGHT:
                self.reset_drop(i)
                d = self._drops[i]
            pg.draw.line(surface, col, (d[0], d[1]), (d[0] - 4, d[1] + 14), 2)


class StaticObstacle:
    WIDTH  = 0
    HEIGHT = 0

    def __init__(self, x, speed):
        self.x     = x
        self.y     = float(-self.HEIGHT)
        self.speed = speed
        if not hasattr(self.__class__, "_surf") or self.__class__._surf is None:
            self.__class__._surf = self._build_surf()

    def _build_surf(self):
        raise NotImplementedError

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface, visibility):
        alpha = self._fade_alpha(visibility)
        if alpha >= 255:
            surface.blit(self.__class__._surf, (self.x, int(self.y)))
        elif alpha > 0:
            s = self.__class__._surf.copy()
            s.set_alpha(alpha)
            surface.blit(s, (self.x, int(self.y)))

    def _fade_alpha(self, visibility):
        if visibility >= HEIGHT:
            return 255
        fade_start = visibility - 80
        if self.y <= fade_start:
            return 0
        if self.y >= visibility:
            return 255
        return int(255 * (self.y - fade_start) / (visibility - fade_start))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Cone(StaticObstacle):
    WIDTH, HEIGHT = 18, 26
    _surf = None

    def _build_surf(self):
        s  = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        cx = self.WIDTH // 2
        pg.draw.polygon(s, ORANGE, [(cx, 0), (0, self.HEIGHT), (self.WIDTH, self.HEIGHT)])
        pg.draw.rect(s, (255, 200, 100), (2, self.HEIGHT - 6, self.WIDTH - 4, 4))
        return s


class Barrier(StaticObstacle):
    WIDTH, HEIGHT = 60, 20
    _surf = None

    def _build_surf(self):
        s = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        pg.draw.rect(s, (200, 200, 210), (0, 0, self.WIDTH, self.HEIGHT), border_radius=3)
        for i in range(3):
            pg.draw.rect(s, ORANGE, (i * 20 + 2, 2, 14, self.HEIGHT - 4), border_radius=2)
        return s


class SpeedBump(StaticObstacle):
    WIDTH, HEIGHT = 70, 12
    _surf = None

    def _build_surf(self):
        s  = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        pg.draw.rect(s, (180, 100, 50), (0, 0, self.WIDTH, self.HEIGHT), border_radius=5)
        sw = 10
        for i in range(self.WIDTH // (sw * 2) + 1):
            sx = i * sw * 2
            cw = min(sw, self.WIDTH - sx)
            if cw > 0:
                pg.draw.rect(s, (255, 220, 80), (sx, 0, cw, self.HEIGHT), border_radius=3)
        return s


class OilSlick:
    WIDTH, HEIGHT = 54, 28
    _surf_outer = None
    _surf_inner = None

    def __init__(self, x, speed):
        self.x     = x
        self.y     = float(-self.HEIGHT)
        self.speed = speed
        self.angle = 0.0
        if OilSlick._surf_outer is None:
            OilSlick._surf_outer = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
            OilSlick._surf_inner = pg.Surface((self.WIDTH - 10, self.HEIGHT - 6), pg.SRCALPHA)

    def update(self, dt):
        self.y     += self.speed * dt
        self.angle += dt * 2.0
        return self.y > HEIGHT

    def draw(self, surface, visibility):
        alpha = self._fade_alpha(visibility)
        if alpha <= 0:
            return
        t  = self.angle
        c0 = (
            clamp(int(100 + 80 * math.sin(t)), 0, 255),
            clamp(int(50  + 80 * math.sin(t + 2.1)), 0, 255),
            clamp(int(150 + 80 * math.sin(t + 4.2)), 0, 255),
            int(200 * alpha / 255),
        )
        c1 = (
            clamp(int(200 + 80 * math.sin(t + 1.0)), 0, 255),
            clamp(int(100 + 80 * math.sin(t + 3.1)), 0, 255),
            clamp(int(50  + 80 * math.sin(t + 5.2)), 0, 255),
            int(180 * alpha / 255),
        )
        OilSlick._surf_outer.fill((0, 0, 0, 0))
        pg.draw.ellipse(OilSlick._surf_outer, c0, OilSlick._surf_outer.get_rect())
        surface.blit(OilSlick._surf_outer, (self.x, self.y))
        OilSlick._surf_inner.fill((0, 0, 0, 0))
        pg.draw.ellipse(OilSlick._surf_inner, c1, OilSlick._surf_inner.get_rect())
        surface.blit(OilSlick._surf_inner, (self.x + 5, self.y + 3))

    def _fade_alpha(self, visibility):
        if visibility >= HEIGHT:
            return 255
        fade_start = visibility - 80
        if self.y <= fade_start:
            return 0
        if self.y >= visibility:
            return 255
        return int(255 * (self.y - fade_start) / (visibility - fade_start))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Coin:
    RADIUS = 11
    _cache = {}
    _MAX_CACHE = 64

    def __init__(self, x, speed):
        self.x     = x
        self.y     = float(-self.RADIUS * 2)
        self.speed = speed
        self.angle = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.y     += self.speed * dt
        self.angle += 8.0 * dt
        return self.y > HEIGHT

    def draw(self, surface, visibility=HEIGHT):
        w   = max(4, int(self.RADIUS * 2 * abs(math.cos(self.angle))))
        key = w
        if key not in Coin._cache:
            if len(Coin._cache) >= Coin._MAX_CACHE:
                Coin._cache.pop(next(iter(Coin._cache)))
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
    _label_cache = {}

    def __init__(self, x, speed, kind):
        self.x     = x
        self.y     = float(-self.RADIUS * 2)
        self.speed = speed
        self.kind  = kind
        self.angle = 0.0

    def update(self, dt):
        self.y     += self.speed * dt
        self.angle += 3.0 * dt
        return self.y > HEIGHT

    def draw(self, surface, visibility=HEIGHT):
        col, label, _ = POWERUP_META[self.kind]
        pulse = abs(math.sin(self.angle))
        r     = int(self.RADIUS + 4 * pulse)
        glow  = pg.Surface((r * 2 + 8, r * 2 + 8), pg.SRCALPHA)
        pg.draw.circle(glow, (*col, 80), (r + 4, r + 4), r + 4)
        surface.blit(glow, (int(self.x) - r - 4, int(self.y) - r - 4))
        pg.draw.circle(surface, col, (int(self.x), int(self.y)), r)
        pg.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r, 2)
        if label not in PowerUp._label_cache:
            f = pg.font.Font(None, 16)
            PowerUp._label_cache[label] = f.render(label[0], True, WHITE)
        surf = PowerUp._label_cache[label]
        surface.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))

    def get_rect(self):
        return pg.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)


class ObstacleCar:
    _cache = {}
    _MAX_CACHE = 64

    def __init__(self, lane, speed):
        self.width    = 48
        self.height   = random.choice([82, 88, 94])
        self.x        = float(LANE_CENTERS[lane] - self.width // 2)
        self.y        = float(-self.height - 10)
        self.speed    = speed
        self.color    = random.choice(OBSTACLE_COLORS)
        self.car_type = random.choice(["sedan", "suv", "truck"])
        self.lane     = lane
        key = (self.color, self.car_type, self.width, self.height)
        if key not in ObstacleCar._cache:
            if len(ObstacleCar._cache) >= ObstacleCar._MAX_CACHE:
                ObstacleCar._cache.pop(next(iter(ObstacleCar._cache)))
            s = pg.Surface((self.width + 8, self.height + 8), pg.SRCALPHA)
            draw_car(s, 4, 4, self.width, self.height, self.color, (100, 100, 120), self.car_type)
            ObstacleCar._cache[key] = s
        self._surf = ObstacleCar._cache[key]

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface, visibility=HEIGHT):
        alpha = self._fade_alpha(visibility)
        if alpha >= 255:
            surface.blit(self._surf, (int(self.x) - 4, int(self.y) - 4))
        elif alpha > 0:
            s = self._surf.copy()
            s.set_alpha(alpha)
            surface.blit(s, (int(self.x) - 4, int(self.y) - 4))

    def _fade_alpha(self, visibility):
        if visibility >= HEIGHT:
            return 255
        fade_start = visibility - 80
        if self.y <= fade_start:
            return 0
        if self.y >= visibility:
            return 255
        return int(255 * (self.y - fade_start) / (visibility - fade_start))

    def get_rect(self):
        return pg.Rect(int(self.x) + 4, int(self.y) + 4, self.width - 8, self.height - 8)


class PoliceCar:
    WIDTH, HEIGHT     = 48, 88
    CHASE_SPEED_MAX   = 260
    LANE_CHANGE_SPEED = 180
    _surf = None

    def __init__(self, lane, base_speed):
        self.lane           = lane
        self.x              = float(LANE_CENTERS[lane] - self.WIDTH // 2)
        self.y              = float(HEIGHT + self.HEIGHT)
        self.base_speed     = base_speed
        self.chase_timer    = 0.0
        self.escaped        = False
        self.light_phase    = 0.0
        self.target_x       = self.x
        self.retarget_timer = 0.0
        if PoliceCar._surf is None:
            s = pg.Surface((self.WIDTH + 8, self.HEIGHT + 8), pg.SRCALPHA)
            draw_car(s, 4, 4, self.WIDTH, self.HEIGHT, (20, 30, 90), (100, 100, 120), "police")
            PoliceCar._surf = s

    def update(self, dt, player_x, player_vel_x, scroll_speed):
        self.chase_timer += dt
        self.light_phase  += dt * 10.0

        self.retarget_timer -= dt
        if self.retarget_timer <= 0:
            lead = clamp(player_vel_x * 0.25, -60, 60)
            self.target_x = player_x + lead
            self.retarget_timer = random.uniform(0.2, 0.4)

        dx = self.target_x - self.x
        self.x += clamp(dx, -self.LANE_CHANGE_SPEED * dt, self.LANE_CHANGE_SPEED * dt)

        gap = self.y - (HEIGHT - self.HEIGHT - 30)
        closing = clamp(gap * 1.8, -self.CHASE_SPEED_MAX, self.CHASE_SPEED_MAX)
        self.y -= closing * dt

        if self.chase_timer >= POLICE_CHASE_DURATION and not self.escaped:
            self.escaped = True
            return True
        return self.y < -self.HEIGHT - 40

    def draw(self, surface, visibility=HEIGHT):
        blink = (int(self.light_phase) % 2 == 0)
        light_col = RED if blink else BLUE
        glow = pg.Surface((self.WIDTH + 30, 16), pg.SRCALPHA)
        pg.draw.ellipse(glow, (*light_col, 140), glow.get_rect())
        surface.blit(glow, (int(self.x) - 15, int(self.y) - 6))
        surface.blit(self._surf, (int(self.x) - 4, int(self.y) - 4))

    def get_rect(self):
        return pg.Rect(int(self.x) + 4, int(self.y) + 4, self.WIDTH - 8, self.HEIGHT - 8)


class Road:
    STRIPE_W    = 10
    STRIPE_H    = 60
    STRIPE_GAP  = 100
    LANE_DIVIDERS = [
        LANE_CENTERS[0] - 8,
        LANE_CENTERS[1] - 8,
        LANE_CENTERS[2] - 8,
        LANE_CENTERS[3] - 8,
    ]
    RUMBLE_W      = 18
    RUMBLE_PERIOD = 50

    def __init__(self, scroll_speed):
        self.scroll       = 0.0
        self.scroll_speed = scroll_speed
        self._base        = self._build_base()
        self._stripe_surf = self._build_stripe_surf()

    def _build_base(self):
        global _ROAD_BASE_SURF
        if _ROAD_BASE_SURF is not None:
            return _ROAD_BASE_SURF

        grass = pg.Surface((ROAD_LEFT, HEIGHT))
        grass.fill(GRASS_COLOR)
        rng = random.Random(42)
        for _ in range(300):
            gx    = rng.randint(0, ROAD_LEFT - 4)
            gy    = rng.randint(0, HEIGHT - 6)
            shade = rng.randint(-20, 20)
            col   = tuple(clamp(GRASS_COLOR[i] + shade, 0, 255) for i in range(3))
            pg.draw.rect(grass, col, (gx, gy, rng.randint(2, 6), rng.randint(3, 8)))

        s = pg.Surface((WIDTH, HEIGHT))
        s.blit(grass, (0, 0))
        s.blit(pg.transform.flip(grass, True, False), (ROAD_RIGHT, 0))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_LEFT - 22, 0, 22, HEIGHT))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_RIGHT, 0, 22, HEIGHT))

        road_w = ROAD_RIGHT - ROAD_LEFT
        road_surface = pg.Surface((road_w, HEIGHT))
        base_intensity = 35
        stripe_count   = 10
        stripe_h       = HEIGHT // stripe_count
        for i in range(stripe_count + 1):
            intensity = base_intensity + int(10 * math.sin(i / stripe_count * math.pi * 2))
            y0 = i * stripe_h
            y1 = min(y0 + stripe_h, HEIGHT)
            pg.draw.rect(road_surface, (intensity, intensity, intensity + 5), (0, y0, road_w, y1 - y0))

        s.blit(road_surface, (ROAD_LEFT, 0))
        pg.draw.line(s, (255, 255, 100), (ROAD_LEFT, 0),  (ROAD_LEFT,  HEIGHT), 4)
        pg.draw.line(s, (255, 255, 100), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)
        _ROAD_BASE_SURF = s
        return s

    def _build_stripe_surf(self):
        period = self.STRIPE_H + self.STRIPE_GAP
        s      = pg.Surface((WIDTH, period), pg.SRCALPHA)
        for lx in self.LANE_DIVIDERS:
            glow = pg.Surface((self.STRIPE_W + 4, self.STRIPE_H), pg.SRCALPHA)
            pg.draw.rect(glow, (100, 100, 150, 80), (0, 0, self.STRIPE_W + 4, self.STRIPE_H), border_radius=3)
            s.blit(glow, (lx - 2, 0))
            pg.draw.rect(s, (180, 180, 200), (lx, 0, self.STRIPE_W, self.STRIPE_H), border_radius=2)
        return s

    def update(self, dt):
        period      = self.STRIPE_H + self.STRIPE_GAP
        self.scroll = (self.scroll + self.scroll_speed * dt) % period

    def draw(self, surface):
        surface.blit(self._base, (0, 0))

        period  = self.RUMBLE_PERIOD
        offset  = self.scroll % period
        elapsed = pg.time.get_ticks() / 1000
        pulse   = abs(math.sin(elapsed * 10))

        for i in range(HEIGHT // period + 2):
            ry         = int(i * period - offset)
            col        = RED if i % 2 == 0 else (255, 200, 100)
            bright_col = tuple(clamp(c + int(50 * pulse), 0, 255) for c in col)
            pg.draw.rect(surface, bright_col, (ROAD_LEFT - self.RUMBLE_W - 22, ry, self.RUMBLE_W, period // 2))
            pg.draw.rect(surface, bright_col, (ROAD_RIGHT + 22, ry, self.RUMBLE_W, period // 2))

        sp = self.STRIPE_H + self.STRIPE_GAP
        so = int(self.scroll % sp)
        y  = -sp + so
        while y < HEIGHT:
            surface.blit(self._stripe_surf, (0, y))
            y += sp


class Player:
    WIDTH  = 48
    HEIGHT = 88
    SPEED  = 400

    def __init__(self, skin):
        self.x                = float(WIDTH // 2 - self.WIDTH // 2)
        self.y                = float(HEIGHT - self.HEIGHT - 30)
        self.color            = skin.color
        self.car_type         = skin.type
        self.speed_bonus      = skin.speed_bonus
        self.vel_x            = 0.0
        self.tilt             = 0.0
        self.slide_vel        = 0.0
        self.slide_timer      = 0.0
        self.slowdown_timer   = 0.0
        self.hazard_lockout   = 0.0
        self.boost_timer      = 0.0
        self.boost_multiplier = 1.0
        self._powerup_timers  = {POWERUP_SHIELD: 0.0, POWERUP_MAGNET: 0.0, POWERUP_TIMEFREEZE: 0.0}
        self._surf            = pg.Surface((self.WIDTH + 12, self.HEIGHT + 12), pg.SRCALPHA)
        self._cached_surf     = None
        self._cache_key       = None
        self._prerender()

    def _prerender(self):
        key = (self.color, self.car_type)
        if self._cache_key != key:
            self._cached_surf = pg.Surface((self.WIDTH + 12, self.HEIGHT + 12), pg.SRCALPHA)
            draw_car(self._cached_surf, 6, 6, self.WIDTH, self.HEIGHT, self.color, CYAN, self.car_type, player=True)
            self._cache_key = key

    def apply_powerup(self, kind):
        _, _, duration = POWERUP_META[kind]
        self._powerup_timers[kind] = duration

    def has_powerup(self, kind):
        return self._powerup_timers[kind] > 0

    def apply_oil(self):
        if self.hazard_lockout > 0:
            return
        self.slide_vel      = random.choice([-1, 1]) * self.SPEED * 1.2
        self.slide_timer    = 1.0
        self.hazard_lockout = 1.0

    def apply_speedbump(self):
        if self.hazard_lockout > 0:
            return
        self.slowdown_timer = 1.2
        self.hazard_lockout  = 1.2

    def apply_boost(self):
        self.boost_timer      = 1.5
        self.boost_multiplier = 1.8

    def update(self, dt, keys, rain_grip_penalty=0.0):
        if self.boost_timer > 0:
            self.boost_timer -= dt
        else:
            self.boost_multiplier = 1.0
        for kind in self._powerup_timers:
            if self._powerup_timers[kind] > 0:
                self._powerup_timers[kind] -= dt
        if self.hazard_lockout > 0:
            self.hazard_lockout -= dt
        if self.slide_timer > 0:
            self.slide_timer -= dt
            self.x           += self.slide_vel * dt
            self.slide_vel   *= (1 - dt * 3.0)
        else:
            accel = 1200 * (1.0 - rain_grip_penalty)
            decel = 800 * (1.0 - rain_grip_penalty)
            if keys[pg.K_LEFT]:
                self.vel_x = max(self.vel_x - accel * dt, -self.SPEED)
            elif keys[pg.K_RIGHT]:
                self.vel_x = min(self.vel_x + accel * dt, self.SPEED)
            else:
                if self.vel_x:
                    self.vel_x = clamp(
                        self.vel_x - math.copysign(min(decel * dt, abs(self.vel_x)), self.vel_x),
                        -self.SPEED, self.SPEED,
                    )
                else:
                    self.vel_x = 0.0
            self.x += self.vel_x * dt
        if self.slowdown_timer > 0:
            self.slowdown_timer -= dt
        self.x         = clamp(self.x, ROAD_LEFT + 2, ROAD_RIGHT - self.WIDTH - 2)
        target_tilt    = (self.vel_x + self.slide_vel) / self.SPEED * 8
        self.tilt     += (target_tilt - self.tilt) * 10 * dt

    def get_speed_factor(self):
        factor = self.speed_bonus
        if self.slowdown_timer > 0:
            factor *= 0.5
        if self.boost_timer > 0:
            factor *= self.boost_multiplier
        return factor

    def draw(self, surface, invincible, ticks, headlights=False):
        if invincible and not self.has_powerup(POWERUP_SHIELD) and (ticks // 60) % 2 == 0:
            return
        cx = int(self.x + self.WIDTH // 2)
        cy = int(self.y + self.HEIGHT // 2)
        if headlights:
            for lx in (self.x + 6, self.x + self.WIDTH - 18):
                cone = pg.Surface((70, 140), pg.SRCALPHA)
                pg.draw.polygon(cone, (255, 250, 200, 50), [(35, 10), (0, 140), (70, 140)])
                surface.blit(cone, (int(lx) - 35 + 6, int(self.y) - 130))
        if self.has_powerup(POWERUP_SHIELD):
            glow = pg.Surface((self.WIDTH + 28, self.HEIGHT + 28), pg.SRCALPHA)
            pg.draw.ellipse(glow, (80, 180, 255, 120), glow.get_rect())
            surface.blit(glow, (int(self.x) - 14, int(self.y) - 14))
            pg.draw.ellipse(surface, (80, 180, 255), (int(self.x) - 10, int(self.y) - 10, self.WIDTH + 20, self.HEIGHT + 20), 3)
        if self.boost_timer > 0:
            glow = pg.Surface((self.WIDTH + 20, self.HEIGHT + 20), pg.SRCALPHA)
            pg.draw.ellipse(glow, (255, 100, 0, 100), glow.get_rect())
            surface.blit(glow, (int(self.x) - 10, int(self.y) - 10))
        if self.has_powerup(POWERUP_MAGNET):
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
        self.tiny  = fonts[2]
        self.surf  = pg.Surface((240, 215), pg.SRCALPHA)
        self._text_cache = {}

    def _render(self, font, text, color):
        key = (id(font), text, color)
        if key not in self._text_cache:
            self._text_cache[key] = font.render(text, True, color)
        return self._text_cache[key]

    def invalidate(self, *keys):
        for k in list(self._text_cache):
            if k[1] in keys:
                del self._text_cache[k]

    def draw(self, surface, score, level, speed_pct, difficulty, multiplier, lives, boost_timer, player, weather, chased):
        self.surf.fill((0, 0, 0, 180))
        pg.draw.rect(self.surf, (255, 255, 255, 40), (0, 0, 240, 215), 3, border_radius=10)
        pulse = int(8 * abs(math.sin(pg.time.get_ticks() / 300)))
        score_col = (255, 220, 50 + pulse)
        self._blit(f"SCORE: {score}", score_col, 12, 10)
        self._blit(f"LEVEL: {level}", CYAN, 12, 40)
        self._blit(f"SPEED: {speed_pct}%", GREEN, 12, 65)
        bar_width, bar_height = 100, 8
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
            col  = YELLOW if multiplier >= 2.0 else (150, 220, 150)
            glow = int(50 * abs(math.sin(pg.time.get_ticks() / 100)))
            self._blit(f"x{multiplier:.1f} COMBO!", clamp_color(col[0] + glow, col[1] + glow, col[2]), 130, 126, tiny=True)
        active_icons = [
            (k, player._powerup_timers[k], POWERUP_META[k][2])
            for k in (POWERUP_SHIELD, POWERUP_MAGNET, POWERUP_TIMEFREEZE)
            if player.has_powerup(k)
        ]
        for idx, (kind, timer, max_t) in enumerate(active_icons):
            col, label, _ = POWERUP_META[kind]
            bw = int(70 * (timer / max_t))
            pg.draw.rect(self.surf, (40, 40, 40), (12 + idx * 80, 158, 70, 8), border_radius=3)
            pg.draw.rect(self.surf, col, (12 + idx * 80, 158, bw, 8), border_radius=3)
            self._blit(label, col, 12 + idx * 80, 166, tiny=True)
        if weather != WEATHER_CLEAR:
            wcol = (140, 170, 220) if weather == WEATHER_RAIN else (200, 200, 200)
            self._blit(weather.upper(), wcol, 12, 182, tiny=True)
        if chased:
            blink = (pg.time.get_ticks() // 250) % 2 == 0
            if blink:
                self._blit("POLICE CHASE!", RED, 110, 182, tiny=True)
        surface.blit(self.surf, (10, 10))

    def _blit(self, text, color, x, y, tiny=False):
        if isinstance(color, tuple):
            color = tuple(int(clamp(c, 0, 255)) for c in color)
        font = self.tiny if tiny else self.small
        self.surf.blit(self._render(font, text, color), (x, y))


class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect        = pg.Rect(x, y, w, h)
        self.text        = text
        self.base_color  = color or (45, 165, 75)
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
        self.screen         = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("HIGH SPEED RACER - Extreme Edition")
        self.clock          = pg.time.Clock()
        self.fonts          = (pg.font.Font(None, 48), pg.font.Font(None, 32), pg.font.Font(None, 24))
        self.selected_skin  = 0
        self.selected_diff  = "Medium"
        self.state          = "menu"
        self.hud            = HUD(self.fonts)
        self._init_ui()
        self._blur_surf     = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self._tint_surf     = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self._particle_pool = ParticlePool(_PARTICLE_POOL_SIZE)
        self._rain_pool      = RainPool(_RAIN_POOL_SIZE)
        self._prerender_blur_lines()
        self.sounds         = _build_sounds()
        self._high_score    = self._load_high_score()
        self._reset_state()

    def _init_ui(self):
        btn_w = min(200, max(160, WIDTH // 5))
        self.btn_play    = Button(WIDTH // 2 - 100, 490, 200, 52, "START RACE")
        self.btn_pause   = Button(WIDTH - 115, 10, 100, 36, "PAUSE", (60, 60, 80))
        self.btn_restart = Button(WIDTH // 2 - btn_w // 2, 0, btn_w, 46, "RESTART")
        self.btn_menu    = Button(WIDTH // 2 - btn_w // 2, 0, btn_w, 46, "MAIN MENU", (60, 80, 160))
        self.btn_quit    = Button(WIDTH // 2 - btn_w // 2, 0, btn_w, 46, "QUIT", (160, 50, 50))
        self._diff_rects = {
            d: pg.Rect(WIDTH // 2 - 90, 148 + i * 46, 180, 36)
            for i, d in enumerate(["Easy", "Medium", "Hard"])
        }
        self._arrow_left_rect  = pg.Rect(WIDTH // 2 - 145, 365, 40, 40)
        self._arrow_right_rect = pg.Rect(WIDTH // 2 + 105, 365, 40, 40)
        self._overlay_btn_w    = btn_w

    def _layout_overlay_buttons(self, by, include_quit=False):
        bw = self._overlay_btn_w
        bx = WIDTH // 2 - bw // 2
        self.btn_restart.rect = pg.Rect(bx, by + 148, bw, 46)
        self.btn_menu.rect    = pg.Rect(bx, by + 200, bw, 46)
        if include_quit:
            self.btn_quit.rect = pg.Rect(bx, by + 252, bw, 46)

    def _prerender_blur_lines(self):
        self._blur_lines = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for i in range(30):
            lx = ROAD_LEFT + (ROAD_RIGHT - ROAD_LEFT) * i // 30
            pg.draw.line(self._blur_lines, (255, 255, 255, 8), (lx, 0), (lx, HEIGHT), 2)

    def _play_sound(self, name):
        self.sounds[name].play()

    def _reset_state(self):
        diff                     = DIFFICULTY[self.selected_diff]
        skin                     = CAR_SKINS[self.selected_skin]
        self.player              = Player(skin)
        self.road                = Road(diff.base_speed)
        self.obs_cars            = []
        self.obs_misc            = []
        self.coins               = []
        self.powerups            = []
        self.police              = []
        self._particle_pool._active.clear()
        self.score               = 0
        self.level               = 1
        self.speed_pct           = 100
        self.scroll_speed        = diff.base_speed
        self.obs_timer           = 0.0
        self.obs_interval        = diff.obs_interval
        self.coin_timer          = 0.0
        self.powerup_timer       = 0.0
        self.combo               = 0
        self.multiplier          = 1.0
        self.combo_timer         = 0.0
        self.fb_text             = ""
        self.fb_pos              = (WIDTH // 2, HEIGHT // 2)
        self.fb_timer            = 0.0
        self.lives               = 3
        self.invincibility_timer = 0.0
        self.level_flash_timer   = 0.0
        self.speed_blur_alpha    = 0.0
        self.screen_shake        = 0.0
        self.day_night_time      = 0.0
        self.weather             = WEATHER_CLEAR
        self.weather_timer       = random.uniform(20.0, 40.0)
        self.police_timer        = random.uniform(*POLICE_SPAWN_INTERVAL)

    def _load_high_score(self):
        try:
            with open("highscore.txt") as f:
                value = f.read().strip()
            score = int(value)
            if score < 0:
                return 0
            return score
        except FileNotFoundError:
            return 0
        except (ValueError, OSError):
            return 0

    def _save_high_score(self):
        self._high_score = max(self.score, self._high_score)
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self._high_score))
        except OSError:
            pass

    def _add_particles(self, x, y, count, color):
        for _ in range(count):
            vx       = random.uniform(-200, 200)
            vy       = random.uniform(-300, -100)
            lifetime = random.uniform(0.3, 0.8)
            self._particle_pool.spawn(x, y, vx, vy, color, lifetime)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw(dt)

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
                        self._reset_state(); self.state = "playing"
                    elif self.btn_menu.rect.collidepoint(pos):
                        self._save_high_score(); self._reset_state(); self.state = "menu"
                elif self.state == "gameover":
                    if self.btn_restart.rect.collidepoint(pos):
                        self._reset_state(); self.state = "playing"
                    elif self.btn_menu.rect.collidepoint(pos):
                        self._save_high_score(); self._reset_state(); self.state = "menu"
                    elif self.btn_quit.rect.collidepoint(pos):
                        self._save_high_score(); pg.quit(); sys.exit()
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_SPACE and self.state == "playing":
                    if self.score >= 50 and self.player.boost_timer <= 0:
                        self.score -= 50
                        self.player.apply_boost()
                        self._set_fb("BOOST!", 0.8)
                        self._add_particles(self.player.x + Player.WIDTH // 2, self.player.y + Player.HEIGHT, 20, ORANGE)
                        self._play_sound("boost")
                    else:
                        self._set_fb("NEED 50 PTS!", 0.7)
                if ev.key in (pg.K_p, pg.K_ESCAPE):
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                    elif self.state == "gameover":
                        self._save_high_score(); self._reset_state(); self.state = "menu"
                if ev.key == pg.K_r and self.state in ("gameover", "paused"):
                    self._reset_state(); self.state = "playing"

    def _handle_menu_click(self, pos):
        for d, r in self._diff_rects.items():
            if r.collidepoint(pos):
                self.selected_diff = d
        if self._arrow_left_rect.collidepoint(pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
        if self._arrow_right_rect.collidepoint(pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
        if self.btn_play.rect.collidepoint(pos):
            self._reset_state(); self.state = "playing"

    def _night_factor(self):
        phase = (self.day_night_time % DAY_NIGHT_PERIOD) / DAY_NIGHT_PERIOD
        return (math.sin(phase * math.pi * 2 - math.pi / 2) + 1) / 2

    def _visibility_distance(self):
        if self.weather == WEATHER_FOG:
            return HEIGHT * 0.45
        return HEIGHT

    def _update_weather(self, dt):
        self.weather_timer -= dt
        if self.weather_timer <= 0:
            if self.weather == WEATHER_CLEAR:
                self.weather = random.choice([WEATHER_RAIN, WEATHER_FOG])
                self.weather_timer = random.uniform(8.0, 15.0)
            else:
                self.weather = WEATHER_CLEAR
                self.weather_timer = random.uniform(20.0, 40.0)
            self._rain_pool.set_active(_RAIN_POOL_SIZE if self.weather == WEATHER_RAIN else 0)

    def _update_police(self, dt, diff):
        if self.level < POLICE_MIN_LEVEL:
            return
        self.police_timer -= dt
        if self.police_timer <= 0:
            lo, hi = POLICE_SPAWN_INTERVAL
            self.police_timer = max(8.0, random.uniform(lo, hi) - self.level * 0.6)
            lane = random.randint(0, 3)
            self.police.append(PoliceCar(lane, diff.base_speed))
            self._play_sound("siren")

        player_rect = self.player.get_rect()
        for car in self.police[:]:
            finished = car.update(dt, self.player.x, self.player.vel_x, self.scroll_speed)
            if finished:
                self.police.remove(car)
                if car.escaped and car.y > -car.HEIGHT:
                    self.score += POLICE_ESCAPE_BONUS
                    self._set_fb(f"ESCAPED! +{POLICE_ESCAPE_BONUS}", 1.0)
                continue
            if not self.invincibility_timer > 0 and not self.player.has_powerup(POWERUP_SHIELD):
                if car.get_rect().colliderect(player_rect):
                    self.police.remove(car)
                    self._on_hit()
                    return

    def _update(self, dt):
        if self.state != "playing":
            self.screen_shake = 0
            return

        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 6)

        self.invincibility_timer = max(0.0, self.invincibility_timer - dt)
        self.level_flash_timer   = max(0.0, self.level_flash_timer - dt)
        self.day_night_time     += dt
        self._update_weather(dt)

        rain_penalty = 0.25 if self.weather == WEATHER_RAIN else 0.0
        self.player.update(dt, pg.key.get_pressed(), rain_grip_penalty=rain_penalty)

        freeze_factor          = 0.3 if self.player.has_powerup(POWERUP_TIMEFREEZE) else 1.0
        rain_speed_factor      = 0.9 if self.weather == WEATHER_RAIN else 1.0
        base_speed_factor      = self.player.get_speed_factor() * freeze_factor * rain_speed_factor
        self.road.scroll_speed = self.scroll_speed * base_speed_factor
        self.road.update(dt)

        self.speed_pct = int(self.scroll_speed / DIFFICULTY[self.selected_diff].base_speed * 100)

        target_blur           = clamp((self.scroll_speed - 250) / 350 * 180, 0, 180)
        self.speed_blur_alpha += (target_blur - self.speed_blur_alpha) * dt * 6

        diff = DIFFICULTY[self.selected_diff]

        self.obs_timer += dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0.0
            self._spawn_obstacle(diff)

        self.coin_timer += dt
        if self.coin_timer >= 1.2:
            self.coin_timer = 0.0
            existing_xs = {c.x for c in self.coins if c.y < 0}
            count = random.randint(2, 4) if random.random() < 0.3 else 1
            available = [lc for lc in LANE_CENTERS if lc not in existing_xs]
            if not available:
                available = LANE_CENTERS
            for lc in random.sample(available, min(count, len(available))):
                self.coins.append(Coin(lc, self.scroll_speed * 0.95))

        self.powerup_timer += dt
        if self.powerup_timer >= 8.0:
            self.powerup_timer = 0.0
            if random.random() < 0.55:
                kind = random.choice([POWERUP_SHIELD, POWERUP_MAGNET, POWERUP_TIMEFREEZE])
                self.powerups.append(PowerUp(LANE_CENTERS[random.randint(0, 3)], self.scroll_speed * 0.85, kind))

        self._update_police(dt, diff)
        if self.state != "playing":
            return

        invincible   = self.invincibility_timer > 0
        player_rect  = self.player.get_rect()
        effective_dt = dt * freeze_factor

        for car in self.obs_cars[:]:
            if car.update(effective_dt):
                self.obs_cars.remove(car)
                self._on_obstacle_passed(2)
                continue
            if not invincible and not self.player.has_powerup(POWERUP_SHIELD) and car.get_rect().colliderect(player_rect):
                self._on_hit()
                return

        for obj in self.obs_misc[:]:
            if obj.update(effective_dt):
                self.obs_misc.remove(obj)
                self._on_obstacle_passed(1)
                continue
            if obj.get_rect().colliderect(player_rect):
                if isinstance(obj, OilSlick):
                    self.obs_misc.remove(obj)
                    if not self.player.has_powerup(POWERUP_SHIELD):
                        self.player.apply_oil()
                        self._set_fb("SLIPPING!", 0.8)
                elif isinstance(obj, SpeedBump):
                    self.obs_misc.remove(obj)
                    if not self.player.has_powerup(POWERUP_SHIELD):
                        self.player.apply_speedbump()
                        self._set_fb("BUMP!", 0.8)
                        self.screen_shake = 0.3
                elif not invincible and not self.player.has_powerup(POWERUP_SHIELD):
                    self._on_hit()
                    return

        for coin in self.coins[:]:
            if coin.update(effective_dt):
                self.coins.remove(coin)
                continue
            collected = coin.get_rect().colliderect(player_rect)
            if not collected and self.player.has_powerup(POWERUP_MAGNET):
                dx   = self.player.x + Player.WIDTH // 2 - coin.x
                dy   = self.player.y + Player.HEIGHT // 2 - coin.y
                dist = math.hypot(dx, dy)
                if dist < 120:
                    coin.x   += dx / dist * 300 * dt
                    coin.y   += dy / dist * 300 * dt
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

        if self.score >= level_threshold(self.level):
            self.level         += 1
            self.scroll_speed   = min(self.scroll_speed + diff.speed_inc, diff.base_speed * 2.5)
            self.obs_interval   = max(0.6, self.obs_interval - 0.05)
            self.speed_pct      = int(self.scroll_speed / diff.base_speed * 100)
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
        spd             = random.uniform(*diff.obs_speed)
        occ             = {c.lane for c in self.obs_cars}
        available_lanes = [i for i in range(4) if i not in occ] or list(range(4))
        lane            = random.choice(available_lanes)
        lc              = LANE_CENTERS[lane]
        roll            = random.random()
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
        self.combo  = 0
        self._recalc_multiplier()
        self._set_fb("-1 LIFE!", 1.0)
        self.screen_shake = 0.5
        self._add_particles(self.player.x + Player.WIDTH // 2, self.player.y + Player.HEIGHT // 2, 30, RED)
        self._play_sound("hit")
        if self.lives <= 0:
            self._trigger_gameover()
            self._play_sound("explosion")
        else:
            self.invincibility_timer = 2.0

    def _on_obstacle_passed(self, base_points):
        self.combo += 1
        self._recalc_multiplier()
        self.score += int(base_points * self.multiplier)

    def _on_coin(self, x, y):
        self.combo += 1
        self._recalc_multiplier()
        gain          = int(COIN_BASE_VALUE * self.multiplier)
        self.score   += gain
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
        col, _, _ = POWERUP_META[kind]
        self._add_particles(x, y, 20, col)
        self._play_sound("powerup")
        self.player.apply_powerup(kind)
        labels = {POWERUP_SHIELD: "SHIELD ON!", POWERUP_MAGNET: "MAGNET!", POWERUP_TIMEFREEZE: "TIME FREEZE!"}
        self._set_fb(labels[kind], 1.0)

    def _recalc_multiplier(self):
        idx = bisect_left(_COMBO_THRESHOLDS, self.combo)
        self.multiplier = _COMBO_MULTIPLIERS[idx] if idx < len(_COMBO_MULTIPLIERS) else 1.0

    def _trigger_gameover(self):
        self.state        = "gameover"
        self.screen_shake = 0
        self._save_high_score()

    def _draw(self, dt):
        shake_x, shake_y = 0, 0
        if self.screen_shake > 0 and self.state == "playing":
            intensity = self.screen_shake * 15
            shake_x   = random.randint(-int(intensity), int(intensity))
            shake_y   = random.randint(-int(intensity // 2), int(intensity // 2))

        self.screen.fill(BLACK)

        if self.state == "menu":
            self._draw_menu()
            pg.display.flip()
            return

        visibility = self._visibility_distance()
        night      = self._night_factor()

        gameplay_surf = pg.Surface((WIDTH, HEIGHT))
        gameplay_surf.fill(BLACK)
        self.road.draw(gameplay_surf)
        for obj in (*self.obs_cars, *self.obs_misc):
            obj.draw(gameplay_surf, visibility)
        for obj in (*self.coins, *self.powerups):
            obj.draw(gameplay_surf)
        for car in self.police:
            car.draw(gameplay_surf, visibility)
        self.player.draw(gameplay_surf, self.invincibility_timer > 0, pg.time.get_ticks(), headlights=night > 0.55)
        self._particle_pool.update_and_draw(gameplay_surf, dt)

        if self.weather == WEATHER_RAIN:
            self._rain_pool.update_and_draw(gameplay_surf, dt, 1.0)

        if night > 0.05:
            self._tint_surf.fill((0, 0, 0, 0))
            tint_alpha = int(140 * night)
            self._tint_surf.fill((10, 15, 45, tint_alpha))
            gameplay_surf.blit(self._tint_surf, (0, 0))

        if self.weather == WEATHER_FOG:
            self._tint_surf.fill((0, 0, 0, 0))
            self._tint_surf.fill((210, 210, 215, 90))
            gameplay_surf.blit(self._tint_surf, (0, 0))

        if self.speed_blur_alpha > 4:
            alpha = int(self.speed_blur_alpha)
            self._blur_surf.fill((0, 0, 0, 0))
            self._blur_surf.blit(self._blur_lines, (0, 0))
            self._blur_surf.set_alpha(alpha)
            gameplay_surf.blit(self._blur_surf, (0, 0))

        self.screen.blit(gameplay_surf, (shake_x, shake_y))

        chased = len(self.police) > 0
        self.hud.draw(
            self.screen, self.score, self.level, self.speed_pct,
            self.selected_diff, self.multiplier, self.lives,
            self.player.boost_timer, self.player, self.weather, chased,
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

        pg.display.flip()

    def _draw_level_flash(self):
        alpha = int(clamp(self.level_flash_timer / 1.0 * 200, 0, 200))
        s     = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        s.fill((255, 255, 100, min(alpha // 4, 40)))
        self.screen.blit(s, (0, 0))
        t = self.fonts[0].render(f"LEVEL {self.level}!", True, YELLOW)
        t.set_alpha(alpha)
        y_offset = int(20 * math.sin(pg.time.get_ticks() / 100))
        self.screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40 + y_offset)))

    def _draw_feedback(self):
        if self.fb_timer <= 0 or not self.fb_text:
            return
        alpha  = int(255 * (self.fb_timer / 0.8))
        y      = self.fb_pos[1] - int((0.8 - self.fb_timer) * 80)
        surf   = self.fonts[1].render(self.fb_text, True, YELLOW)
        surf.set_alpha(clamp(alpha, 0, 255))
        shadow = self.fonts[1].render(self.fb_text, True, BLACK)
        shadow.set_alpha(alpha // 2)
        self.screen.blit(shadow, (self.fb_pos[0] - surf.get_width() // 2 + 2, y + 2))
        self.screen.blit(surf, surf.get_rect(center=(self.fb_pos[0], y)))

    def _draw_menu(self):
        f_main, f_small, f_tiny = self.fonts
        elapsed = pg.time.get_ticks() / 1000
        for y in range(HEIGHT):
            shade = clamp(10 + int(25 * math.sin(y / 30 + elapsed)), 0, 255)
            pg.draw.line(self.screen, (shade, shade, min(shade + 10, 255)), (0, y), (WIDTH, y))

        title = f_main.render("HIGH SPEED RACER", True, YELLOW)
        tx    = WIDTH // 2 - title.get_width() // 2
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
        for d, r in self._diff_rects.items():
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
        skin     = CAR_SKINS[self.selected_skin]
        px, py   = WIDTH // 2 - 24, 345
        pbg      = pg.Surface((100, 110), pg.SRCALPHA)
        pbg.fill((25, 25, 35, 220))
        pg.draw.rect(pbg, (255, 255, 255, 40), (0, 0, 100, 110), 1, border_radius=8)
        self.screen.blit(pbg, (px - 26, py - 5))
        draw_car(self.screen, px, py, 48, 88, skin.color, CYAN, skin.type, player=True)

        mouse = pg.mouse.get_pos()
        for rect, direction in [(self._arrow_left_rect, "left"), (self._arrow_right_rect, "right")]:
            col = GREEN if rect.collidepoint(mouse) else (70, 70, 75)
            if rect.collidepoint(mouse):
                pg.draw.rect(self.screen, (0, 200, 0, 80), rect.inflate(10, 10), border_radius=8)
            pg.draw.rect(self.screen, col, rect, border_radius=6)
            pg.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
            draw_arrow(self.screen, rect.centerx, rect.centery, 18, WHITE, direction)

        bonus_val  = skin.speed_bonus
        bonus_text = f_tiny.render(
            f"{skin.name} - {'+' if bonus_val > 1 else ''}{int((bonus_val - 1) * 100)}% SPEED",
            True, GREEN if bonus_val >= 1 else ORANGE,
        )
        self.screen.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, 445))
        hs_text = f"HIGH SCORE: {self._high_score}"
        self.screen.blit(f_tiny.render(hs_text, True, YELLOW), (WIDTH // 2 - f_tiny.size(hs_text)[0] // 2, 465))
        self.btn_play.draw(self.screen, f_small)

        hint    = f_tiny.render("   Move  |  SPACE to boost  |  P - Pause  |  R - Restart", True, GRAY)
        text_x  = WIDTH // 2 - hint.get_width() // 2
        MARGIN  = 20
        al_x    = text_x - 22
        ar_x    = text_x - 4
        if al_x < MARGIN:
            shift  = MARGIN - al_x
            al_x  += shift
            ar_x  += shift
            text_x += shift
        self.screen.blit(hint, (text_x, 555))
        draw_arrow(self.screen, al_x, 560, 14, GRAY, "left")
        draw_arrow(self.screen, ar_x, 560, 14, GRAY, "right")

    def _draw_overlay(self, title_text, title_color, box_h, box_border_color):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))
        bx, by  = WIDTH // 2 - 200, HEIGHT // 2 - box_h // 2
        box     = pg.Surface((400, box_h), pg.SRCALPHA)
        box.fill((20, 20, 30, 250))
        pg.draw.rect(box, box_border_color, (0, 0, 400, box_h), 3, border_radius=15)
        self.screen.blit(box, (bx, by))
        t = self.fonts[0].render(title_text, True, title_color)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 18))
        return by

    def _draw_overlay_stats(self, by):
        f_small = self.fonts[1]
        cx      = WIDTH // 2
        for text, color, dy in [
            (f"SCORE: {self.score}", WHITE, 62),
            (f"LEVEL: {self.level}", CYAN,  90),
        ]:
            t = f_small.render(text, True, color)
            self.screen.blit(t, (cx - t.get_width() // 2, by + dy))

    def _draw_pause(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        by = self._draw_overlay("PAUSED", YELLOW, 260, (255, 255, 255, 60))
        self._draw_overlay_stats(by)
        cx = WIDTH // 2
        for text, dy in [("P / ESC to resume", 125), ("R to restart", 143)]:
            t = f_tiny.render(text, True, GRAY)
            self.screen.blit(t, (cx - t.get_width() // 2, by + dy))
        self._layout_overlay_buttons(by)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)

    def _draw_gameover(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        by = self._draw_overlay("GAME OVER", RED, 340, (200, 30, 30, 100))
        self._draw_overlay_stats(by)
        cx = WIDTH // 2
        if self.score >= self._high_score:
            hs_surf = f_small.render("NEW HIGH SCORE!", True, YELLOW)
        else:
            hs_surf = f_tiny.render(f"BEST: {self._high_score}", True, GRAY)
        self.screen.blit(hs_surf, (cx - hs_surf.get_width() // 2, by + 118))
        self._layout_overlay_buttons(by, include_quit=True)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)
        self.btn_quit.draw(self.screen, f_small)
        hint = f_tiny.render("R restart  |  ESC menu", True, GRAY)
        self.screen.blit(hint, (cx - hint.get_width() // 2, by + 308))


if __name__ == "__main__":
    Game().run()
