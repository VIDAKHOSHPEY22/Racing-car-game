"""Runtime patch to add coin spawn/collect money behavior to Game class.
This keeps changes minimal and avoids large rewrites of game/game.py.
"""
import random
import pygame as pg
from . import constants as const
from .game_state import GameState
# Use conservative defaults when constants are not present in this branch
COIN_MAX_ACTIVE = getattr(const, 'COIN_MAX_ACTIVE', {'Easy': 2, 'Medium': 2, 'Hard': 2})
COIN_CHAIN_LENGTH = getattr(const, 'COIN_CHAIN_LENGTH', 3)
COIN_CHAIN_VERTICAL_SPACING = getattr(const, 'COIN_CHAIN_VERTICAL_SPACING', 36)
COIN_RADIUS = getattr(const, 'COIN_RADIUS', 12)
COIN_SPAWN_BASE_INTERVAL = getattr(const, 'COIN_SPAWN_BASE_INTERVAL', { 'Easy': 2200, 'Medium': 2000, 'Hard': 1800 })
COIN_SPAWN_MIN_INTERVAL = getattr(const, 'COIN_SPAWN_MIN_INTERVAL', 800)
COIN_SPAWN_STAGE_STEP = getattr(const, 'COIN_SPAWN_STAGE_STEP', 40)
COIN_CHAIN_SPAWN_BASE_CHANCE = getattr(const, 'COIN_CHAIN_SPAWN_BASE_CHANCE', { 'Easy': 0.10, 'Medium': 0.10, 'Hard': 0.07 })
COIN_CHAIN_SPAWN_STAGE_STEP = getattr(const, 'COIN_CHAIN_SPAWN_STAGE_STEP', 0.02)
COIN_CHAIN_SPAWN_MAX_CHANCE = getattr(const, 'COIN_CHAIN_SPAWN_MAX_CHANCE', 0.30)
COIN_RED_SPAWN_BASE_CHANCE = getattr(const, 'COIN_RED_SPAWN_BASE_CHANCE', { 'Easy': 0.03, 'Medium': 0.025, 'Hard': 0.02 })
COIN_RED_SPAWN_STAGE_STEP = getattr(const, 'COIN_RED_SPAWN_STAGE_STEP', 0.01)
COIN_RED_SPAWN_MAX_CHANCE = getattr(const, 'COIN_RED_SPAWN_MAX_CHANCE', 0.08)
GOLD_COIN_BASE_CHANCE = getattr(const, 'GOLD_COIN_BASE_CHANCE', {'Easy': 0.03, 'Medium': 0.025, 'Hard': 0.02})
GOLD_COIN_STAGE_STEP = getattr(const, 'GOLD_COIN_STAGE_STEP', 0.004)
GOLD_COIN_MAX_CHANCE = getattr(const, 'GOLD_COIN_MAX_CHANCE', 0.08)


def _get_coin_spawn_interval(self):
    cfg = getattr(self, "current_stage_config", {}) or {}
    base_interval = COIN_SPAWN_BASE_INTERVAL.get(self.selected_difficulty, 1900)
    stage_id = max(1, int(getattr(self, "stage", 1)))
    traffic_density = max(0.6, float(cfg.get("traffic_density", 1.0)))
    stage_penalty = (stage_id - 1) * COIN_SPAWN_STAGE_STEP
    interval = int((base_interval + stage_penalty) / traffic_density)
    return max(COIN_SPAWN_MIN_INTERVAL, interval)


def _choose_coin_lane_ratio(self):
    lane = random.randint(0, 2)
    ratio = (lane + 0.5) / 3
    if lane == 1 and random.random() < 0.6:
        ratio = max(0.34, min(0.66, 0.5 + random.uniform(-0.12, 0.12)))
    return ratio


def _get_coin_spawn_variant(self):
    stage_id = max(1, int(getattr(self, "stage", 1)))
    diff = getattr(self, "selected_difficulty", None)
    base_chance = float(GOLD_COIN_BASE_CHANCE.get(diff, 0.025))
    stage_bonus = max(0, stage_id - 1)
    gold_chance = min(GOLD_COIN_MAX_CHANCE, base_chance + stage_bonus * GOLD_COIN_STAGE_STEP)
    if random.random() < gold_chance:
        return "gold"
    return "normal"


