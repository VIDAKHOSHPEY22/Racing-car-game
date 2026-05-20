import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from game.game import Game
from game.game_state import GameState
from game.coin import Coin
from game.hazard import Hazard
from game import storage
from game.constants import ECONOMY_DISTANCE_REWARD_STEP
from unittest.mock import patch


class DummyRoad:
    def get_travel_x(self, y, ratio, width):
        return int(100 + ratio * 300)


class DummyCoin:
    def __init__(self, x=140, y=120, money_value=7, score_value=5):
        self.x = x
        self.y = y
        self.money_value = money_value
        self.score_value = score_value


def build_game_stub(stage=2, difficulty="Medium"):
    game = Game.__new__(Game)
    game.selected_difficulty = difficulty
    game.stage = stage
    game.level = stage
    game.current_stage_config = {
        "traffic_density": 0.8,
        "distance_target": 500,
        "enemy_speed_multiplier": 1.0,
    }
    game.road = DummyRoad()
    game.player = SimpleNamespace(x=350, y=450, width=50, height=80, max_speed_bonus=0.0)
    game.obstacles = []
    game.coins = []
    game.nitro_pickups = []
    game.finish_sign = None
    game.score = 0
    game.total_money = 100
    game.current_level_money = 0
    game.selected_skin = 0
    game.stage_coin_count = 0
    game.stage_coin_money = 0
    game.stage_distance_reward_money = 0
    game.stage_reward_money = 0
    game.stage_collision_penalty_money = 0
    game.next_distance_reward_at = ECONOMY_DISTANCE_REWARD_STEP
    game.money_popup_amount = 0
    game.money_popup_start_time = 0
    game.multiplier_display_time = 0
    game.multiplier_text_pos = (0, 0)
    game.consecutive_actions = 0
    game.score_multiplier = 1.0
    game.last_coin_time = -9999
    game.coin_frequency = 0
    game.last_stage_score_bonus = 0
    game.last_stage_money_bonus = 0
    game.last_stage_bonus_total = 0
    game.state = GameState.PLAYING
    game.music_muted = True
    game.coin_sound = None
    game.current_music = False
    game.nitro_active = False
    game.nitro_charge = 0
    game.nitro_cooldown_until = 0
    game.last_damage_time = 0
    game.damage_flash_time = 0
    game.paused = False
    game.lives = 3
    game.current_speed = 10
    game.base_speed = 10
    game.stage_progress_distance = 0
    game.best_score = 0
    game.best_stage = stage
    game.games_played = 0
    game.total_score = 0
    game.status_message = ""
    game.status_message_until = 0
    game.clear_hazard_effects()
    return game


