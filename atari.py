# sleek_street_racer_ultra_full_fixed_plus_nitro.py
# Full game source (based on your original file) with:
# - Screen shaking/jitter fixed (no random jitter or aggressive rotation)
# - Blue neon side-line artifact removed (reflections toned down to neutral)
# - Nitro boost feature added (SPACE to boost, with timer + visual)
# - All other original systems preserved (procedural audio fallback, particles, rain, coins, obstacles, HUD, photo mode, etc.)
# NOTE: This file keeps original structure and logic as much as possible while applying the above fixes.

import pygame as pg
import sys
import random
import os
import math
from pathlib import Path
from collections import deque

# Try to import numpy for procedural sound; fallback if missing
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except Exception:
    NUMPY_AVAILABLE = False
    print("NumPy not found — procedural audio will be limited. Install numpy for full sound effects: pip install numpy")

# -------------------- Initialization --------------------
pg.init()
try:
    pg.mixer.init()
    pg.mixer.set_num_channels(32)
except Exception as e:
    print("Audio init failed:", e)

# -------------------- Settings --------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
BASE_SPEED = 10

# Colors (neon-ish palette)
BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
RED = (230, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 120, 220)
YELLOW = (240, 220, 50)
CYAN = (50, 220, 220)
MAGENTA = (220, 50, 200)
BUTTON_COLOR = (50, 180, 80)
ROAD_COLOR = (30, 30, 36)
SHOULDER_COLOR = (18, 18, 20)
HUD_BG = (0, 0, 0, 150)

# Asset folders
ASSET_DIR = Path("assets")
MUSIC_DIR = ASSET_DIR / "music"
SOUND_DIR = ASSET_DIR / "sounds"
FONT_DIR = ASSET_DIR / "fonts"

for d in (ASSET_DIR, MUSIC_DIR, SOUND_DIR, FONT_DIR):
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {d} (add assets here for music/sounds/fonts)")

# -------------------- Procedural Sound Engine --------------------
if NUMPY_AVAILABLE:
    def make_wave(freq=440.0, duration=0.25, vol=0.5, wave='sine', sr=44100):
        t = np.linspace(0, duration, int(sr * duration), False)
        if wave == 'sine':
            data = np.sin(freq * t * 2 * np.pi)
        elif wave == 'square':
            data = np.sign(np.sin(freq * t * 2 * np.pi))
        elif wave == 'triangle':
            data = 2*np.abs(2*((t*freq)%1)-1)-1
        elif wave == 'saw':
            data = 2*(t*freq % 1)-1
        else:
            data = np.sin(freq * t * 2 * np.pi)
        audio = np.int16(data * vol * 32767)
        return audio

    def make_sound_buffer(freq, duration=0.25, vol=0.5, wave='sine'):
        arr = make_wave(freq, duration, vol, wave)
        try:
            # pygame accepts bytes; provide stereo by repeating mono
            stereo = np.column_stack((arr, arr)).astype(np.int16)
            return pg.mixer.Sound(buffer=stereo.tobytes())
        except Exception:
            return pg.mixer.Sound(buffer=arr.tobytes())

else:
    # Minimal fallback: produce a very short silent or low notification sound using pygame beep if available
    def make_sound_buffer(freq, duration=0.1, vol=0.5, wave='sine'):
        print("NumPy not available: make_sound_buffer will try minimal fallback (may be silent).")
        # Try to create a tiny buffer with array module — but leave as silent Sound object if fails
        try:
            import array
            sr = 44100
            n = int(sr * duration)
            arr = array.array('h', [0] * n)
            return pg.mixer.Sound(buffer=arr.tobytes())
        except Exception:
            return None

# -------------------- Audio helpers (procedural + file support) --------------------
def load_music():
    try:
        music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
        if music_files:
            selected = os.path.join(MUSIC_DIR, random.choice(music_files))
            pg.mixer.music.load(selected)
            pg.mixer.music.set_volume(0.45)
            return selected
        else:
            # fallback: generate procedural loop if numpy available
            if NUMPY_AVAILABLE:
                print("No external music found — starting procedural beat.")
                s = make_procedural_music()
                return "procedural"
            else:
                print("No external music found and NumPy missing — music disabled.")
                return None
    except Exception as e:
        print("Music load error:", e)
        if NUMPY_AVAILABLE:
            return make_procedural_music()
        return None

def make_procedural_music():
    """Create a looping techno-style beat procedurally (numpy required)."""
    if not NUMPY_AVAILABLE:
        return None
    sr = 44100
    length = 1.0  # one-second loop
    t = np.linspace(0, length, int(sr*length), False)
    # base thump (kick-like)
    kick_env = np.exp(-5 * (t))
    kick = 0.6 * np.sin(2*np.pi*60*t) * kick_env
    # simple hi-hat-ish ticks
    hats = 0.12 * (np.sign(np.sin(2*np.pi*800*t)))* (np.sin(2*np.pi*8*t)>0)
    # bass
    bass = 0.25 * np.sin(2*np.pi*110*t) * (np.sin(2*np.pi*2*t)>0)
    beat = kick + hats + bass
    beat = np.clip(beat, -1, 1)
    arr = np.int16(beat * 32767)
    # stereo
    stereo = np.column_stack((arr, arr)).astype(np.int16)
    try:
        snd = pg.mixer.Sound(buffer=stereo.tobytes())
        ch = pg.mixer.Channel(0)
        ch.play(snd, loops=-1)
        ch.set_volume(0.22)
        return snd
    except Exception as e:
        print("Procedural music play failed:", e)
        return None

