import pygame as pg
import sys
import random
import os
import math

# Initialize pygame
pg.init()
pg.mixer.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
BASE_SPEED = 10

# Colors
BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
RED = (230, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 120, 220)
YELLOW = (240, 220, 50)
CYAN = (50, 220, 220)
BUTTON_COLOR = (50, 180, 80)
ROAD_COLOR = (40, 40, 45)
SHOULDER_COLOR = (70, 70, 75)
ORANGE = (255, 140, 0)
PURPLE = (180, 60, 180)
PINK = (255, 105, 180)

# Car Skins - Different colors and types
CAR_SKINS = [
    {"name": "Blue Racer", "color": BLUE, "type": "sedan"},
    {"name": "Red Speedster", "color": RED, "type": "sedan"},
    {"name": "Green Machine", "color": GREEN, "type": "suv"},
    {"name": "Yellow Lightning", "color": YELLOW, "type": "sedan"},
    {"name": "Purple Power", "color": PURPLE, "type": "suv"},
    {"name": "Orange Blaze", "color": ORANGE, "type": "truck"},
    {"name": "Cyan Cruiser", "color": CYAN, "type": "sedan"},
    {"name": "Pink Dream", "color": PINK, "type": "suv"},
]

# Difficulty Settings
DIFFICULTY_SETTINGS = {
    "Easy": {"base_speed": 8, "obstacle_freq": 1500, "speed_increase": 0.1, "obstacle_speed": (6, 9)},
    "Medium": {"base_speed": 10, "obstacle_freq": 1200, "speed_increase": 0.15, "obstacle_speed": (8, 12)},
    "Hard": {"base_speed": 12, "obstacle_freq": 900, "speed_increase": 0.2, "obstacle_speed": (10, 15)},
}


# Music setup
def load_music():
    music_folder = "music"  # Folder where music files are stored
    try:
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            print(f"Created '{music_folder}' folder. Please add your music files there.")
            return None
        music_files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
        if not music_files:
            print(f"No music files found in '{music_folder}' folder.")
            return None
        selected_music = os.path.join(music_folder, random.choice(music_files))
        pg.mixer.music.load(selected_music)
        pg.mixer.music.set_volume(0.5)
        return selected_music
    except Exception as e:
        print(f"Error loading music: {e}")
        return None


# ------------------ Coin class ------------------
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (240, 220, 50)
        self.speed = 8

    def draw(self, screen):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pg.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 2)

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

    def grow(self):
        self.radius += 5


# Enhanced car class
class Car:
    def __init__(self, x, y, color, player=False, car_type="sedan"):
        self.width = 50
        self.height = 90 if player else random.choice([80, 85, 90, 95])
        self.x = x
        self.y = y
        self.speed = BASE_SPEED if player else random.randint(6, 10)
        self.color = color
        self.player = player
        self.window_color = CYAN if player else WHITE
        self.type = car_type if player else random.choice(["sedan", "truck", "suv"])
        self.road_boundary_left = 150
        self.road_boundary_right = WIDTH - 200

    def draw(self, screen):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(screen, (min(self.color[0] + 20, 255), min(self.color[1] + 20, 255),
                              min(self.color[2] + 20, 255)), (self.x + 2, self.y + 2, self.width - 4, 10))
        if self.type == "sedan":
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25))
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 40, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 40, self.width - 10, 25), 1)
        elif self.type == "truck":
            pg.draw.rect(screen, self.window_color, (self.x + 10, self.y - 15, 30, 10))
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 10, self.y - 15, 30, 10), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1)
        else:
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 40))
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 40), 1)
        wheel_color = (20, 20, 20)
        rim_color = (80, 80, 80)
        for wheel_pos in [(5, self.height - 15), (self.width - 20, self.height - 15), (5, 0), (self.width - 20, 0)]:
            pg.draw.ellipse(screen, wheel_color, (self.x + wheel_pos[0], self.y + wheel_pos[1], 15, 15))
            pg.draw.ellipse(screen, rim_color, (self.x + wheel_pos[0] + 3, self.y + wheel_pos[1] + 3, 9, 9))

    def move(self, direction=None):
        if self.player:
            if direction == "left":
                self.x = max(self.road_boundary_left, self.x - self.speed)
            if direction == "right":
                self.x = min(self.road_boundary_right, self.x + self.speed)
        else:
            self.y += self.speed
            return self.y > HEIGHT


