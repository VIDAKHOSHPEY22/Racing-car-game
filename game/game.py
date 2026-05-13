import math
import random
import sys

import pygame as pg

from .button import Button
from .car import Car
from .coin import Coin
from .constants import (
    ACCELERATION,
    FRICTION,
    BRAKE_DECEL,
    BASE_SPEED,
    DAMAGE_COOLDOWN,
    CAR_SKINS,
    CYAN,
    DEFAULT_DIFFICULTY,
    DEFAULT_STAGE,
    DIFFICULTY_SETTINGS,
    FPS,
    GOLD,
    GRAY,
    GREEN,
    HEIGHT,
    MENU_CARD_HEIGHT,
    MENU_CARD_WIDTH,
    NAVY,
    PLAYER_START_LIVES,
    RED,
    SLATE,
    SURFACE,
    SURFACE_ALT,
    TEAL,
    WHITE,
    WIDTH,
    YELLOW,
)
from .game_state import GameState
from .music_utils import load_music
from .road import Road
from .storage import read_high_score, write_high_score
from . import constants as const


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Sleek Street Racer")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 42)
        self.small_font = pg.font.Font(None, 28)
        self.tiny_font = pg.font.Font(None, 20)

        self.state = GameState.MENU
        self.paused = False
        self.music_muted = False
        self.selected_skin = 0
        self.selected_difficulty = DEFAULT_DIFFICULTY
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]

        self.stage = DEFAULT_STAGE
        self.level = DEFAULT_STAGE
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.last_damage_time = 0
        self.damage_flash_time = 0
        self.base_speed = DIFFICULTY_SETTINGS[self.selected_difficulty]["base_speed"]
        self.current_speed = self.base_speed
        # displayed speed (reflects player velocity) kept separate from current_speed game logic
        self.display_speed = float(self.current_speed)
        self.score_animation = 0
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.multiplier_text_pos = (0, 0)
        self.consecutive_actions = 0

        self.player = None
        self.obstacles = []
        self.coins = []
        self.road = None
        self.last_obstacle_time = 0
        self.last_coin_time = 0
        self.coin_frequency = 2000
        self.obstacle_frequency = DIFFICULTY_SETTINGS[self.selected_difficulty]["obstacle_freq"]
        self.best_score = read_high_score()

        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 60, "START RACE")
        self.high_score_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 45, "HIGH SCORES")
        self.menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 250, 200, 45, "MAIN MENU")
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 310, 200, 45, "EXIT")
        self.pause_button = Button(WIDTH - 120, 10, 100, 40, "PAUSE")
        self.restart_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 50, "RESTART")
        self.pause_menu_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 120, 160, 45, "MAIN MENU")
        self.sound_button = Button(WIDTH - 120, 55, 100, 35, "SOUND: ON")

        self.current_music = load_music()
        if self.current_music:
            pg.mixer.music.play(-1)

        self.reset_game(change_state=False)

    def set_state(self, state):
        self.state = state

    def _sync_player_skin(self):
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]

    def reset_game(self, change_state=True):
        self._sync_player_skin()
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        self.obstacles = []
        self.coins = []
        self.stage = DEFAULT_STAGE
        self.level = DEFAULT_STAGE
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.last_damage_time = 0
        self.damage_flash_time = 0
        self.last_obstacle_time = pg.time.get_ticks()
        self.last_coin_time = pg.time.get_ticks()

        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.base_speed = diff_settings["base_speed"]
        # apply difficulty-specific max speed at runtime so `Car.accelerate` clamps correctly
        try:
            import game.constants as const

            const.MAX_SPEED = float(diff_settings.get("max_speed", const.MAX_SPEED))
        except Exception:
            pass
        self.current_speed = self.base_speed
        # ensure player's internal velocity starts at the PLAYER_SPEED_DEFAULT
        from .constants import PLAYER_SPEED_DEFAULT
        if self.player and hasattr(self.player, "velocity"):
            try:
                self.player.velocity = float(PLAYER_SPEED_DEFAULT)
            except Exception:
                pass
        self.obstacle_frequency = diff_settings["obstacle_freq"]
        self.road = Road(self.base_speed)
        self.paused = False
        self.pause_button.text = "PAUSE"
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.consecutive_actions = 0
        self.update_player_bounds()

        if change_state:
            self.set_state(GameState.PLAYING)

    def start_game(self):
        self.reset_game(change_state=True)
        if self.current_music and not self.music_muted:
            pg.mixer.music.play(-1)

    def open_high_scores(self):
        self.best_score = read_high_score()
        self.set_state(GameState.HIGH_SCORE)

    def enter_game_over(self):
        self.best_score = write_high_score(self.score)
        self.set_state(GameState.GAME_OVER)

    def return_to_menu(self):
        self.best_score = read_high_score()
        self.reset_game(change_state=False)
        self.set_state(GameState.MENU)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.current_music:
                    pg.mixer.music.stop()
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.MENU:
                    self.handle_menu_click(event.pos)
                elif self.state == GameState.HIGH_SCORE:
                    if self.menu_button.is_clicked(event.pos):
                        self.return_to_menu()
                elif self.state == GameState.PLAYING:
                    self.handle_playing_click(event.pos)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_click(event.pos)

            if event.type == pg.KEYDOWN:
                if event.key in {pg.K_p, pg.K_ESCAPE}:
                    if self.state == GameState.PLAYING:
                        self.toggle_pause()
                    elif self.state in {GameState.GAME_OVER, GameState.HIGH_SCORE}:
                        self.return_to_menu()
                if event.key == pg.K_h and self.state == GameState.MENU:
                    self.open_high_scores()
                if event.key == pg.K_r and (self.state == GameState.GAME_OVER or self.paused):
                    self.reset_game()

    def handle_menu_click(self, mouse_pos):
        layout = self.get_menu_layout()
        self.sync_menu_button_rects(layout)

        for index, difficulty in enumerate(["Easy", "Medium", "Hard"]):
            button_rect = layout["difficulty_buttons"][index]
            if button_rect.collidepoint(mouse_pos):
                self.selected_difficulty = difficulty
                self.reset_game(change_state=False)
                break

        left_arrow = layout["left_arrow"]
        right_arrow = layout["right_arrow"]
        if left_arrow.collidepoint(mouse_pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
            self._sync_player_skin()
            self.reset_game(change_state=False)
        if right_arrow.collidepoint(mouse_pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
            self._sync_player_skin()
            self.reset_game(change_state=False)

        if self.play_button.is_clicked(mouse_pos):
            self.start_game()
        if self.high_score_button.is_clicked(mouse_pos):
            self.open_high_scores()
        if self.exit_button.is_clicked(mouse_pos):
            if self.current_music:
                pg.mixer.music.stop()
            pg.quit()
            sys.exit()

    def handle_playing_click(self, mouse_pos):
        if self.pause_button.is_clicked(mouse_pos):
            self.toggle_pause()

        if self.sound_button.is_clicked(mouse_pos):
            self.music_muted = not self.music_muted
            if self.music_muted:
                pg.mixer.music.set_volume(0.0)
                self.sound_button.text = "SOUND: OFF"
            else:
                pg.mixer.music.set_volume(0.5)
                self.sound_button.text = "SOUND: ON"
                if not self.paused:
                    pg.mixer.music.unpause()

        if self.paused and self.restart_button.is_clicked(mouse_pos):
            self.reset_game()
        if self.paused and self.pause_menu_button.is_clicked(mouse_pos):
            self.return_to_menu()

    def handle_game_over_click(self, mouse_pos):
        button_y_start = HEIGHT // 2 - 20
        button_spacing = 60
        restart_button_rect = pg.Rect(WIDTH // 2 - 100, button_y_start, 200, 45)
        menu_button_rect = pg.Rect(WIDTH // 2 - 100, button_y_start + button_spacing, 200, 45)
        quit_button_rect = pg.Rect(WIDTH // 2 - 100, button_y_start + button_spacing * 2, 200, 45)

        if restart_button_rect.collidepoint(mouse_pos):
            self.reset_game()
        if menu_button_rect.collidepoint(mouse_pos):
            self.return_to_menu()
        if quit_button_rect.collidepoint(mouse_pos):
            if self.current_music:
                pg.mixer.music.stop()
            pg.quit()
            sys.exit()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.text = "RESUME" if self.paused else "PAUSE"
        if self.paused:
            if not self.music_muted:
                pg.mixer.music.pause()
        else:
            if not self.music_muted:
                pg.mixer.music.unpause()

    def update_player_bounds(self):
        left, max_x = self.road.get_drive_bounds(self.player.y + self.player.height // 2, self.player.width)
        self.player.road_boundary_left = left
        self.player.road_boundary_right = max_x
        self.player.x = max(left, min(max_x, self.player.x))

    def align_obstacle_to_road(self, obstacle):
        if hasattr(obstacle, "road_ratio"):
            obstacle.x = self.road.get_travel_x(obstacle.y + obstacle.height // 2, obstacle.road_ratio, obstacle.width)

    def align_coin_to_road(self, coin):
        if hasattr(coin, "road_ratio"):
            coin.x = self.road.get_travel_x(coin.y, coin.road_ratio, coin.radius * 2) + coin.radius

    def update(self):
        if self.state != GameState.PLAYING or self.paused:
            return

        self.road.update()
        self.update_player_bounds()

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.player.move("left")
        if keys[pg.K_RIGHT]:
            self.player.move("right")
        # Frame-time (seconds) for frame-independent accel/decel
        dt = max(1 / FPS, self.clock.get_time() / 1000.0)
        # Brake input (S or Down) takes priority, then accelerate, otherwise friction
        if (keys[pg.K_s] or keys[pg.K_DOWN]) and hasattr(self.player, "accelerate"):
            # strong deceleration while braking
            self.player.accelerate(-BRAKE_DECEL * dt)
        elif (keys[pg.K_w] or keys[pg.K_UP]) and hasattr(self.player, "accelerate"):
            # regular acceleration
            self.player.accelerate(ACCELERATION * dt)
        else:
            # apply friction (deceleration) when not accelerating nor braking
            if hasattr(self.player, "accelerate"):
                self.player.accelerate(-FRICTION * dt)

        # update display-only speed from player's internal velocity (do not change game logic current_speed)
        try:
            self.display_speed = float(self.player.get_velocity())
        except Exception:
            self.display_speed = float(self.current_speed)
        self.update_player_bounds()

        current_time = pg.time.get_ticks()
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        speed_factor = max(self.current_speed / BASE_SPEED, 1)

        if current_time - self.last_obstacle_time > self.obstacle_frequency / speed_factor:
            min_spacing = 120
            safe_to_spawn = True

            for existing_obstacle in self.obstacles:
                if existing_obstacle.y > -150 - min_spacing and existing_obstacle.y < -150 + min_spacing:
                    safe_to_spawn = False
                    break

            if safe_to_spawn:
                color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
                lane = random.randint(0, 2)
                lane_ratio = (lane + 0.5) / 3
                x_position = self.road.get_travel_x(0, lane_ratio, 50)

                new_obstacle = Car(x_position, -150, color)
                new_obstacle.road_ratio = lane_ratio
                min_speed, max_speed = diff_settings["obstacle_speed"]
                new_obstacle.speed = random.randint(min_speed, max_speed)

                can_spawn = True
                for existing_obstacle in self.obstacles:
                    if existing_obstacle.y > -200 and existing_obstacle.y < -100:
                        if (
                            new_obstacle.x < existing_obstacle.x + existing_obstacle.width
                            and new_obstacle.x + new_obstacle.width > existing_obstacle.x
                        ):
                            can_spawn = False
                            break

                if can_spawn:
                    self.obstacles.append(new_obstacle)
                    self.last_obstacle_time = current_time

            if self.score > 0 and self.score % 3 == 0:
                self.level += 1
                self.stage = self.level
                self.obstacle_frequency = max(600, self.obstacle_frequency - 100)
                self.current_speed = min(self.base_speed * 2.5, self.current_speed + diff_settings["speed_increase"] * 10)

        for obstacle in self.obstacles[:]:
            if obstacle.move():
                self.obstacles.remove(obstacle)
                self.consecutive_actions += 1
                self.update_multiplier()
                self.score += int(1 * self.score_multiplier)
                continue
            self.align_obstacle_to_road(obstacle)

            try:
                vel = float(self.player.get_velocity())
                frac = (vel - const.MIN_SPEED) / max(1.0, (const.MAX_SPEED - const.MIN_SPEED))
                frac = max(0.0, min(1.0, frac))
            except Exception:
                frac = 0.0

            player_collision_y = int(
                self.player.y - frac * max(0, (self.player.y - HEIGHT // 2))
            )

            if (
                self.player.x < obstacle.x + obstacle.width
                and self.player.x + self.player.width > obstacle.x
                and player_collision_y < obstacle.y + obstacle.height
                and player_collision_y + self.player.height > obstacle.y
            ):
                current_time = pg.time.get_ticks()
                if current_time - self.last_damage_time > DAMAGE_COOLDOWN:
                    self.lives -= 1
                    self.last_damage_time = current_time
                    self.damage_flash_time = current_time
                    if obstacle in self.obstacles:
                        self.obstacles.remove(obstacle)
                    if self.lives <= 0:
                        self.enter_game_over()
                        if self.current_music:
                            pg.mixer.music.fadeout(2000)

        if current_time - self.last_coin_time > self.coin_frequency:
            coin_ratio = random.uniform(0.08, 0.92)
            new_coin = Coin(self.road.get_travel_x(0, coin_ratio, 24) + 12, -50)
            new_coin.road_ratio = coin_ratio
            self.coins.append(new_coin)
            self.last_coin_time = current_time

        for coin in self.coins[:]:
            if coin.move():
                self.coins.remove(coin)
                continue
            self.align_coin_to_road(coin)
            if (
                self.player.x < coin.x + coin.radius
                and self.player.x + self.player.width > coin.x - coin.radius
                and self.player.y < coin.y + coin.radius
                and self.player.y + self.player.height > coin.y - coin.radius
            ):
                coin.grow()
                self.coins.remove(coin)
                self.consecutive_actions += 1
                self.update_multiplier()
                self.score += int(5 * self.score_multiplier)
                self.multiplier_display_time = pg.time.get_ticks()
                self.multiplier_text_pos = (coin.x, coin.y)

        if current_time - self.multiplier_timer > 3000:
            if self.score_multiplier > 1.0:
                self.consecutive_actions = max(0, self.consecutive_actions - 1)
                self.update_multiplier()
            self.multiplier_timer = current_time

    def draw(self):
        self.draw_background()

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.HIGH_SCORE:
            self.draw_high_score_screen()
        else:
            self.road.draw(self.screen)
            # draw player with a visual vertical offset based on forward velocity
            baseline_y = self.player.y
            mid_y = HEIGHT // 2
            # fraction of speed between MIN_SPEED and current runtime MAX_SPEED
            try:
                vel = float(self.player.get_velocity())
                frac = (vel - const.MIN_SPEED) / max(1.0, (const.MAX_SPEED - const.MIN_SPEED))
                frac = max(0.0, min(1.0, frac))
            except Exception:
                frac = 0.0
            target_visual_y = int(baseline_y - frac * max(0, (baseline_y - mid_y)))

            # draw player shadow and player at visual y
            shadow = pg.Surface((self.player.width, self.player.height // 3), pg.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            self.screen.blit(shadow, (self.player.x, target_visual_y + self.player.height - 10))
            self.player.draw(self.screen, y_override=target_visual_y)

            # draw obstacles normally
            for car in self.obstacles:
                shadow = pg.Surface((car.width, car.height // 3), pg.SRCALPHA)
                shadow.fill((0, 0, 0, 80))
                self.screen.blit(shadow, (car.x, car.y + car.height - 10))
                car.draw(self.screen)

            for coin in self.coins:
                coin.draw(self.screen)

            self.draw_scoreboard()
            self.pause_button.draw(self.screen, self.tiny_font)
            self.sound_button.draw(self.screen, self.tiny_font)
            # Speed HUD: show player's forward velocity in top-right
            try:
                vel = self.player.get_velocity()
            except Exception:
                vel = None
            if vel is not None:
                speed_text = self.small_font.render(f"Speed: {vel:.1f} km/h", True, WHITE)
                speed_rect = speed_text.get_rect(topright=(WIDTH - 10, 10))
                # Draw background box for readability
                bg = pg.Surface((speed_rect.width + 8, speed_rect.height + 6), pg.SRCALPHA)
                bg.fill((0, 0, 0, 140))
                self.screen.blit(bg, (speed_rect.left - 4, speed_rect.top - 3))
                self.screen.blit(speed_text, speed_rect)
            self.draw_multiplier_feedback()
            self.draw_damage_feedback()
            if self.paused:
                self.draw_pause_screen()
            if self.state == GameState.GAME_OVER:
                self.draw_game_over()

        pg.display.flip()

    def draw_background(self):
        for y in range(HEIGHT):
            blend = y / HEIGHT
            red = int(NAVY[0] + (SURFACE_ALT[0] - NAVY[0]) * blend)
            green = int(NAVY[1] + (SURFACE_ALT[1] - NAVY[1]) * blend)
            blue = int(NAVY[2] + (SURFACE_ALT[2] - NAVY[2]) * blend)
            pg.draw.line(self.screen, (red, green, blue), (0, y), (WIDTH, y))

        for index in range(5):
            radius = 140 + index * 90
            alpha = max(18, 78 - index * 12)
            glow = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow, (TEAL[0], TEAL[1], TEAL[2], alpha), (radius, radius), radius)
            self.screen.blit(glow, (WIDTH - 220 - radius, -40 + index * 46))

    def draw_menu_shell(self, title, subtitle):
        panel = pg.Surface((MENU_CARD_WIDTH, MENU_CARD_HEIGHT), pg.SRCALPHA)
        panel.fill((SURFACE[0], SURFACE[1], SURFACE[2], 232))
        pg.draw.rect(panel, (255, 255, 255, 28), (0, 0, MENU_CARD_WIDTH, MENU_CARD_HEIGHT), 2, border_radius=22)
        pg.draw.rect(panel, (GOLD[0], GOLD[1], GOLD[2], 62), (18, 18, MENU_CARD_WIDTH - 36, 92), border_radius=18)
        card_x = WIDTH // 2 - MENU_CARD_WIDTH // 2
        card_y = 58
        self.screen.blit(panel, (card_x, card_y))

        title_text = self.font.render(title, True, WHITE)
        subtitle_text = self.tiny_font.render(subtitle, True, (210, 220, 230))
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, card_y + 34))
        self.screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, card_y + 72))
        return card_x, card_y

    def get_menu_layout(self):
        card_x = WIDTH // 2 - MENU_CARD_WIDTH // 2
        card_y = 58
        content_top = card_y + 126

        left_panel = pg.Rect(card_x + 28, content_top, 230, 214)
        right_panel = pg.Rect(card_x + 302, content_top, 230, 214)
        difficulty_buttons = [
            pg.Rect(left_panel.x + 15, left_panel.y + 48 + index * 44, left_panel.width - 30, 36)
            for index in range(3)
        ]
        preview_rect = pg.Rect(right_panel.centerx - 50, right_panel.y + 42, 100, 110)
        left_arrow = pg.Rect(right_panel.x + 18, right_panel.y + 74, 40, 40)
        right_arrow = pg.Rect(right_panel.right - 58, right_panel.y + 74, 40, 40)

        action_y = content_top + 228
        start_button = pg.Rect(card_x + 30, action_y, 155, 48)
        score_button = pg.Rect(card_x + 196, action_y, 168, 48)
        exit_button = pg.Rect(card_x + 375, action_y, 155, 48)
        footer_rect = pg.Rect(card_x + 30, card_y + 418, MENU_CARD_WIDTH - 60, 74)

        return {
            "card_x": card_x,
            "card_y": card_y,
            "left_panel": left_panel,
            "right_panel": right_panel,
            "difficulty_buttons": difficulty_buttons,
            "preview_rect": preview_rect,
            "left_arrow": left_arrow,
            "right_arrow": right_arrow,
            "start_button": start_button,
            "score_button": score_button,
            "exit_button": exit_button,
            "footer_rect": footer_rect,
        }

    def sync_menu_button_rects(self, layout):
        self.play_button.rect.topleft = layout["start_button"].topleft
        self.play_button.rect.size = layout["start_button"].size
        self.high_score_button.rect.topleft = layout["score_button"].topleft
        self.high_score_button.rect.size = layout["score_button"].size
        self.exit_button.rect.topleft = layout["exit_button"].topleft
        self.exit_button.rect.size = layout["exit_button"].size

    def draw_menu_panel(self, rect, title):
        panel = pg.Surface(rect.size, pg.SRCALPHA)
        panel.fill((SLATE[0], SLATE[1], SLATE[2], 205))
        pg.draw.rect(panel, (255, 255, 255, 24), (0, 0, rect.width, rect.height), 1, border_radius=18)
        self.screen.blit(panel, rect.topleft)
        title_text = self.small_font.render(title, True, WHITE)
        self.screen.blit(title_text, (rect.centerx - title_text.get_width() // 2, rect.y + 16))

    def draw_menu(self):
        card_x, card_y = self.draw_menu_shell(
            "SLEEK STREET RACER",
            "Choose your difficulty, pick a car skin, and start the race.",
        )

        layout = self.get_menu_layout()
        self.sync_menu_button_rects(layout)

        self.draw_menu_panel(layout["left_panel"], "Difficulty")
        self.draw_menu_panel(layout["right_panel"], "Car Skin")

        for index, difficulty in enumerate(["Easy", "Medium", "Hard"]):
            button_rect = layout["difficulty_buttons"][index]
            color = GREEN if difficulty == self.selected_difficulty else GRAY
            hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
            mouse_pos = pg.mouse.get_pos()
            button_color = hover_color if button_rect.collidepoint(mouse_pos) else color
            pg.draw.rect(self.screen, button_color, button_rect, border_radius=8)
            pg.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=8)
            text = self.small_font.render(difficulty, True, WHITE)
            self.screen.blit(text, text.get_rect(center=button_rect.center))

        preview_rect = layout["preview_rect"]
        preview_bg = pg.Surface(preview_rect.size, pg.SRCALPHA)
        preview_bg.fill((30, 30, 40, 200))
        pg.draw.rect(preview_bg, (255, 255, 255, 30), (0, 0, preview_rect.width, preview_rect.height), 2, border_radius=10)
        self.screen.blit(preview_bg, preview_rect.topleft)

        preview_car = Car(preview_rect.centerx - 25, preview_rect.y + 6, self.player_color, True, self.player_type)
        preview_car.draw(self.screen)

        mouse_pos = pg.mouse.get_pos()
        for arrow_rect, symbol in [(layout["left_arrow"], "<"), (layout["right_arrow"], ">")]:
            hover = arrow_rect.collidepoint(mouse_pos)
            color = GREEN if hover else GRAY
            pg.draw.rect(self.screen, color, arrow_rect, border_radius=5)
            pg.draw.rect(self.screen, WHITE, arrow_rect, 2, border_radius=5)
            arrow_text = self.small_font.render(symbol, True, WHITE)
            self.screen.blit(arrow_text, arrow_text.get_rect(center=arrow_rect.center))

        skin_name = self.tiny_font.render(CAR_SKINS[self.selected_skin]["name"], True, YELLOW)
        self.screen.blit(skin_name, (layout["right_panel"].centerx - skin_name.get_width() // 2, layout["right_panel"].y + 164))

        best_text = self.tiny_font.render(f"Best Score: {self.best_score}", True, YELLOW)
        self.screen.blit(best_text, (layout["right_panel"].centerx - best_text.get_width() // 2, layout["right_panel"].y + 186))

        self.play_button.draw(self.screen, self.font)
        self.high_score_button.draw(self.screen, self.small_font)
        self.exit_button.draw(self.screen, self.small_font)

        footer = pg.Surface(layout["footer_rect"].size, pg.SRCALPHA)
        footer.fill((SLATE[0], SLATE[1], SLATE[2], 205))
        pg.draw.rect(footer, (255, 255, 255, 20), (0, 0, layout["footer_rect"].width, layout["footer_rect"].height), 1, border_radius=16)
        self.screen.blit(footer, layout["footer_rect"].topleft)

        summary_items = [
            f"Lives {PLAYER_START_LIVES}",
            f"Stage {self.stage}",
            f"Speed {self.base_speed}",
            f"State {self.state.name}",
        ]
        for index, item in enumerate(summary_items):
            text = self.tiny_font.render(item, True, (220, 230, 240))
            slot_width = layout["footer_rect"].width // len(summary_items)
            slot_x = layout["footer_rect"].x + index * slot_width + (slot_width - text.get_width()) // 2
            self.screen.blit(text, (slot_x, layout["footer_rect"].y + 16))

        help_text = self.tiny_font.render("Arrow keys steer | P pause | R restart | H high scores", True, GRAY)
        self.screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, layout["footer_rect"].y + 42))

    def draw_high_score_screen(self):
        card_x, card_y = self.draw_menu_shell("HIGH SCORES", "Prepared for future leaderboard and garage integration.")

        score_panel = pg.Surface((MENU_CARD_WIDTH - 110, 170), pg.SRCALPHA)
        score_panel.fill((SLATE[0], SLATE[1], SLATE[2], 220))
        pg.draw.rect(score_panel, (255, 255, 255, 30), (0, 0, MENU_CARD_WIDTH - 110, 170), 2, border_radius=18)
        self.screen.blit(score_panel, (card_x + 55, card_y + 130))

        best_label = self.small_font.render("Best Score", True, GOLD)
        best_value = self.font.render(str(self.best_score), True, WHITE)
        note = self.tiny_font.render("This screen now has its own state and persistence hook.", True, (205, 215, 225))
        self.screen.blit(best_label, (WIDTH // 2 - best_label.get_width() // 2, card_y + 162))
        self.screen.blit(best_value, (WIDTH // 2 - best_value.get_width() // 2, card_y + 204))
        self.screen.blit(note, (WIDTH // 2 - note.get_width() // 2, card_y + 258))

        self.menu_button.rect.y = card_y + 348
        self.menu_button.draw(self.screen, self.small_font)

    def draw_scoreboard(self):
        self.score_animation += 0.1
        pulse = int(5 * abs(math.sin(self.score_animation)))

        hud_bg = pg.Surface((280, 190), pg.SRCALPHA)
        hud_bg.fill((0, 0, 0, 180))
        pg.draw.rect(hud_bg, (255, 255, 255, 50 + pulse), (0, 0, 280, 190), 3, border_radius=10)

        for index in range(190):
            alpha = int(30 * (1 - index / 190))
            pg.draw.line(hud_bg, (50, 180, 80, alpha), (0, index), (280, index))

        self.screen.blit(hud_bg, (10, 10))

        score_color = (255, 255, 100 + pulse) if self.score > 0 else WHITE
        score_text = self.small_font.render(f"Score: {self.score}", True, score_color)
        self.screen.blit(score_text, (25, 25))

        stage_text = self.small_font.render(f"Stage: {self.stage}", True, CYAN)
        self.screen.blit(stage_text, (25, 55))

        speed_val = getattr(self, "display_speed", self.current_speed)
        speed_text = self.small_font.render(f"Speed: {speed_val:.1f} km/h", True, GREEN)
        self.screen.blit(speed_text, (25, 85))

        lives_label = self.small_font.render("Lives:", True, WHITE)
        self.screen.blit(lives_label, (25, 115))

        for i in range(self.lives):
            heart_x = 112 + i * 34
            heart_y = 126
            heart_points = []

            for angle in range(0, 360, 10):
                t = math.radians(angle)
                x = 16 * math.sin(t) ** 3
                y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))

                scale = 0.7
                heart_points.append((heart_x + int(x * scale), heart_y + int(y * scale)))

            pg.draw.polygon(self.screen, RED, heart_points)
            pg.draw.polygon(self.screen, WHITE, heart_points, 1)

        mode_text = self.tiny_font.render(f"Mode: {self.selected_difficulty}", True, YELLOW)
        self.screen.blit(mode_text, (25, 145))

        if self.score_multiplier > 1.0:
            multiplier_color = YELLOW if self.score_multiplier >= 2.0 else GREEN
            multiplier_text = self.tiny_font.render(f"Multiplier: x{self.score_multiplier:.1f}", True, multiplier_color)
            self.screen.blit(multiplier_text, (25, 165))

    def update_multiplier(self):
        self.multiplier_timer = pg.time.get_ticks()
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
        if self.multiplier_display_time > 0:
            current_time = pg.time.get_ticks()
            elapsed = current_time - self.multiplier_display_time
            if elapsed < 1000:
                alpha = int(255 * (1 - elapsed / 1000))
                if alpha > 0 and self.score_multiplier > 1.0:
                    y_offset = -elapsed // 10
                    x, y = self.multiplier_text_pos
                    y += y_offset
                    multiplier_str = f"x{self.score_multiplier:.1f}!"
                    color = YELLOW if self.score_multiplier >= 2.0 else GREEN

                    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                        glow_text = self.small_font.render(
                            multiplier_str,
                            True,
                            (color[0] // 3, color[1] // 3, color[2] // 3),
                        )
                        self.screen.blit(glow_text, (x - glow_text.get_width() // 2 + offset[0], y + offset[1]))

                    main_text = self.small_font.render(multiplier_str, True, color)
                    self.screen.blit(main_text, (x - main_text.get_width() // 2, y))
            else:
                self.multiplier_display_time = 0

    def draw_damage_feedback(self):
        if self.damage_flash_time > 0:
            current_time = pg.time.get_ticks()
            elapsed = current_time - self.damage_flash_time

            if elapsed < 600:
                alpha = int(120 * (1 - elapsed / 600))
                flash = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                flash.fill((255, 0, 0, alpha))
                self.screen.blit(flash, (0, 0))

                damage_text = self.font.render("DAMAGE!", True, RED)
                text_rect = damage_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
                self.screen.blit(damage_text, text_rect)
            else:
                self.damage_flash_time = 0

    def draw_pause_screen(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        box_width = 350
        box_height = 360
        box_left = WIDTH // 2 - box_width // 2
        box_top = HEIGHT // 2 - box_height // 2

        box = pg.Surface((box_width, box_height), pg.SRCALPHA)
        box.fill((20, 20, 30, 240))
        pg.draw.rect(box, (255, 255, 255, 50), (0, 0, box_width, box_height), 3, border_radius=15)
        self.screen.blit(box, (box_left, box_top))

        title_y = box_top + 28
        score_y = box_top + 92
        stage_y = box_top + 127
        restart_hint_y = box_top + 168
        resume_hint_y = box_top + 192
        menu_hint_y = box_top + 216

        title = self.font.render("PAUSED", True, YELLOW)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))

        score = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, score_y))

        stage = self.small_font.render(f"Stage: {self.stage}", True, WHITE)
        self.screen.blit(stage, (WIDTH // 2 - stage.get_width() // 2, stage_y))

        restart_text = self.tiny_font.render("Press R to restart", True, GRAY)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, restart_hint_y))

        resume_text = self.tiny_font.render("Press P or ESC to resume", True, GRAY)
        self.screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, resume_hint_y))

        menu_text = self.tiny_font.render("Click Main Menu to return", True, GRAY)
        self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, menu_hint_y))

        button_gap = 14
        buttons_height = self.restart_button.rect.height + button_gap + self.pause_menu_button.rect.height
        buttons_top = box_top + box_height - buttons_height - 22

        self.restart_button.rect.topleft = (WIDTH // 2 - self.restart_button.rect.width // 2, buttons_top)
        self.pause_menu_button.rect.topleft = (
            WIDTH // 2 - self.pause_menu_button.rect.width // 2,
            buttons_top + self.restart_button.rect.height + button_gap,
        )
        self.restart_button.draw(self.screen, self.small_font)
        self.pause_menu_button.draw(self.screen, self.tiny_font)

    def draw_game_over(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        box = pg.Surface((450, 380), pg.SRCALPHA)
        box.fill((20, 20, 30, 240))
        pg.draw.rect(box, (255, 0, 0, 80), (0, 0, 450, 380), 3, border_radius=15)
        self.screen.blit(box, (WIDTH // 2 - 225, HEIGHT // 2 - 190))

        title = self.font.render("GAME OVER", True, RED)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 170))

        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 120))

        stage = self.small_font.render(f"Reached Stage: {self.stage}", True, CYAN)
        self.screen.blit(stage, (WIDTH // 2 - stage.get_width() // 2, HEIGHT // 2 - 90))

        if self.score >= self.best_score:
            new_record = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, HEIGHT // 2 - 60))
        else:
            high_score_text = self.tiny_font.render(f"High Score: {self.best_score}", True, GRAY)
            self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - 55))

        button_y_start = HEIGHT // 2 - 20
        button_spacing = 60
        restart_button = Button(WIDTH // 2 - 100, button_y_start, 200, 45, "RESTART")
        restart_button.draw(self.screen, self.small_font)
        menu_button = Button(WIDTH // 2 - 100, button_y_start + button_spacing, 200, 45, "MAIN MENU")
        menu_button.draw(self.screen, self.small_font)
        quit_button = Button(WIDTH // 2 - 100, button_y_start + button_spacing * 2, 200, 45, "QUIT")
        quit_button.draw(self.screen, self.small_font)

        hint_text = self.tiny_font.render("Press R to restart | ESC for menu", True, GRAY)
        self.screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, button_y_start + button_spacing * 3 + 10))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
