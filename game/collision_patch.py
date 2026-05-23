"""Runtime patch for collision money penalties."""

import pygame as pg

from . import constants as const
from .car import Car
from .hazard import Hazard


def calculate_collision_penalty(self, stage_id=None):
    stage_value = getattr(self, "stage", 1) if stage_id is None else stage_id
    stage_id = max(1, int(stage_value))
    return int(const.COLLISION_MONEY_PENALTY_BASE + (stage_id - 1) * const.COLLISION_MONEY_PENALTY_STAGE_STEP)


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

    remaining_penalty = penalty
    # Deduct penalty from transient current_level_money first, then from saved total_money.
    current_level_money = int(getattr(self, "current_level_money", 0))
    level_money_loss = min(max(0, current_level_money), remaining_penalty)
    current_level_money = max(0, current_level_money - level_money_loss)
    remaining_penalty -= level_money_loss

    if remaining_penalty > 0:
        self.total_money = max(0, int(getattr(self, "total_money", 0)) - remaining_penalty)
        if isinstance(getattr(self, "save_data", None), dict):
            self.save_data["total_money"] = self.total_money

    self.current_level_money = current_level_money
    # Maintain session_money for compatibility (mirror of current_level_money)
    self.session_money = max(0, int(getattr(self, 'session_money', 0)) - level_money_loss)

    self.stage_collision_penalty_money = int(getattr(self, "stage_collision_penalty_money", 0)) + penalty
    self.money_popup_amount = -penalty
    self.money_popup_start_time = int(current_time or pg.time.get_ticks())
    self.register_status_message(f"Crash penalty -{penalty}", int(current_time or pg.time.get_ticks()), duration=900)
    return penalty


def apply_patch(GameClass):
    GameClass.calculate_collision_penalty = calculate_collision_penalty
    GameClass.should_apply_collision_penalty = should_apply_collision_penalty
    GameClass.apply_collision_penalty = apply_collision_penalty
