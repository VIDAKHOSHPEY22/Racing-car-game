import os
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
    COIN_MAX_ACTIVE,
    COIN_CHAIN_LENGTH,
    COIN_CHAIN_VERTICAL_SPACING,
    COIN_RADIUS,
    COIN_CHAIN_SPAWN_BASE_CHANCE,
    COIN_CHAIN_SPAWN_STAGE_STEP,
    COIN_CHAIN_SPAWN_MAX_CHANCE,
    COIN_RED_SPAWN_BASE_CHANCE,
    COIN_RED_SPAWN_STAGE_STEP,
    COIN_RED_SPAWN_MAX_CHANCE,
    COIN_SPAWN_BASE_INTERVAL,
    COIN_SPAWN_MIN_INTERVAL,
    COIN_SPAWN_STAGE_STEP,
    ECONOMY_DISTANCE_REWARD_MONEY,
    ECONOMY_DISTANCE_REWARD_STEP,
    ECONOMY_STAGE_REWARD_MONEY,
    COLLISION_MONEY_PENALTY_BASE,
    COLLISION_MONEY_PENALTY_STAGE_STEP,
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
    NITRO_BOOST_ACCEL,
    NITRO_COOLDOWN_MS,
    NITRO_DRAIN_PER_SECOND,
    NITRO_MAX_CHARGE,
    NITRO_MAX_SPEED_BONUS,
    NITRO_MIN_ACTIVATION,
    NITRO_SPAWN_INTERVAL,
    NITRO_WORLD_SPEED_MULTIPLIER,
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
<<<<<<< HEAD
=======
from .constants import STAGE_DEFINITIONS
from .game_state import GameState
from .nitro import NitroPickup
# FinishLine moved here from game/finish_line.py to keep repository structure flat.
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
class FinishLine:
    def __init__(self, road, stage_id, speed):
        self.road = road
        self.stage_id = stage_id
        self.width = 180
        self.height = 96
        self.speed = max(6, int(speed))
        self.y = -self.height - 24
        self.road_ratio = 0.5
        self.x = self.road.get_travel_x(self.y + self.height // 2, self.road_ratio, self.width)

    def move(self, speed_multiplier=1.0):
        self.y += self.speed * speed_multiplier
        self.x = self.road.get_travel_x(self.y + self.height // 2, self.road_ratio, self.width)
        return self.y > HEIGHT + self.height

    def get_collision_rect(self):
        return pg.Rect(self.x + 10, self.y + 8, self.width - 20, self.height - 12)

    def draw(self, screen):
        # Respect global visibility toggle in constants; collision remains active.
        try:
            if not const.SHOW_FINISH_SIGN:
                return
        except Exception:
            pass

        pole_color = (88, 88, 94)
        accent_color = (255, 245, 225)
        flag_color = RED if self.stage_id % 2 == 0 else YELLOW

        shadow = pg.Surface((self.width + 24, self.height + 18), pg.SRCALPHA)
        pg.draw.ellipse(shadow, (0, 0, 0, 55), (6, self.height - 6, self.width, 12))
        screen.blit(shadow, (self.x - 12, self.y - 2))

        for pole_x in (self.x + 14, self.x + self.width - 20):
            pg.draw.rect(screen, pole_color, (pole_x, self.y + 8, 8, self.height - 4), border_radius=3)
            pg.draw.circle(screen, (135, 135, 142), (pole_x + 4, self.y + self.height - 4), 4)

        banner_rect = pg.Rect(self.x + 12, self.y + 10, self.width - 24, 26)
        pg.draw.rect(screen, (22, 22, 26), banner_rect, border_radius=10)
        pg.draw.rect(screen, accent_color, banner_rect, 2, border_radius=10)

        for idx in range(8):
            stripe_x = banner_rect.x + 6 + idx * 20
            stripe_rect = pg.Rect(stripe_x, banner_rect.y + 4, 12, banner_rect.height - 8)
            pg.draw.rect(screen, flag_color, stripe_rect, border_radius=3)
            pg.draw.line(screen, WHITE, stripe_rect.topleft, stripe_rect.bottomright, 1)

        text = pg.font.Font(None, 34).render("FINISH", True, WHITE)
        screen.blit(text, text.get_rect(center=banner_rect.center))

        tag = pg.font.Font(None, 24).render(f"Level {self.stage_id}", True, accent_color)
        screen.blit(tag, tag.get_rect(center=(self.x + self.width // 2, self.y + 58)))
from .hazard import Hazard
from .music_utils import create_coin_sound, load_music
from .road import Road
from .storage import (
    buy_skin,
    load_save_data,
    read_high_score,
    select_skin,
    update_progress,
    save_player_preferences,
)
from . import constants as const
<<<<<<< HEAD
from .game_state import GameState

=======
from .weather import WeatherManager
>>>>>>> 3df94ff (Add dynamic weather system with visual and driving effects)

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
        self.selected_difficulty = self.save_data.get("selected_difficulty", DEFAULT_DIFFICULTY)

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
        self.distance = 0.0
        # distance progressed within current stage (separate from total runtime distance)
        self.stage_progress_distance = 0.0
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
        self.stage_coin_count = 0
        self.stage_coin_money = 0
        self.stage_distance_reward_money = 0
        self.stage_reward_money = 0
        self.stage_collision_penalty_money = 0
        self.next_distance_reward_at = ECONOMY_DISTANCE_REWARD_STEP
        self.skid_end_time = 0
        self.skid_direction = 0
        self.skid_strength = 0.0
        self.water_slow_end_time = 0
        self.pothole_recovery_end_time = 0
        self.status_message = ""
        self.status_message_until = 0
        self.finish_sign = None
        self.completed_stage = None
        self.weather = WeatherManager()

        # Level transition / map animation state
        self.level_transition_start = None
        self.level_transition_duration = 1400  # ms for marker to travel between nodes
        self.level_transition_pause = 600  # ms pause after animation

        self.player = None
        self.obstacles = []
        self.coins = []
        self.nitro_pickups = []
        self.road = None
        self.last_obstacle_time = 0
        self.last_coin_time = 0
        self.last_nitro_time = 0
        self.coin_frequency = 2000
        self.max_active_coins = COIN_MAX_ACTIVE.get(self.selected_difficulty, 2)
        self.obstacle_frequency = DIFFICULTY_SETTINGS[self.selected_difficulty]["obstacle_freq"]
        self.nitro_charge = 0.0
        self.nitro_active = False
        self.nitro_cooldown_until = 0
        self.boost_pressed_last_frame = False
        
        self.best_score = self.save_data.get("high_score", read_high_score())
        self.current_level_money = 0
        self.is_new_high_score = False

        self.money_popup_amount = 0
        self.money_popup_start_time = 0

        self.play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 60, "START RACE")
        self.garage_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 45, "GARAGE")
        self.high_score_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 190, 200, 45, "HIGH SCORES")
        self.menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 250, 200, 45, "MAIN MENU")
        self.garage_buy_button = Button(WIDTH // 2 - 110, HEIGHT // 2 + 125, 220, 45, "BUY")
        self.garage_select_button = Button(WIDTH // 2 - 110, HEIGHT // 2 + 125, 220, 45, "SELECT")
        self.garage_back_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 185, 200, 45, "BACK")
        self.garage_index = self.selected_skin
        self.garage_message = ""
        self.garage_message_until = 0
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 310, 200, 45, "EXIT")
        self.pause_button = Button(WIDTH - 120, 10, 100, 40, "PAUSE")
        self.restart_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 50, "RESTART")
        self.pause_menu_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 120, 160, 45, "MAIN MENU")
        self.game_over_restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 45, "RESTART")
        self.game_over_menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 45, "MAIN MENU")
        self.game_over_quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 160, 200, 45, "QUIT")
        self.sound_button = Button(WIDTH - 120, 55, 100, 35, "SOUND: ON")

        self.current_music = load_music()
        self.coin_sound = create_coin_sound()
        if self.current_music:
            pg.mixer.music.play(-1)

        self.reset_game(change_state=False)

        # load initial stage config
        self.load_stage_config(self.stage)

    def set_state(self, state):
        self.state = state

    def _sync_player_skin(self):
        self.player_color = CAR_SKINS[self.selected_skin]["color"]
        self.player_type = CAR_SKINS[self.selected_skin]["type"]

    def _get_selected_skin_stats(self):
        skin = CAR_SKINS[self.selected_skin]
        return {
            "speed_bonus": float(skin.get("speed_bonus", 0)),
            "handling_bonus": float(skin.get("handling_bonus", 0)),
        }

    def _apply_vehicle_starting_stats(self):
        if self.player is None:
            return

        stats = self._get_selected_skin_stats()

        if hasattr(self.player, "velocity"):
            self.player.velocity = float(const.PLAYER_SPEED_DEFAULT + stats["speed_bonus"])

    def _get_unlocked_skin_indices(self):
        unlocked = self.save_data.get("unlocked_skins", [0])
        valid_indices = []

        for index in unlocked:
            try:
                index = int(index)
            except (TypeError, ValueError):
                continue

            if 0 <= index < len(CAR_SKINS) and index not in valid_indices:
                valid_indices.append(index)

        if 0 not in valid_indices:
            valid_indices.insert(0, 0)

        return valid_indices or [0]

    def _refresh_profile_from_save(self):
        self.save_data = load_save_data()
        self.selected_skin = self.save_data.get("selected_skin", 0)
        self.selected_skin = max(0, min(self.selected_skin, len(CAR_SKINS) - 1))
        self.selected_difficulty = self.save_data.get("selected_difficulty", DEFAULT_DIFFICULTY)

        if self.selected_difficulty not in DIFFICULTY_SETTINGS:
            self.selected_difficulty = DEFAULT_DIFFICULTY

        self.total_money = self.save_data.get("total_money", 0)
        self.best_stage = self.save_data.get("best_stage", DEFAULT_STAGE)
        self.games_played = self.save_data.get("games_played", 0)
        self.total_score = self.save_data.get("total_score", 0)
<<<<<<< HEAD
=======
        self._sync_player_skin()

    def _cycle_unlocked_skin(self, direction):
        unlocked = self._get_unlocked_skin_indices()

        if self.selected_skin not in unlocked:
            self.selected_skin = unlocked[0]

        current_pos = unlocked.index(self.selected_skin)
        self.selected_skin = unlocked[(current_pos + direction) % len(unlocked)]

        self._sync_player_skin()
        self.save_preferences()
        self.reset_game(change_state=False)

    def register_garage_message(self, message, duration=1600):
        self.garage_message = message
        self.garage_message_until = pg.time.get_ticks() + duration

    def reset_game(self, change_state=True):
<<<<<<< HEAD
>>>>>>> e19a521 (Add garage vehicle progression system)
=======
        previous_state = self.state
        was_paused = self.paused