def _get_coin_collision_rect(self, coin):
    radius = max(1, int(getattr(coin, "radius", 12)))
    return pg.Rect(int(coin.x - radius), int(coin.y - radius), radius * 2, radius * 2)


def can_spawn_coin_pickup(self, coin_pickups):
    pickups = coin_pickups if isinstance(coin_pickups, (list, tuple)) else [coin_pickups]
    if not pickups:
        return False

    for pickup in pickups:
        new_rect = _get_coin_collision_rect(self, pickup)
        for obstacle in getattr(self, "obstacles", []):
            try:
                obstacle_rect = self.get_obstacle_rect(obstacle)
            except Exception:
                continue
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
    if getattr(self, "finish_sign", None) is not None:
        return
    coin_capacity = int(getattr(self, "max_active_coins", 2)) + COIN_CHAIN_LENGTH - 1
    if len(getattr(self, "coins", [])) >= coin_capacity:
        return
    last = int(getattr(self, "last_coin_time", 0))
    freq = int(getattr(self, "coin_frequency", 1900))
    if current_time - last <= freq:
        return

    coin_ratio = self._choose_coin_lane_ratio()
    coin_y = -50
    coin_variant = forced_variant or _get_coin_spawn_variant(self)
    new_coin = _create_coin_pickup(self, coin_y, coin_ratio, variant=coin_variant)
    if not can_spawn_coin_pickup(self, new_coin):
        return
    self.coins.append(new_coin)
    self.last_coin_time = current_time


def collect_coin_pickup(self, coin, current_time):
    coin_value = max(0, int(getattr(coin, "money_value", 10)))
    self.stage_coin_count = int(getattr(self, "stage_coin_count", 0)) + 1
    self.stage_coin_money = int(getattr(self, "stage_coin_money", 0)) + coin_value
    current_level_money = int(getattr(self, "current_level_money", 0)) + coin_value
    session_money = int(getattr(self, "session_money", 0)) + coin_value
    self.current_level_money = current_level_money
    self.session_money = session_money
    self.money_popup_amount = coin_value
    self.money_popup_start_time = int(current_time or pg.time.get_ticks())
    self.multiplier_display_time = int(current_time or pg.time.get_ticks())
    self.multiplier_text_pos = (coin.x, coin.y)
    self.consecutive_actions = int(getattr(self, "consecutive_actions", 0)) + 1
    try:
        self.update_multiplier()
    except Exception:
        pass
    try:
        if getattr(self, "coin_sound", None) and not getattr(self, "music_muted", False):
            self.coin_sound.play()
    except Exception:
        pass