def load_sound(name, default_volume=0.7):
    """Load real file if exists else create procedural effect."""
    path = SOUND_DIR / name
    if path.exists():
        try:
            s = pg.mixer.Sound(str(path))
            s.set_volume(default_volume)
            return s
        except Exception as e:
            print("Error loading sound", path, e)
            return None
    # procedural fallback
    print(f"Procedural sound substitute for {name}")
    if "coin" in name:
        s = make_sound_buffer(freq=880, duration=0.1, vol=default_volume, wave='square')
    elif "crash" in name:
        s = make_sound_buffer(freq=60, duration=0.4, vol=default_volume, wave='saw')
    elif "level" in name:
        s = make_sound_buffer(freq=440, duration=0.28, vol=default_volume, wave='triangle')
    elif "honk" in name:
        s = make_sound_buffer(freq=300, duration=0.18, vol=default_volume, wave='square')
    else:
        s = make_sound_buffer(freq=220, duration=0.18, vol=default_volume)
    return s

def play_engine_loop():
    """Procedural continuous low-pitched rumble that changes with speed."""
    # If numpy available, create a looping low rumble
    if NUMPY_AVAILABLE:
        try:
            base_freq = 70.0
            sr = 44100
            t = np.linspace(0, 0.25, int(sr*0.25), False)
            wave = np.sin(2*np.pi*base_freq*t) + 0.4*np.sin(2*np.pi*base_freq*2*t)
            arr = np.int16(wave * 32767 * 0.4)
            stereo = np.column_stack((arr, arr)).astype(np.int16)
            snd = pg.mixer.Sound(buffer=stereo.tobytes())
            ch = pg.mixer.Channel(1)
            ch.play(snd, loops=-1)
            ch.set_volume(0.25)
            return ch
        except Exception as e:
            print("Engine loop failed:", e)
            return None
    else:
        print("NumPy not available — engine loop needs numpy for procedural loop.")
        return None

# -------------------- Particle system --------------------
class Particle:
    def __init__(self, x, y, vx, vy, life, size, color, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.fade = fade

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        # gravity-like downwards subtle pull
        self.vy += 0.12

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life)) if self.fade else 255
        col = (self.color[0], self.color[1], self.color[2], alpha)
        s = pg.Surface((self.size*2, self.size*2), pg.SRCALPHA)
        pg.draw.circle(s, col, (self.size, self.size), self.size)
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# -------------------- Visual helpers --------------------
def lerp(a, b, t):
    return a + (b - a) * t

# global-ish visual settings (you can tweak)
RAIN_DENSITY = 0.009    # fraction of screen for raindrops
LIGHTNING_PROB = 0.0009  # per frame chance of a flash
FOG_ALPHA = 28           # fog overlay alpha base