>>>>>>> 5b18a38 (Add weather system updates and fix restart/HUD issues)
        self._sync_player_skin()

    def _cycle_unlocked_skin(self, direction):
        unlocked = self._get_unlocked_skin_indices()

        if self.selected_skin not in unlocked:
            self.selected_skin = unlocked[0]

        current_pos = unlocked.index(self.selected_skin)
        self.selected_skin = unlocked[(current_pos + direction) % len(unlocked)]

        self._sync_player_skin()
        self.save_preferences()
        self.reset_game(change_state=False)

    def register_garage_message(self, message, duration=1600):
        self.garage_message = message
        self.garage_message_until = pg.time.get_ticks() + duration

    def get_checkpoint_stage(self):
        try:
            checkpoint_stage = int(self.stage)
        except (TypeError, ValueError):
            checkpoint_stage = DEFAULT_STAGE
        return max(DEFAULT_STAGE, checkpoint_stage)

    def has_checkpoint(self):
        return self.get_checkpoint_stage() > DEFAULT_STAGE

    def calculate_stage_rewards(self, stage_id):
        stage_id = max(1, int(stage_id))
        score_bonus = const.STAGE_CLEAR_SCORE_BONUS + stage_id * const.STAGE_LEVEL_SCORE_MULTIPLIER
        money_bonus = ECONOMY_STAGE_REWARD_MONEY
        return int(score_bonus), int(money_bonus)

    def reset_game(self, change_state=True, start_stage=None):
        previous_state = self.state
        was_paused = self.paused
    def _get_selected_skin_stats(self):
        skin = CAR_SKINS[self.selected_skin]
        return {
            "speed_bonus": float(skin.get("speed_bonus", 0)),
            "handling_bonus": float(skin.get("handling_bonus", 0)),
        }

    def _apply_vehicle_starting_stats(self):
        if self.player is None:
            return

        stats = self._get_selected_skin_stats()

        if hasattr(self.player, "velocity"):
            self.player.velocity = float(const.PLAYER_SPEED_DEFAULT + stats["speed_bonus"])

    def _get_unlocked_skin_indices(self):
        unlocked = self.save_data.get("unlocked_skins", [0])
        valid_indices = []

        for index in unlocked:
            try:
                index = int(index)
            except (TypeError, ValueError):
                continue

            if 0 <= index < len(CAR_SKINS) and index not in valid_indices:
                valid_indices.append(index)

        if 0 not in valid_indices:
            valid_indices.insert(0, 0)

        return valid_indices or [0]

    def _refresh_profile_from_save(self):
        self.save_data = load_save_data()
        self.selected_skin = self.save_data.get("selected_skin", 0)
        self.selected_skin = max(0, min(self.selected_skin, len(CAR_SKINS) - 1))
        self.selected_difficulty = self.save_data.get("selected_difficulty", DEFAULT_DIFFICULTY)

        if self.selected_difficulty not in DIFFICULTY_SETTINGS:
            self.selected_difficulty = DEFAULT_DIFFICULTY

        self.total_money = self.save_data.get("total_money", 0)
        self.best_stage = self.save_data.get("best_stage", DEFAULT_STAGE)
        self.games_played = self.save_data.get("games_played", 0)
        self.total_score = self.save_data.get("total_score", 0)
        self._sync_player_skin()

    def _cycle_unlocked_skin(self, direction):
        unlocked = self._get_unlocked_skin_indices()

        if self.selected_skin not in unlocked:
            self.selected_skin = unlocked[0]

        current_pos = unlocked.index(self.selected_skin)
        self.selected_skin = unlocked[(current_pos + direction) % len(unlocked)]

        self._sync_player_skin()
        self.save_preferences()
        self.reset_game(change_state=False)

    def register_garage_message(self, message, duration=1600):
        self.garage_message = message
        self.garage_message_until = pg.time.get_ticks() + duration

    def get_checkpoint_stage(self):
        try:
            checkpoint_stage = int(self.stage)
        except (TypeError, ValueError):
            checkpoint_stage = DEFAULT_STAGE
        return max(DEFAULT_STAGE, checkpoint_stage)

    def has_checkpoint(self):
        return self.get_checkpoint_stage() > DEFAULT_STAGE

    def calculate_stage_rewards(self, stage_id):
        stage_id = max(1, int(stage_id))
        score_bonus = const.STAGE_CLEAR_SCORE_BONUS + stage_id * const.STAGE_LEVEL_SCORE_MULTIPLIER
        money_bonus = ECONOMY_STAGE_REWARD_MONEY
        return int(score_bonus), int(money_bonus)

    def reset_game(self, change_state=True, start_stage=None):
        previous_state = self.state
        was_paused = self.paused
        self._sync_player_skin()
        if previous_state == GameState.GAME_OVER:
            self._restore_money_after_game_over()
        self.player = Car(WIDTH // 2 - 25, HEIGHT - 150, self.player_color, True, self.player_type)
        self.obstacles = []
        self.coins = []
        self.nitro_pickups = []
<<<<<<< HEAD

        # Determine starting stage:
        # - If an explicit `start_stage` is provided, use it.
        # - If not provided and we're resetting from GAME_OVER, resume from the
        #   current `self.stage` so the player continues from the same level.
        # - Otherwise fall back to DEFAULT_STAGE.
        if start_stage is not None:
            try:
                starting_stage = int(start_stage)
            except (TypeError, ValueError):
                starting_stage = DEFAULT_STAGE
        else:
            if previous_state == GameState.GAME_OVER:
                try:
                    starting_stage = int(getattr(self, "stage", DEFAULT_STAGE))
                except (TypeError, ValueError):
                    starting_stage = DEFAULT_STAGE
            else:
                starting_stage = DEFAULT_STAGE

        starting_stage = max(DEFAULT_STAGE, starting_stage)

        self.stage = starting_stage
        self.level = starting_stage

        self._apply_level_one_wallet_floor(previous_state)
=======
        self.stage = DEFAULT_STAGE
        self.level = DEFAULT_STAGE
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
        self.score = 0
        self.current_level_money = 0
        self.is_new_high_score = False

        self.money_popup_amount = 0
        self.money_popup_start_time = 0


        self.lives = PLAYER_START_LIVES
        self.last_damage_time = 0
        self.damage_flash_time = 0
        self.distance = 0.0
        self.last_obstacle_time = pg.time.get_ticks()
        self.last_coin_time = pg.time.get_ticks()
        self.last_nitro_time = pg.time.get_ticks()

        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        self.base_speed = diff_settings["base_speed"]
        # apply difficulty-specific max speed at runtime so `Car.accelerate` clamps correctly
        try:
            import game.constants as const

            vehicle_stats = self._get_selected_skin_stats()
            const.MAX_SPEED = float(diff_settings.get("max_speed", const.MAX_SPEED)) + vehicle_stats["speed_bonus"]
        except Exception:
            pass
        self.current_speed = self.base_speed
        # ensure player's internal velocity starts with the selected vehicle speed bonus
        try:
            self._apply_vehicle_starting_stats()
        except Exception:
            pass
        self.obstacle_frequency = diff_settings["obstacle_freq"]
        self.road = Road(self.base_speed)
        self.load_stage_config(self.stage)
        self.coin_frequency = self.get_coin_spawn_interval()
        self.max_active_coins = self.get_max_active_coins()
        # reset stage progress tracking (do not reset `distance` which is runtime total)
        self.stage_progress_distance = 0.0
        self._reset_stage_economy_counters()
        self.finish_sign = None
        self.completed_stage = None
        self.nitro_charge = 0.0
        self.nitro_active = False
        self.nitro_cooldown_until = 0
        self.boost_pressed_last_frame = False
        self.paused = False
        self.pause_button.text = "PAUSE"
        self.score_multiplier = 1.0
        self.multiplier_timer = 0
        self.multiplier_display_time = 0
        self.consecutive_actions = 0
        self.next_stage_score = 3
        self.clear_hazard_effects()
        self.weather.reset()
        self.weather.update_for_stage(
            stage=self.stage,
            progress_ratio=0.0,
            selected_difficulty=self.selected_difficulty,
            current_time=pg.time.get_ticks(),
        )
        self.update_player_bounds()

        
        try:
            if self.current_music and not self.music_muted:
                if previous_state == GameState.GAME_OVER:
                    pg.mixer.music.stop()
                    pg.mixer.music.play(-1)
                elif was_paused:
                    if not pg.mixer.music.get_busy():
                        pg.mixer.music.play(-1)
                    else:
                        pg.mixer.music.unpause()
        except Exception:
            pass

        if change_state:
            self.set_state(GameState.PLAYING)

    def stop_nitro_boost(self, current_time=None, start_cooldown=True):
        """Stop any active nitro effect; optionally start cooldown."""
        if not getattr(self, "nitro_active", False):
            return
        try:
            self.nitro_active = False
            if start_cooldown:
                now = int(current_time or pg.time.get_ticks())
                # use configured cooldown if present, otherwise default 3000ms
                self.nitro_cooldown_until = now + int(getattr(self, "NITRO_COOLDOWN_MS", 3000))
        except Exception:
            # be tolerant in tests and gameplay
            pass

    def _apply_level_one_wallet_floor(self, previous_state):
        """Ensure a fresh Level 1 run starts with exactly 100 money."""
        if self.stage == 1 and previous_state != GameState.GAME_OVER:
            self.total_money = 100
            self.save_data["total_money"] = 100
            try:
                from game.storage import save_save_data

                save_save_data(self.save_data)
            except Exception:
                pass

    def _restore_money_after_game_over(self):
        self.save_data = load_save_data()
        self.total_money = self.save_data.get("total_money", self.total_money)

    def get_stage_distance_target(self, stage_id, cfg=None):
        stage_id = max(1, int(stage_id))
        base_target = 560
        level_step = 280
        computed_target = base_target + (stage_id - 1) * level_step

        if isinstance(cfg, dict):
            configured_target = cfg.get("distance_target", computed_target)
            try:
                configured_target = int(configured_target)
            except (TypeError, ValueError):
                configured_target = computed_target
            return max(configured_target, computed_target)

        return computed_target

    def _reset_stage_economy_counters(self):
        self.stage_coin_count = 0
        self.stage_coin_money = 0
        self.stage_distance_reward_money = 0
        self.stage_reward_money = 0
        self.stage_collision_penalty_money = 0
        self.next_distance_reward_at = ECONOMY_DISTANCE_REWARD_STEP

    def get_coin_spawn_interval(self):
        cfg = getattr(self, "current_stage_config", {}) or {}
        base_interval = COIN_SPAWN_BASE_INTERVAL.get(self.selected_difficulty, 1900)
        stage_id = max(1, int(getattr(self, "stage", DEFAULT_STAGE)))
        traffic_density = max(0.6, float(cfg.get("traffic_density", 1.0)))
        stage_penalty = (stage_id - 1) * COIN_SPAWN_STAGE_STEP
        interval = int((base_interval + stage_penalty) / traffic_density)
        return max(COIN_SPAWN_MIN_INTERVAL, interval)

    def get_max_active_coins(self):
        diff = getattr(self, "selected_difficulty", DEFAULT_DIFFICULTY)
        return int(COIN_MAX_ACTIVE.get(diff, 2))

    def _choose_coin_lane_ratio(self):
        lane = self._choose_spawn_lane()
        ratio = (lane + 0.5) / 3
        if lane == 1 and random.random() < 0.6:
            ratio = max(0.34, min(0.66, 0.5 + random.uniform(-0.12, 0.12)))
        return ratio

    def get_coin_spawn_variant(self):
        stage_id = max(1, int(getattr(self, "stage", 1)))
        diff = getattr(self, "selected_difficulty", DEFAULT_DIFFICULTY)
        chain_base = float(COIN_CHAIN_SPAWN_BASE_CHANCE.get(diff, 0.10))
        red_base = float(COIN_RED_SPAWN_BASE_CHANCE.get(diff, 0.025))
        stage_bonus = max(0, stage_id - 1)
        chain_chance = min(COIN_CHAIN_SPAWN_MAX_CHANCE, chain_base + stage_bonus * COIN_CHAIN_SPAWN_STAGE_STEP)
        red_chance = min(COIN_RED_SPAWN_MAX_CHANCE, red_base + stage_bonus * COIN_RED_SPAWN_STAGE_STEP)
        roll = random.random()
        if roll < red_chance:
            return "red"
        if roll < red_chance + chain_chance:
            return "chain"
        return "normal"

    def get_coin_collision_rect(self, coin):
        radius = max(1, int(getattr(coin, "radius", 12)))
        return pg.Rect(int(coin.x - radius), int(coin.y - radius), radius * 2, radius * 2)

    def can_spawn_coin_pickup(self, coin_pickups):
        pickups = coin_pickups if isinstance(coin_pickups, (list, tuple)) else [coin_pickups]
        if not pickups:
            return False

        for pickup in pickups:
            new_rect = self.get_coin_collision_rect(pickup)
            for obstacle in self.obstacles:
                obstacle_rect = self.get_obstacle_rect(obstacle)
                vertical_gap = max(getattr(obstacle, "height", 0), getattr(pickup, "radius", 12) * 2) + 88
                if abs(getattr(obstacle, "y", 0) - pickup.y) < vertical_gap:
                    if obstacle_rect.inflate(20, 28).colliderect(new_rect):
                        return False
        return True

    def _create_coin_pickup(self, coin_y, coin_ratio, variant="normal"):
        from .coin import Coin as CoinClass

        c = CoinClass(self.road.get_travel_x(coin_y, coin_ratio, COIN_RADIUS * 2) + COIN_RADIUS, coin_y, variant=variant)
        c.road_ratio = coin_ratio
        return c

    def spawn_coin_pickup(self, current_time, forced_variant=None):
        if self.finish_sign is not None:
            return
        coin_capacity = self.get_max_active_coins() + COIN_CHAIN_LENGTH - 1
        if len(self.coins) >= coin_capacity:
            return
        if current_time - self.last_coin_time <= self.coin_frequency:
            return

        variant = forced_variant or self.get_coin_spawn_variant()
        available_slots = coin_capacity - len(self.coins)
        if variant == "chain" and available_slots < COIN_CHAIN_LENGTH:
            variant = "normal"
        elif variant in {"red", "normal"} and available_slots < 1:
            return

        coin_ratio = self._choose_coin_lane_ratio()
        if variant == "chain":
            coin_line = [
                self._create_coin_pickup(-50 - index * COIN_CHAIN_VERTICAL_SPACING, coin_ratio, variant="normal")
                for index in range(COIN_CHAIN_LENGTH)
            ]
            if not self.can_spawn_coin_pickup(coin_line):
                if available_slots < 1:
                    return
                variant = "normal"
            else:
                self.coins.extend(coin_line)
                self.last_coin_time = current_time
                return

        coin_y = -50
        coin_variant = "red" if variant == "red" else "normal"
        new_coin = self._create_coin_pickup(coin_y, coin_ratio, variant=coin_variant)
        if not self.can_spawn_coin_pickup(new_coin):
            return
        self.coins.append(new_coin)
        self.last_coin_time = current_time

    def collect_coin_pickup(self, coin, current_time):
        coin_value = max(0, int(getattr(coin, "money_value", 0)))
        self.stage_coin_count += 1
        self.stage_coin_money += coin_value
        self.current_level_money += coin_value
        self.money_popup_amount = coin_value
        self.money_popup_start_time = current_time
        self.multiplier_display_time = current_time
        self.multiplier_text_pos = (coin.x, coin.y)
        self.consecutive_actions += 1
        self.update_multiplier()
        if self.coin_sound and not self.music_muted:
            self.coin_sound.play()

    def apply_distance_rewards(self, current_time):
        step = max(1, int(ECONOMY_DISTANCE_REWARD_STEP))
        reward_money = max(0, int(ECONOMY_DISTANCE_REWARD_MONEY))

        while self.distance >= self.next_distance_reward_at:
            self.stage_distance_reward_money += reward_money
            self.current_level_money += reward_money
            self.money_popup_amount = reward_money
            self.money_popup_start_time = current_time
            self.register_status_message(f"Distance bonus +{reward_money}", current_time, duration=900)
            self.next_distance_reward_at += step

    def calculate_collision_penalty(self, stage_id=None):
        stage_id = max(1, int(self.stage if stage_id is None else stage_id))
        return int(COLLISION_MONEY_PENALTY_BASE + (stage_id - 1) * COLLISION_MONEY_PENALTY_STAGE_STEP)

    def should_apply_collision_penalty(self, obstacle):
        return (
            isinstance(obstacle, Car)
            or getattr(obstacle, "kind", None) == "car"
            or (isinstance(obstacle, Hazard) and getattr(obstacle, "damage_on_hit", False))
        )

    def apply_collision_penalty(self, current_time, stage_id=None):
        penalty = max(0, self.calculate_collision_penalty(stage_id))
        if penalty <= 0:
            return 0

        self.current_level_money -= penalty
        self.stage_collision_penalty_money += penalty
        self.money_popup_amount = -penalty
        self.money_popup_start_time = current_time
        self.register_status_message(f"Collision penalty -{penalty}", current_time, duration=900)
        return penalty

    def load_stage_config(self, stage_id):
        # Load stage config from constants.STAGE_DEFINITIONS, fall back to scaling
        cfg = STAGE_DEFINITIONS.get(stage_id)
        if not cfg:
            # simple fallback: increase difficulty gradually
            base = STAGE_DEFINITIONS[max(STAGE_DEFINITIONS.keys())]
            cfg = dict(base)
            cfg["stage_id"] = stage_id
            cfg["distance_target"] = int(base["distance_target"] + (stage_id - base["stage_id"]) * 60)
            cfg["enemy_speed_multiplier"] = min(2.0, base["enemy_speed_multiplier"] + 0.08 * (stage_id - base["stage_id"]))
            cfg["obstacle_frequency"] = max(700, int(base["obstacle_frequency"] - 80 * (stage_id - base["stage_id"])))

        self.current_stage_config = cfg
        cfg["distance_target"] = self.get_stage_distance_target(stage_id, cfg)
        # apply runtime-influencing values conservatively
        try:
            self.obstacle_frequency = cfg.get("obstacle_frequency", self.obstacle_frequency)
            self.current_speed = self.base_speed * cfg.get("enemy_speed_multiplier", 1.0)
            self.coin_frequency = self.get_coin_spawn_interval()
            # stage speed bonus applied per obstacle creation via get_stage_speed_bonus()
        except Exception:
            pass

    def start_game(self):
        self.reset_game(change_state=True)
        if self.current_music and not self.music_muted:
            pg.mixer.music.play(-1)
    
    def continue_from_checkpoint(self):
        self.save_data = load_save_data()
        checkpoint_stage = self.get_checkpoint_stage()
        self.reset_game(change_state=True, start_stage=checkpoint_stage)
        # Use a neutral message instead of showing the level number
        self.register_status_message("Play again", pg.time.get_ticks(), duration=1600)
        if self.current_music and not self.music_muted:
            pg.mixer.music.play(-1)
    def open_high_scores(self):
        self.best_score = read_high_score()
        self.set_state(GameState.HIGH_SCORE)

    def enter_game_over(self):
        previous_best_score = read_high_score()
        self.is_new_high_score = self.score > previous_best_score

        # Persist non-money progress only. Money stays at the last completed level.
        self.save_data = update_progress(
            score=self.score,
            stage=self.stage,
            money_earned=0,
            distance=int(getattr(self, "distance", 0)),
            persist_money=False,
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
        previous_state = self.state
        self.save_preferences()
        self.save_data = load_save_data()
        self.best_score = self.save_data["high_score"]
        self.total_money = self.save_data["total_money"]
        self.best_stage = self.save_data["best_stage"]
        self.games_played = self.save_data["games_played"]
        self.total_score = self.save_data["total_score"]
        self.reset_game(change_state=False)
        self.set_state(GameState.MENU)

       
        try:
            if previous_state == GameState.GAME_OVER and self.current_music and not self.music_muted:
                pg.mixer.music.stop()
                pg.mixer.music.play(-1)
        except Exception:
            pass

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
                elif self.state == GameState.GARAGE:
                    self.handle_garage_click(event.pos)
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
                if event.key == pg.K_g and self.state == GameState.MENU:
                    self.garage_index = self.selected_skin
                    self.set_state(GameState.GARAGE)

                if self.state == GameState.GARAGE:
                    if event.key == pg.K_LEFT:
                        self.garage_index = (self.garage_index - 1) % len(CAR_SKINS)
                    elif event.key == pg.K_RIGHT:
                        self.garage_index = (self.garage_index + 1) % len(CAR_SKINS)
                    elif event.key in {pg.K_ESCAPE, pg.K_BACKSPACE}:
                        self.return_to_menu()
                if event.key == pg.K_r and (self.state == GameState.GAME_OVER or self.paused):
                    # Restart: when in GAME_OVER this will resume the same stage
                    # (reset_game uses previous_state to preserve stage on GAME_OVER).
                    self.reset_game()
                if self.state == GameState.STAGE_COMPLETE and event.key in {pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE}:
                    self.start_next_stage()

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
        if left_arrow.collidepoint(mouse_pos) or right_arrow.collidepoint(mouse_pos):
            self.garage_index = self.selected_skin
            self.set_state(GameState.GARAGE)
            return

        if self.play_button.is_clicked(mouse_pos):
            self.start_game()
        if self.garage_button.is_clicked(mouse_pos):
            self.garage_index = self.selected_skin
            self.set_state(GameState.GARAGE)
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
            # Restart from the Game Over screen: resume the same stage.
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

    def align_nitro_to_road(self, pickup):
        if hasattr(pickup, "road_ratio"):
            pickup.x = self.road.get_travel_x(pickup.y, pickup.road_ratio, pickup.radius * 2) + pickup.radius

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
            max_speed = const.MAX_SPEED + getattr(self.player, "max_speed_bonus", 0.0)
            frac = (vel - const.MIN_SPEED) / max(1.0, (max_speed - const.MIN_SPEED))
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

    def get_stage_speed_bonus(self):
        cfg = getattr(self, "current_stage_config", {}) or {}
        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        cap = diff_settings.get(
            "stage_speed_cap",
            4.0 if self.selected_difficulty == "Easy" else 5.5 if self.selected_difficulty == "Medium" else 7.0,
        )
        multiplier_bonus = max(0.0, (cfg.get("enemy_speed_multiplier", 1.0) - 1.0) * 8.0)
        density_bonus = max(0.0, (cfg.get("traffic_density", 1.0) - 0.6) * 4.0)
        return min(cap, multiplier_bonus + density_bonus)

    def create_track_obstacle(self, diff_settings):
        cfg = getattr(self, "current_stage_config", {}) or {}
        track_weights = TRACK_OBJECT_WEIGHTS[self.selected_difficulty]
        obstacle_kind = random.choices(
            list(track_weights.keys()),
            weights=list(track_weights.values()),
            k=1,
        )[0]
        # Choose a spawn lane that is not overcrowded so obstacles appear
        # across all lanes instead of leaving long empty spots.
        lane = self._choose_spawn_lane()
        lane_ratio = (lane + 0.5) / 3
        # If spawning in the center lane, occasionally offset slightly left/right
        # so obstacles appear just off-center as well.
        if lane == 1 and random.random() < 0.5:
            lane_ratio = max(0.33, min(0.66, 0.5 + random.uniform(-0.16, 0.16)))
        min_speed, max_speed = diff_settings["obstacle_speed"]
        stage_speed_bonus = self.get_stage_speed_bonus()
        speed_multiplier = cfg.get("enemy_speed_multiplier", 1.0)

        # More frequently spawn obstacles exactly at the extreme left/right
        # so players can't permanently safe-spot at the absolute screen sides.
        # 40% chance to spawn at an edge, placed at 0.0 (left) or 1.0 (right).
        if random.random() < 0.40:
            if random.choice([True, False]):
                lane_ratio = 0.0
            else:
                lane_ratio = 1.0

        if obstacle_kind == "car":
            color = random.choice([(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180)])
            obstacle = Car(0, -150, color)
            obstacle.kind = "car"
            obstacle.label = "Traffic Car"
            obstacle.damage_on_hit = True
            obstacle.remove_on_hit = True
            obstacle.shadow = True
            obstacle.speed = int((random.randint(min_speed, max_speed) * speed_multiplier) + stage_speed_bonus)
        else:
            hazard_speed = int((random.randint(max(5, min_speed - 2), max(7, max_speed - 2)) * speed_multiplier) + stage_speed_bonus)
            spawn_y = -165 if obstacle_kind == "barrier" else -125
            obstacle = Hazard(0, spawn_y, obstacle_kind, hazard_speed)

        obstacle.road_ratio = lane_ratio
        obstacle.x = self.road.get_travel_x(0, lane_ratio, obstacle.width)
        return obstacle

    def _choose_spawn_lane(self):
        """Pick a lane index (0..2) preferring lanes with fewer obstacles.

        This reduces the chance of long empty stretches where no obstacle
        appears because a single lane is overcrowded.
        """
        # Small bias to spawn in the center lane more often to keep
        # mid-screen traffic denser (helps avoid too-few middle obstacles).
        if random.random() < 0.25:
            return 1
        # Count obstacles per lane (approximate by road_ratio)
        counts = [0, 0, 0]
        for ob in getattr(self, "obstacles", []):
            if not hasattr(ob, "road_ratio"):
                continue
            try:
                idx = int(min(2, max(0, math.floor(ob.road_ratio * 3))))
            except Exception:
                # fallback mapping
                try:
                    idx = int(min(2, max(0, int(ob.road_ratio * 3))))
                except Exception:
                    idx = 0
            counts[idx] += 1

        # Determine player's approximate lane (0..2) using screen thirds
        player_lane = None
        try:
            px = int(self.player.x + getattr(self.player, "width", 0) / 2)
            player_lane = int(min(2, max(0, px * 3 // max(1, WIDTH))))
        except Exception:
            player_lane = None

        # With some probability, prefer spawning in/near the player's lane
        if player_lane is not None and random.random() < 0.45:
            # pick player's lane or one adjacent to it
            choices = [player_lane]
            if player_lane - 1 >= 0:
                choices.append(player_lane - 1)
            if player_lane + 1 <= 2:
                choices.append(player_lane + 1)
            return random.choice(choices)

        # Otherwise prefer lanes with the minimum count
        min_count = min(counts)
        preferred = [i for i, c in enumerate(counts) if c == min_count]
        if preferred:
            return random.choice(preferred)

        return random.randint(0, 2)


    def register_status_message(self, message, current_time, duration=1200):
        self.status_message = message
        self.status_message_until = current_time + duration

    def get_effective_world_speed(self):
        if self.nitro_active:
            return self.current_speed * NITRO_WORLD_SPEED_MULTIPLIER
        return self.current_speed

    def get_nitro_motion_multiplier(self):
        if not self.nitro_active:
            return 1.0
        return NITRO_WORLD_SPEED_MULTIPLIER

    def circle_hits_player(self, circle_x, circle_y, radius, tolerance=6):
        rect = pg.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        nearest_x = max(rect.left, min(circle_x, rect.right))
        nearest_y = max(rect.top, min(circle_y, rect.bottom))
        dx = circle_x - nearest_x
        dy = circle_y - nearest_y
        return dx * dx + dy * dy <= (radius + tolerance) ** 2

    def can_activate_nitro(self, current_time):
        return (
            not self.nitro_active
            and self.nitro_charge >= NITRO_MIN_ACTIVATION
            and current_time >= self.nitro_cooldown_until
        )

    def start_nitro_boost(self, current_time):
        if not self.can_activate_nitro(current_time):
            return False

        self.nitro_active = True
        self.player.max_speed_bonus = NITRO_MAX_SPEED_BONUS
        self.player.accelerate(NITRO_MAX_SPEED_BONUS * 0.45)
        self.road.speed_multiplier = NITRO_WORLD_SPEED_MULTIPLIER
        self.register_status_message("Nitro engaged", current_time, duration=900)
        return True

    def stop_nitro_boost(self, current_time, start_cooldown=True):
        self.nitro_active = False
        if self.player is not None:
            self.player.max_speed_bonus = 0.0
        if self.road is not None:
            self.road.speed_multiplier = 1.0
        if start_cooldown:
            self.nitro_cooldown_until = current_time + NITRO_COOLDOWN_MS

    def update_nitro_state(self, current_time, dt):
        if not self.nitro_active:
            if self.player is not None:
                self.player.max_speed_bonus = 0.0
            if self.road is not None:
                self.road.speed_multiplier = 1.0
            return

        self.nitro_charge = max(0.0, self.nitro_charge - (NITRO_DRAIN_PER_SECOND * dt))
        self.player.max_speed_bonus = NITRO_MAX_SPEED_BONUS
        self.road.speed_multiplier = NITRO_WORLD_SPEED_MULTIPLIER
        self.player.accelerate(NITRO_BOOST_ACCEL * dt)

        if self.nitro_charge <= 0:
            self.stop_nitro_boost(current_time, start_cooldown=True)
            self.register_status_message("Nitro cooling down", current_time, duration=1200)

    def spawn_nitro_pickup(self, current_time):
        if self.finish_sign is not None or self.nitro_active or len(self.nitro_pickups) >= 1:
            return
        if current_time - self.last_nitro_time <= NITRO_SPAWN_INTERVAL:
            return

        lane_ratio = random.uniform(0.14, 0.86)
        pickup = NitroPickup(self.road.get_travel_x(0, lane_ratio, 26) + 13, -70)
        pickup.road_ratio = lane_ratio
        self.nitro_pickups.append(pickup)
        self.last_nitro_time = current_time

    def collect_nitro_pickup(self, pickup, current_time):
        self.nitro_charge = min(NITRO_MAX_CHARGE, self.nitro_charge + pickup.charge_value)
        self.consecutive_actions += 1
        self.update_multiplier()
        if self.player is not None:
            self.player.accelerate(max(8.0, pickup.charge_value * 0.75))

        activated = self.start_nitro_boost(current_time)
        if activated:
            self.register_status_message("Nitro pickup: boost engaged", current_time, duration=1000)
        else:
            self.register_status_message("Nitro collected", current_time, duration=900)

    def get_level_label(self, level=None):
        return f"Level {self.stage if level is None else level}"

    def update_player_handling(self, current_time, dt):
        speed_val = getattr(self.player, "velocity", const.PLAYER_SPEED_DEFAULT)
        vehicle_stats = self._get_selected_skin_stats()
        base_lateral_speed = max(5, int(6 + speed_val / 12 + vehicle_stats["handling_bonus"]))
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
        # Backwards-compatible stub: old score-based leveling is deprecated.
        # Keep this function present so existing calls don't break, but do not
        # drive stage changes. True stage progression is distance/finish-line based.
        return

    def check_stage_progression(self, current_time):
        """Check current stage progress and spawn the finish sign when ready."""
        cfg = getattr(self, "current_stage_config", None)
        if not cfg:
            return

        target = cfg.get("distance_target", None)
        if target is None:
            return

        if self.finish_sign is None and self.stage_progress_distance >= target:
            sign_speed = max(7, int(self.base_speed * cfg.get("enemy_speed_multiplier", 1.0)))
            self.finish_sign = FinishLine(self.road, self.stage, sign_speed)
            self.register_status_message(f"Finish sign appeared for Level {self.stage}", current_time, duration=1800)

    def enter_stage_complete(self, current_time=None):
        self.completed_stage = self.stage
        self.finish_sign = None
        self.obstacles = []
        self.coins = []
        self.nitro_pickups = []
        self.clear_hazard_effects()
        if current_time is None:
            current_time = pg.time.get_ticks()
<<<<<<< HEAD

        self.stop_nitro_boost(current_time, start_cooldown=False)

        self.last_stage_score_bonus, self.last_stage_money_bonus = self.calculate_stage_rewards(self.stage)
        self.last_stage_bonus_total = self.last_stage_score_bonus + self.last_stage_money_bonus
        self.score += self.last_stage_score_bonus
        self.current_level_money += self.last_stage_money_bonus
        self.stage_reward_money = self.last_stage_money_bonus
        self.money_popup_amount = self.last_stage_money_bonus
        self.money_popup_start_time = current_time

        self.save_data = update_progress(
            score=self.score,
            stage=self.stage,
            money_earned=self.current_level_money,
            distance=int(getattr(self, "distance", 0)),
            persist_money=True,
        )
        self.total_money = self.save_data["total_money"]
        self.best_score = self.save_data["high_score"]
        self.best_stage = self.save_data["best_stage"]
        self.games_played = self.save_data["games_played"]
        self.total_score = self.save_data["total_score"]
        self.current_level_money = 0

        self.register_status_message(
            f"Level {self.stage} complete: +{self.last_stage_score_bonus} score, +{self.last_stage_money_bonus} money",
            current_time,
            duration=1800,
        )
=======
        self.stop_nitro_boost(current_time, start_cooldown=False)
        self.register_status_message(f"Level {self.stage} complete", current_time, duration=1200)
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
        self.set_state(GameState.STAGE_COMPLETE)
        # initialize map-style transition animation
        try:
            self.level_transition_start = pg.time.get_ticks()
        except Exception:
            self.level_transition_start = current_time

    def start_next_stage(self, current_time=None):
        # Advance stage counter and load the next config. Keep total distance.
        next_stage = self.stage + 1
        self.stage = next_stage
        self.level = next_stage
        # Each new stage starts with a fresh 3-life budget.
        self.lives = PLAYER_START_LIVES
        self.stage_progress_distance = 0.0
        self._reset_stage_economy_counters()
        self.finish_sign = None
        self.completed_stage = None
        self.obstacles = []
        self.coins = []
        self.nitro_pickups = []
        self.clear_hazard_effects()
        self.stop_nitro_boost(pg.time.get_ticks(), start_cooldown=False)
        self.load_stage_config(self.stage)
<<<<<<< HEAD
        self.coin_frequency = self.get_coin_spawn_interval()
        self.max_active_coins = self.get_max_active_coins()
        try:
            self.weather.update_for_stage(
                stage=self.stage,
                progress_ratio=0.0,
                selected_difficulty=self.selected_difficulty,
                current_time=pg.time.get_ticks(),
            )
        except Exception:
            pass
=======
        self.weather.update_for_stage(
            stage=self.stage,
            progress_ratio=0.0,
            selected_difficulty=self.selected_difficulty,
            current_time=pg.time.get_ticks(),
        )
>>>>>>> 3df94ff (Add dynamic weather system with visual and driving effects)
        self.last_obstacle_time = pg.time.get_ticks()
        self.last_coin_time = pg.time.get_ticks()
        self.last_nitro_time = pg.time.get_ticks()
        self.paused = False
        self.set_state(GameState.PLAYING)
        if current_time is None:
            current_time = pg.time.get_ticks()
        self.register_status_message(f"Level {self.stage} Started", current_time, duration=1400)

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
        boost_pressed = keys[pg.K_SPACE] or keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]
        if boost_pressed and not self.boost_pressed_last_frame:
            self.start_nitro_boost(current_time)
        self.boost_pressed_last_frame = boost_pressed
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

        self.update_nitro_state(current_time, dt)

        # update display-only speed from player's internal velocity (do not change game logic current_speed)
        try:
            self.display_speed = float(self.player.get_velocity())
        except Exception:
            self.display_speed = float(self.current_speed)
        # accumulate runtime-only distance (units: player velocity * seconds)
        try:
            vel = float(self.player.get_velocity())
            # dt is seconds since last frame
            self.distance += vel * dt
            # only advance stage progress if the player is actually moving
            # forward above a small threshold — this prevents the level from
            # completing when the car is effectively stationary.
            player_speed_frac = self.get_player_speed_fraction()
            MIN_VEL_FOR_STAGE = 1.5
            if vel >= MIN_VEL_FOR_STAGE and player_speed_frac > 0.05:
                self.stage_progress_distance += vel * dt
        except Exception:
            pass
        
        try:
            target_distance = float(
                getattr(self, "current_stage_config", {}).get("distance_target", 1)
            )
            stage_progress_ratio = self.stage_progress_distance / max(1.0, target_distance)
            stage_progress_ratio = max(0.0, min(1.0, stage_progress_ratio))
        except Exception:
            stage_progress_ratio = 0.0

        try:
            hazard_slip_active = current_time < self.skid_end_time
            self.weather.update(
                current_time=current_time,
                dt=dt,
                player=self.player,
                keys=keys,
                stage=self.stage,
                stage_progress_ratio=stage_progress_ratio,
                selected_difficulty=self.selected_difficulty,
                hazard_slip_active=hazard_slip_active,
            )
        except Exception:
            pass
        
        self.update_player_bounds()

        diff_settings = DIFFICULTY_SETTINGS[self.selected_difficulty]
        speed_factor = max(self.get_effective_world_speed() / BASE_SPEED, 1)
        motion_multiplier = self.get_nitro_motion_multiplier()

        stage_density = max(0.55, getattr(self, "current_stage_config", {}).get("traffic_density", 1.0))
        # If the player is mostly stationary, increase spawn rate so obstacles
        # still appear across the screen and prevent safe camping at edges.
        try:
            player_speed_frac = self.get_player_speed_fraction()
        except Exception:
            player_speed_frac = 1.0

        spawn_bias = 0.6 if player_speed_frac < 0.25 else 1.0
        effective_obstacle_interval = (self.obstacle_frequency / stage_density) / (speed_factor * spawn_bias)

        if self.finish_sign is None and current_time - self.last_obstacle_time > effective_obstacle_interval:
            new_obstacle = self.create_track_obstacle(diff_settings)
            if self.can_spawn_obstacle(new_obstacle):
                self.obstacles.append(new_obstacle)
                self.last_obstacle_time = current_time

        player_rect = self.get_player_collision_rect()
        for obstacle in self.obstacles[:]:
            if obstacle.move(speed_multiplier=motion_multiplier):
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

                self.consecutive_actions = 0
                self.update_multiplier()
                self.lives -= 1
                self.last_damage_time = current_time
                self.damage_flash_time = current_time
<<<<<<< HEAD
                if self.damage_sound and not self.music_muted:
                    self.damage_sound.play()
                if getattr(self, "nitro_active", False):
                    try:
                        self.stop_nitro_boost(current_time, start_cooldown=True)
                    except Exception:
                        pass
                if self.should_apply_collision_penalty(obstacle):
                    self.apply_collision_penalty(current_time, self.stage)
=======
                if self.nitro_active:
                    self.stop_nitro_boost(current_time, start_cooldown=True)
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
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

        if self.finish_sign is not None:
            if self.finish_sign.move(speed_multiplier=motion_multiplier):
                self.enter_stage_complete(current_time)
            else:
                player_rect = self.get_player_collision_rect()
                if player_rect.colliderect(self.finish_sign.get_collision_rect()):
                    self.enter_stage_complete(current_time)

        if self.finish_sign is None:
            self.spawn_coin_pickup(current_time)

        self.spawn_nitro_pickup(current_time)

        for coin in self.coins[:]:
            if coin.move(speed_multiplier=motion_multiplier):
                self.coins.remove(coin)
                continue
            self.align_coin_to_road(coin)
            if self.circle_hits_player(coin.x, coin.y, coin.radius):
<<<<<<< HEAD
=======
                coin.grow()
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
                self.coins.remove(coin)
                self.collect_coin_pickup(coin, current_time)

                self.score += int(coin.score_value * self.score_multiplier)
                self.update_stage_progression()
        self.apply_distance_rewards(current_time)

<<<<<<< HEAD
        for pickup in list(getattr(self, "nitro_pickups", [])):
            if pickup.move(speed_multiplier=getattr(self, "motion_multiplier", 1.0)):
                try:
                    self.nitro_pickups.remove(pickup)
                except Exception:
                    pass
                continue
            try:
                self.align_nitro_to_road(pickup)
            except Exception:
                pass
            if self.circle_hits_player(pickup.x, pickup.y, pickup.radius, tolerance=4):
                try:
                    self.collect_nitro_pickup(pickup, current_time)
                except Exception:
                    pass
                try:
                    self.nitro_pickups.remove(pickup)
                except Exception:
                    pass
=======
        for pickup in self.nitro_pickups[:]:
            if pickup.move(speed_multiplier=motion_multiplier):
                self.nitro_pickups.remove(pickup)
                continue
            self.align_nitro_to_road(pickup)
            if self.circle_hits_player(pickup.x, pickup.y, pickup.radius, tolerance=4):
                self.collect_nitro_pickup(pickup, current_time)
                self.nitro_pickups.remove(pickup)

        if current_time - self.multiplier_timer > 3000:
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
            if self.score_multiplier > 1.0:
                self.consecutive_actions = max(0, self.consecutive_actions - 1)
                self.update_multiplier()
            self.multiplier_timer = current_time

        # Check stage progression and finish-line logic
        try:
            self.check_stage_progression(current_time)
        except Exception:
            pass

    def draw(self):
        self.draw_background()

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.HIGH_SCORE:
            self.draw_high_score_screen()
        elif self.state == GameState.GARAGE:
            self.draw_garage_screen()
        elif self.state == GameState.STAGE_COMPLETE:
            self.draw_stage_complete_screen()
        else:
            self.road.draw(self.screen)
            # draw player with a visual vertical offset based on forward velocity
            baseline_y = self.player.y
            mid_y = HEIGHT // 2
            # fraction of speed between MIN_SPEED and current runtime MAX_SPEED
            try:
                vel = float(self.player.get_velocity())
                max_speed = const.MAX_SPEED + getattr(self.player, "max_speed_bonus", 0.0)
                frac = (vel - const.MIN_SPEED) / max(1.0, (max_speed - const.MIN_SPEED))
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

            if self.finish_sign is not None:
                self.finish_sign.draw(self.screen)

            for coin in self.coins:
                coin.draw(self.screen)
            for pickup in self.nitro_pickups:
                pickup.draw(self.screen)

            self.weather.draw_environment(
                self.screen,
                self.player,
                self.selected_difficulty,
                player_visual_y=target_visual_y,
            )

            self.draw_scoreboard()
            self.draw_status_banner()
<<<<<<< HEAD
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
                
            self.weather.draw_hud(
                self.screen,
                self.small_font,
                self.tiny_font,
                self.selected_difficulty,
            )    
=======
            self.draw_top_right_hud()
>>>>>>> bcd0777 (feat: add nitro boost gameplay system)
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
        start_button = pg.Rect(card_x + 30, action_y, 122, 48)
        garage_button = pg.Rect(card_x + 162, action_y, 110, 48)
        score_button = pg.Rect(card_x + 282, action_y, 148, 48)
        exit_button = pg.Rect(card_x + 440, action_y, 90, 48)
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
            "garage_button": garage_button,
            "score_button": score_button,
            "exit_button": exit_button,
            "footer_rect": footer_rect,
        }

    def sync_menu_button_rects(self, layout):
        self.play_button.rect.topleft = layout["start_button"].topleft
        self.play_button.rect.size = layout["start_button"].size

        self.garage_button.rect.topleft = layout["garage_button"].topleft
        self.garage_button.rect.size = layout["garage_button"].size

        self.high_score_button.rect.topleft = layout["score_button"].topleft
        self.high_score_button.rect.size = layout["score_button"].size

        self.exit_button.rect.topleft = layout["exit_button"].topleft
        self.exit_button.rect.size = layout["exit_button"].size

    def sync_game_over_button_rects(self):
        button_y_start = HEIGHT // 2 - 20
        button_spacing = 60
        button_size = (200, 45)

        restart_y = HEIGHT // 2 + 28

        self.game_over_restart_button.rect.topleft = (WIDTH // 2 - 100, restart_y)
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

        garage_hint = self.tiny_font.render("Change vehicle in Garage", True, GRAY)
        self.screen.blit(garage_hint, (layout["right_panel"].centerx - garage_hint.get_width() // 2, layout["right_panel"].y + 186))

        self.play_button.draw(self.screen, self.small_font)
        self.garage_button.draw(self.screen, self.small_font)
        self.high_score_button.draw(self.screen, self.tiny_font)
        self.exit_button.draw(self.screen, self.small_font)

        footer = pg.Surface(layout["footer_rect"].size, pg.SRCALPHA)
        footer.fill((SLATE[0], SLATE[1], SLATE[2], 205))
        pg.draw.rect(footer, (255, 255, 255, 20), (0, 0, layout["footer_rect"].width, layout["footer_rect"].height), 1, border_radius=16)
        self.screen.blit(footer, layout["footer_rect"].topleft)

        summary_items = [
            f"Lives {PLAYER_START_LIVES}",
            f"Level {self.stage}",
            f"Speed {self.base_speed}",
            f"State {self.state.name}",
        ]
        for index, item in enumerate(summary_items):
            text = self.tiny_font.render(item, True, (220, 230, 240))
            slot_width = layout["footer_rect"].width // len(summary_items)
            slot_x = layout["footer_rect"].x + index * slot_width + (slot_width - text.get_width()) // 2
            self.screen.blit(text, (slot_x, layout["footer_rect"].y + 16))

        help_text = self.tiny_font.render("Arrow keys steer | G garage | P pause | R restart | H high scores", True, GRAY)
        self.screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, layout["footer_rect"].y + 42))

    def get_garage_layout(self):
        card_x = WIDTH // 2 - MENU_CARD_WIDTH // 2
        card_y = 58

        preview_rect = pg.Rect(WIDTH // 2 - 55, card_y + 120, 110, 120)
        left_arrow = pg.Rect(card_x + 72, card_y + 162, 46, 42)
        right_arrow = pg.Rect(card_x + MENU_CARD_WIDTH - 118, card_y + 162, 46, 42)

        buy_button = pg.Rect(WIDTH // 2 - 120, card_y + 382, 240, 45)
        select_button = pg.Rect(WIDTH // 2 - 120, card_y + 382, 240, 45)
        back_button = pg.Rect(WIDTH // 2 - 95, card_y + 435, 190, 42)

        return {
            "card_x": card_x,
            "card_y": card_y,
            "preview_rect": preview_rect,
            "left_arrow": left_arrow,
            "right_arrow": right_arrow,
            "buy_button": buy_button,
            "select_button": select_button,
            "back_button": back_button,
        }

    def sync_garage_button_rects(self, layout):
        self.garage_buy_button.rect.topleft = layout["buy_button"].topleft
        self.garage_buy_button.rect.size = layout["buy_button"].size

        self.garage_select_button.rect.topleft = layout["select_button"].topleft
        self.garage_select_button.rect.size = layout["select_button"].size

        self.garage_back_button.rect.topleft = layout["back_button"].topleft
        self.garage_back_button.rect.size = layout["back_button"].size

    def handle_garage_click(self, mouse_pos):
        layout = self.get_garage_layout()
        self.sync_garage_button_rects(layout)

        if layout["left_arrow"].collidepoint(mouse_pos):
            self.garage_index = (self.garage_index - 1) % len(CAR_SKINS)
            return

        if layout["right_arrow"].collidepoint(mouse_pos):
            self.garage_index = (self.garage_index + 1) % len(CAR_SKINS)
            return

        if self.garage_back_button.is_clicked(mouse_pos):
            self.return_to_menu()
            return

        self._refresh_profile_from_save()
        unlocked = self._get_unlocked_skin_indices()
        is_unlocked = self.garage_index in unlocked
        is_selected = self.garage_index == self.selected_skin

        if not is_unlocked and self.garage_buy_button.is_clicked(mouse_pos):
            success, message = buy_skin(self.garage_index)
            self._refresh_profile_from_save()

            if success:
                self.garage_index = self.selected_skin
                self.reset_game(change_state=False)

            self.register_garage_message(message)
            return

        if is_unlocked and not is_selected and self.garage_select_button.is_clicked(mouse_pos):
            success, message = select_skin(self.garage_index)
            self._refresh_profile_from_save()

            if success:
                self.reset_game(change_state=False)

            self.register_garage_message(message)
            return

    def draw_garage_screen(self):
        self._refresh_profile_from_save()

        card_x, card_y = self.draw_menu_shell(
            "GARAGE",
            "Buy, unlock, and select your vehicle.",
        )

        layout = self.get_garage_layout()
        self.sync_garage_button_rects(layout)

        skin = CAR_SKINS[self.garage_index]
        unlocked = self._get_unlocked_skin_indices()

        is_unlocked = self.garage_index in unlocked
        is_selected = self.garage_index == self.selected_skin
        price = skin.get("price", 0)

        money_text = self.small_font.render(f"Money: {self.total_money}", True, GOLD)
        self.screen.blit(
            money_text,
            (card_x + 38, card_y + 112),
        )

        preview_rect = layout["preview_rect"]
        preview_bg = pg.Surface(preview_rect.size, pg.SRCALPHA)
        preview_bg.fill((30, 30, 40, 210))
        pg.draw.rect(
            preview_bg,
            (255, 255, 255, 40),
            (0, 0, preview_rect.width, preview_rect.height),
            2,
            border_radius=12,
        )
        self.screen.blit(preview_bg, preview_rect.topleft)

        preview_car = Car(
            preview_rect.centerx - 25,
            preview_rect.y + 14,
            skin["color"],
            True,
            skin["type"],
        )
        preview_car.draw(self.screen)

        mouse_pos = pg.mouse.get_pos()
        for arrow_rect, symbol in [
            (layout["left_arrow"], "<"),
            (layout["right_arrow"], ">"),
        ]:
            hover = arrow_rect.collidepoint(mouse_pos)
            color = GREEN if hover else GRAY
            pg.draw.rect(self.screen, color, arrow_rect, border_radius=8)
            pg.draw.rect(self.screen, WHITE, arrow_rect, 2, border_radius=8)
            arrow_text = self.small_font.render(symbol, True, WHITE)
            self.screen.blit(arrow_text, arrow_text.get_rect(center=arrow_rect.center))

        name_text = self.small_font.render(skin["name"], True, YELLOW)
        self.screen.blit(
            name_text,
            (WIDTH // 2 - name_text.get_width() // 2, card_y + 248),
        )

        info_lines = [
            f"Type: {skin.get('type', 'sedan').title()}",
            f"Price: {price if price > 0 else 'Free'}",
            f"Speed Bonus: +{skin.get('speed_bonus', 0)}",
            f"Handling Bonus: +{skin.get('handling_bonus', 0)}",
        ]

        start_y = card_y + 278
        for index, line in enumerate(info_lines):
            info_text = self.tiny_font.render(line, True, WHITE)
            self.screen.blit(
                info_text,
                (WIDTH // 2 - info_text.get_width() // 2, start_y + index * 19),
            )

        if is_selected:
            status = "SELECTED"
            status_color = GREEN
        elif is_unlocked:
            status = "UNLOCKED"
            status_color = CYAN
        else:
            status = "LOCKED"
            status_color = RED

        status_text = self.small_font.render(f"Status: {status}", True, status_color)
        self.screen.blit(
            status_text,
            (WIDTH // 2 - status_text.get_width() // 2, card_y + 356),
        )

        if not is_unlocked:
            self.garage_buy_button.text = "BUY"
            if self.total_money < price:
                self.garage_buy_button.text = "NOT ENOUGH MONEY"
            self.garage_buy_button.draw(self.screen, self.tiny_font)
        elif not is_selected:
            self.garage_select_button.text = "SELECT"
            self.garage_select_button.draw(self.screen, self.small_font)

        self.garage_back_button.text = "BACK"
        self.garage_back_button.draw(self.screen, self.small_font)

        if self.garage_message and pg.time.get_ticks() < self.garage_message_until:
            message_text = self.tiny_font.render(self.garage_message, True, YELLOW)
            self.screen.blit(
                message_text,
                (WIDTH // 2 - message_text.get_width() // 2, card_y + 482),
            )

        help_text = self.tiny_font.render(
            "Use arrows or click < > to browse vehicles.",
            True,
            GRAY,
        )
        self.screen.blit(
            help_text,
            (WIDTH // 2 - help_text.get_width() // 2, card_y + 505),
        )

    def draw_high_score_screen(self):
        self.save_data = load_save_data()
        self.best_score = self.save_data["high_score"]
        self.total_money = self.save_data["total_money"]
        self.best_stage = self.save_data["best_stage"]
        self.best_distance = self.save_data.get("best_distance", 0)
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
            ("Best Distance", f"{int(self.best_distance)} m"),
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
        hud_height = 448
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

        level_text = self.small_font.render(f"Level: {self.stage}", True, CYAN)
        self.screen.blit(level_text, (24, 52))

        speed_val = getattr(self, "display_speed", self.current_speed)
        speed_text = self.small_font.render(f"Speed: {speed_val:.1f} km/h", True, GREEN)
        self.screen.blit(speed_text, (24, 80))

        # Distance (runtime-only): display as whole meters/units
        distance_text = self.small_font.render(f"Distance: {int(self.distance)} m", True, WHITE)
        self.screen.blit(distance_text, (24, 104))

        # Show distance-to-finish for the current stage.
        cfg = getattr(self, "current_stage_config", None)
        finish_line = None
        if cfg:
            remaining = int(max(0, cfg.get("distance_target", 0) - self.stage_progress_distance))
            finish_line = f"To Finish: {remaining} m"

        lives_label = self.small_font.render("Lives:", True, WHITE)
        self.screen.blit(lives_label, (24, 132))

        for i in range(self.lives):
            heart_x = 108 + i * 30
            heart_y = 150
            heart_points = []

            for angle in range(0, 360, 10):
                t = math.radians(angle)
                x = 16 * math.sin(t) ** 3
                y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))

                scale = 0.7
                heart_points.append((heart_x + int(x * scale), heart_y + int(y * scale)))

            pg.draw.polygon(self.screen, RED, heart_points)
            pg.draw.polygon(self.screen, WHITE, heart_points, 1)
        weather_lines = []
        try:
            road_type, safe_speed, high_risk_speed = self.weather.get_active_speed_limits(self.selected_difficulty)
        except Exception:
            road_type, safe_speed, high_risk_speed = None, None, None

<<<<<<< HEAD
=======
        weather_lines = []
        try:
            road_type, safe_speed, high_risk_speed = self.weather.get_active_speed_limits(self.selected_difficulty)
        except Exception:
            road_type, safe_speed, high_risk_speed = None, None, None

>>>>>>> 5b18a38 (Add weather system updates and fix restart/HUD issues)
        if road_type and safe_speed is not None and high_risk_speed is not None:
            weather_lines.append(f"{road_type} Safe: {safe_speed:.0f}  Risk: {high_risk_speed:.0f} km/h")

        try:
            fog_intensity = float(self.weather.weather_intensity.get("fog", 0.0))
        except Exception:
            fog_intensity = 0.0

        if ("fog" in getattr(self.weather, "active_weather", [])) or (fog_intensity > 0.05):
            fog_trigger = self.weather.get_fog_speed_trigger(self.selected_difficulty)
            weather_lines.append(f"Fog drift: > {fog_trigger:.0f} km/h")

<<<<<<< HEAD
        active_statuses = self.get_active_hazard_statuses(pg.time.get_ticks())
        visible_status_count = max(1, min(3, len(active_statuses)))
        legend_card_width = 188

        dynamic_texts = [
            f"Score: {self.score}",
            f"Level: {self.stage}",
            f"Speed: {speed_val:.1f} km/h",
            f"Distance: {int(self.distance)} m",
            f"Mode: {self.selected_difficulty}",
            f"Vehicle: {CAR_SKINS[self.selected_skin]['name']}",
            f"Money: {self.total_money + (self.current_level_money if self.state != GameState.GAME_OVER else 0)}",
            f"Multiplier: x{self.score_multiplier:.1f}",
            "Track Watch",
            "Active",
        ]
        if finish_line:
            dynamic_texts.append(finish_line)
        dynamic_texts.extend(weather_lines[:2])

        max_text_width = 0
        for text in dynamic_texts:
            width = self.tiny_font.size(text)[0]
            if width > max_text_width:
                max_text_width = width

        hud_width = max(236, max_text_width + 56, legend_card_width + 48)
        status_rows_bottom = 440 + (visible_status_count - 1) * 16 + 18
        hud_height = max(448, status_rows_bottom + 18)

        hud_bg = pg.Surface((hud_width, hud_height), pg.SRCALPHA)
        hud_bg.fill((10, 14, 22, 208))
        pg.draw.rect(hud_bg, (255, 255, 255, 50 + pulse), (0, 0, hud_width, hud_height), 3, border_radius=14)

        for index in range(hud_height):
            alpha = int(30 * (1 - index / hud_height))
            pg.draw.line(hud_bg, (38, 164, 184, alpha), (0, index), (hud_width, index))

        self.screen.blit(hud_bg, (10, 10))

        for idx, line in enumerate(weather_lines[:2]):
            info = self.tiny_font.render(line, True, CYAN)
            self.screen.blit(info, (24, 176 + idx * 16))
        
=======
        for idx, line in enumerate(weather_lines[:2]):
            info = self.tiny_font.render(line, True, CYAN)
            self.screen.blit(info, (24, 176 + idx * 16))

>>>>>>> 5b18a38 (Add weather system updates and fix restart/HUD issues)
        mode_text = self.tiny_font.render(f"Mode: {self.selected_difficulty}", True, YELLOW)
        self.screen.blit(mode_text, (24, 200))

        vehicle_name = CAR_SKINS[self.selected_skin]["name"]
        if len(vehicle_name) > 16:
            vehicle_name = vehicle_name[:15] + "."
        vehicle_text = self.tiny_font.render(f"Vehicle: {vehicle_name}", True, CYAN)
        self.screen.blit(vehicle_text, (24, 220))

        display_money = self.total_money

        if self.state != GameState.GAME_OVER:
            display_money = max(0, display_money + self.current_level_money)



        money_text = self.tiny_font.render(
            f"Money: {display_money}",
            True,
            GOLD,
        )
        self.screen.blit(money_text, (24, 246))

        popup_age = pg.time.get_ticks() - self.money_popup_start_time
        popup_duration = 950

        if self.money_popup_amount > 0 and popup_age < popup_duration:
            progress = popup_age / popup_duration
            popup_y = 246 - int(progress * 20)
            popup_alpha = max(0, 255 - int(progress * 220))

            popup_sign = "+" if self.money_popup_amount >= 0 else "-"
            popup_text = self.small_font.render(
                f"{popup_sign}{abs(self.money_popup_amount)}",
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
            self.screen.blit(multiplier_text, (24, 266))

        if finish_line:
            finish_y = 284 if self.score_multiplier > 1.0 else 268
            finish_text = self.tiny_font.render(finish_line, True, WHITE)
            self.screen.blit(finish_text, (24, finish_y))

        section_title_y = 304 if (finish_line and self.score_multiplier > 1.0) else 296
        section_title = self.tiny_font.render("Track Watch", True, WHITE)
        self.screen.blit(section_title, (24, section_title_y))

        legend_items = [
            ("Oil", "drift", (210, 210, 220)),
            ("Water", "slow", (96, 176, 240)),
            ("Pothole", "drop", (196, 142, 110)),
            ("Barrier", "hit", (232, 98, 32)),
        ]
        for index, (label, effect, color) in enumerate(legend_items):
            card_x = 24
            card_y = (326 if (finish_line and self.score_multiplier > 1.0) else 318) + index * 22
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
        self.screen.blit(status_title, (24, 418))
        if active_statuses:
            for index, (label, color) in enumerate(active_statuses[:3]):
                badge = pg.Surface((188, 18), pg.SRCALPHA)
                badge.fill((255, 255, 255, 10))
                pg.draw.rect(badge, (*color, 90), (0, 0, 188, 18), 1, border_radius=8)
                status_text = self.tiny_font.render(label, True, color)
                badge.blit(status_text, (8, 2))
<<<<<<< HEAD
<<<<<<< HEAD
                self.screen.blit(badge, (24, 398 + index * 16))
            else:
                badge = pg.Surface((188, 18), pg.SRCALPHA)
                badge.fill((255, 255, 255, 10))
                pg.draw.rect(badge, (*GREEN, 90), (0, 0, 188, 18), 1, border_radius=8)
                status_text = self.tiny_font.render("Road stable", True, GREEN)
                badge.blit(status_text, (8, 2))
                self.screen.blit(badge, (24, 440))

        def draw_top_right_hud(self):
            panel_width = 226
            panel_height = 132
            panel_x = WIDTH - panel_width - 14
            panel_y = 12

            self.pause_button.rect.topleft = (panel_x + 122, panel_y + 10)
            self.pause_button.rect.size = (92, 30)
            self.sound_button.rect.topleft = (panel_x + 122, panel_y + 48)
            self.sound_button.rect.size = (92, 30)

            panel = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
            panel.fill((8, 14, 24, 220))
            pg.draw.rect(panel, (255, 255, 255, 42), (0, 0, panel_width, panel_height), 2, border_radius=16)

            speed_text = self.tiny_font.render(f"Speed {self.display_speed:.1f} km/h", True, WHITE)
            panel.blit(speed_text, (14, 14))

            current_money = max(0, self.total_money + self.current_level_money)
            money_text = self.tiny_font.render(f"Money {current_money}", True, GOLD)
            panel.blit(money_text, (14, 34))

            label = self.tiny_font.render("Nitro", True, (175, 235, 255))
            panel.blit(label, (14, 58))

            bar_rect = pg.Rect(14, 80, 96, 15)
            pg.draw.rect(panel, (24, 34, 48), bar_rect, border_radius=7)
            fill_width = int(bar_rect.width * (self.nitro_charge / max(1.0, NITRO_MAX_CHARGE)))
            if fill_width > 0:
                fill_rect = pg.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
                bar_color = (64, 220, 255) if not getattr(self, "nitro_active", False) else (255, 170, 72)
                pg.draw.rect(panel, bar_color, fill_rect, border_radius=7)
            pg.draw.rect(panel, (210, 245, 255), bar_rect, 2, border_radius=7)

            if getattr(self, "nitro_active", False):
                status = "Boost active"
                status_color = (255, 190, 92)
            elif pg.time.get_ticks() < getattr(self, "nitro_cooldown_until", 0):
                remaining = max(0.0, (getattr(self, "nitro_cooldown_until", 0) - pg.time.get_ticks()) / 1000.0)
                status = f"Cooldown {remaining:.1f}s"
                status_color = YELLOW
            elif getattr(self, "nitro_charge", 0) >= getattr(self, "NITRO_MIN_ACTIVATION", 0):
                status = "SPACE / SHIFT"
                status_color = GREEN
            else:
                status = "Collect nitro"
                status_color = GRAY

            status_text = self.tiny_font.render(status, True, status_color)
            charge_text = self.tiny_font.render(f"{int(getattr(self, "nitro_charge", 0))}%", True, WHITE)
            panel.blit(status_text, (14, 104))
            panel.blit(charge_text, (panel_width - charge_text.get_width() - 14, 104))

            self.screen.blit(panel, (panel_x, panel_y))
            self.pause_button.draw(self.screen, self.tiny_font)
            self.sound_button.draw(self.screen, self.tiny_font)
=======
                self.screen.blit(badge, (24, 432 + index * 16))
=======
                self.screen.blit(badge, (24, 440 + index * 16))
>>>>>>> 5b18a38 (Add weather system updates and fix restart/HUD issues)
        else:
            badge = pg.Surface((188, 18), pg.SRCALPHA)
            badge.fill((255, 255, 255, 10))
            pg.draw.rect(badge, (*GREEN, 90), (0, 0, 188, 18), 1, border_radius=8)
            status_text = self.tiny_font.render("Road stable", True, GREEN)
            badge.blit(status_text, (8, 2))
<<<<<<< HEAD
            self.screen.blit(badge, (24, 432))
>>>>>>> e19a521 (Add garage vehicle progression system)
=======
            self.screen.blit(badge, (24, 440))
>>>>>>> 5b18a38 (Add weather system updates and fix restart/HUD issues)

    def draw_top_right_hud(self):
        panel_width = 226
        panel_height = 112
        panel_x = WIDTH - panel_width - 14
        panel_y = 12

        self.pause_button.rect.topleft = (panel_x + 122, panel_y + 10)
        self.pause_button.rect.size = (92, 30)
        self.sound_button.rect.topleft = (panel_x + 122, panel_y + 48)
        self.sound_button.rect.size = (92, 30)

        panel = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
        panel.fill((8, 14, 24, 220))
        pg.draw.rect(panel, (255, 255, 255, 42), (0, 0, panel_width, panel_height), 2, border_radius=16)

        speed_text = self.tiny_font.render(f"Speed {self.display_speed:.1f} km/h", True, WHITE)
        panel.blit(speed_text, (14, 14))

        label = self.tiny_font.render("Nitro", True, (175, 235, 255))
        panel.blit(label, (14, 40))

        bar_rect = pg.Rect(14, 62, 96, 15)
        pg.draw.rect(panel, (24, 34, 48), bar_rect, border_radius=7)
        fill_width = int(bar_rect.width * (self.nitro_charge / max(1.0, NITRO_MAX_CHARGE)))
        if fill_width > 0:
            fill_rect = pg.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
            bar_color = (64, 220, 255) if not self.nitro_active else (255, 170, 72)
            pg.draw.rect(panel, bar_color, fill_rect, border_radius=7)
        pg.draw.rect(panel, (210, 245, 255), bar_rect, 2, border_radius=7)

        if self.nitro_active:
            status = "Boost active"
            status_color = (255, 190, 92)
        elif pg.time.get_ticks() < self.nitro_cooldown_until:
            remaining = max(0.0, (self.nitro_cooldown_until - pg.time.get_ticks()) / 1000.0)
            status = f"Cooldown {remaining:.1f}s"
            status_color = YELLOW
        elif self.nitro_charge >= NITRO_MIN_ACTIVATION:
            status = "SPACE / SHIFT"
            status_color = GREEN
        else:
            status = "Collect nitro"
            status_color = GRAY

        status_text = self.tiny_font.render(status, True, status_color)
        charge_text = self.tiny_font.render(f"{int(self.nitro_charge)}%", True, WHITE)
        panel.blit(status_text, (14, 86))
        panel.blit(charge_text, (panel_width - charge_text.get_width() - 14, 86))

        self.screen.blit(panel, (panel_x, panel_y))
        self.pause_button.draw(self.screen, self.tiny_font)
        self.sound_button.draw(self.screen, self.tiny_font)

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

                  
                    text_probe = self.small_font.render(multiplier_str, True, color)
                    half_w = text_probe.get_width() // 2
                    min_x = 10 + 236 + 18 + half_w
                    max_x = WIDTH - 10 - half_w
                    x = max(min_x, min(int(x), max_x))
                    y = max(10, min(int(y), HEIGHT - 10))

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

        stage = self.small_font.render(f"Level: {self.stage}", True, WHITE)
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

        
        checkpoint_stage = self.get_checkpoint_stage()

        box_width = 470
        box_height = 400
        box_left = WIDTH // 2 - box_width // 2
        box_top = HEIGHT // 2 - box_height // 2

        box = pg.Surface((box_width, box_height), pg.SRCALPHA)
        box.fill((18, 18, 30, 248))
        pg.draw.rect(box, (255, 45, 45, 115), (0, 0, box_width, box_height), 3, border_radius=18)
        pg.draw.rect(box, (255, 255, 255, 25), (12, 12, box_width - 24, box_height - 24), 1, border_radius=14)
        self.screen.blit(box, (box_left, box_top))

        title = self.font.render("GAME OVER", True, RED)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 170))

        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 120))

        stage = self.small_font.render(f"Reached Level: {self.stage}", True, CYAN)
        self.screen.blit(stage, (WIDTH // 2 - stage.get_width() // 2, HEIGHT // 2 - 90))

        
        money_sign = "+" if self.current_level_money >= 0 else "-"
        money = self.small_font.render(f"Money Earned: {money_sign}{abs(self.current_level_money)}", True, GOLD)
        self.screen.blit(money, (WIDTH // 2 - money.get_width() // 2, box_top + 148))

        if self.is_new_high_score:
            high_score = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(high_score, (WIDTH // 2 - high_score.get_width() // 2, HEIGHT // 2 - 35))

        # Inform the player how Restart behaves: it will resume the same level.
        hint = self.tiny_font.render("Press R to restart (resumes current level).", True, GRAY)
        try:
            info_y = box_top + 6
        except Exception:
            info_y = HEIGHT // 2 + 6
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, info_y + 6))

        self.game_over_restart_button.draw(self.screen, self.small_font)
        self.game_over_menu_button.draw(self.screen, self.small_font)
        self.game_over_quit_button.draw(self.screen, self.small_font)

    def draw_stage_complete_screen(self):
        # Map-style level transition animation
        current_time = pg.time.get_ticks()

        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # card
        card_w, card_h = 760, 470
        card = pg.Surface((card_w, card_h), pg.SRCALPHA)
        card.fill((14, 18, 24, 230))
        pg.draw.rect(card, (255, 255, 255, 28), (6, 6, card_w - 12, card_h - 12), 2, border_radius=20)

        title = self.font.render("Level Complete", True, YELLOW)
        card.blit(title, (34, 24))
        subtitle = self.small_font.render(f"Level {self.completed_stage or self.stage} finished — next: Level { (self.completed_stage or self.stage) + 1 }", True, WHITE)
        card.blit(subtitle, (34, 74))

        reward_panel = pg.Surface((card_w - 68, 86), pg.SRCALPHA)
        reward_panel.fill((255, 255, 255, 12))
        pg.draw.rect(reward_panel, (255, 214, 90, 90), reward_panel.get_rect(), 2, border_radius=14)

        reward_title = self.tiny_font.render("Stage Rewards", True, GOLD)
        coin_text = self.tiny_font.render(
            f"Coins: {self.stage_coin_count} picked up (+{self.stage_coin_money} money)",
            True,
            WHITE,
        )
        distance_text = self.tiny_font.render(
            f"Distance Reward: +{self.stage_distance_reward_money}",
            True,
            CYAN,
        )
        stage_text = self.tiny_font.render(
            f"Stage Reward: +{self.stage_reward_money}",
            True,
            GREEN,
        )
        score_text = self.tiny_font.render(
            f"Score Bonus: +{self.last_stage_score_bonus}",
            True,
            WHITE,
        )
        checkpoint_note = self.tiny_font.render(
            f"Checkpoint unlocked: Level {(self.completed_stage or self.stage) + 1}",
            True,
            CYAN,
        )

        reward_panel.blit(reward_title, (18, 7))
        reward_panel.blit(coin_text, (170, 7))
        reward_panel.blit(distance_text, (18, 31))
        reward_panel.blit(stage_text, (260, 31))
        reward_panel.blit(score_text, (460, 31))
        reward_panel.blit(checkpoint_note, (18, 55))
        card.blit(reward_panel, (34, 104))
        
        # map area
        map_x, map_y = 34, 200
        map_w, map_h = card_w - 68, 190
        map_rect = pg.Rect(map_x, map_y, map_w, map_h)
        # subtle panel
        panel = pg.Surface((map_w, map_h), pg.SRCALPHA)
        panel.fill((30, 34, 40, 180))
        pg.draw.rect(panel, (255, 255, 255, 18), (0, 0, map_w, map_h), 1, border_radius=14)
        card.blit(panel, (map_x, map_y))

        # compute nodes: show 5 nodes centered on current/next
        center_index = 2
        nodes = []
        base_level = max(1, (self.completed_stage or self.stage) - 2)
        num_nodes = 5
        spacing = int((map_w - 80) / (num_nodes - 1))
        y_node = map_y + map_h // 2
        for i in range(num_nodes):
            lvl = base_level + i
            x = map_x + 40 + i * spacing
            nodes.append((lvl, (x, y_node)))

        # draw path
        path_points = [pos for (_, pos) in nodes]
        for i in range(len(path_points) - 1):
            a = path_points[i]
            b = path_points[i + 1]
            pg.draw.line(card, (200, 200, 200, 40), a, b, 6)
            pg.draw.line(card, (255, 214, 90, 140), a, b, 2)

        # draw nodes
        completed_lvl = self.completed_stage or self.stage
        next_lvl = completed_lvl + 1
        for lvl, (x, y) in nodes:
            is_completed = lvl <= completed_lvl
            color = (77, 215, 120) if is_completed else (120, 130, 142)
            outer_r = 18
            inner_r = 10
            pg.draw.circle(card, (*color, 200), (x, y), outer_r)
            pg.draw.circle(card, (18, 20, 22), (x, y), inner_r)
            num = self.tiny_font.render(str(lvl), True, WHITE if is_completed else (220, 230, 240))
            card.blit(num, num.get_rect(center=(x, y)))

        # marker animation: travels from completed node to next node
        try:
            start = self.level_transition_start or current_time
        except Exception:
            start = current_time

        anim_total = self.level_transition_duration + self.level_transition_pause
        t = (current_time - start) % anim_total
        travel_t = min(1.0, max(0.0, t / float(self.level_transition_duration)))

        # find positions for completed and next on our nodes list
        src = None
        dst = None
        for lvl, pos in nodes:
            if lvl == completed_lvl:
                src = pos
            if lvl == next_lvl:
                dst = pos
        if src is None:
            src = nodes[ max(0, center_index) ][1]
        if dst is None:
            dst = nodes[min(len(nodes)-1, center_index+1)][1]

        # simple ease in-out
        ease = (math.sin((travel_t - 0.5) * math.pi) + 1) / 2 if travel_t > 0 and travel_t < 1 else (1.0 if travel_t >= 1.0 else 0.0)
        mx = int(src[0] + (dst[0] - src[0]) * ease)
        my = int(src[1] + (dst[1] - src[1]) * ease)

        # trail
        trail_len = 6
        for i in range(trail_len):
            p = i / float(trail_len)
            tx = int(src[0] + (mx - src[0]) * p)
            ty = int(src[1] + (my - src[1]) * p)
            alpha = int(180 * (1 - p))
            pg.draw.circle(card, (255, 214, 90, alpha), (tx, ty), max(2, 6 - i))

        # marker
        pg.draw.circle(card, (255, 214, 90), (mx, my), 9)
        pg.draw.circle(card, (255, 255, 255), (mx, my), 3)

        # instructions and details
        hint = self.tiny_font.render("Press Enter or Space to continue", True, WHITE)
        card.blit(hint, (card_w - hint.get_width() - 34, card_h - 46))

        footer = self.tiny_font.render("Map shows nearby levels; progress on next run continues.", True, CYAN)
        card.blit(footer, (34, card_h - 46))

        self.screen.blit(card, (WIDTH // 2 - card_w // 2, HEIGHT // 2 - card_h // 2))

    def run(self):
        """Main game loop. Kept minimal so `atari.py` can call `game.run()`.

        The loop handles events, updates game state, draws frames, and
        enforces the configured `FPS`.
        """
        try:
            while True:
                self.clock.tick(FPS)
                self.handle_events()
                self.update()
                self.draw()
        except KeyboardInterrupt:
            # allow clean exit when run from terminal
            if self.current_music:
                pg.mixer.music.stop()
            pg.quit()
            sys.exit()
        except Exception:
            if self.current_music:
                pg.mixer.music.stop()
            pg.quit()
            raise

    def draw_game_complete_screen(self):
        # (disabled) Game complete UI removed in this flow; keep placeholder.
        return


# Developer notes and lightweight dev-tests moved here so extra files are not required.
# PHASE2_PERSON2_LIVES_CHECKLIST (originally a separate markdown file)
PHASE2_PERSON2_LIVES_CHECKLIST = '''
# Phase 2 Person 2: Lives / Collision / Game Over Verification

Purpose: this note documents the existing lives flow without changing gameplay behavior.

Safe Verification Checklist

- Player starts with `PLAYER_START_LIVES` after `reset_game()` or `start_game()`.
- A valid collision decreases `lives` by 1.
- `DAMAGE_COOLDOWN` prevents rapid repeated damage from the same contact.
- When `lives <= 0`, the existing game over flow is triggered.
- `reset_game()` restores `lives` to the starting value.
- `reset_game()` also clears cooldown-related state such as `last_damage_time` and `damage_flash_time`.
- HUD still displays lives correctly during gameplay.
- Stage progression, score, difficulty, and progress tracking continue to work as before.

Manual Test Notes

1. Start a new run and confirm the HUD shows the expected number of lives.
2. Collide with one traffic car or barrier and verify only one life is removed.
3. Keep the player overlapping the same obstacle and confirm no additional life is lost until the cooldown expires.
4. Wait for the cooldown window to pass, then confirm a new collision can reduce lives again.
5. Reduce lives to zero and confirm the current game over screen appears.
6. Restart the run and confirm lives return to the starting value.

Important References

- Lives setup and reset: `game/game.py`
- Damage cooldown constant: `game/constants.py`
- Collision and game over flow: `game/game.py`
- HUD rendering: `game/game.py`

Scope Reminder: Do not add a parallel lives system; do not modify `atari.py`.
'''


def dev_run_distance_test(frames=60, fps=60):
    """Headless developer test for runtime-only distance accumulation.

    Usage: `python -m game.game --distance-test` or call directly.
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pg.init()
    g = Game()
    g.reset_game(change_state=True)

    print("Initial distance:", g.distance)

    for i in range(frames):
        g.clock.tick(fps)
        g.update()

    print(f"Distance after {frames} frames:", int(g.distance))
    # Simulate game over to persist progress and then inspect save data
    g.enter_game_over()
    from .storage import load_save_data
    sd = load_save_data()
    print("Saved best_distance:", sd.get("best_distance", 0))

    g.reset_game()
    print("Distance after reset:", g.distance)


def dev_run_stage_test():
    """Headless developer test for stage progression behavior.

    Usage: `python -m game.game --stage-test` or call directly.
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pg.init()
    g = Game()
    g.reset_game(change_state=True)

    cfg = g.current_stage_config
    target = cfg.get("distance_target", 0)
    print("Initial stage:", g.stage, "target:", target)

    # Just below target: no finish sign yet
    g.stage_progress_distance = max(0, target - 1)
    g.check_stage_progression(pg.time.get_ticks())
    print("After below-target progress: finish_sign", g.finish_sign is not None, "state", g.state.name)

    # Reach the target: finish sign should appear and gameplay should remain on the stage
    g.stage_progress_distance = target
    g.check_stage_progression(pg.time.get_ticks())
    print("After target reached: finish_sign", g.finish_sign is not None, "state", g.state.name)

    # Force a collision with the finish sign, then verify stage complete state
    if g.finish_sign is not None:
        g.finish_sign.y = g.player.y - 10
        g.finish_sign.x = g.player.x
        g.update()
    print("After finish sign collision: state", g.state.name, "completed_stage", g.completed_stage)

    # Simulate Enter/Space flow into next stage
    g.start_next_stage()
    print("After start_next_stage: stage", g.stage, "state", g.state.name, "finish_sign", g.finish_sign is not None)

    g.reset_game()
    print("After reset: stage", g.stage, "stage_progress_distance", int(g.stage_progress_distance), "finish_sign", g.finish_sign is not None)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Developer runner for game module")
    parser.add_argument("--distance-test", action="store_true", help="Run distance headless test")
    parser.add_argument("--stage-test", action="store_true", help="Run stage progression headless test")
    args = parser.parse_args()
    if args.distance_test:
        dev_run_distance_test()
    elif args.stage_test:
        dev_run_stage_test()
    else:
        # If module executed directly without flags, start the game loop for convenience
        pg.init()
        pg.mixer.init()
        Game().run()
