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
    HAZARD_EFFECT_DURATIONS,
    HEIGHT,
    MENU_CARD_HEIGHT,
    MENU_CARD_WIDTH,
    NAVY,
    TRACK_OBJECT_WEIGHTS,
    PLAYER_START_LIVES,
    RED,
    SLATE,
    SURFACE,
    SURFACE_ALT,
    TEAL,
    WHITE,
    WIDTH,
    YELLOW,
    OBSTACLE_PASS_SCORE,
)
from .game_state import GameState
from .hazard import Hazard
from .music_utils import create_coin_sound, load_music
from .road import Road
from .storage import (
    load_save_data,
    read_high_score,
    update_progress,
    save_player_preferences,
)
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
        self.save_data = load_save_data()
        self.selected_skin = self.save_data.get("selected_skin", 0)
        self.selected_skin = max(0, min(self.selected_skin, len(CAR_SKINS) - 1))
        self.selected_difficulty = DEFAULT_DIFFICULTY

        if self.selected_difficulty not in DIFFICULTY_SETTINGS:
            self.selected_difficulty = DEFAULT_DIFFICULTY

        self.total_money = self.save_data.get("total_money", 0)
        self.best_stage = self.save_data.get("best_stage", DEFAULT_STAGE)
        self.games_played = self.save_data.get("games_played", 0)
        self.total_score = self.save_data.get("total_score", 0)
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
        self.next_stage_score = 3
        self.skid_end_time = 0
        self.skid_direction = 0
        self.skid_strength = 0.0
        self.water_slow_end_time = 0
        self.pothole_recovery_end_time = 0
        self.status_message = ""
        self.status_message_until = 0

        self.player = None
        self.obstacles = []
        self.coins = []
        self.road = None
        self.last_obstacle_time = 0
        self.last_coin_time = 0
        self.coin_frequency = 2000
        self.obstacle_frequency = DIFFICULTY_SETTINGS[self.selected_difficulty]["obstacle_freq"]
        
        self.best_score = self.save_data.get("high_score", read_high_score())
        self.session_money = 0
        self.is_new_high_score = False

        self.money_popup_amount = 0
        self.money_popup_start_time = 0

        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 60, "START RACE")
        self.high_score_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 45, "HIGH SCORES")
        self.menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 250, 200, 45, "MAIN MENU")
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 310, 200, 45, "EXIT")
        self.pause_button = Button(WIDTH - 120, 10, 100, 40, "PAUSE")
        self.restart_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 50, "RESTART")
        self.pause_menu_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 120, 160, 45, "MAIN MENU")
        self.game_over_restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 45, "RESTART")
        self.game_over_menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 45, "MAIN MENU")
        self.game_over_quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 45, "QUIT")
        self.sound_button = Button(WIDTH - 120, 55, 100, 35, "SOUND: ON")

        self.current_music = load_music()
        self.coin_sound = create_coin_sound()
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
        self.session_money = 0
        self.is_new_high_score = False

        self.money_popup_amount = 0
        self.money_popup_start_time = 0


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
        self.next_stage_score = 3
        self.clear_hazard_effects()
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
        previous_best_score = read_high_score()
        self.is_new_high_score = self.score > previous_best_score

        self.save_data = update_progress(
            score=self.score,
            stage=self.stage,
            money_earned=self.session_money,
        )

        self.best_score = self.save_data["high_score"]
        self.total_money = self.save_data["total_money"]
        self.best_stage = self.save_data["best_stage"]
        self.games_played = self.save_data["games_played"]
        self.total_score = self.save_data["total_score"]

        self.set_state(GameState.GAME_OVER)

    def save_preferences(self):
        self.save_data = save_player_preferences(
            self.selected_skin,
            self.selected_difficulty,
    )    

    def return_to_menu(self):
        self.save_preferences()
        self.save_data = load_save_data()
        self.best_score = self.save_data["high_score"]
        self.total_money = self.save_data["total_money"]
        self.best_stage = self.save_data["best_stage"]
        self.games_played = self.save_data["games_played"]
        self.total_score = self.save_data["total_score"]
        self.reset_game(change_state=False)
        self.set_state(GameState.MENU)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.save_preferences()
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
                self.save_preferences()
                self.reset_game(change_state=False)
                break

        left_arrow = layout["left_arrow"]
        right_arrow = layout["right_arrow"]
        if left_arrow.collidepoint(mouse_pos):
            self.selected_skin = (self.selected_skin - 1) % len(CAR_SKINS)
            self._sync_player_skin()
            self.save_preferences()
            self.reset_game(change_state=False)
        if right_arrow.collidepoint(mouse_pos):
            self.selected_skin = (self.selected_skin + 1) % len(CAR_SKINS)
            self._sync_player_skin()
            self.save_preferences()
            self.reset_game(change_state=False)

        if self.play_button.is_clicked(mouse_pos):
            self.start_game()
        if self.high_score_button.is_clicked(mouse_pos):
            self.open_high_scores()
        if self.exit_button.is_clicked(mouse_pos):
            self.save_preferences()
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
        self.sync_game_over_button_rects()

        if self.game_over_restart_button.is_clicked(mouse_pos):
            self.reset_game()
        if self.game_over_menu_button.is_clicked(mouse_pos):
            self.return_to_menu()
        if self.game_over_quit_button.is_clicked(mouse_pos):
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

    def clear_hazard_effects(self):
        self.skid_end_time = 0
        self.skid_direction = 0
        self.skid_strength = 0.0
        self.water_slow_end_time = 0
        self.pothole_recovery_end_time = 0
        self.status_message = ""
        self.status_message_until = 0

    def get_player_speed_fraction(self):
        try:
            vel = float(self.player.get_velocity())
            frac = (vel - const.MIN_SPEED) / max(1.0, (const.MAX_SPEED - const.MIN_SPEED))
            return max(0.0, min(1.0, frac))
        except Exception:
            return 0.0

    def get_player_collision_rect(self):
        frac = self.get_player_speed_fraction()
        player_collision_y = int(self.player.y - frac * max(0, (self.player.y - HEIGHT // 2)))
        return pg.Rect(self.player.x, player_collision_y, self.player.width, self.player.height)

    def get_obstacle_rect(self, obstacle):
        if hasattr(obstacle, "get_collision_rect"):
            return obstacle.get_collision_rect()
        return pg.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)

    def can_spawn_obstacle(self, new_obstacle):
        new_rect = self.get_obstacle_rect(new_obstacle)
        spacing = DIFFICULTY_SETTINGS[self.selected_difficulty].get("spawn_spacing", 140)
        for existing_obstacle in self.obstacles:
            existing_rect = self.get_obstacle_rect(existing_obstacle)
            vertical_gap = max(existing_obstacle.height, new_obstacle.height) + spacing
            if abs(existing_obstacle.y - new_obstacle.y) < vertical_gap:
                if existing_rect.inflate(22, 32).colliderect(new_rect):
                    return False
        return True

    def create_track_obstacle(self, diff_settings):
        track_weights = TRACK_OBJECT_WEIGHTS[self.selected_difficulty]
        obstacle_kind = random.choices(
            list(track_weights.keys()),
            weights=list(track_weights.values()),
            k=1,
        )[0]
        lane = random.randint(0, 2)
        lane_ratio = (lane + 0.5) / 3
        min_speed, max_speed = diff_settings["obstacle_speed"]

        if obstacle_kind == "car":
            color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
            obstacle = Car(0, -150, color)
            obstacle.kind = "car"
            obstacle.label = "Traffic Car"
            obstacle.damage_on_hit = True
            obstacle.remove_on_hit = True
            obstacle.shadow = True
            obstacle.speed = random.randint(min_speed, max_speed)
        else:
            hazard_speed = random.randint(max(5, min_speed - 2), max(7, max_speed - 2))
            spawn_y = -165 if obstacle_kind == "barrier" else -125
            obstacle = Hazard(0, spawn_y, obstacle_kind, hazard_speed)

        obstacle.road_ratio = lane_ratio
        obstacle.x = self.road.get_travel_x(0, lane_ratio, obstacle.width)
        return obstacle

    def register_status_message(self, message, current_time, duration=1200):
        self.status_message = message
        self.status_message_until = current_time + duration

    def update_player_handling(self, current_time, dt):
        speed_val = getattr(self.player, "velocity", const.PLAYER_SPEED_DEFAULT)
        base_lateral_speed = max(5, int(6 + speed_val / 12))
        control_factor = 1.0

        if current_time < self.water_slow_end_time:
            control_factor *= 0.72
        if current_time < self.pothole_recovery_end_time:
            control_factor *= 0.84

        self.player.speed = max(4, int(base_lateral_speed * control_factor))

        if current_time < self.skid_end_time and self.skid_strength > 0:
            self.player.x += int(self.skid_direction * self.skid_strength * dt)
            self.skid_strength = max(0.0, self.skid_strength - 120 * dt)

    def update_stage_progression(self):
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        while self.score >= self.next_stage_score:
            self.level += 1
            self.stage = self.level
            self.obstacle_frequency = max(diff_settings.get("freq_floor", 600), self.obstacle_frequency - diff_settings.get("freq_step", 100))
            self.current_speed = min(self.base_speed * 2.5, self.current_speed + diff_settings["speed_increase"] * 10)
            self.next_stage_score += 3

    def apply_hazard_effect(self, obstacle, current_time):
        self.consecutive_actions = 0
        self.update_multiplier()

        if obstacle.kind == "oil_spill":
            self.skid_end_time = current_time + HAZARD_EFFECT_DURATIONS["oil_spill"]
            self.skid_direction = random.choice([-1, 1])
            self.skid_strength = max(160.0, getattr(self.player, "velocity", const.MIN_SPEED) * 1.9)
            self.player.velocity = max(const.MIN_SPEED, self.player.velocity - 4)
            self.register_status_message("Oil spill: steering drift", current_time)
        elif obstacle.kind == "water_puddle":
            self.water_slow_end_time = current_time + HAZARD_EFFECT_DURATIONS["water_puddle"]
            self.player.velocity = max(const.MIN_SPEED, self.player.velocity - 10)
            self.register_status_message("Water puddle: traction reduced", current_time)
        elif obstacle.kind == "pothole":
            self.pothole_recovery_end_time = current_time + HAZARD_EFFECT_DURATIONS["pothole"]
            self.player.velocity = max(const.MIN_SPEED, self.player.velocity - 14)
            self.register_status_message("Pothole: suspension hit", current_time)

    def get_active_hazard_statuses(self, current_time):
        statuses = []
        if current_time < self.skid_end_time:
            statuses.append(("Oil drift active", (210, 210, 220)))
        if current_time < self.water_slow_end_time:
            statuses.append(("Water slow active", (96, 176, 240)))
        if current_time < self.pothole_recovery_end_time:
            statuses.append(("Pothole recovery", (196, 142, 110)))
        return statuses

    def draw_status_banner(self):
        current_time = pg.time.get_ticks()
        if current_time >= self.status_message_until or not self.status_message:
            return

        banner_text = self.tiny_font.render(self.status_message, True, WHITE)
        banner_width = banner_text.get_width() + 28
        banner = pg.Surface((banner_width, 34), pg.SRCALPHA)
        banner.fill((12, 18, 28, 210))
        pg.draw.rect(banner, (255, 255, 255, 45), (0, 0, banner_width, 34), 1, border_radius=12)
        banner.blit(banner_text, (14, 8))
        self.screen.blit(banner, (WIDTH // 2 - banner_width // 2, HEIGHT - 54))

    def update(self):
        if self.state != GameState.PLAYING or self.paused:
            return

        current_time = pg.time.get_ticks()
        self.road.update()
        self.update_player_bounds()

        dt = max(1 / FPS, self.clock.get_time() / 1000.0)
        self.update_player_handling(current_time, dt)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.player.move("left")
        if keys[pg.K_RIGHT]:
            self.player.move("right")
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

        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        speed_factor = max(self.current_speed / BASE_SPEED, 1)

        if current_time - self.last_obstacle_time > self.obstacle_frequency / speed_factor:
            new_obstacle = self.create_track_obstacle(diff_settings)
            if self.can_spawn_obstacle(new_obstacle):
                self.obstacles.append(new_obstacle)
                self.last_obstacle_time = current_time

        player_rect = self.get_player_collision_rect()
        for obstacle in self.obstacles[:]:
            if obstacle.move():
                self.obstacles.remove(obstacle)
                self.consecutive_actions += 1
                self.update_multiplier()
                self.score += int(OBSTACLE_PASS_SCORE * self.score_multiplier)
                self.update_stage_progression()
                continue
            self.align_obstacle_to_road(obstacle)

            if player_rect.colliderect(self.get_obstacle_rect(obstacle)):
                if isinstance(obstacle, Hazard) and not obstacle.damage_on_hit:
                    self.apply_hazard_effect(obstacle, current_time)
                    if obstacle in self.obstacles and obstacle.remove_on_hit:
                        self.obstacles.remove(obstacle)
                    continue

                if current_time - self.last_damage_time > DAMAGE_COOLDOWN:
                    self.consecutive_actions = 0
                    self.update_multiplier()
                    self.lives -= 1
                    self.last_damage_time = current_time
                    self.damage_flash_time = current_time
                    if isinstance(obstacle, Hazard) and obstacle.kind == "barrier":
                        self.register_status_message("Barrier impact: heavy damage", current_time)
                    else:
                        self.register_status_message("Collision: avoid traffic", current_time)
                    if obstacle in self.obstacles and getattr(obstacle, "remove_on_hit", True):
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
                if self.coin_sound and not self.music_muted:
                    self.coin_sound.play()
                self.consecutive_actions += 1
                self.update_multiplier()

                self.score += int(coin.score_value * self.score_multiplier)
                self.session_money += coin.money_value

                self.money_popup_amount = coin.money_value
                self.money_popup_start_time = pg.time.get_ticks()

                self.multiplier_display_time = pg.time.get_ticks()
                self.multiplier_text_pos = (coin.x, coin.y)
                self.update_stage_progression()

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
            for obstacle in self.obstacles:
                if getattr(obstacle, "shadow", True):
                    shadow = pg.Surface((obstacle.width, max(10, obstacle.height // 3)), pg.SRCALPHA)
                    shadow.fill((0, 0, 0, 80))
                    self.screen.blit(shadow, (obstacle.x, obstacle.y + obstacle.height - 10))
                obstacle.draw(self.screen)

            for coin in self.coins:
                coin.draw(self.screen)

            self.draw_scoreboard()
            self.draw_status_banner()
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

    def sync_game_over_button_rects(self):
        button_y_start = HEIGHT // 2 - 20
        button_spacing = 60
        button_size = (200, 45)

        self.game_over_restart_button.rect.topleft = (WIDTH // 2 - 100, button_y_start)
        self.game_over_restart_button.rect.size = button_size
        self.game_over_menu_button.rect.topleft = (WIDTH // 2 - 100, button_y_start + button_spacing)
        self.game_over_menu_button.rect.size = button_size
        self.game_over_quit_button.rect.topleft = (WIDTH // 2 - 100, button_y_start + button_spacing * 2)
        self.game_over_quit_button.rect.size = button_size

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
        self.save_data = load_save_data()
        self.best_score = self.save_data["high_score"]
        self.total_money = self.save_data["total_money"]
        self.best_stage = self.save_data["best_stage"]
        self.games_played = self.save_data["games_played"]
        self.total_score = self.save_data["total_score"]

        card_x, card_y = self.draw_menu_shell("HIGH SCORES", "Saved player progress and race statistics.")

        score_panel = pg.Surface((MENU_CARD_WIDTH - 110, 230), pg.SRCALPHA)
        score_panel.fill((SLATE[0], SLATE[1], SLATE[2], 220))
        pg.draw.rect(score_panel, (255, 255, 255, 30), (0, 0, MENU_CARD_WIDTH - 110, 230), 2, border_radius=18)
        self.screen.blit(score_panel, (card_x + 55, card_y + 115))

        progress_items = [
            ("Best Score", self.best_score),
            ("Total Money", self.total_money),
            ("Best Stage", self.best_stage),
            ("Games Played", self.games_played),
            ("Total Score", self.total_score),
        ]

        start_y = card_y + 145
        for index, (label, value) in enumerate(progress_items):
            y = start_y + index * 36
            label_text = self.small_font.render(f"{label}:", True, GOLD)
            value_text = self.small_font.render(str(value), True, WHITE)

            self.screen.blit(label_text, (card_x + 105, y))
            self.screen.blit(value_text, (card_x + MENU_CARD_WIDTH - 190, y))

        #note = self.tiny_font.render("Progress is loaded from local save_data.json.", True, (205, 215, 225))
        #self.screen.blit(note, (WIDTH // 2 - note.get_width() // 2, card_y + 360))

        self.menu_button.rect.y = card_y + 370
        self.menu_button.draw(self.screen, self.small_font)

    def draw_scoreboard(self):
        self.score_animation += 0.1
        pulse = int(5 * abs(math.sin(self.score_animation)))

        hud_width = 236
        hud_height = 394
        hud_bg = pg.Surface((hud_width, hud_height), pg.SRCALPHA)
        hud_bg.fill((10, 14, 22, 208))
        pg.draw.rect(hud_bg, (255, 255, 255, 50 + pulse), (0, 0, hud_width, hud_height), 3, border_radius=14)

        for index in range(hud_height):
            alpha = int(30 * (1 - index / hud_height))
            pg.draw.line(hud_bg, (38, 164, 184, alpha), (0, index), (hud_width, index))

        self.screen.blit(hud_bg, (10, 10))

        score_color = (255, 255, 100 + pulse) if self.score > 0 else WHITE
        score_text = self.small_font.render(f"Score: {self.score}", True, score_color)
        self.screen.blit(score_text, (24, 24))

        stage_text = self.small_font.render(f"Stage: {self.stage}", True, CYAN)
        self.screen.blit(stage_text, (24, 52))

        speed_val = getattr(self, "display_speed", self.current_speed)
        speed_text = self.small_font.render(f"Speed: {speed_val:.1f} km/h", True, GREEN)
        self.screen.blit(speed_text, (24, 80))

        lives_label = self.small_font.render("Lives:", True, WHITE)
        self.screen.blit(lives_label, (24, 108))

        for i in range(self.lives):
            heart_x = 108 + i * 30
            heart_y = 118
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
        self.screen.blit(mode_text, (24, 142))

        display_money = self.total_money

        if self.state != GameState.GAME_OVER:
            display_money += self.session_money



        money_text = self.tiny_font.render(
            f"Money: {display_money}",
            True,
            GOLD,
        )
        self.screen.blit(money_text, (24, 160))

        popup_age = pg.time.get_ticks() - self.money_popup_start_time
        popup_duration = 950

        if self.money_popup_amount > 0 and popup_age < popup_duration:
            progress = popup_age / popup_duration
            popup_y = 158 - int(progress * 20)
            popup_alpha = max(0, 255 - int(progress * 220))

            popup_text = self.small_font.render(
                f"+{self.money_popup_amount}",
                True,
                GOLD,
            )

            popup_padding_x = 8
            popup_padding_y = 3

            popup_surface = pg.Surface(
                (
                    popup_text.get_width() + popup_padding_x * 2,
                    popup_text.get_height() + popup_padding_y * 2,
                ),
                pg.SRCALPHA,
            )

            bg_color = (20, 20, 20, popup_alpha)
            border_color = (240, 220, 50, popup_alpha)

            pg.draw.rect(
                popup_surface,
                bg_color,
                popup_surface.get_rect(),
                border_radius=10,
            )

            pg.draw.rect(
                popup_surface,
                border_color,
                popup_surface.get_rect(),
                2,
                border_radius=10,
            )

            popup_surface.blit(
                popup_text,
                (popup_padding_x, popup_padding_y),
            )

            popup_surface.set_alpha(popup_alpha)

            self.screen.blit(popup_surface, (136, popup_y))

        if self.score_multiplier > 1.0:
            multiplier_color = YELLOW if self.score_multiplier >= 2.0 else GREEN
            multiplier_text = self.tiny_font.render(f"Multiplier: x{self.score_multiplier:.1f}", True, multiplier_color)
            self.screen.blit(multiplier_text, (24, 182))

        section_title = self.tiny_font.render("Track Watch", True, WHITE)
        self.screen.blit(section_title, (24, 204))

        legend_items = [
            ("Oil", "drift", (210, 210, 220)),
            ("Water", "slow", (96, 176, 240)),
            ("Pothole", "drop", (196, 142, 110)),
            ("Barrier", "hit", (232, 98, 32)),
        ]
        for index, (label, effect, color) in enumerate(legend_items):
            card_x = 24
            card_y = 226 + index * 22
            card = pg.Surface((188, 20), pg.SRCALPHA)
            card.fill((255, 255, 255, 12))
            pg.draw.rect(card, (*color, 92), (0, 0, 188, 20), 1, border_radius=8)
            pg.draw.circle(card, color, (10, 10), 4)
            label_text = self.tiny_font.render(label, True, WHITE)
            effect_text = self.tiny_font.render(effect, True, color)
            card.blit(label_text, (18, 2))
            card.blit(effect_text, (18 + label_text.get_width() + 6, 2))
            self.screen.blit(card, (card_x, card_y))

        active_statuses = self.get_active_hazard_statuses(pg.time.get_ticks())
        status_title = self.tiny_font.render("Active", True, YELLOW)
        self.screen.blit(status_title, (24, 318))
        if active_statuses:
            for index, (label, color) in enumerate(active_statuses[:3]):
                badge = pg.Surface((188, 18), pg.SRCALPHA)
                badge.fill((255, 255, 255, 10))
                pg.draw.rect(badge, (*color, 90), (0, 0, 188, 18), 1, border_radius=8)
                status_text = self.tiny_font.render(label, True, color)
                badge.blit(status_text, (8, 2))
                self.screen.blit(badge, (24, 340 + index * 16))
        else:
            badge = pg.Surface((188, 18), pg.SRCALPHA)
            badge.fill((255, 255, 255, 10))
            pg.draw.rect(badge, (*GREEN, 90), (0, 0, 188, 18), 1, border_radius=8)
            status_text = self.tiny_font.render("Road stable", True, GREEN)
            badge.blit(status_text, (8, 2))
            self.screen.blit(badge, (24, 340))

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
        self.sync_game_over_button_rects()

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

        money = self.small_font.render(f"Money Earned: +{self.session_money}", True, GOLD)
        self.screen.blit(money, (WIDTH // 2 - money.get_width() // 2, HEIGHT // 2 - 65))

        """if self.score >= self.best_score:
            new_record = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, HEIGHT // 2 - 35))
        else:
            high_score_text = self.tiny_font.render(f"High Score: {self.best_score}", True, GRAY)
            self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - 32))"""

        if self.is_new_high_score:
            badge_text = self.tiny_font.render("NEW HIGH SCORE!", True, (10, 10, 10))

            badge_padding_x = 14
            badge_padding_y = 8
            badge_width = badge_text.get_width() + badge_padding_x * 2
            badge_height = badge_text.get_height() + badge_padding_y * 2

            badge_x = WIDTH // 2 + 145
            badge_y = HEIGHT // 2 - 190

            badge_rect = pg.Rect(badge_x, badge_y, badge_width, badge_height)

            pg.draw.rect(self.screen, YELLOW, badge_rect, border_radius=14)
            pg.draw.rect(self.screen, WHITE, badge_rect, 2, border_radius=14)

            self.screen.blit(
                badge_text,
                (
                    badge_rect.centerx - badge_text.get_width() // 2,
                    badge_rect.centery - badge_text.get_height() // 2,
                ),
            )
        else:
            high_score_text = self.tiny_font.render(f"High Score: {self.best_score}", True, GRAY)
            self.screen.blit(
                high_score_text,
                (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - 35),
            )

        self.game_over_restart_button.draw(self.screen, self.small_font)
        self.game_over_menu_button.draw(self.screen, self.small_font)
        self.game_over_quit_button.draw(self.screen, self.small_font)

        button_y_start = self.game_over_restart_button.rect.y
        button_spacing = 60
        hint_text = self.tiny_font.render("Press R to restart | ESC for menu", True, GRAY)
        self.screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, button_y_start + button_spacing * 3 + 10))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