# -------------------- Coin class --------------------
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = YELLOW
        self.speed = 8
        self.spin_angle = 0
        self.collected = False
        self.spark_timer = 0

    def draw(self, screen):
        # spinning coin (draw as concentric circles + rotation shimmer)
        self.spin_angle = (self.spin_angle + 18) % 360
        # coin base
        pg.draw.circle(screen, self.color, (self.x, int(self.y)), self.radius)
        # edge highlight rotated
        highlight = pg.Surface((self.radius*2, self.radius*2), pg.SRCALPHA)
        pg.draw.circle(highlight, (255,255,255,120), (self.radius, self.radius), self.radius, 2)
        try:
            rotated = pg.transform.rotate(highlight, self.spin_angle)
            screen.blit(rotated, (self.x - rotated.get_width()//2, int(self.y) - rotated.get_height()//2))
        except Exception:
            screen.blit(highlight, (self.x - self.radius, int(self.y) - self.radius))
        # small inner ring
        pg.draw.circle(screen, (255,255,200), (self.x, int(self.y)), max(2, self.radius//3))

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT + 50

    def grow(self):
        # grow is visual (we return an animation trigger)
        self.collected = True
        self.spark_timer = 14

    def spark(self, screen):
        # simple spark particles while collected
        if self.spark_timer > 0:
            for _ in range(10):
                rx = self.x + random.randint(-14, 14)
                ry = self.y + random.randint(-14, 14)
                r = random.randint(2, 4)
                pg.draw.circle(screen, (255, 255, random.randint(180, 255)), (rx, int(ry)), r)
            self.spark_timer -= 1

# -------------------- Car class --------------------
class Car:
    def __init__(self, x, y, color, player=False):
        self.width = 50
        self.height = 90 if player else random.choice([80, 85, 90, 95])
        self.x = x
        self.y = y
        self.speed = BASE_SPEED if player else random.randint(6, 10)
        self.color = color
        self.player = player
        self.window_color = CYAN if player else WHITE
        self.type = "player" if player else random.choice(["sedan", "truck", "suv"])
        self.road_boundary_left = 150
        self.road_boundary_right = WIDTH - 200
        # trail deque for motion blur
        self.trail = deque(maxlen=8)

    def draw(self, screen, neon_mode=False, headlight=False):
        # draw motion trail (subtle)
        if len(self.trail) > 1:
            for i, (tx, ty) in enumerate(list(self.trail)):
                alpha = int(60 * (i / len(self.trail)))
                trail_surf = pg.Surface((self.width, max(1, self.height//4)), pg.SRCALPHA)
                pg.draw.rect(trail_surf, (self.color[0], self.color[1], self.color[2], alpha), (0,0,self.width,max(1,self.height//4)), border_radius=6)
                screen.blit(trail_surf, (tx, ty + self.height - 18))
        # body
        rect = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.rect(screen, self.color, rect, border_radius=6)
        # top sheen
        sheen = pg.Rect(self.x + 2, self.y + 2, self.width - 4, 10)
        pg.draw.rect(screen, (min(self.color[0] + 20, 255), min(self.color[1] + 20, 255), min(self.color[2] + 20, 255)), sheen, border_radius=4)
        # windows / style
        if self.type == "sedan":
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25), border_radius=4)
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 40, self.width - 10, 25), border_radius=4)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1, border_radius=4)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 40, self.width - 10, 25), 1, border_radius=4)
        elif self.type == "truck":
            pg.draw.rect(screen, self.window_color, (self.x + 10, self.y - 15, 30, 10))
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 10, self.y - 15, 30, 10), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1)
        else:
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 40))
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 40), 1)

        # wheels
        wheel_color = (20, 20, 20)
        rim_color = (80, 80, 80)
        wheel_positions = [(5, self.height - 15), (self.width - 20, self.height - 15)]
        if not self.player:
            wheel_positions += [(5, 0), (self.width - 20, 0)]
        for wp in wheel_positions:
            pg.draw.ellipse(screen, wheel_color, (self.x + wp[0], self.y + wp[1], 15, 15))
            pg.draw.ellipse(screen, rim_color, (self.x + wp[0] + 3, self.y + wp[1] + 3, 9, 9))

        # neon outline if enabled on player
        if neon_mode and self.player:
            outline = pg.Surface((self.width+14, self.height+14), pg.SRCALPHA)
            # create a glowing rectangle
            for i in range(4):
                alpha = 80 - i*20
                pg.draw.rect(outline, (0, 255, 255, alpha), (4-i,4-i,self.width + i*2, self.height + i*2), border_radius=8)
            screen.blit(outline, (self.x-7, self.y-7))

        # headlights if player and headlight flag
        if self.player and headlight:
            beam = pg.Surface((150, 80), pg.SRCALPHA)
            for i in range(8):
                a = max(0, 120 - i*14)
                pg.draw.polygon(beam, (80, 160, 255, a), [(0, 40), (150 - i*6, 10 + i*5), (150 - i*6, 70 - i*5)])
            screen.blit(beam, (self.x + self.width//2 - 10, self.y + self.height - 30), special_flags=pg.BLEND_RGBA_ADD)

    def move(self, direction=None):
        # store trail record for blur
        self.trail.appendleft((self.x, self.y))
        if self.player:
            if direction == "left":
                self.x = max(self.road_boundary_left, self.x - self.speed)
            if direction == "right":
                self.x = min(self.road_boundary_right, self.x + self.speed)
        else:
            self.y += self.speed
            return self.y > HEIGHT

# -------------------- Road class (upgraded: reflections + rain interact) --------------------
class Road:
    def __init__(self):
        self.road_width = 500
        self.road_x = (WIDTH - self.road_width) // 2
        self.stripes = []
        for i in range(12):
            self.stripes.append({
                'y': i * 120 - 100,
                'width': 60,
                'height': 20,
                'speed': BASE_SPEED + 2
            })
        # Parallax layers (for cyber skyline)
        self.parallax_layers = []
        for i in range(3):
            # wider surface for smooth tiling
            layer = pg.Surface((WIDTH * 2, HEIGHT), pg.SRCALPHA)
            color_shift = 20 + i * 40
            for s in range(30):
                w = random.randint(40, 120) - i*10
                h = random.randint(40 + i*20, 140 + i*30)
                x = s * (w // 2) + random.randint(-40, 40)
                y = HEIGHT - h - (i*12)
                pg.draw.rect(layer, (12 + color_shift, 8 + color_shift, 36 + color_shift), (x, y, w, h))
                # neon windows
                for wy in range(y + 8, y + h - 8, 18):
                    if random.random() < 0.5:
                        pg.draw.rect(layer, (random.randint(40,255), random.randint(40,255), random.randint(120,255), 120),
                                     (x + 6, wy, min(18, w-12), 10))
            self.parallax_layers.append(layer)

    def draw(self, screen, offset_x=0, rain_drops=None, lightning_alpha=0):
        # shoulders
        pg.draw.rect(screen, SHOULDER_COLOR, (0, 0, self.road_x, HEIGHT))
        pg.draw.rect(screen, SHOULDER_COLOR, (self.road_x + self.road_width, 0, WIDTH, HEIGHT))
        # road base
        pg.draw.rect(screen, ROAD_COLOR, (self.road_x, 0, self.road_width, HEIGHT))

        # neon side reflections -- toned down to neutral to remove the blue lines artifact
        # Replaced the blue/teal gradient with a subtle dark gray shimmer to avoid strong blue lines
        grad = pg.Surface((self.road_x, HEIGHT), pg.SRCALPHA)
        t = pg.time.get_ticks() / 900.0
        for i in range(0, self.road_x, 8):
            alpha = int(10 + 8 * math.sin(t + i * 0.04))  # much lower alpha
            pg.draw.line(grad, (40, 40, 40, alpha), (i, 0), (i, HEIGHT))
        screen.blit(grad, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
        screen.blit(pg.transform.flip(grad, True, False), (self.road_x + self.road_width, 0), special_flags=pg.BLEND_RGBA_ADD)

        # subtle wetness reflection when raining (rain_drops is list of (x,y))
        if rain_drops:
            reflect = pg.Surface((self.road_width, HEIGHT), pg.SRCALPHA)
            for rx, ry in rain_drops:
                # reflect only if over road area
                if self.road_x < rx < self.road_x + self.road_width:
                    # small horizontal smear
                    rel_x = rx - self.road_x
                    h = 2 + (random.random() * 3)
                    pg.draw.line(reflect, (180, 220, 255, 20), (rel_x, ry + 8), (rel_x + int(6*math.sin(pg.time.get_ticks()/200 + rx)), ry + 8), int(h))
            screen.blit(reflect, (self.road_x, 0), special_flags=pg.BLEND_RGBA_ADD)

        # texture lines + center stripes
        for i in range(0, HEIGHT, 4):
            brightness = random.randint(-3, 3)
            shade = (ROAD_COLOR[0] + brightness, ROAD_COLOR[1] + brightness, ROAD_COLOR[2] + brightness)
            pg.draw.line(screen, shade, (self.road_x, i), (self.road_x + self.road_width, i), 1)
        for stripe in self.stripes:
            pg.draw.rect(screen, WHITE,
                         (WIDTH // 2 - stripe['width'] // 2, stripe['y'], stripe['width'], stripe['height']))
            if stripe['y'] % 240 < 120:
                reflect = pg.Surface((stripe['width'], stripe['height'] // 3), pg.SRCALPHA)
                reflect.fill((255, 255, 255, 30))
                screen.blit(reflect, (WIDTH // 2 - stripe['width'] // 2, stripe['y']))
        # side lines (kept thin & neutral)
        pg.draw.line(screen, (200,200,200), (self.road_x, 0), (self.road_x + self.road_width, HEIGHT), 1)
        pg.draw.line(screen, (200,200,200), (self.road_x + self.road_width, 0), (self.road_x + self.road_width, HEIGHT), 1)

    def update(self):
        for stripe in self.stripes:
            stripe['y'] += stripe['speed']
            if stripe['y'] > HEIGHT:
                stripe['y'] = -stripe['height']

# -------------------- Button class --------------------
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = (50, 180, 80)
        self.hover_color = (80, 220, 100)
        self.shadow = pg.Surface((width, height), pg.SRCALPHA)
        self.shadow.fill((0, 0, 0, 50))

    def draw(self, screen, font):
        mouse_pos = pg.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos)
        # pulsing effect
        pulse = 40 + int(30 * math.sin(pg.time.get_ticks() / 400))
        base_color = self.hover_color if hovering else self.color
        color = (min(base_color[0] + pulse % 30, 255),
                 min(base_color[1] + pulse % 40, 255),
                 min(base_color[2] + pulse % 20, 255))
        screen.blit(self.shadow, (self.rect.x + 4, self.rect.y + 4))
        pg.draw.rect(screen, color, self.rect, border_radius=10)
        # border
        border_surf = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        pg.draw.rect(border_surf, (255,255,255,60), (0,0,self.rect.width, self.rect.height), 2, border_radius=10)
        screen.blit(border_surf, (self.rect.x, self.rect.y))
        # text with shadow
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# -------------------- Game class --------------------
class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Sleek Street Racer — Ultra Ultra Deluxe (Fixed)")
        self.clock = pg.time.Clock()
        # fonts
        self.font = None
        self.small_font = None
        self.try_load_fonts()
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, BLUE, True)
        self.obstacles = []
        self.road = Road()
        # coins
        self.coins = []
        self.last_coin_time = 0
        self.coin_frequency = 1800
        # game state
        self.score = 0
        self.level = 1
        self.game_over = False
        self.in_menu = True
        self.paused = False
        self.last_obstacle_time = 0
        self.obstacle_frequency = 1100
        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 60, "START RACE")
        self.clock_speed = 1.2
        # neon mode toggle
        self.neon_mode = True
        # screen buffer for shake effect (kept but no jitter)
        self.buffer = pg.Surface((WIDTH, HEIGHT))
        # assets
        self.current_music = load_music()
        if self.current_music and isinstance(self.current_music, str) and self.current_music != "procedural":
            try:
                pg.mixer.music.play(-1)
            except Exception:
                pass
        self.snd_coin = load_sound("coin.wav", 0.8)
        self.snd_crash = load_sound("crash.wav", 0.9)
        self.snd_level = load_sound("levelup.wav", 0.8)
        self.snd_honk = load_sound("honk.wav", 0.7)
        self.engine_channel = play_engine_loop()
        # particle system container
        self.particles = []
        # parallax bg offset
        self.bg_offset = 0
        # for animated menu car
        self.menu_car_x = WIDTH//2 - 25
        self.menu_car_dir = 1
        # HUD animation helpers
        self.displayed_score = 0.0
        # photo mode
        self.photo_mode = False
        # game over letter-by-letter
        self.gameover_text_progress = 0
        # rain init
        self.rain_drops = []
        for _ in range(int(WIDTH * HEIGHT * RAIN_DENSITY / 1000) or 80):
            self.rain_drops.append([random.randint(0, WIDTH), random.randint(-HEIGHT, HEIGHT)])
        # camera tilt (small subtle tilt preserved, but no rotation jitter)
        self.camera_tilt = 0.0

        # ----------------- NEW: Nitro feature -----------------
        self.nitro_active = False
        self.nitro_timer = 0
        self.nitro_duration_frames = int(1.6 * FPS)  # ~1.6 seconds
        self.nitro_cooldown_frames = int(3.0 * FPS)  # 3s cooldown
        self.nitro_cooldown = 0

    def try_load_fonts(self):
        # try custom Orbitron-like font, else default
        orbitron = FONT_DIR / "Orbitron-Regular.ttf"
        if orbitron.exists():
            try:
                self.font = pg.font.Font(str(orbitron), 48)
                self.small_font = pg.font.Font(str(orbitron), 26)
                return
            except Exception as e:
                print("Failed loading orbitron:", e)
        # fallback
        self.font = pg.font.SysFont("dejavusansmono", 48, bold=True)
        self.small_font = pg.font.SysFont("dejavusansmono", 24)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.current_music:
                    try:
                        pg.mixer.music.stop()
                    except Exception:
                        pass
                self.save_high_score()
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.in_menu and self.play_button.is_clicked(event.pos):
                    self.in_menu = False
                if self.in_menu:
                    mx, my = event.pos
                    if self.play_button.rect.collidepoint((mx, my)):
                        self.in_menu = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r and self.game_over:
                    self.reset_game()
                if event.key == pg.K_n:
                    self.neon_mode = not self.neon_mode
                if event.key == pg.K_p:
                    # pause toggle (only while playing)
                    if not self.in_menu:
                        self.paused = not self.paused
                if event.key == pg.K_m:
                    self.photo_mode = not self.photo_mode
                if event.key == pg.K_b:
                    # toggle procedural music on/off by muting channel 0 if used
                    try:
                        ch = pg.mixer.Channel(0)
                        if ch.get_busy():
                            ch.set_volume(0.0)
                        else:
                            ch.set_volume(0.22)
                    except Exception:
                        pass
                if event.key == pg.K_ESCAPE:
                    # quit gracefully
                    self.save_high_score()
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_SPACE:
                    # Nitro activation (space)
                    if not self.nitro_active and self.nitro_cooldown <= 0 and not self.in_menu and not self.paused and not self.game_over:
                        self.nitro_active = True
                        self.nitro_timer = self.nitro_duration_frames
                        # subtle engine bump
                        if self.engine_channel:
                            try:
                                self.engine_channel.set_volume(0.6)
                            except Exception:
                                pass

    def spawn_particle_explosion(self, x, y, count=18, color=(255,180,20)):
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-6, -1)
            life = random.randint(20, 36)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, vx, vy, life, size, color))

    def spawn_tire_smoke(self, x, y, count=6):
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1, 0)
            life = random.randint(18, 28)
            size = random.randint(6, 12)
            self.particles.append(Particle(x, y, vx, vy, life, size, (40,40,40), fade=True))

    def update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0 or p.y > HEIGHT + 50:
                try:
                    self.particles.remove(p)
                except ValueError:
                    pass

    # -------------------- Update method (full upgraded) --------------------
    def update(self):
        # update engine sound volume with speed (keeps old behavior)
        if self.engine_channel:
            try:
                base_vol = min(0.7, 0.08 + (self.clock_speed / 3.0) * 0.6)
                # nitro slightly louder if active
                vol = min(1.0, base_vol + (0.12 if self.nitro_active else 0.0))
                self.engine_channel.set_volume(vol)
            except Exception:
                pass

        # lightning chance (random flash) while in menu/game
        if random.random() < LIGHTNING_PROB:
            # spawn a quick bright flash by storing a short-life particle
            self.spawn_particle_explosion(random.randint(self.road.road_x, self.road.road_x + self.road.road_width), random.randint(40, 150), count=10, color=(255,255,255))
            # flash overlay stored as short-lived particle as well
            self.particles.append(Particle(WIDTH//2, HEIGHT//2, 0, 0, 6, 200, (255,255,255), fade=True))

        # rain generation: animate raindrops list in self for reflection
        for rd in self.rain_drops:
            rd[1] += 12 + int(6 * self.clock_speed)
            if rd[1] > HEIGHT + 20:
                rd[0] = random.randint(0, WIDTH)
                rd[1] = random.randint(-120, -10)

        # when game is over/menu/paused, still animate particles and menu car
        if self.game_over or self.in_menu or self.paused:
            if self.in_menu:
                # animate menu car lateral movement
                self.menu_car_x += self.menu_car_dir * 1.8
                if self.menu_car_x < self.play_button.rect.left - 40 or self.menu_car_x > self.play_button.rect.right + 40:
                    self.menu_car_dir *= -1
            # update particles and return early
            self.update_particles()
            # update nitro cooldown even while menu/paused (optional)
            if self.nitro_cooldown > 0:
                self.nitro_cooldown -= 1
            return

        # Nitro update & cooldown
        if self.nitro_active:
            self.nitro_timer -= 1
            if self.nitro_timer <= 0:
                self.nitro_active = False
                self.nitro_cooldown = self.nitro_cooldown_frames
                # restore engine volume fallback
                if self.engine_channel:
                    try:
                        self.engine_channel.set_volume(0.25)
                    except Exception:
                        pass
        else:
            if self.nitro_cooldown > 0:
                self.nitro_cooldown -= 1

        # read inputs & apply tilt effect
        keys = pg.key.get_pressed()
        turning_left = keys[pg.K_LEFT]
        turning_right = keys[pg.K_RIGHT]

        if turning_left:
            self.player.move("left")
            if random.random() < 0.22:
                self.spawn_tire_smoke(self.player.x + 8, self.player.y + self.player.height - 8, count=3)
            # small camera tilt accumulator (kept subtle)
            self.camera_tilt = lerp(getattr(self, "camera_tilt", 0), -3, 0.18)
        elif turning_right:
            self.player.move("right")
            if random.random() < 0.22:
                self.spawn_tire_smoke(self.player.x + self.player.width - 10, self.player.y + self.player.height - 8, count=3)
            self.camera_tilt = lerp(getattr(self, "camera_tilt", 0), 3, 0.18)
        else:
            self.camera_tilt = lerp(getattr(self, "camera_tilt", 0), 0, 0.12)

        # modify spawn rates & speeds by nitro
        speed_multiplier = 1.0 + (0.65 if self.nitro_active else 0.0)

        current_time = pg.time.get_ticks()
        # obstacles spawn & slight AI drift behavior
        if current_time - self.last_obstacle_time > (self.obstacle_frequency / (self.clock_speed * speed_multiplier)):
            color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
            spawn_x = random.randint(self.player.road_boundary_left, self.player.road_boundary_right)
            new_obstacle = Car(spawn_x, -150, color)
            new_obstacle.speed = random.randint(int(7 + self.clock_speed), int(10 + self.clock_speed))
            # give occasional lateral drift
            new_obstacle.drift = random.choice([-1, 0, 1])
            new_obstacle.drift_timer = random.randint(30, 120)
            self.obstacles.append(new_obstacle)
            self.last_obstacle_time = current_time
            if self.score > 0 and self.score % 3 == 0:
                self.obstacle_frequency = max(550, self.obstacle_frequency - 80)
                self.level += 1
                self.clock_speed = min(3.2, self.clock_speed + 0.18)
                if self.snd_level:
                    try:
                        self.snd_level.play()
                    except Exception:
                        pass

        # move obstacles with simple drift AI
        for obstacle in self.obstacles[:]:
            # drift lateral slightly
            if hasattr(obstacle, "drift") and obstacle.drift != 0:
                if obstacle.drift_timer > 0:
                    obstacle.x += obstacle.drift * 0.6
                    obstacle.drift_timer -= 1
                else:
                    obstacle.drift = -obstacle.drift
                    obstacle.drift_timer = random.randint(20, 140)
            # move obstacle downward; apply nitro speed multiplier slightly
            obstacle.y += int(obstacle.speed * speed_multiplier)
            if obstacle.y > HEIGHT:
                try:
                    self.obstacles.remove(obstacle)
                except ValueError:
                    pass
                self.score += 1
            # collision check stays same
            if (self.player.x < obstacle.x + obstacle.width and
                self.player.x + self.player.width > obstacle.x and
                self.player.y < obstacle.y + obstacle.height and
                self.player.y + self.player.height > obstacle.y):
                self.spawn_particle_explosion(self.player.x + self.player.width//2, self.player.y + self.player.height//2, count=30, color=(255,80,60))
                self.game_over = True
                if self.current_music:
                    try:
                        pg.mixer.music.fadeout(900)
                    except Exception:
                        pass
                if self.snd_crash:
                    try:
                        self.snd_crash.play()
                    except Exception:
                        pass

        # coins spawn & collisions (with extra effects)
        if current_time - self.last_coin_time > max(800, self.coin_frequency / (self.clock_speed * speed_multiplier)):
            new_coin = Coin(random.randint(self.player.road_boundary_left + 20, self.player.road_boundary_right - 20), -50)
            self.coins.append(new_coin)
            self.last_coin_time = current_time

        for coin in self.coins[:]:
            if coin.move():
                try:
                    self.coins.remove(coin)
                except ValueError:
                    pass
            if (self.player.x < coin.x + coin.radius and
                    self.player.x + self.player.width > coin.x - coin.radius and
                    self.player.y < coin.y + coin.radius and
                    self.player.y + self.player.height > coin.y - coin.radius):
                coin.grow()
                if self.snd_coin:
                    try:
                        self.snd_coin.play()
                    except Exception:
                        pass
                self.score += 5
                self.spawn_particle_explosion(coin.x, coin.y, count=12, color=(255,220,80))
                try:
                    self.coins.remove(coin)
                except ValueError:
                    pass

        # update road, parallax offset, and particles
        self.road.update()
        self.bg_offset = (self.bg_offset + 0.8 * self.clock_speed * speed_multiplier) % WIDTH
        self.update_particles()

        # smooth score display
        if self.displayed_score < self.score:
            self.displayed_score += max(0.6, (self.score - self.displayed_score) * 0.14)
        else:
            self.displayed_score = float(self.score)

        # occasional honk from AI cars
        if random.random() < 0.0025:
            if self.snd_honk:
                try:
                    self.snd_honk.play()
                except Exception:
                    pass

    # -------------------- Draw method (full upgraded) --------------------
    def draw(self):
        # draw everything to buffer for possible tilt/shake
        buf = self.buffer
        buf.fill((0,0,0))

        # dynamic background gradient (more vivid)
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(6 + 26 * t)
            g = int(6 + 14 * (1-t))
            b = int(30 + 150 * (1-t))
            pg.draw.line(buf, (r, g, b), (0, y), (WIDTH, y))

        # parallax neon skyline (tile blit)
        for i, layer in enumerate(self.road.parallax_layers):
            offset = int(self.bg_offset * (0.08 + i*0.22))
            w = layer.get_width()
            x = -offset % w
            buf.blit(layer, (x - w, 0), special_flags=pg.BLEND_RGBA_ADD)
            buf.blit(layer, (x, 0), special_flags=pg.BLEND_RGBA_ADD)
            buf.blit(layer, (x + w, 0), special_flags=pg.BLEND_RGBA_ADD)

        # animated billboards
        for i in range(6):
            bx = (pg.time.get_ticks() // (40 + i*10) + i*120) % (WIDTH + 400) - 200
            by = 60 + i * 40
            b_surf = pg.Surface((140, 18), pg.SRCALPHA)
            color = (120 + i*10, 40 + i*20, 180 + i*5, 120)
            pg.draw.rect(b_surf, color, (0,0,140,18), border_radius=6)
            # slight flashing
            if (pg.time.get_ticks() // 300 + i) % 4 == 0:
                pg.draw.rect(b_surf, (255,255,255,30), (8,2,40,12), border_radius=4)
            buf.blit(b_surf, (bx, by), special_flags=pg.BLEND_RGBA_ADD)

        if self.in_menu:
            # menu title and lines
            title = self.font.render("SLEEK STREET RACER", True, (200, 220, 255))
            shadow = self.font.render("SLEEK STREET RACER", True, (30, 30, 60))
            buf.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 104))
            buf.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            wave = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            for i in range(0, HEIGHT, 8):
                alpha = 40 + int(40 * math.sin(pg.time.get_ticks() / 800 + i * 0.06))
                pg.draw.line(wave, (120, 80, 200, alpha), (0, i), (WIDTH, i), 2)
            buf.blit(wave, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
            instructions = [
                "Use LEFT/RIGHT arrows to steer your car",
                "Avoid other vehicles on the road",
                f"Current high score: {self.get_high_score()}",
                "Press 'N' to toggle Neon | 'M' Photo | 'P' Pause | SPACE Nitro"
            ]
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, WHITE)
                buf.blit(text, (WIDTH // 2 - text.get_width() // 2, 180 + i * 36))
            # animated menu car
            menu_car = Car(self.menu_car_x, HEIGHT//2 + 30, (120,200,255), player=False)
            menu_car.draw(buf, neon_mode=True, headlight=True)
            # play button
            self.play_button.draw(buf, self.small_font)
            glow = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            pg.draw.rect(glow, (60, 120, 220, 8), (50, 60, WIDTH-100, HEIGHT-140), border_radius=12)
            buf.blit(glow, (0,0))
        else:
            # compute rain list for road reflections
            rain_points = [(rd[0], rd[1]) for rd in getattr(self, "rain_drops", [])]

            # draw road with reflection overlay support
            self.road.draw(buf, offset_x=0, rain_drops=rain_points)

            # obstacles and shadows
            for car in self.obstacles:
                shadow = pg.Surface((car.width, car.height//3), pg.SRCALPHA)
                shadow.fill((0,0,0,80))
                buf.blit(shadow, (car.x, car.y + car.height - 10))
                car.draw(buf, neon_mode=self.neon_mode, headlight=False)

            # player shadow & glow
            shadow = pg.Surface((self.player.width, self.player.height//2), pg.SRCALPHA)
            shadow.fill((0,0,0,140))
            buf.blit(shadow, (self.player.x, self.player.y + self.player.height - 8))

            # engine flame effect at rear when speed high or nitro active
            if self.clock_speed > 2.0 or self.nitro_active:
                fx = self.player.x + self.player.width//2
                fy = self.player.y + self.player.height
                # spawn a short flame particle cluster
                for _ in range(3 + (3 if self.nitro_active else 0)):
                    self.particles.append(Particle(fx + random.uniform(-6,6), fy + random.uniform(0,6),
                                                   random.uniform(-0.6,0.6), random.uniform(0.6, 1.6),
                                                   random.randint(10, 18), random.randint(3,6), (255,120,40)))

            self.player.draw(buf, neon_mode=self.neon_mode, headlight=True)

            # speed lines
            if self.clock_speed > 1.8 or self.nitro_active:
                for i in range(6 + (4 if self.nitro_active else 0)):
                    sx = random.randint(self.player.x - 40, self.player.x + self.player.width + 40)
                    sy = random.randint(self.player.y - 40, self.player.y + 10)
                    l = pg.Surface((3, 24), pg.SRCALPHA)
                    pg.draw.rect(l, (180,220,255, 80), (0,0,3,24))
                    buf.blit(l, (sx, sy), special_flags=pg.BLEND_RGBA_ADD)

            # draw coins & sparks
            for coin in self.coins:
                coin.draw(buf)

            # draw particles (smoke, sparks)
            for p in list(self.particles):
                p.draw(buf)

            # rain streak overlay (light streaks falling)
            rain_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            for rx, ry in getattr(self, "rain_drops", []):
                # draw only a faint streak for speed
                a = 90 if ry % 10 == 0 else 36
                lx = rx + int(6 * math.sin(pg.time.get_ticks() / 200 + rx))
                ly = ry
                pg.draw.line(rain_surf, (200, 220, 255, 24), (lx, ly), (lx + 2, ly + 10), 1)
            buf.blit(rain_surf, (0,0), special_flags=pg.BLEND_RGBA_ADD)

            # HUD (skip in photo mode)
            if not self.photo_mode:
                hud_bg = pg.Surface((320, 140), pg.SRCALPHA)
                hud_bg.fill(HUD_BG)
                pg.draw.rect(hud_bg, (255,255,255,30), (0, 0, 320, 140), 2, border_radius=8)
                buf.blit(hud_bg, (10, 10))
                score_text = self.small_font.render(f"Score: {int(self.displayed_score)}", True, WHITE)
                lvl_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
                spd_text = self.small_font.render(f"Speed: {int(self.clock_speed * 100)}%", True, WHITE)
                buf.blit(score_text, (20, 18))
                buf.blit(lvl_text, (20, 18 + 34))
                buf.blit(spd_text, (20, 18 + 68))
                # coin icon + count
                coin_icon = pg.Surface((36, 36), pg.SRCALPHA)
                pg.draw.circle(coin_icon, YELLOW, (18, 18), 14)
                pg.draw.circle(coin_icon, (255,255,255), (18,18), 14, 2)
                buf.blit(coin_icon, (20, 100))
                coin_text = self.small_font.render(f"x {self.score//5}", True, WHITE)
                buf.blit(coin_text, (68, 106))
                # speedometer
                speed_x, speed_y = WIDTH - 170, 20
                pg.draw.circle(buf, (0,0,0,160), (speed_x + 60, speed_y + 60), 58)
                pg.draw.circle(buf, (255,255,255,40), (speed_x + 60, speed_y + 60), 58, 2)
                angle = -90 + (self.clock_speed - 0.5) * 80
                # Nitro influence on needle angle
                if self.nitro_active:
                    angle += 22
                length = 42
                nx = int(speed_x + 60 + length * math.cos(math.radians(angle)))
                ny = int(speed_y + 60 + length * math.sin(math.radians(angle)))
                pg.draw.line(buf, CYAN, (speed_x + 60, speed_y + 60), (nx, ny), 5)
                lbl = self.small_font.render("SPD", True, WHITE)
                buf.blit(lbl, (speed_x + 46, speed_y + 114))
                # nitro HUD small bar
                nitro_bar_x, nitro_bar_y = speed_x + 10, speed_y + 150 - 10
                # draw small nitro indicator (present only as text / color not to alter layout)
                nitro_txt = self.small_font.render(f"NITRO: {'ON' if self.nitro_active else 'READY' if self.nitro_cooldown <= 0 else 'CD'}", True, (255,200,20) if self.nitro_active else WHITE)
                # (placed carefully)
                buf.blit(nitro_txt, (speed_x - 10, speed_y + 88))

            # coin spark animations
            for coin in self.coins:
                if coin.collected:
                    coin.spark(buf)

            # cinematic game over overlay
            if self.game_over:
                overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                buf.blit(overlay, (0, 0))
                # show explosion particles (already spawned in update)
                # box and text
                box = pg.Surface((520, 300), pg.SRCALPHA)
                box.fill((6, 6, 10, 240))
                pg.draw.rect(box, (255,255,255,30), (0,0,520,300), 2, border_radius=12)
                buf.blit(box, (WIDTH // 2 - 260, HEIGHT // 2 - 150))
                # gameover text reveal — note we removed shake/jitter but keep letter-by-letter
                self.gameover_text_progress = min(len("GAME OVER"), self.gameover_text_progress + 0.12)
                prog = int(self.gameover_text_progress)
                title = self.font.render("GAME OVER"[:prog], True, RED)
                buf.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
                score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
                buf.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 30))
                restart = self.small_font.render("Press R to restart", True, YELLOW)
                buf.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 30))

        # paused overlay
        if self.paused and not self.in_menu:
            pause_overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 180))
            buf.blit(pause_overlay, (0,0))
            ptext = self.font.render("PAUSED", True, (200,200,255))
            buf.blit(ptext, (WIDTH//2 - ptext.get_width()//2, HEIGHT//2 - ptext.get_height()//2))

        # apply camera tilt (subtle) but DO NOT apply random jitter/shake to avoid the shaking issue.
        tilt = getattr(self, "camera_tilt", 0)
        # We keep tilt but avoid rotation of the whole screen which previously caused jitter issues.
        # Instead we apply a small vertical offset to simulate lean (non-destructive)
        offset_x = 0
        offset_y = int(tilt * 0.8)  # very subtle vertical shift based on tilt
        # For game over do NOT add random offsets — keep stable presentation
        self.screen.fill((0,0,0))
        self.screen.blit(buf, (offset_x, offset_y))

        # Nitro small screen glow when active (non-shaking)
        if self.nitro_active:
            glow = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            glow.fill((255, 120, 40, 20))
            self.screen.blit(glow, (0,0), special_flags=pg.BLEND_RGBA_ADD)

        # FPS counter & small debug
        if not self.photo_mode:
            fps = int(self.clock.get_fps())
            fps_text = self.small_font.render(f"FPS: {fps}", True, WHITE)
            self.screen.blit(fps_text, (WIDTH - fps_text.get_width() - 8, HEIGHT - 28))

        pg.display.flip()

    # -------------------- High score helpers --------------------
    def get_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(max(self.score, self.get_high_score())))
        except Exception as e:
            print("Couldn't save high score:", e)

    # -------------------- Reset --------------------
    def reset_game(self):
        self.save_high_score()
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, BLUE, True)
        self.obstacles = []
        self.coins = []
        self.road = Road()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.last_obstacle_time = pg.time.get_ticks()
        self.obstacle_frequency = 1100
        self.clock_speed = 1.2
        self.gameover_text_progress = 0
        self.particles = []
        if self.current_music and isinstance(self.current_music, str) and self.current_music != "procedural":
            try:
                pg.mixer.music.play(-1)
            except Exception:
                pass
        if self.engine_channel:
            try:
                self.engine_channel.set_volume(0.25)
            except Exception:
                pass
        # reset nitro
        self.nitro_active = False
        self.nitro_timer = 0
        self.nitro_cooldown = 0

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# -------------------- Entrypoint -------------------
if __name__ == "__main__":
    game = Game()
    game.run()