class Road:
    def __init__(self, base_speed=10):
        self.road_width = 500
        self.road_x = (WIDTH - self.road_width) // 2
        self.stripes = []
        for i in range(10):
            self.stripes.append({
                'y': i * 120 - 100,
                'width': 60,
                'height': 20,
                'speed': base_speed + 2
            })

    def draw(self, screen):
        pg.draw.rect(screen, SHOULDER_COLOR, (0, 0, self.road_x, HEIGHT))
        pg.draw.rect(screen, SHOULDER_COLOR, (self.road_x + self.road_width, 0, WIDTH, HEIGHT))
        pg.draw.rect(screen, ROAD_COLOR, (self.road_x, 0, self.road_width, HEIGHT))
        for i in range(0, HEIGHT, 4):
            brightness = random.randint(-5, 5)
            shade = (ROAD_COLOR[0] + brightness, ROAD_COLOR[1] + brightness, ROAD_COLOR[2] + brightness)
            pg.draw.line(screen, shade, (self.road_x, i), (self.road_x + self.road_width, i), 1)
        for stripe in self.stripes:
            pg.draw.rect(screen, WHITE,
                         (WIDTH // 2 - stripe['width'] // 2, stripe['y'], stripe['width'], stripe['height']))
            if stripe['y'] % 240 < 120:
                reflect = pg.Surface((stripe['width'], stripe['height'] // 3), pg.SRCALPHA)
                reflect.fill((255, 255, 255, 30))
                screen.blit(reflect, (WIDTH // 2 - stripe['width'] // 2, stripe['y']))
        pg.draw.line(screen, WHITE, (self.road_x, 0), (self.road_x, HEIGHT), 2)
        pg.draw.line(screen, WHITE, (self.road_x + self.road_width, 0), (self.road_x + self.road_width, HEIGHT), 2)

    def update(self):
        for stripe in self.stripes:
            stripe['y'] += stripe['speed']
            if stripe['y'] > HEIGHT:
                stripe['y'] = -stripe['height']


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Sleek Street Racer")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 42)
        self.small_font = pg.font.Font(None, 28)
        self.tiny_font = pg.font.Font(None, 20)
        
        # Game state
        self.selected_skin = 0
        self.selected_difficulty = "Medium"
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        self.obstacles = []
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.base_speed = diff_settings["base_speed"]
        self.road = Road(self.base_speed)

        # ----------------- Coins initialize -----------------
        self.coins = []
        self.last_coin_time = 0
        self.coin_frequency = 2000
        # ----------------------------------------------------

        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.in_menu = True
        self.in_skin_selection = False
        self.last_obstacle_time = 0
        self.obstacle_frequency = DIFFICULTY_SETTINGS[self.selected_difficulty]["obstacle_freq"]
        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 60, "START RACE")
        self.pause_button = Button(WIDTH - 120, 10, 100, 40, "PAUSE")
        self.restart_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 50, "RESTART")
        self.sound_button = Button(WIDTH - 120, 55, 100, 35, "SOUND: ON")
        self.clock_speed = 1.2
        self.score_animation = 0
        self.music_muted = False
        
        # Score multiplier system
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.multiplier_text_pos = (0, 0)
        self.consecutive_actions = 0  # Track consecutive coins/obstacles avoided

        # Load and play music
        self.current_music = load_music()
        if self.current_music:
            pg.mixer.music.play(-1)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.current_music:
                    pg.mixer.music.stop()
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.in_menu:
                    # Difficulty selection (matching draw_menu coordinates)
                    y_offset = 100  # Same as in draw_menu
                    for i, diff in enumerate(["Easy", "Medium", "Hard"]):
                        btn_rect = pg.Rect(WIDTH // 2 - 100, y_offset + 30 + i * 45, 200, 35)
                        if btn_rect.collidepoint(event.pos):
                            self.selected_difficulty = diff
                            break  # Exit loop once clicked
                    # Skin selection arrows (matching draw_menu coordinates)
                    # In draw_menu: y_offset starts at 100, adds 180, then preview_y = y_offset + 35 = 315
                    # Arrows are at preview_y + 30 = 345
                    preview_y_base = 100 + 180 + 35  # = 315 (matches draw_menu)
                    left_arrow = pg.Rect(WIDTH // 2 - 150, preview_y_base + 30, 40, 40)
                    right_arrow = pg.Rect(WIDTH // 2 + 110, preview_y_base + 30, 40, 40)
                    if left_arrow.collidepoint(event.pos):
                        self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
                        self.player_color = CAR_SKINS[self.selected_skin]["color"]
                        self.player_type = CAR_SKINS[self.selected_skin]["type"]
                    if right_arrow.collidepoint(event.pos):
                        self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
                        self.player_color = CAR_SKINS[self.selected_skin]["color"]
                        self.player_type = CAR_SKINS[self.selected_skin]["type"]
                    # Play button
                    if self.play_button.is_clicked(event.pos):
                        self.start_game()
                elif not self.game_over:
                    # Pause button
                    if self.pause_button.is_clicked(event.pos):
                        self.paused = not self.paused
                        if self.paused:
                            if not self.music_muted:
                                pg.mixer.music.pause()
                        else:
                            if not self.music_muted:
                                pg.mixer.music.unpause()
                    # Sound toggle button
                    if self.sound_button.is_clicked(event.pos):
                        self.music_muted = not self.music_muted
                        if self.music_muted:
                            pg.mixer.music.set_volume(0.0)
                            self.sound_button.text = "SOUND: OFF"
                        else:
                            pg.mixer.music.set_volume(0.5)
                            self.sound_button.text = "SOUND: ON"
                            if not self.paused:
                                pg.mixer.music.unpause()
                    # Restart button (when paused)
                    if self.paused and self.restart_button.is_clicked(event.pos):
                        self.reset_game()
                elif self.game_over:
                    # Buttons in game over screen
                    button_y_start = HEIGHT // 2 - 20
                    button_spacing = 60
                    
                    # Restart button
                    restart_btn_rect = pg.Rect(WIDTH // 2 - 100, button_y_start, 200, 45)
                    if restart_btn_rect.collidepoint(event.pos):
                        self.reset_game()
                    
                    # Return to Menu button
                    menu_btn_rect = pg.Rect(WIDTH // 2 - 100, button_y_start + button_spacing, 200, 45)
                    if menu_btn_rect.collidepoint(event.pos):
                        self.return_to_menu()
                    
                    # Quit button
                    quit_btn_rect = pg.Rect(WIDTH // 2 - 100, button_y_start + button_spacing * 2, 200, 45)
                    if quit_btn_rect.collidepoint(event.pos):
                        if self.current_music:
                            pg.mixer.music.stop()
                        pg.quit()
                        sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p or event.key == pg.K_ESCAPE:
                    if not self.in_menu and not self.game_over:
                        self.paused = not self.paused
                        if self.paused:
                            pg.mixer.music.pause()
                        else:
                            pg.mixer.music.unpause()
                    elif self.game_over:
                        # ESC from game over returns to menu
                        self.return_to_menu()
                if event.key == pg.K_r and (self.game_over or self.paused):
                    self.reset_game()

    def start_game(self):
        self.in_menu = False
        self.paused = False
        self.game_over = False
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.level = 1
        self.last_obstacle_time = pg.time.get_ticks()
        self.last_coin_time = pg.time.get_ticks()
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.obstacle_frequency = diff_settings["obstacle_freq"]
        self.clock_speed = 1.0
        self.base_speed = diff_settings["base_speed"]
        self.road = Road(self.base_speed)
        # Reset multiplier
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.consecutive_actions = 0
        if self.current_music:
            if not self.music_muted:
                pg.mixer.music.play(-1)

    def update(self):
        if self.game_over or self.in_menu or self.paused:
            return

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.player.move("left")
        if keys[pg.K_RIGHT]:
            self.player.move("right")

        current_time = pg.time.get_ticks()
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        
        # -------------- Obstacles ----------------
        if current_time - self.last_obstacle_time > self.obstacle_frequency / self.clock_speed:
            color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
            new_obstacle = Car(random.randint(self.player.road_boundary_left, self.player.road_boundary_right), -150,
                               color)
            min_speed, max_speed = diff_settings["obstacle_speed"]
            new_obstacle.speed = random.randint(min_speed, max_speed)
            self.obstacles.append(new_obstacle)
            self.last_obstacle_time = current_time
            if self.score > 0 and self.score % 3 == 0:
                self.obstacle_frequency = max(600, self.obstacle_frequency - 100)
                self.level += 1
                self.clock_speed = min(2.5, self.clock_speed + diff_settings["speed_increase"])

        for obstacle in self.obstacles[:]:
            if obstacle.move():
                self.obstacles.remove(obstacle)
                # Increase multiplier for avoiding obstacles
                self.consecutive_actions += 1
                self.update_multiplier()
                base_score = 1
                self.score += int(base_score * self.score_multiplier)
            if (self.player.x < obstacle.x + obstacle.width and
                    self.player.x + self.player.width > obstacle.x and
                    self.player.y < obstacle.y + obstacle.height and
                    self.player.y + self.player.height > obstacle.y):
                self.game_over = True
                if self.current_music:
                    pg.mixer.music.fadeout(2000)

        # ---------------- Coins Spawn ----------------
        if current_time - self.last_coin_time > self.coin_frequency:
            new_coin = Coin(random.randint(self.player.road_boundary_left, self.player.road_boundary_right), -50)
            self.coins.append(new_coin)
            self.last_coin_time = current_time

        # ---------------- Coins Move & Collision ----------------
        for coin in self.coins[:]:
            if coin.move():
                self.coins.remove(coin)
            if (self.player.x < coin.x + coin.radius and
                    self.player.x + self.player.width > coin.x - coin.radius and
                    self.player.y < coin.y + coin.radius and
                    self.player.y + self.player.height > coin.y - coin.radius):
                coin.grow()
                self.coins.remove(coin)
                # Increase multiplier for collecting coins
                self.consecutive_actions += 1
                self.update_multiplier()
                base_score = 5
                score_gain = int(base_score * self.score_multiplier)
                self.score += score_gain
                # Show multiplier feedback
                self.multiplier_display_time = pg.time.get_ticks()
                self.multiplier_text_pos = (coin.x, coin.y)

        self.road.update()
        
        # Update multiplier timer (decrease multiplier if no actions)
        current_time = pg.time.get_ticks()
        if current_time - self.multiplier_timer > 3000:  # 3 seconds without action
            if self.score_multiplier > 1.0:
                self.consecutive_actions = max(0, self.consecutive_actions - 1)
                self.update_multiplier()
            self.multiplier_timer = current_time

    def draw(self):
        for y in range(HEIGHT):
            shade = 10 + int(10 * (y / HEIGHT))
            pg.draw.line(self.screen, (shade, shade, shade), (0, y), (WIDTH, y))

        if self.in_menu:
            self.draw_menu()
        else:
            self.road.draw(self.screen)
            for car in [self.player] + self.obstacles:
                shadow = pg.Surface((car.width, car.height // 3), pg.SRCALPHA)
                shadow.fill((0, 0, 0, 80))
                self.screen.blit(shadow, (car.x, car.y + car.height - 10))
                car.draw(self.screen)

            # Draw Coins
            for coin in self.coins:
                coin.draw(self.screen)

            self.draw_scoreboard()
            self.pause_button.draw(self.screen, self.tiny_font)
            self.sound_button.draw(self.screen, self.tiny_font)
            self.draw_multiplier_feedback()
            if self.paused:
                self.draw_pause_screen()
            if self.game_over:
                self.draw_game_over()
        pg.display.flip()

    def draw_menu(self):
        # Background gradient
        for y in range(HEIGHT):
            shade = 10 + int(15 * (y / HEIGHT))
            pg.draw.line(self.screen, (shade, shade, shade + 5), (0, y), (WIDTH, y))
        
        # Title with better styling
        title = self.font.render("SLEEK STREET RACER", True, (200, 200, 0))
        shadow = self.font.render("SLEEK STREET RACER", True, (80, 80, 0))
        self.screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 33))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # Menu container background
        menu_bg = pg.Surface((500, 480), pg.SRCALPHA)
        menu_bg.fill((0, 0, 0, 180))
        pg.draw.rect(menu_bg, (255, 255, 255, 40), (0, 0, 500, 480), 2, border_radius=10)
        self.screen.blit(menu_bg, (WIDTH // 2 - 250, 80))
        
        y_offset = 100
        
        # Difficulty Selection
        diff_text = self.small_font.render("Difficulty:", True, WHITE)
        self.screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, y_offset))
        
        for i, diff in enumerate(["Easy", "Medium", "Hard"]):
            btn_rect = pg.Rect(WIDTH // 2 - 100, y_offset + 30 + i * 45, 200, 35)
            color = GREEN if diff == self.selected_difficulty else GRAY
            hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
            mouse_pos = pg.mouse.get_pos()
            btn_color = hover_color if btn_rect.collidepoint(mouse_pos) else color
            pg.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            pg.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=8)
            text = self.small_font.render(diff, True, WHITE)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
        
        y_offset += 180
        
        # Car Skin Selection
        skin_text = self.small_font.render("Car Skin:", True, WHITE)
        self.screen.blit(skin_text, (WIDTH // 2 - skin_text.get_width() // 2, y_offset))
        
        # Skin preview area
        preview_x = WIDTH // 2 - 25
        preview_y = y_offset + 35
        
        # Background for car preview
        preview_bg = pg.Surface((100, 110), pg.SRCALPHA)
        preview_bg.fill((30, 30, 40, 200))
        pg.draw.rect(preview_bg, (255, 255, 255, 30), (0, 0, 100, 110), 2, border_radius=5)
        self.screen.blit(preview_bg, (preview_x - 25, preview_y - 5))
        
        preview_car = Car(preview_x, preview_y, self.player_color, True, self.player_type)
        preview_car.draw(self.screen)
        
        # Navigation arrows
        left_arrow = pg.Rect(WIDTH // 2 - 150, preview_y + 30, 40, 40)
        right_arrow = pg.Rect(WIDTH // 2 + 110, preview_y + 30, 40, 40)
        mouse_pos = pg.mouse.get_pos()
        
        for arrow_rect, symbol in [(left_arrow, "<"), (right_arrow, ">")]:
            hover = arrow_rect.collidepoint(mouse_pos)
            color = GREEN if hover else GRAY
            pg.draw.rect(self.screen, color, arrow_rect, border_radius=5)
            pg.draw.rect(self.screen, WHITE, arrow_rect, 2, border_radius=5)
            arrow_text = self.small_font.render(symbol, True, WHITE)
            arrow_text_rect = arrow_text.get_rect(center=arrow_rect.center)
            self.screen.blit(arrow_text, arrow_text_rect)
        
        # Skin name
        skin_name = self.tiny_font.render(CAR_SKINS[self.selected_skin]["name"], True, YELLOW)
        self.screen.blit(skin_name, (WIDTH // 2 - skin_name.get_width() // 2, preview_y + 100))
        
        y_offset += 150
        
        # High score
        hs_text = self.tiny_font.render(f"High Score: {self.get_high_score()}", True, YELLOW)
        self.screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, y_offset))
        
        y_offset += 30
        
        # Play button
        self.play_button.rect.y = y_offset
        self.play_button.draw(self.screen, self.font)
        
        y_offset += 80
        
        # Instructions (compact)
        instructions = [
            "← → to steer | P to pause | R to restart"
        ]
        for i, line in enumerate(instructions):
            text = self.tiny_font.render(line, True, GRAY)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset + i * 20))

    def draw_scoreboard(self):
        # Animated scoreboard with smooth design
        self.score_animation += 0.1
        pulse = int(5 * abs(math.sin(self.score_animation)))
        
        hud_bg = pg.Surface((280, 160), pg.SRCALPHA)
        hud_bg.fill((0, 0, 0, 180))
        pg.draw.rect(hud_bg, (255, 255, 255, 50 + pulse), (0, 0, 280, 160), 3, border_radius=10)
        
        # Gradient effect
        for i in range(160):
            alpha = int(30 * (1 - i / 160))
            pg.draw.line(hud_bg, (50, 180, 80, alpha), (0, i), (280, i))
        
        self.screen.blit(hud_bg, (10, 10))
        
        # Score with animation
        score_color = (255, 255, 100 + pulse) if self.score > 0 else WHITE
        score_text = self.small_font.render(f"Score: {self.score}", True, score_color)
        self.screen.blit(score_text, (25, 25))
        
        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_text, (25, 55))
        
        # Speed
        speed_text = self.small_font.render(f"Speed: {int(self.clock_speed * 100)}%", True, GREEN)
        self.screen.blit(speed_text, (25, 85))
        
        # Difficulty indicator
        diff_indicator = self.tiny_font.render(f"Mode: {self.selected_difficulty}", True, YELLOW)
        self.screen.blit(diff_indicator, (25, 115))
        
        # Score multiplier display
        if self.score_multiplier > 1.0:
            multiplier_color = YELLOW if self.score_multiplier >= 2.0 else GREEN
            multiplier_text = self.tiny_font.render(f"Multiplier: x{self.score_multiplier:.1f}", True, multiplier_color)
            self.screen.blit(multiplier_text, (25, 135))

    def update_multiplier(self):
        """Update score multiplier based on consecutive actions"""
        self.multiplier_timer = pg.time.get_ticks()
        # Multiplier increases: 1.0 -> 1.5 -> 2.0 -> 2.5 -> 3.0 (max)
        if self.consecutive_actions >= 20:
            self.score_multiplier = 3.0
        elif self.consecutive_actions >= 15:
            self.score_multiplier = 2.5
        elif self.consecutive_actions >= 10:
            self.score_multiplier = 2.0
        elif self.consecutive_actions >= 5:
            self.score_multiplier = 1.5
        else:
            self.score_multiplier = 1.0
    
    def draw_multiplier_feedback(self):
        """Draw multiplier feedback when collecting coins"""
        if self.multiplier_display_time > 0:
            current_time = pg.time.get_ticks()
            elapsed = current_time - self.multiplier_display_time
            
            if elapsed < 1000:  # Show for 1 second
                # Fade out effect
                alpha = int(255 * (1 - elapsed / 1000))
                if alpha > 0:
                    # Animate upward
                    y_offset = -elapsed // 10
                    x, y = self.multiplier_text_pos
                    y += y_offset
                    
                    # Draw multiplier text with glow effect
                    if self.score_multiplier > 1.0:
                        multiplier_str = f"x{self.score_multiplier:.1f}!"
                        color = YELLOW if self.score_multiplier >= 2.0 else GREEN
                        
                        # Glow effect
                        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                            glow_text = self.small_font.render(multiplier_str, True, (color[0]//3, color[1]//3, color[2]//3))
                            self.screen.blit(glow_text, (x - glow_text.get_width()//2 + offset[0], y + offset[1]))
                        
                        # Main text
                        main_text = self.small_font.render(multiplier_str, True, color)
                        self.screen.blit(main_text, (x - main_text.get_width()//2, y))
            else:
                self.multiplier_display_time = 0

    def draw_pause_screen(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        box = pg.Surface((350, 250), pg.SRCALPHA)
        box.fill((20, 20, 30, 240))
        pg.draw.rect(box, (255, 255, 255, 50), (0, 0, 350, 250), 3, border_radius=15)
        self.screen.blit(box, (WIDTH // 2 - 175, HEIGHT // 2 - 125))
        
        title = self.font.render("PAUSED", True, YELLOW)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
        
        score = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 50))
        
        level = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level, (WIDTH // 2 - level.get_width() // 2, HEIGHT // 2 - 20))
        
        restart_text = self.tiny_font.render("Press R to restart", True, GRAY)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        
        resume_text = self.tiny_font.render("Press P or ESC to resume", True, GRAY)
        self.screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 45))
        
        self.restart_button.draw(self.screen, self.small_font)

    def draw_game_over(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Larger box to fit all buttons
        box = pg.Surface((450, 380), pg.SRCALPHA)
        box.fill((20, 20, 30, 240))
        pg.draw.rect(box, (255, 0, 0, 80), (0, 0, 450, 380), 3, border_radius=15)
        self.screen.blit(box, (WIDTH // 2 - 225, HEIGHT // 2 - 190))
        
        title = self.font.render("GAME OVER", True, RED)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 170))
        
        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 120))
        
        level = self.small_font.render(f"Reached Level: {self.level}", True, CYAN)
        self.screen.blit(level, (WIDTH // 2 - level.get_width() // 2, HEIGHT // 2 - 90))
        
        high_score = self.get_high_score()
        if self.score >= high_score:
            new_record = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, HEIGHT // 2 - 60))
        else:
            hs_text = self.tiny_font.render(f"High Score: {high_score}", True, GRAY)
            self.screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 - 55))
        
        # Button area
        button_y_start = HEIGHT // 2 - 20
        button_spacing = 60
        
        # Restart button
        restart_btn = Button(WIDTH // 2 - 100, button_y_start, 200, 45, "RESTART")
        restart_btn.draw(self.screen, self.small_font)
        
        # Return to Menu button
        menu_btn = Button(WIDTH // 2 - 100, button_y_start + button_spacing, 200, 45, "MAIN MENU")
        menu_btn.draw(self.screen, self.small_font)
        
        # Quit button
        quit_btn = Button(WIDTH // 2 - 100, button_y_start + button_spacing * 2, 200, 45, "QUIT")
        quit_btn.draw(self.screen, self.small_font)
        
        # Keyboard hint
        hint_text = self.tiny_font.render("Press R to restart | ESC for menu", True, GRAY)
        self.screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, button_y_start + button_spacing * 3 + 10))

    def get_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self.get_high_score())))

    def return_to_menu(self):
        """Return to main menu from game over screen"""
        self.save_high_score()
        self.in_menu = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.obstacles = []
        self.coins = []
        # Reset player to current selected skin
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.base_speed = diff_settings["base_speed"]
        self.road = Road(self.base_speed)
        self.obstacle_frequency = diff_settings["obstacle_freq"]
        self.clock_speed = 1.0
        if self.current_music:
            pg.mixer.music.play(-1)

    def reset_game(self):
        self.save_high_score()
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        self.obstacles = []
        self.coins = []
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.base_speed = diff_settings["base_speed"]
        self.road = Road(self.base_speed)
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.last_obstacle_time = pg.time.get_ticks()
        self.last_coin_time = pg.time.get_ticks()
        self.obstacle_frequency = diff_settings["obstacle_freq"]
        self.clock_speed = 1.0
        # Reset multiplier
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.consecutive_actions = 0
        if self.current_music:
            if not self.music_muted:
                pg.mixer.music.play(-1)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


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
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        screen.blit(self.shadow, (self.rect.x + 3, self.rect.y + 3))
        pg.draw.rect(screen, color, self.rect, border_radius=8)
        pg.draw.rect(screen, (255, 255, 255, 80), self.rect, 2, border_radius=8)
        text_shadow = font.render(self.text, True, (0, 0, 0, 100))
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


if __name__ == "__main__":
    game = Game()
    game.run()
