import pygame as pg
import sys
import random
import os

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
    def __init__(self):
        self.road_width = 500
        self.road_x = (WIDTH - self.road_width) // 2
        self.stripes = []
        for i in range(10):
            self.stripes.append({
                'y': i * 120 - 100,
                'width': 60,
                'height': 20,
                'speed': BASE_SPEED + 2
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
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, BLUE, True)
        self.obstacles = []
        self.road = Road()

        # ----------------- Coins initialize -----------------
        self.coins = []
        self.last_coin_time = 0
        self.coin_frequency = 2000
        # ----------------------------------------------------

        self.score = 0
        self.level = 1
        self.game_over = False
        self.in_menu = True
        self.last_obstacle_time = 0
        self.obstacle_frequency = 1200
        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 60, "START RACE")
        self.clock_speed = 1.2

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
                if self.in_menu and self.play_button.is_clicked(event.pos):
                    self.in_menu = False
            if event.type == pg.KEYDOWN and self.game_over:
                if event.key == pg.K_r:
                    self.reset_game()

    def update(self):
        if self.game_over or self.in_menu:
            return

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.player.move("left")
        if keys[pg.K_RIGHT]:
            self.player.move("right")

        current_time = pg.time.get_ticks()
        # -------------- Obstacles ----------------
        if current_time - self.last_obstacle_time > self.obstacle_frequency / self.clock_speed:
            color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
            new_obstacle = Car(random.randint(self.player.road_boundary_left, self.player.road_boundary_right), -150,
                               color)
            new_obstacle.speed = random.randint(8, 12)
            self.obstacles.append(new_obstacle)
            self.last_obstacle_time = current_time
            if self.score > 0 and self.score % 3 == 0:
                self.obstacle_frequency = max(600, self.obstacle_frequency - 100)
                self.level += 1
                self.clock_speed = min(2.5, self.clock_speed + 0.15)

        for obstacle in self.obstacles[:]:
            if obstacle.move():
                self.obstacles.remove(obstacle)
                self.score += 1
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
                self.score += 5

        self.road.update()

    def draw(self):
        for y in range(HEIGHT):
            shade = 10 + int(10 * (y / HEIGHT))
            pg.draw.line(self.screen, (shade, shade, shade), (0, y), (WIDTH, y))

        if self.in_menu:
            title = self.font.render("SLEEK STREET RACER", True, (200, 200, 0))
            shadow = self.font.render("SLEEK STREET RACER", True, (80, 80, 0))
            self.screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 103))
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            instructions = [
                "Use LEFT/RIGHT arrows to steer your car",
                "Avoid other vehicles on the road",
                f"Current high score: {self.get_high_score()}"
            ]
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 180 + i * 40))
            self.play_button.draw(self.screen, self.font)
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

            hud_bg = pg.Surface((250, 110), pg.SRCALPHA)
            hud_bg.fill((0, 0, 0, 150))
            pg.draw.rect(hud_bg, (255, 255, 255, 30), (0, 0, 250, 110), 2, border_radius=5)
            self.screen.blit(hud_bg, (10, 10))
            texts = [f"Score: {self.score}", f"Level: {self.level}", f"Speed: {int(self.clock_speed * 100)}%"]
            for i, text in enumerate(texts):
                rendered = self.small_font.render(text, True, WHITE)
                self.screen.blit(rendered, (20, 20 + i * 30))
            if self.game_over:
                self.draw_game_over()
        pg.display.flip()

    def draw_game_over(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        box = pg.Surface((400, 200), pg.SRCALPHA)
        box.fill((0, 0, 0, 200))
        pg.draw.rect(box, (255, 255, 255, 30), (0, 0, 400, 200), 2)
        self.screen.blit(box, (WIDTH // 2 - 200, HEIGHT // 2 - 100))
        title = self.font.render("GAME OVER", True, RED)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 30))
        restart = self.small_font.render("Press R to restart", True, YELLOW)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 20))

    def get_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self.get_high_score())))

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
        self.obstacle_frequency = 1200
        self.clock_speed = 1.2
        if self.current_music:
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
