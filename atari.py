import pygame as pg
import sys
import random
import os
import math

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 45)
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

CAR_SKINS = [
    {"name": "Blue Racer",      "color": BLUE,   "type": "sedan"},
    {"name": "Red Speedster",   "color": RED,    "type": "sedan"},
    {"name": "Green Machine",   "color": GREEN,  "type": "suv"},
    {"name": "Yellow Lightning","color": YELLOW, "type": "sedan"},
    {"name": "Purple Power",    "color": PURPLE, "type": "suv"},
    {"name": "Orange Blaze",    "color": ORANGE, "type": "truck"},
    {"name": "Cyan Cruiser",    "color": CYAN,   "type": "sedan"},
    {"name": "Pink Dream",      "color": PINK,   "type": "suv"},
]

DIFFICULTY = {
    "Easy":   {"base_speed": 220, "obs_interval": 2.2, "speed_inc": 4,  "obs_speed": (180, 250)},
    "Medium": {"base_speed": 280, "obs_interval": 1.6, "speed_inc": 6,  "obs_speed": (230, 320)},
    "Hard":   {"base_speed": 340, "obs_interval": 1.1, "speed_inc": 8,  "obs_speed": (280, 400)},
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
        pg.draw.line(surface, (0, 0, 0, 80), (x + 6, y + 23), (x + w - 6, y + 23), 1)
    elif car_type == "truck":
        pg.draw.rect(surface, window_color, (x + 8, y + 8, w - 16, 18), border_radius=3)
        pg.draw.rect(surface, shadow_col, (x + 4, y + 35, w - 8, h - 42), border_radius=2)
        pg.draw.line(surface, highlight, (x + 4, y + 34), (x + w - 4, y + 34), 1)
    else:
        pg.draw.rect(surface, window_color, (x + 6, y + 10, w - 12, 30), border_radius=3)
        pg.draw.line(surface, (0, 0, 0, 80), (x + w // 2, y + 10), (x + w // 2, y + 40), 1)

    wheel_col = (18, 18, 18)
    rim_col = (90, 90, 95)
    for wx, wy in [(x - 4, y + 8), (x + w - 9, y + 8), (x - 4, y + h - 20), (x + w - 9, y + h - 20)]:
        pg.draw.rect(surface, wheel_col, (wx, wy, 13, 13), border_radius=3)
        pg.draw.rect(surface, rim_col, (wx + 3, wy + 3, 7, 7), border_radius=2)

    if player:
        for lx in [x + 4, x + w - 12]:
            pg.draw.ellipse(surface, (255, 255, 180), (lx, y - 5, 8, 6))
        pg.draw.rect(surface, RED, (x + 4, y + h - 4, w - 8, 4), border_radius=2)


class Cone:
    WIDTH = 18
    HEIGHT = 26

    def __init__(self, x, speed):
        self.x = x
        self.y = -self.HEIGHT
        self.speed = speed

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

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


class Barrier:
    WIDTH = 60
    HEIGHT = 20

    def __init__(self, x, speed):
        self.x = x
        self.y = -self.HEIGHT
        self.speed = speed

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        pg.draw.rect(surface, (220, 220, 220), (self.x, self.y, self.WIDTH, self.HEIGHT), border_radius=3)
        for i in range(3):
            stripe_x = self.x + i * 20
            pg.draw.rect(surface, ORANGE, (stripe_x + 2, self.y + 2, 14, self.HEIGHT - 4), border_radius=2)

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)


class Pothole:
    RADIUS = 14

    def __init__(self, x, speed):
        self.x = x
        self.y = -self.RADIUS * 2
        self.speed = speed

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

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


class Coin:
    RADIUS = 11

    def __init__(self, x, speed):
        self.x = x
        self.y = -self.RADIUS * 2
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


class ObstacleCar:
    def __init__(self, lane, speed):
        self.width = 48
        self.height = random.choice([82, 88, 94])
        self.x = float(LANE_CENTERS[lane] - self.width // 2)
        self.y = float(-self.height - 10)
        self.speed = speed
        self.color = random.choice(OBSTACLE_COLORS)
        self.car_type = random.choice(["sedan", "suv", "truck"])
        self.lane = lane

    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT

    def draw(self, surface):
        draw_car(surface, int(self.x), int(self.y), self.width, self.height,
                 self.color, WHITE, self.car_type)

    def get_rect(self):
        return pg.Rect(int(self.x) + 4, int(self.y) + 4, self.width - 8, self.height - 8)


class Road:
    STRIPE_W = 8
    STRIPE_H = 50
    STRIPE_GAP = 80
    LANE_DIVIDERS = [LANE_CENTERS[1] - 6, LANE_CENTERS[2] - 6, LANE_CENTERS[3] - 6]

    def __init__(self, scroll_speed):
        self.scroll = 0.0
        self.scroll_speed = scroll_speed
        total = self.STRIPE_H + self.STRIPE_GAP
        self.offsets = [i * total for i in range((HEIGHT // total) + 2)]

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

        for rx in range(ROAD_LEFT, ROAD_RIGHT, 6):
            shade = random.randint(-3, 3)
            c = clamp(ROAD_COLOR[0] + shade, 0, 255)
            pg.draw.line(surface, (c, c, c + 2), (rx, 0), (rx, HEIGHT))

        period = self.STRIPE_H + self.STRIPE_GAP
        num = (HEIGHT // period) + 2
        for i in range(num):
            y = int(i * period - self.scroll % period)
            for lx in self.LANE_DIVIDERS:
                pg.draw.rect(surface, (90, 90, 95), (lx, y, self.STRIPE_W, self.STRIPE_H))

        pg.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
        pg.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)

        for gx in range(0, ROAD_LEFT - 18, 22):
            for gy in range(0, HEIGHT, 18):
                c = clamp(GRASS_COLOR[1] + random.randint(-6, 6), 0, 255)
                pg.draw.line(surface, (30, c, 25), (gx, gy), (gx + 10, gy + 8), 1)
        for gx in range(ROAD_RIGHT + 18, WIDTH, 22):
            for gy in range(0, HEIGHT, 18):
                c = clamp(GRASS_COLOR[1] + random.randint(-6, 6), 0, 255)
                pg.draw.line(surface, (30, c, 25), (gx, gy), (gx + 10, gy + 8), 1)


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

    def get_rect(self):
        margin = 6
        return pg.Rect(int(self.x) + margin, int(self.y) + margin,
                       self.WIDTH - margin * 2, self.HEIGHT - margin * 2)


class HUD:
    def __init__(self, fonts):
        self.font, self.small, self.tiny = fonts
        self._surf = pg.Surface((200, 120), pg.SRCALPHA)

    def draw(self, surface, score, level, speed_pct, difficulty, multiplier):
        self._surf.fill((0, 0, 0, 0))
        self._surf.fill((10, 10, 18, 170), special_flags=0)
        pg.draw.rect(self._surf, (255, 255, 255, 30), (0, 0, 200, 120), 2, border_radius=8)

        pulse = int(4 * abs(math.sin(pg.time.get_ticks() / 400)))
        sc = (255, 255, 90 + pulse)
        self._blit(self._surf, self.small, f"Score  {score}", sc, 14, 10)
        self._blit(self._surf, self.small, f"Level  {level}", CYAN, 14, 36)
        self._blit(self._surf, self.small, f"Speed  {speed_pct}%", GREEN, 14, 60)
        self._blit(self._surf, self.tiny, f"Mode: {difficulty}", YELLOW, 14, 86)
        if multiplier > 1.0:
            mc = YELLOW if multiplier >= 2.0 else (150, 220, 150)
            self._blit(self._surf, self.tiny, f"x{multiplier:.1f} combo!", mc, 14, 102)
        surface.blit(self._surf, (10, 10))

    def _blit(self, surf, font, text, color, x, y):
        surf.blit(font.render(text, True, color), (x, y))


class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.base_color = color or (45, 165, 75)
        self.hover_color = tuple(clamp(c + 35, 0, 255) for c in self.base_color)

    def draw(self, surface, font):
        mouse = pg.mouse.get_pos()
        col = self.hover_color if self.rect.collidepoint(mouse) else self.base_color
        shadow = pg.Rect(self.rect.x + 3, self.rect.y + 4, self.rect.w, self.rect.h)
        pg.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=8)
        pg.draw.rect(surface, col, self.rect, border_radius=8)
        pg.draw.rect(surface, (255, 255, 255, 60), self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    COIN_INTERVAL = 1.8
    MULTIPLIER_DECAY = 3.5

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
        self._init_ui()
        self._reset_state()

    def _init_ui(self):
        f_main, f_small, _ = self.fonts
        self.hud = HUD(self.fonts)
        self.btn_play = Button(WIDTH // 2 - 100, 0, 200, 52, "START RACE")
        self.btn_pause = Button(WIDTH - 115, 10, 100, 36, "PAUSE", (60, 60, 80))
        self.btn_sound = Button(WIDTH - 115, 52, 100, 32, "SFX: ON", (60, 60, 80))
        self.btn_restart = Button(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 46, "RESTART")
        self.btn_menu = Button(WIDTH // 2 - 90, HEIGHT // 2 + 96, 180, 46, "MAIN MENU",
                               (60, 80, 160))
        self.btn_quit = Button(WIDTH // 2 - 90, HEIGHT // 2 + 152, 180, 46, "QUIT",
                               (160, 50, 50))

    def _reset_state(self):
        diff = DIFFICULTY[self.selected_diff]
        skin = CAR_SKINS[self.selected_skin]
        self.player = Player(skin["color"], skin["type"])
        self.road = Road(diff["base_speed"])
        self.obs_cars = []
        self.obs_misc = []
        self.coins = []
        self.score = 0
        self.level = 1
        self.speed_pct = 100
        self.scroll_speed = diff["base_speed"]
        self.obs_timer = 0.0
        self.obs_interval = diff["obs_interval"]
        self.coin_timer = 0.0
        self.combo = 0
        self.multiplier = 1.0
        self.combo_timer = 0.0
        self.fb_text = ""
        self.fb_pos = (WIDTH // 2, HEIGHT // 2)
        self.fb_timer = 0.0

    def _get_high_score(self):
        try:
            with open("highscore.txt") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_high_score(self):
        hs = max(self.score, self._get_high_score())
        with open("highscore.txt", "w") as f:
            f.write(str(hs))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        f_main, f_small, f_tiny = self.fonts
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
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                elif self.state == "gameover":
                    if self.btn_restart.clicked(pos):
                        self._reset_state()
                        self.state = "playing"
                        self.music.play()
                    if self.btn_menu.clicked(pos):
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                    if self.btn_quit.clicked(pos):
                        self._save_high_score()
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
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                        self.music.play()
                if ev.key == pg.K_r and self.state in ("gameover", "paused"):
                    self._reset_state()
                    self.state = "playing"
                    self.music.play()

    def _handle_menu_click(self, pos):
        for i, diff in enumerate(["Easy", "Medium", "Hard"]):
            r = pg.Rect(WIDTH // 2 - 90, 138 + i * 46, 180, 36)
            if r.collidepoint(pos):
                self.selected_diff = diff

        left = pg.Rect(WIDTH // 2 - 145, 345, 40, 40)
        right = pg.Rect(WIDTH // 2 + 105, 345, 40, 40)
        if left.collidepoint(pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
        if right.collidepoint(pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)

        self.btn_play.rect.y = 470
        if self.btn_play.clicked(pos):
            self._reset_state()
            self.state = "playing"
            self.music.play()

    def _update(self, dt):
        self.music.update()
        if self.state != "playing":
            return

        keys = pg.key.get_pressed()
        self.player.update(dt, keys)
        self.road.scroll_speed = self.scroll_speed
        self.road.update(dt)

        diff = DIFFICULTY[self.selected_diff]

        self.obs_timer += dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0.0
            self._spawn_obstacle(diff)

        self.coin_timer += dt
        if self.coin_timer >= self.COIN_INTERVAL:
            self.coin_timer = 0.0
            lane = random.randint(0, 3)
            spd = self.scroll_speed * 0.9
            self.coins.append(Coin(LANE_CENTERS[lane], spd))

        player_rect = self.player.get_rect()

        for car in self.obs_cars[:]:
            if car.update(dt):
                self.obs_cars.remove(car)
                self._on_passed()
                continue
            if car.get_rect().colliderect(player_rect):
                self._trigger_gameover()
                return

        for obj in self.obs_misc[:]:
            if obj.update(dt):
                self.obs_misc.remove(obj)
                self._on_passed()
                continue
            if obj.get_rect().colliderect(player_rect):
                self._trigger_gameover()
                return

        for coin in self.coins[:]:
            if coin.update(dt):
                self.coins.remove(coin)
                continue
            if coin.get_rect().colliderect(player_rect):
                self.coins.remove(coin)
                self._on_coin(int(coin.x), int(coin.y))

        self.combo_timer += dt
        if self.combo_timer >= self.MULTIPLIER_DECAY:
            self.combo_timer = 0.0
            if self.combo > 0:
                self.combo = max(0, self.combo - 1)
                self._recalc_multiplier()

        if self.fb_timer > 0:
            self.fb_timer -= dt

        level_threshold = 5 + self.level * 3
        if self.score >= level_threshold * self.level:
            self.level += 1
            self.scroll_speed = min(
                self.scroll_speed + diff["speed_inc"],
                diff["base_speed"] * 2.5
            )
            self.obs_interval = max(0.55, self.obs_interval - 0.05)
            self.speed_pct = int(self.scroll_speed / diff["base_speed"] * 100)

    def _spawn_obstacle(self, diff):
        min_spd, max_spd = diff["obs_speed"]
        spd = random.uniform(min_spd, max_spd)

        occupied = {c.lane for c in self.obs_cars}
        lanes = [l for l in range(4) if l not in occupied]
        if not lanes:
            lanes = list(range(4))
        lane = random.choice(lanes)

        roll = random.random()
        if roll < 0.55:
            self.obs_cars.append(ObstacleCar(lane, spd))
        elif roll < 0.75:
            x = LANE_CENTERS[lane] - Cone.WIDTH // 2
            self.obs_misc.append(Cone(x, spd))
        elif roll < 0.88:
            x = LANE_CENTERS[lane] - Barrier.WIDTH // 2
            self.obs_misc.append(Barrier(x, spd))
        else:
            self.obs_misc.append(Pothole(LANE_CENTERS[lane], spd))

    def _on_passed(self):
        self.combo += 1
        self._recalc_multiplier()
        gain = int(1 * self.multiplier)
        self.score += gain

    def _on_coin(self, x, y):
        self.combo += 1
        self._recalc_multiplier()
        gain = int(5 * self.multiplier)
        self.score += gain
        self.fb_text = f"+{gain}"
        self.fb_pos = (x, y)
        self.fb_timer = 0.9

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

    def _trigger_gameover(self):
        self.state = "gameover"
        self._save_high_score()
        self.music.fadeout(1500)

    def _draw(self):
        self.screen.fill(BLACK)
        if self.state == "menu":
            self._draw_menu()
        else:
            self.road.draw(self.screen)
            for car in self.obs_cars:
                car.draw(self.screen)
            for obj in self.obs_misc:
                obj.draw(self.screen)
            for coin in self.coins:
                coin.draw(self.screen)
            self.player.draw(self.screen)
            self.hud.draw(self.screen, self.score, self.level,
                          self.speed_pct, self.selected_diff, self.multiplier)
            self.btn_pause.draw(self.screen, self.fonts[2])
            self.btn_sound.draw(self.screen, self.fonts[2])
            self._draw_feedback()
            if self.state == "paused":
                self._draw_pause()
            elif self.state == "gameover":
                self._draw_gameover()
        pg.display.flip()

    def _draw_feedback(self):
        if self.fb_timer <= 0 or not self.fb_text:
            return
        alpha = int(255 * (self.fb_timer / 0.9))
        y = self.fb_pos[1] - int((0.9 - self.fb_timer) * 60)
        surf = self.fonts[1].render(self.fb_text, True, YELLOW)
        surf.set_alpha(alpha)
        self.screen.blit(surf, surf.get_rect(center=(self.fb_pos[0], y)))

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
            col = GREEN if sel else (70, 70, 75)
            pg.draw.rect(self.screen, col, r, border_radius=7)
            pg.draw.rect(self.screen, WHITE, r, 1 if not sel else 2, border_radius=7)
            t = f_small.render(d, True, WHITE)
            self.screen.blit(t, t.get_rect(center=r.center))

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

        hs = f_tiny.render(f"High Score: {self._get_high_score()}", True, GRAY)
        self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 445))

        self.btn_play.rect.y = 470
        self.btn_play.draw(self.screen, f_small)

        hint = f_tiny.render("Arrow keys to steer  |  P pause  |  R restart", True, GRAY)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 530))

    def _draw_overlay(self, title_text, title_color, box_h, box_border_color):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))
        bx, by = WIDTH // 2 - 200, HEIGHT // 2 - box_h // 2
        box = pg.Surface((400, box_h), pg.SRCALPHA)
        box.fill((18, 18, 28, 245))
        pg.draw.rect(box, box_border_color, (0, 0, 400, box_h), 3, border_radius=14)
        self.screen.blit(box, (bx, by))
        f_main = self.fonts[0]
        t = f_main.render(title_text, True, title_color)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 18))
        return by

    def _draw_pause(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        by = self._draw_overlay("PAUSED", YELLOW, 260, (255, 255, 255, 40))
        for text, col, dy in [
            (f"Score: {self.score}", WHITE, 62),
            (f"Level:  {self.level}", CYAN, 90),
        ]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        for text, dy in [
            ("P / ESC to resume", 125),
            ("R to restart", 143),
        ]:
            t = f_tiny.render(text, True, GRAY)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        self.btn_restart.rect.topleft = (WIDTH // 2 - 90, by + 168)
        self.btn_menu.rect.topleft = (WIDTH // 2 - 90, by + 220)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)

    def _draw_gameover(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        hs = self._get_high_score()
        by = self._draw_overlay("GAME OVER", RED, 340, (200, 30, 30, 80))
        for text, col, dy in [
            (f"Score: {self.score}", WHITE, 62),
            (f"Level: {self.level}", CYAN, 90),
        ]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + dy))
        if self.score >= hs:
            t = f_small.render("NEW HIGH SCORE!", True, YELLOW)
        else:
            t = f_tiny.render(f"Best: {hs}", True, GRAY)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 118))
        self.btn_restart.rect.topleft = (WIDTH // 2 - 90, by + 148)
        self.btn_menu.rect.topleft = (WIDTH // 2 - 90, by + 200)
        self.btn_quit.rect.topleft = (WIDTH // 2 - 90, by + 252)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)
        self.btn_quit.draw(self.screen, f_small)
        hint = f_tiny.render("R restart  |  ESC menu", True, GRAY)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, by + 308))


if __name__ == "__main__":
    game = Game()
    game.run()
