import pygame as pg
import sys
import random
import math

pg.init()
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
ROAD_LEFT, ROAD_RIGHT = 150, 650
COIN_INTERVAL = 1.8
MULTIPLIER_DECAY = 3.5
MAX_LIVES = 3
INVINCIBILITY_DURATION = 2.2

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
OBSTACLE_COLORS = [(210,55,55),(55,170,55),(210,130,50),(160,55,170),(50,100,200),(180,170,50)]

def clamp(v, lo, hi): return max(lo, min(hi, v))

def draw_heart(surface, cx, cy, size, color):
    r = size // 2
    pg.draw.circle(surface, color, (cx - r // 2, cy), r // 2)
    pg.draw.circle(surface, color, (cx + r // 2, cy), r // 2)
    pg.draw.polygon(surface, color, [(cx - r, cy), (cx + r, cy), (cx, cy + int(r * 1.2))])

def draw_arrow(surface, cx, cy, size, color, direction):
    h = size // 2
    pts = [(cx + h, cy - h), (cx + h, cy + h), (cx - h, cy)] if direction == "left" else \
          [(cx - h, cy - h), (cx - h, cy + h), (cx + h, cy)]
    pg.draw.polygon(surface, color, pts)

def draw_car(surface, x, y, w, h, body_color, window_color, car_type, player=False):
    shadow = pg.Surface((w + 6, h // 3), pg.SRCALPHA)
    pg.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
    surface.blit(shadow, (x - 3, y + h - h // 6))
    r, g, b = body_color
    hi = (clamp(r+40,0,255), clamp(g+40,0,255), clamp(b+40,0,255))
    sh = (clamp(r-40,0,255), clamp(g-40,0,255), clamp(b-40,0,255))
    pg.draw.rect(surface, sh, (x+2, y+4, w-4, h-4), border_radius=5)
    pg.draw.rect(surface, body_color, (x, y, w, h), border_radius=5)
    pg.draw.rect(surface, hi, (x+3, y+3, w-6, 8), border_radius=3)
    if car_type == "sedan":
        pg.draw.rect(surface, window_color, (x+6, y+12, w-12, 20), border_radius=3)
        pg.draw.rect(surface, window_color, (x+6, y+38, w-12, 18), border_radius=3)
        pg.draw.line(surface, (0,0,0), (x+6, y+23), (x+w-6, y+23), 1)
    elif car_type == "truck":
        pg.draw.rect(surface, window_color, (x+8, y+8, w-16, 18), border_radius=3)
        pg.draw.rect(surface, sh, (x+4, y+35, w-8, h-42), border_radius=2)
        pg.draw.line(surface, hi, (x+4, y+34), (x+w-4, y+34), 1)
    else:
        pg.draw.rect(surface, window_color, (x+6, y+10, w-12, 30), border_radius=3)
        pg.draw.line(surface, (0,0,0), (x+w//2, y+10), (x+w//2, y+40), 1)
    wheel_col, rim_col = (18,18,18), (90,90,95)
    for wx, wy in [(x-4,y+8),(x+w-9,y+8),(x-4,y+h-20),(x+w-9,y+h-20)]:
        pg.draw.rect(surface, wheel_col, (wx, wy, 13, 13), border_radius=3)
        pg.draw.rect(surface, rim_col, (wx+3, wy+3, 7, 7), border_radius=2)
    if player:
        for lx in [x+4, x+w-12]:
            pg.draw.ellipse(surface, (255,255,180), (lx, y-5, 8, 6))
        pg.draw.rect(surface, RED, (x+4, y+h-4, w-8, 4), border_radius=2)

class Cone:
    WIDTH, HEIGHT = 18, 26
    def __init__(self, x, speed):
        self.x, self.y, self.speed = x, -self.HEIGHT, speed
    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT
    def draw(self, surface):
        cx = self.x + self.WIDTH // 2
        pg.draw.polygon(surface, ORANGE, [(cx, self.y), (self.x, self.y+self.HEIGHT), (self.x+self.WIDTH, self.y+self.HEIGHT)])
        pg.draw.rect(surface, WHITE, (self.x+2, self.y+self.HEIGHT-6, self.WIDTH-4, 4))
    def get_rect(self): return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

class Barrier:
    WIDTH, HEIGHT = 60, 20
    def __init__(self, x, speed):
        self.x, self.y, self.speed = x, -self.HEIGHT, speed
    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT
    def draw(self, surface):
        pg.draw.rect(surface, (220,220,220), (self.x, self.y, self.WIDTH, self.HEIGHT), border_radius=3)
        for i in range(3):
            pg.draw.rect(surface, ORANGE, (self.x+i*20+2, self.y+2, 14, self.HEIGHT-4), border_radius=2)
    def get_rect(self): return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

class Pothole:
    RADIUS = 14
    def __init__(self, x, speed):
        self.x, self.y, self.speed = x, -self.RADIUS*2, speed
    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT
    def draw(self, surface):
        R = self.RADIUS
        pg.draw.ellipse(surface, (20,18,15), (self.x-R, self.y-R//2, R*2, R))
        pg.draw.ellipse(surface, (50,45,40), (self.x-R+3, self.y-R//2+2, R*2-6, R-4))
    def get_rect(self): return pg.Rect(self.x-self.RADIUS, self.y-self.RADIUS//2, self.RADIUS*2, self.RADIUS)

class OilSlick:
    WIDTH, HEIGHT = 54, 28
    def __init__(self, x, speed):
        self.x, self.y, self.speed, self.angle = x, -self.HEIGHT, speed, 0.0
        self._s0 = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        self._s1 = pg.Surface((self.WIDTH-10, self.HEIGHT-6), pg.SRCALPHA)
    def update(self, dt):
        self.y += self.speed * dt
        self.angle += dt * 1.2
        return self.y > HEIGHT
    def draw(self, surface):
        t = self.angle
        c0 = (clamp(int(60+40*math.sin(t)),0,255), clamp(int(180+40*math.sin(t+2.1)),0,255), clamp(int(60+40*math.sin(t+4.2)),0,255), 190)
        c1 = (clamp(int(180+40*math.sin(t+1.0)),0,255), clamp(int(60+40*math.sin(t+3.1)),0,255), clamp(int(200+40*math.sin(t+5.2)),0,255), 160)
        self._s0.fill((0,0,0,0))
        pg.draw.ellipse(self._s0, c0, self._s0.get_rect())
        surface.blit(self._s0, (self.x, self.y))
        self._s1.fill((0,0,0,0))
        pg.draw.ellipse(self._s1, c1, self._s1.get_rect())
        surface.blit(self._s1, (self.x+5, self.y+3))
    def get_rect(self): return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

class SpeedBump:
    WIDTH, HEIGHT = 70, 12
    def __init__(self, x, speed):
        self.x, self.y, self.speed = x, -self.HEIGHT, speed
    def update(self, dt):
        self.y += self.speed * dt
        return self.y > HEIGHT
    def draw(self, surface):
        pg.draw.rect(surface, (140,120,80), (self.x, self.y, self.WIDTH, self.HEIGHT), border_radius=5)
        sw = 10
        for i in range(self.WIDTH // (sw*2) + 1):
            sx = self.x + i*sw*2
            cw = min(sw, self.x+self.WIDTH-sx)
            if cw > 0:
                pg.draw.rect(surface, (220,200,60), (sx, self.y, cw, self.HEIGHT), border_radius=3)
        pg.draw.rect(surface, (180,160,100), (self.x, self.y, self.WIDTH, 3), border_radius=5)
    def get_rect(self): return pg.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

class Coin:
    RADIUS = 11
    def __init__(self, x, speed):
        self.x, self.y, self.speed, self.angle = x, -self.RADIUS*2, speed, 0.0
    def update(self, dt):
        self.y += self.speed * dt
        self.angle += 3.0 * dt
        return self.y > HEIGHT
    def draw(self, surface):
        w = max(4, int(self.RADIUS * 2 * abs(math.cos(self.angle))))
        h = self.RADIUS * 2
        s = pg.Surface((w, h), pg.SRCALPHA)
        pg.draw.ellipse(s, (200,170,20), (0,0,w,h))
        pg.draw.ellipse(s, (240,210,60), (1,1,w-2,h-2))
        pg.draw.ellipse(s, (255,235,100), (w//4,2,w//2,h//4))
        surface.blit(s, (self.x-w//2, self.y-self.RADIUS))
    def get_rect(self): return pg.Rect(self.x-self.RADIUS, self.y-self.RADIUS, self.RADIUS*2, self.RADIUS*2)

class ObstacleCar:
    def __init__(self, lane, speed):
        self.width, self.height = 48, random.choice([82, 88, 94])
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
        draw_car(surface, int(self.x), int(self.y), self.width, self.height, self.color, WHITE, self.car_type)
    def get_rect(self): return pg.Rect(int(self.x)+4, int(self.y)+4, self.width-8, self.height-8)

class Road:
    STRIPE_W, STRIPE_H, STRIPE_GAP = 8, 50, 80
    LANE_DIVIDERS = [LANE_CENTERS[1]-6, LANE_CENTERS[2]-6, LANE_CENTERS[3]-6]
    RUMBLE_W, RUMBLE_PERIOD = 14, 60

    def __init__(self, scroll_speed):
        self.scroll, self.scroll_speed = 0.0, scroll_speed
        self._grass = self._build_grass()
        self._base = self._build_base()

    def _build_grass(self):
        s = pg.Surface((ROAD_LEFT, HEIGHT))
        s.fill(GRASS_COLOR)
        rng = random.Random(42)
        for _ in range(180):
            gx, gy = rng.randint(0, ROAD_LEFT-4), rng.randint(0, HEIGHT-6)
            shade = rng.randint(-12, 12)
            col = tuple(clamp(GRASS_COLOR[i]+shade, 0, 255) for i in range(3))
            pg.draw.rect(s, col, (gx, gy, rng.randint(2,5), rng.randint(3,7)))
        return s

    def _build_base(self):
        s = pg.Surface((WIDTH, HEIGHT))
        s.blit(self._grass, (0, 0))
        s.blit(pg.transform.flip(self._grass, True, False), (ROAD_RIGHT, 0))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_LEFT-18, 0, 18, HEIGHT))
        pg.draw.rect(s, SHOULDER_COLOR, (ROAD_RIGHT, 0, 18, HEIGHT))
        pg.draw.rect(s, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT-ROAD_LEFT, HEIGHT))
        pg.draw.line(s, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
        pg.draw.line(s, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)
        return s

    def update(self, dt):
        self.scroll += self.scroll_speed * dt
        period = self.STRIPE_H + self.STRIPE_GAP
        if self.scroll >= period:
            self.scroll -= period

    def draw(self, surface):
        surface.blit(self._base, (0, 0))
        period, offset = self.RUMBLE_PERIOD, self.scroll % self.RUMBLE_PERIOD
        for i in range(HEIGHT // period + 2):
            ry = int(i * period - offset)
            col = RED if i % 2 == 0 else WHITE
            pg.draw.rect(surface, col, (ROAD_LEFT-self.RUMBLE_W-18, ry, self.RUMBLE_W, period//2))
            pg.draw.rect(surface, col, (ROAD_RIGHT+18, ry, self.RUMBLE_W, period//2))
        sp = self.STRIPE_H + self.STRIPE_GAP
        so = self.scroll % sp
        for i in range(HEIGHT // sp + 2):
            y = int(i * sp - so)
            if y > HEIGHT or y + self.STRIPE_H < 0:
                continue
            for lx in self.LANE_DIVIDERS:
                pg.draw.rect(surface, (90,90,95), (lx, y, self.STRIPE_W, self.STRIPE_H))

class Player:
    WIDTH, HEIGHT, SPEED = 48, 88, 320

    def __init__(self, color, car_type):
        self.x = float(WIDTH // 2 - self.WIDTH // 2)
        self.y = float(HEIGHT - self.HEIGHT - 30)
        self.color, self.car_type = color, car_type
        self.vel_x = self.tilt = self.slide_vel = self.slide_timer = self.slowdown_timer = 0.0

    def apply_oil(self):
        self.slide_vel = random.choice([-1, 1]) * self.SPEED * 0.9
        self.slide_timer = 1.4

    def apply_speedbump(self):
        self.slowdown_timer = 1.8

    def update(self, dt, keys):
        if self.slide_timer > 0:
            self.slide_timer -= dt
            self.x += self.slide_vel * dt
            self.slide_vel *= (1 - dt * 2.5)
        else:
            if keys[pg.K_LEFT]:
                self.vel_x = max(self.vel_x - 900*dt, -self.SPEED)
            elif keys[pg.K_RIGHT]:
                self.vel_x = min(self.vel_x + 900*dt, self.SPEED)
            else:
                self.vel_x = clamp(
                    self.vel_x - math.copysign(min(600*dt, abs(self.vel_x)), self.vel_x),
                    -self.SPEED, self.SPEED
                ) if self.vel_x else 0.0
            self.x += self.vel_x * dt
        if self.slowdown_timer > 0:
            self.slowdown_timer -= dt
        self.x = clamp(self.x, ROAD_LEFT+2, ROAD_RIGHT-self.WIDTH-2)
        self.tilt += ((self.vel_x + self.slide_vel) / self.SPEED * 6 - self.tilt) * 8 * dt

    def get_speed_factor(self): return 0.45 if self.slowdown_timer > 0 else 1.0

    def draw(self, surface, invincible, ticks):
        if invincible and (ticks // 80) % 2 == 0:
            return
        if abs(self.tilt) > 0.3:
            tmp = pg.Surface((self.WIDTH+12, self.HEIGHT+12), pg.SRCALPHA)
            draw_car(tmp, 6, 6, self.WIDTH, self.HEIGHT, self.color, CYAN, self.car_type, player=True)
            rot = pg.transform.rotate(tmp, -self.tilt)
            surface.blit(rot, rot.get_rect(center=(int(self.x+self.WIDTH//2), int(self.y+self.HEIGHT//2))))
        else:
            draw_car(surface, int(self.x), int(self.y), self.WIDTH, self.HEIGHT, self.color, CYAN, self.car_type, player=True)

    def get_rect(self):
        m = 6
        return pg.Rect(int(self.x)+m, int(self.y)+m, self.WIDTH-m*2, self.HEIGHT-m*2)

class HUD:
    def __init__(self, fonts):
        self.small, self.tiny = fonts[1], fonts[2]
        self.surf = pg.Surface((210, 140), pg.SRCALPHA)

    def draw(self, surface, score, level, speed_pct, difficulty, multiplier, lives):
        self.surf.fill((10,10,18,170))
        pg.draw.rect(self.surf, (255,255,255,30), (0,0,210,140), 2, border_radius=8)
        pulse = int(4 * abs(math.sin(pg.time.get_ticks() / 400)))
        self._blit(f"Score  {score}", (255, 255, 90+pulse), 14, 10)
        self._blit(f"Level  {level}", CYAN, 14, 36)
        self._blit(f"Speed  {speed_pct}%", GREEN, 14, 60)
        self._blit(f"Mode: {difficulty}", YELLOW, 14, 86, tiny=True)
        for i in range(MAX_LIVES):
            draw_heart(self.surf, 22 + i*20, 106, 14, RED if i < lives else GRAY)
        if multiplier > 1.0:
            self._blit(f"x{multiplier:.1f} combo!", YELLOW if multiplier >= 2.0 else (150,220,150), 14, 118, tiny=True)
        surface.blit(self.surf, (10, 10))

    def _blit(self, text, color, x, y, tiny=False):
        self.surf.blit((self.tiny if tiny else self.small).render(text, True, color), (x, y))

class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.base_color = color or (45, 165, 75)
        self.hover_color = tuple(clamp(c+35, 0, 255) for c in self.base_color)

    def draw(self, surface, font):
        col = self.hover_color if self.rect.collidepoint(pg.mouse.get_pos()) else self.base_color
        pg.draw.rect(surface, (0,0,0), (self.rect.x+3, self.rect.y+4, self.rect.w, self.rect.h), border_radius=8)
        pg.draw.rect(surface, col, self.rect, border_radius=8)
        pg.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        surface.blit(t := font.render(self.text, True, WHITE), t.get_rect(center=self.rect.center))

    def clicked(self, pos): return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Sleek Street Racer")
        self.clock = pg.time.Clock()
        self.fonts = (pg.font.Font(None, 44), pg.font.Font(None, 30), pg.font.Font(None, 22))
        self.selected_skin, self.selected_diff, self.state = 0, "Medium", "menu"
        self.hud = HUD(self.fonts)
        self.btn_play    = Button(WIDTH//2-100, 0, 200, 52, "START RACE")
        self.btn_pause   = Button(WIDTH-115, 10, 100, 36, "PAUSE", (60,60,80))
        self.btn_restart = Button(WIDTH//2-90, HEIGHT//2+40, 180, 46, "RESTART")
        self.btn_menu    = Button(WIDTH//2-90, HEIGHT//2+96, 180, 46, "MAIN MENU", (60,80,160))
        self.btn_quit    = Button(WIDTH//2-90, HEIGHT//2+152, 180, 46, "QUIT", (160,50,50))
        self._blur_surf  = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self._reset_state()

    def _reset_state(self):
        diff = DIFFICULTY[self.selected_diff]
        skin = CAR_SKINS[self.selected_skin]
        self.player       = Player(skin["color"], skin["type"])
        self.road         = Road(diff["base_speed"])
        self.obs_cars     = []
        self.obs_misc     = []
        self.coins        = []
        self.score        = 0
        self.level        = 1
        self.speed_pct    = 100
        self.scroll_speed = diff["base_speed"]
        self.obs_timer    = 0.0
        self.obs_interval = diff["obs_interval"]
        self.coin_timer   = 0.0
        self.combo        = 0
        self.multiplier   = 1.0
        self.combo_timer  = 0.0
        self.fb_text      = ""
        self.fb_pos       = (WIDTH//2, HEIGHT//2)
        self.fb_timer     = 0.0
        self.lives               = MAX_LIVES
        self.invincibility_timer = 0.0
        self.level_flash_timer   = 0.0
        self.speed_blur_alpha    = 0

    def _get_high_score(self):
        try:
            with open("highscore.txt") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self._get_high_score())))

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
                    if self.btn_pause.clicked(pos):
                        self.state = "paused"
                elif self.state == "paused":
                    if self.btn_pause.clicked(pos):
                        self.state = "playing"
                    if self.btn_restart.clicked(pos):
                        self._reset_state()
                        self.state = "playing"
                    if self.btn_menu.clicked(pos):
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                elif self.state == "gameover":
                    if self.btn_restart.clicked(pos):
                        self._reset_state()
                        self.state = "playing"
                    if self.btn_menu.clicked(pos):
                        self._save_high_score()
                        self._reset_state()
                        self.state = "menu"
                    if self.btn_quit.clicked(pos):
                        self._save_high_score()
                        pg.quit()
                        sys.exit()
            if ev.type == pg.KEYDOWN:
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
            if pg.Rect(WIDTH//2-90, 138+i*46, 180, 36).collidepoint(pos):
                self.selected_diff = d
        if pg.Rect(WIDTH//2-145, 345, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
        if pg.Rect(WIDTH//2+105, 345, 40, 40).collidepoint(pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
        self.btn_play.rect.y = 470
        if self.btn_play.clicked(pos):
            self._reset_state()
            self.state = "playing"

    def _update(self, dt):
        if self.state != "playing":
            return
        self.invincibility_timer = max(0.0, self.invincibility_timer - dt)
        self.level_flash_timer   = max(0.0, self.level_flash_timer - dt)
        self.player.update(dt, pg.key.get_pressed())
        self.road.scroll_speed = self.scroll_speed * self.player.get_speed_factor()
        self.road.update(dt)
        self.speed_blur_alpha += (clamp((self.scroll_speed-300)/400*120, 0, 110) - self.speed_blur_alpha) * dt * 4
        diff = DIFFICULTY[self.selected_diff]
        self.obs_timer += dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0.0
            self._spawn_obstacle(diff)
        self.coin_timer += dt
        if self.coin_timer >= COIN_INTERVAL:
            self.coin_timer = 0.0
            self.coins.append(Coin(LANE_CENTERS[random.randint(0,3)], self.scroll_speed * 0.9))
        invincible  = self.invincibility_timer > 0
        player_rect = self.player.get_rect()
        for car in self.obs_cars[:]:
            if car.update(dt):
                self.obs_cars.remove(car)
                self._on_car_passed()
                continue
            if not invincible and car.get_rect().colliderect(player_rect):
                self._on_hit()
                return
        for obj in self.obs_misc[:]:
            if obj.update(dt):
                self.obs_misc.remove(obj)
                self._on_misc_passed()
                continue
            if obj.get_rect().colliderect(player_rect):
                if isinstance(obj, OilSlick):
                    self.obs_misc.remove(obj)
                    self.player.apply_oil()
                    self._set_fb("SLIPPING!", 1.0)
                elif isinstance(obj, SpeedBump):
                    self.obs_misc.remove(obj)
                    self.player.apply_speedbump()
                    self._set_fb("SLOW!", 1.0)
                elif not invincible:
                    self._on_hit()
                    return
        for coin in self.coins[:]:
            if coin.update(dt):
                self.coins.remove(coin)
                continue
            if coin.get_rect().colliderect(player_rect):
                self.coins.remove(coin)
                self._on_coin(int(coin.x), int(coin.y))
        self.combo_timer += dt
        if self.combo_timer >= MULTIPLIER_DECAY:
            self.combo_timer = 0.0
            if self.combo > 0:
                self.combo = max(0, self.combo-1)
                self._recalc_multiplier()
        if self.fb_timer > 0:
            self.fb_timer -= dt
        if self.score >= (5 + self.level*3) * self.level:
            self.level += 1
            self.scroll_speed  = min(self.scroll_speed + diff["speed_inc"], diff["base_speed"] * 2.5)
            self.obs_interval  = max(0.55, self.obs_interval - 0.05)
            self.speed_pct     = int(self.scroll_speed / diff["base_speed"] * 100)
            self.level_flash_timer = 1.2

    def _set_fb(self, text, duration):
        self.fb_text  = text
        self.fb_pos   = (int(self.player.x + Player.WIDTH//2), int(self.player.y))
        self.fb_timer = duration

    def _spawn_obstacle(self, diff):
        spd  = random.uniform(*diff["obs_speed"])
        occ  = {c.lane for c in self.obs_cars}
        lane = random.choice([i for i in range(4) if i not in occ] or list(range(4)))
        lc   = LANE_CENTERS[lane]
        roll = random.random()
        if roll < 0.45:
            self.obs_cars.append(ObstacleCar(lane, spd))
        elif roll < 0.60:
            self.obs_misc.append(Cone(lc - Cone.WIDTH//2, spd))
        elif roll < 0.72:
            self.obs_misc.append(Barrier(lc - Barrier.WIDTH//2, spd))
        elif roll < 0.82:
            self.obs_misc.append(Pothole(lc, spd))
        elif roll < 0.91:
            self.obs_misc.append(OilSlick(lc - OilSlick.WIDTH//2, spd*0.7))
        else:
            self.obs_misc.append(SpeedBump(lc - SpeedBump.WIDTH//2, spd*0.8))

    def _on_hit(self):
        self.lives -= 1
        self.combo = 0
        self._recalc_multiplier()
        self._set_fb("-1 LIFE!", 1.1)
        if self.lives <= 0:
            self._trigger_gameover()
        else:
            self.invincibility_timer = INVINCIBILITY_DURATION

    def _on_car_passed(self): self.score += 1

    def _on_misc_passed(self):
        self.combo += 1
        self._recalc_multiplier()
        self.score += int(self.multiplier)

    def _on_coin(self, x, y):
        self.combo += 1
        self._recalc_multiplier()
        gain = int(5 * self.multiplier)
        self.score += gain
        self.fb_text, self.fb_pos, self.fb_timer = f"+{gain}", (x, y), 0.9

    def _recalc_multiplier(self):
        self.multiplier = (
            3.0 if self.combo >= 20 else
            2.5 if self.combo >= 15 else
            2.0 if self.combo >= 10 else
            1.5 if self.combo >= 5 else 1.0
        )

    def _trigger_gameover(self):
        self.state = "gameover"
        self._save_high_score()

    def _draw(self):
        self.screen.fill(BLACK)
        if self.state == "menu":
            self._draw_menu()
        else:
            self.road.draw(self.screen)
            for obj in (*self.obs_cars, *self.obs_misc, *self.coins):
                obj.draw(self.screen)
            self.player.draw(self.screen, self.invincibility_timer > 0, pg.time.get_ticks())
            if self.speed_blur_alpha > 4:
                self._blur_surf.fill((0,0,0,0))
                la = int(self.speed_blur_alpha) // 2
                for i in range(18):
                    lx = ROAD_LEFT + (ROAD_RIGHT-ROAD_LEFT)*i//18
                    pg.draw.line(self._blur_surf, (255,255,255,la), (lx,0), (lx,HEIGHT), 1)
                self.screen.blit(self._blur_surf, (0,0))
            self.hud.draw(self.screen, self.score, self.level, self.speed_pct, self.selected_diff, self.multiplier, self.lives)
            self.btn_pause.draw(self.screen, self.fonts[2])
            self._draw_feedback()
            if self.level_flash_timer > 0:
                self._draw_level_flash()
            if self.state == "paused":
                self._draw_pause()
            elif self.state == "gameover":
                self._draw_gameover()
        pg.display.flip()

    def _draw_level_flash(self):
        alpha = int(clamp(self.level_flash_timer / 1.2 * 220, 0, 220))
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        s.fill((255,255,255, min(alpha//6, 30)))
        self.screen.blit(s, (0,0))
        t = self.fonts[0].render(f"LEVEL {self.level}!", True, YELLOW)
        t.set_alpha(alpha)
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2-40)))

    def _draw_feedback(self):
        if self.fb_timer <= 0 or not self.fb_text:
            return
        alpha = int(255 * (self.fb_timer / 0.9))
        y = self.fb_pos[1] - int((0.9 - self.fb_timer) * 60)
        surf = self.fonts[1].render(self.fb_text, True, YELLOW)
        surf.set_alpha(clamp(alpha, 0, 255))
        self.screen.blit(surf, surf.get_rect(center=(self.fb_pos[0], y)))

    def _draw_menu(self):
        f_main, f_small, f_tiny = self.fonts
        for y in range(HEIGHT):
            shade = 8 + int(18 * y / HEIGHT)
            pg.draw.line(self.screen, (shade, shade, shade+6), (0,y), (WIDTH,y))
        title = f_main.render("SLEEK STREET RACER", True, YELLOW)
        sh    = f_main.render("SLEEK STREET RACER", True, (70,70,0))
        tx = WIDTH//2 - title.get_width()//2
        self.screen.blit(sh, (tx+3, 38))
        self.screen.blit(title, (tx, 35))
        bg = pg.Surface((440, 460), pg.SRCALPHA)
        bg.fill((0,0,0,170))
        pg.draw.rect(bg, (255,255,255,30), (0,0,440,460), 2, border_radius=12)
        self.screen.blit(bg, (WIDTH//2-220, 115))
        lbl = f_small.render("Difficulty", True, WHITE)
        self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 122))
        for i, d in enumerate(["Easy", "Medium", "Hard"]):
            r = pg.Rect(WIDTH//2-90, 138+i*46, 180, 36)
            sel = d == self.selected_diff
            pg.draw.rect(self.screen, GREEN if sel else (70,70,75), r, border_radius=7)
            pg.draw.rect(self.screen, WHITE, r, 1 if not sel else 2, border_radius=7)
            t = f_small.render(d, True, WHITE)
            self.screen.blit(t, t.get_rect(center=r.center))
        lbl2 = f_small.render("Car Skin", True, WHITE)
        self.screen.blit(lbl2, (WIDTH//2 - lbl2.get_width()//2, 296))
        skin = CAR_SKINS[self.selected_skin]
        px, py = WIDTH//2-24, 315
        pbg = pg.Surface((96, 108), pg.SRCALPHA)
        pbg.fill((25,25,35,200))
        pg.draw.rect(pbg, (255,255,255,30), (0,0,96,108), 1, border_radius=6)
        self.screen.blit(pbg, (px-24, py-5))
        draw_car(self.screen, px, py, 48, 88, skin["color"], CYAN, skin["type"], player=True)
        mouse = pg.mouse.get_pos()
        for rect, direction in [
            (pg.Rect(WIDTH//2-145, 345, 40, 40), "left"),
            (pg.Rect(WIDTH//2+105, 345, 40, 40), "right"),
        ]:
            col = GREEN if rect.collidepoint(mouse) else (70,70,75)
            pg.draw.rect(self.screen, col, rect, border_radius=6)
            pg.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
            draw_arrow(self.screen, rect.centerx, rect.centery, 18, WHITE, direction)
        self.screen.blit(f_tiny.render(skin["name"], True, YELLOW),
                         (WIDTH//2 - f_tiny.size(skin["name"])[0]//2, 425))
        hs_text = f"High Score: {self._get_high_score()}"
        self.screen.blit(f_tiny.render(hs_text, True, GRAY),
                         (WIDTH//2 - f_tiny.size(hs_text)[0]//2, 445))
        self.btn_play.rect.y = 470
        self.btn_play.draw(self.screen, f_small)
        hint = f_tiny.render("Use arrow keys to steer  |  P - Pause  |  R - Restart", True, GRAY)
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 530))

    def _draw_overlay(self, title_text, title_color, box_h, box_border_color):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0,0,0,195))
        self.screen.blit(overlay, (0,0))
        bx, by = WIDTH//2-200, HEIGHT//2-box_h//2
        box = pg.Surface((400, box_h), pg.SRCALPHA)
        box.fill((18,18,28,245))
        pg.draw.rect(box, box_border_color, (0,0,400,box_h), 3, border_radius=14)
        self.screen.blit(box, (bx, by))
        t = self.fonts[0].render(title_text, True, title_color)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, by+18))
        return by

    def _draw_pause(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        by = self._draw_overlay("PAUSED", YELLOW, 260, (255,255,255,40))
        for text, col, dy in [(f"Score: {self.score}", WHITE, 62), (f"Level:  {self.level}", CYAN, 90)]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, by+dy))
        for text, dy in [("P / ESC to resume", 125), ("R to restart", 143)]:
            t = f_tiny.render(text, True, GRAY)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, by+dy))
        self.btn_restart.rect.topleft = (WIDTH//2-90, by+168)
        self.btn_menu.rect.topleft    = (WIDTH//2-90, by+220)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)

    def _draw_gameover(self):
        f_small, f_tiny = self.fonts[1], self.fonts[2]
        hs = self._get_high_score()
        by = self._draw_overlay("GAME OVER", RED, 340, (200,30,30,80))
        for text, col, dy in [(f"Score: {self.score}", WHITE, 62), (f"Level: {self.level}", CYAN, 90)]:
            t = f_small.render(text, True, col)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, by+dy))
        t = f_small.render("NEW HIGH SCORE!", True, YELLOW) if self.score >= hs else f_tiny.render(f"Best: {hs}", True, GRAY)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, by+118))
        self.btn_restart.rect.topleft = (WIDTH//2-90, by+148)
        self.btn_menu.rect.topleft    = (WIDTH//2-90, by+200)
        self.btn_quit.rect.topleft    = (WIDTH//2-90, by+252)
        self.btn_restart.draw(self.screen, f_small)
        self.btn_menu.draw(self.screen, f_small)
        self.btn_quit.draw(self.screen, f_small)
        hint = f_tiny.render("R restart  |  ESC menu", True, GRAY)
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, by+308))

if __name__ == "__main__":
    Game().run()