def apply_patch(GameClass):
    GameClass.can_spawn_coin_pickup = can_spawn_coin_pickup
    GameClass.spawn_coin_pickup = spawn_coin_pickup
    GameClass.collect_coin_pickup = collect_coin_pickup
    # utility helpers (weakly bound)
    GameClass._create_coin_pickup = _create_coin_pickup
    GameClass._choose_coin_lane_ratio = _choose_coin_lane_ratio
    GameClass.get_coin_spawn_variant = _get_coin_spawn_variant
    GameClass.get_coin_spawn_interval = _get_coin_spawn_interval
    GameClass.get_coin_collision_rect = _get_coin_collision_rect

    orig_update = getattr(GameClass, 'update', None)
    orig_reset_game = getattr(GameClass, 'reset_game', None)
    orig_enter_game_over = getattr(GameClass, 'enter_game_over', None)
    orig_enter_stage_complete = getattr(GameClass, 'enter_stage_complete', None)

    def _patched_update(self, *args, **kwargs):
        if getattr(self, 'state', None) == GameState.STAGE_COMPLETE:
            if not getattr(self, 'paused', False):
                advance_at = getattr(self, 'level_complete_auto_advance_at', None)
                if advance_at is not None and pg.time.get_ticks() >= int(advance_at):
                    try:
                        self.start_next_stage(pg.time.get_ticks())
                    except Exception:
                        pass
            return

        pre_lives = int(getattr(self, 'lives', 0))
        pre_visible_money = int(getattr(self, 'total_money', 0)) + int(getattr(self, 'current_level_money', 0)) + int(getattr(self, 'session_money', 0))

        if orig_update:
            result = orig_update(self, *args, **kwargs)
        else:
            result = None

        if int(getattr(self, 'lives', 0)) < pre_lives:
            post_visible_money = int(getattr(self, 'total_money', 0)) + int(getattr(self, 'current_level_money', 0)) + int(getattr(self, 'session_money', 0))
            if post_visible_money >= pre_visible_money:
                try:
                    self.apply_collision_penalty(pg.time.get_ticks(), getattr(self, 'stage', 1))
                except Exception:
                    pass

        return result

    def _patched_reset_game(self, *args, **kwargs):
        result = None
        if orig_reset_game:
            result = orig_reset_game(self, *args, **kwargs)
        # Keep both legacy and current run-money fields in sync.
        self.current_level_money = 0
        self.session_money = 0
        # Record the stage the run started on so Restart from GAME_OVER can
        # explicitly return to that starting level.
        try:
            self.run_start_stage = int(getattr(self, 'stage', const.DEFAULT_STAGE))
        except Exception:
            self.run_start_stage = getattr(self, 'stage', const.DEFAULT_STAGE)
        # If a temporary `_force_next_start_stage` was set by the caller,
        # honor it (this avoids relying on kwargs propagation through
        # multiple wrapper layers).
        if hasattr(self, '_force_next_start_stage'):
            try:
                desired = int(getattr(self, '_force_next_start_stage'))
                desired = max(1, desired)
                self.stage = desired
                self.level = desired
                try:
                    self.run_start_stage = desired
                except Exception:
                    pass
            except Exception:
                pass
            try:
                delattr(self, '_force_next_start_stage')
            except Exception:
                try:
                    del self._force_next_start_stage
                except Exception:
                    pass
        return result

    def _patched_enter_game_over(self, *args, **kwargs):
        # Preserve score/stage progress, but do not add run money to the
        # persistent wallet on failure.
        try:
            from .storage import load_save_data, save_save_data, read_high_score

            save_data = load_save_data()
            previous_best_score = read_high_score()
            self.is_new_high_score = self.score > previous_best_score
            save_data['high_score'] = max(int(save_data.get('high_score', 0)), int(self.score))
            save_data['best_stage'] = max(int(save_data.get('best_stage', 1)), int(self.stage))
            save_data['total_score'] = int(save_data.get('total_score', 0)) + int(self.score)
            save_data['games_played'] = int(save_data.get('games_played', 0)) + 1
            try:
                save_data['best_distance'] = max(int(save_data.get('best_distance', 0)), int(getattr(self, 'distance', 0)))
            except Exception:
                pass
            self.save_data = save_save_data(save_data)
            self.best_score = self.save_data['high_score']
            self.total_money = self.save_data['total_money']
            # Roll back transient run money so UI shows persisted saved money.
            try:
                self.current_level_money = 0
                self.session_money = 0
            except Exception:
                pass
            self.best_stage = self.save_data['best_stage']
            self.games_played = self.save_data['games_played']
            self.total_score = self.save_data['total_score']
            # Ensure the next reset honors the run start stage so Restart
            # returns the player to the level they began on.
            try:
                self._force_next_start_stage = int(getattr(self, 'run_start_stage', getattr(self, 'stage', const.DEFAULT_STAGE)))
            except Exception:
                self._force_next_start_stage = getattr(self, 'run_start_stage', getattr(self, 'stage', const.DEFAULT_STAGE))
            self.set_state(GameState.GAME_OVER)
            return None
        except Exception:
            if orig_enter_game_over:
                return orig_enter_game_over(self, *args, **kwargs)
            return None

    def _patched_enter_stage_complete(self, current_time=None):
        self.completed_stage = self.stage
        self.finish_sign = None
        self.obstacles = []
        self.coins = []
        self.nitro_pickups = []
        self.clear_hazard_effects()
        if current_time is None:
            current_time = pg.time.get_ticks()

        self.stop_nitro_boost(current_time, start_cooldown=False)

        # Fixed stage-complete money reward: +100 each level.
        self.last_stage_score_bonus = 0
        self.last_stage_money_bonus = 100
        self.last_stage_bonus_total = self.last_stage_score_bonus + self.last_stage_money_bonus
        self.score += self.last_stage_score_bonus
        # Show the fixed level reward as a popup; persist below.
        self.money_popup_amount = self.last_stage_money_bonus
        self.money_popup_start_time = current_time

        try:
            from .storage import load_save_data, save_save_data

            save_data = load_save_data()
            # Persist the transient level result first (without the fixed +100 bonus):
            # saved_total := previous_saved + run_current
            run_current = int(getattr(self, 'current_level_money', 0))
            start_saved = int(save_data.get('total_money', 0))
            mid_total = max(0, start_saved + run_current)

            # Update summary fields once and persist the mid_total
            save_data['high_score'] = max(int(save_data.get('high_score', 0)), int(self.score))
            save_data['best_stage'] = max(int(save_data.get('best_stage', 1)), int(self.stage))
            save_data['total_money'] = mid_total
            save_data['total_score'] = int(save_data.get('total_score', 0)) + int(self.score)
            save_data['games_played'] = int(save_data.get('games_played', 0)) + 1
            try:
                save_data['best_distance'] = max(int(save_data.get('best_distance', 0)), int(getattr(self, 'distance', 0)))
            except Exception:
                pass

            # First persist: current money saved (no bonus yet)
            self.save_data = save_save_data(save_data)
            self.total_money = self.save_data['total_money']
            self.best_score = self.save_data['high_score']
            self.best_stage = self.save_data['best_stage']
            self.games_played = self.save_data['games_played']
            self.total_score = self.save_data['total_score']

            # Then apply the fixed level-complete bonus (+100) and persist only the money change.
            try:
                save_data = load_save_data()
                bonus = int(self.last_stage_money_bonus)
                save_data['total_money'] = max(0, int(save_data.get('total_money', 0)) + bonus)
                # Persist the updated wallet. Do not re-increment games_played/total_score.
                self.save_data = save_save_data(save_data)
                self.total_money = self.save_data['total_money']
            except Exception:
                pass
        except Exception:
            pass

        # After persisting, reset transient level money buckets.
        self.current_level_money = 0
        self.session_money = 0

        self.register_status_message(
            f"Level {self.stage} complete: +{self.last_stage_score_bonus} score, +{self.last_stage_money_bonus} money",
            current_time,
            duration=1800,
        )
        self.level_complete_auto_advance_at = current_time + 1800
        self.set_state(GameState.STAGE_COMPLETE)
        try:
            self.level_transition_start = pg.time.get_ticks()
        except Exception:
            self.level_transition_start = current_time

    # Ensure essential coin-related attributes exist after initialization
    orig_init = getattr(GameClass, '__init__', None)

    def _patched_init(self, *args, **kwargs):
        if orig_init:
            orig_init(self, *args, **kwargs)
        # minimal defaults to make coin logic safe
        if not hasattr(self, 'coins'):
            self.coins = []
        if not hasattr(self, 'last_coin_time'):
            self.last_coin_time = 0
        if not hasattr(self, 'coin_frequency'):
            self.coin_frequency = 2000
        if not hasattr(self, 'max_active_coins'):
            self.max_active_coins = int(COIN_MAX_ACTIVE.get(getattr(self, 'selected_difficulty', None), 2))
        if not hasattr(self, 'current_level_money'):
            self.current_level_money = 0
        if not hasattr(self, 'session_money'):
            self.session_money = 0
        # minimal defaults only
        if not hasattr(self, 'current_level_money'):
            self.current_level_money = 0
        if not hasattr(self, 'session_money'):
            self.session_money = 0
        if not hasattr(self, 'level_complete_auto_advance_at'):
            self.level_complete_auto_advance_at = None

    GameClass.__init__ = _patched_init
    GameClass.update = _patched_update
    GameClass.reset_game = _patched_reset_game
    GameClass.enter_game_over = _patched_enter_game_over
    GameClass.enter_stage_complete = _patched_enter_stage_complete