class EconomySystemTests(unittest.TestCase):
    def test_level_one_starts_with_hundred_money(self):
        game = build_game_stub(stage=1)
        game.total_money = 734
        game.save_data = {"total_money": 734}
        game.selected_skin = 0
        game.player_color = (50, 120, 220)
        game.player_type = "sedan"

        original_save_save_data = storage.save_save_data

        def fake_save_save_data(data):
            return data

        storage.save_save_data = fake_save_save_data
        try:
            game.stage = 1
            game.level = 1
            game._apply_level_one_wallet_floor(previous_state=GameState.MENU)
            self.assertEqual(game.total_money, 100)
            self.assertEqual(game.save_data["total_money"], 100)
        finally:
            storage.save_save_data = original_save_save_data

    def test_game_over_restart_keeps_saved_money(self):
        game = build_game_stub(stage=3)
        original_save_file = storage.SAVE_FILE

        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.SAVE_FILE = Path(tmp_dir) / "save_data.json"
            try:
                storage.save_save_data({"total_money": 734})
                game.total_money = 0
                game.save_data = {"total_money": 0}

                game._restore_money_after_game_over()

                self.assertEqual(game.total_money, 734)
                self.assertEqual(game.save_data["total_money"], 734)
            finally:
                storage.SAVE_FILE = original_save_file

    def test_stage_distance_target_grows_with_level(self):
        game = build_game_stub(stage=1)
        stage_1 = game.get_stage_distance_target(1)
        stage_2 = game.get_stage_distance_target(2)
        stage_3 = game.get_stage_distance_target(3)

        self.assertLess(stage_1, stage_2)
        self.assertLess(stage_2, stage_3)

    def test_coin_spawn_creates_pickup(self):
        game = build_game_stub()
        with patch.object(Game, "_choose_coin_lane_ratio", return_value=0.5):
            game.spawn_coin_pickup(current_time=1000, forced_variant="normal")

        self.assertEqual(len(game.coins), 1)
        coin = game.coins[0]
        self.assertEqual(coin.y, -50)
        self.assertTrue(hasattr(coin, "road_ratio"))
        self.assertGreaterEqual(coin.road_ratio, 0.0)
        self.assertLessEqual(coin.road_ratio, 1.0)

    def test_coin_chain_spawns_three_normal_coins(self):
        game = build_game_stub(stage=4)

        with patch.object(Game, "_choose_coin_lane_ratio", return_value=0.5):
            game.spawn_coin_pickup(current_time=1000, forced_variant="chain")

        self.assertEqual(len(game.coins), 3)
        self.assertTrue(all(getattr(coin, "money_value", 10) == 10 for coin in game.coins))
        self.assertEqual([coin.y for coin in game.coins], [-50, -50 - 58, -50 - 58 * 2])
        self.assertTrue(all(coin.road_ratio == 0.5 for coin in game.coins))

    def test_red_coin_uses_bonus_value_and_style(self):
        coin = Coin(120, 120, variant="red")

        self.assertEqual(getattr(coin, "money_value", 0), 75)
        self.assertEqual(coin.variant, "red")
        self.assertGreater(coin.radius, 12)

    def test_blue_bonus_coin_increases_current_level_money(self):
        game = build_game_stub()
        coin = Coin(140, 120, variant="red")

        game.collect_coin_pickup(coin, current_time=1111)

        self.assertEqual(game.stage_coin_count, 1)
        self.assertEqual(game.stage_coin_money, 75)
        self.assertEqual(game.current_level_money, 75)
        self.assertEqual(game.money_popup_amount, 75)

    def test_coin_spawn_avoids_obstacle_overlap(self):
        game = build_game_stub()
        blocker = SimpleNamespace(x=230, y=-50, width=64, height=64)
        game.obstacles = [blocker]

        with patch.object(Game, "_choose_coin_lane_ratio", return_value=0.5):
            game.spawn_coin_pickup(current_time=1000, forced_variant="normal")

        self.assertEqual(len(game.coins), 0)

    def test_coin_pickup_increases_money(self):
        game = build_game_stub()
        coin = DummyCoin()

        game.collect_coin_pickup(coin, current_time=1234)

        self.assertEqual(game.stage_coin_count, 1)
        self.assertEqual(game.stage_coin_money, 7)
        self.assertEqual(game.current_level_money, 7)
        self.assertEqual(game.money_popup_amount, 7)

    def test_distance_rewards_award_money_at_steps(self):
        game = build_game_stub()
        game.distance = 1100
        game.next_distance_reward_at = ECONOMY_DISTANCE_REWARD_STEP

        game.apply_distance_rewards(current_time=4321)

        self.assertEqual(game.stage_distance_reward_money, 20)
        self.assertEqual(game.current_level_money, 20)
        self.assertEqual(game.next_distance_reward_at, ECONOMY_DISTANCE_REWARD_STEP * 3)

    def test_stage_complete_awards_stage_reward(self):
        game = build_game_stub(stage=2)
        game.current_level_money = 250
        game.score = 10

        original_save_file = storage.SAVE_FILE
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.SAVE_FILE = Path(tmp_dir) / "save_data.json"
            try:
                storage.save_save_data(storage._default_save_data())
                game.enter_stage_complete(current_time=5000)

                self.assertEqual(game.state, GameState.STAGE_COMPLETE)
                self.assertEqual(game.stage_reward_money, 100)
                self.assertEqual(game.last_stage_money_bonus, 100)
                self.assertEqual(game.total_money, 450)
                self.assertEqual(game.current_level_money, 0)
                self.assertEqual(game.save_data["total_money"], 450)
            finally:
                storage.SAVE_FILE = original_save_file

    def test_collision_penalty_reduces_money_by_stage(self):
        game = build_game_stub(stage=3)

        penalty = game.apply_collision_penalty(current_time=2222)

        self.assertEqual(penalty, 150)
        self.assertEqual(game.stage_collision_penalty_money, 150)
        self.assertEqual(game.current_level_money, -150)
        self.assertEqual(game.money_popup_amount, -150)

    def test_barrier_collision_uses_same_penalty_rule(self):
        game = build_game_stub(stage=4)
        barrier = Hazard(0, 0, "barrier", 0)

        self.assertTrue(game.should_apply_collision_penalty(barrier))

        penalty = game.apply_collision_penalty(current_time=3333)

        self.assertEqual(penalty, 205)
        self.assertEqual(game.stage_collision_penalty_money, 205)
        self.assertEqual(game.current_level_money, -205)

    def test_game_over_discards_unfinished_level_money(self):
        game = build_game_stub(stage=3)
        original_save_file = storage.SAVE_FILE

        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.SAVE_FILE = Path(tmp_dir) / "save_data.json"
            try:
                storage.save_save_data({"total_money": 250})
                game.current_level_money = 80
                game.save_data = {"total_money": 250}
                game.distance = 900

                game.enter_game_over()

                self.assertEqual(game.total_money, 250)
                self.assertEqual(game.save_data["total_money"], 250)
            finally:
                storage.SAVE_FILE = original_save_file

    def test_save_load_preserves_money(self):
        original_save_file = storage.SAVE_FILE

        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.SAVE_FILE = Path(tmp_dir) / "save_data.json"
            try:
                storage.save_save_data(storage._default_save_data())
                storage.update_progress(score=12, stage=3, money_earned=375, distance=900)
                loaded = storage.load_save_data()

                self.assertEqual(loaded["total_money"], 475)
                self.assertGreaterEqual(loaded["best_stage"], 3)
                self.assertGreaterEqual(loaded["best_distance"], 900)
            finally:
                storage.SAVE_FILE = original_save_file

    def test_load_old_save_without_money_fields(self):
        original_save_file = storage.SAVE_FILE

        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.SAVE_FILE = Path(tmp_dir) / "save_data.json"
            try:
                storage.SAVE_FILE.write_text(json.dumps({"selected_skin": 0}), encoding="utf-8")
                loaded = storage.load_save_data()

                self.assertIn("total_money", loaded)
                self.assertEqual(loaded["total_money"], 100)
            finally:
                storage.SAVE_FILE = original_save_file


if __name__ == "__main__":
    unittest.main()
