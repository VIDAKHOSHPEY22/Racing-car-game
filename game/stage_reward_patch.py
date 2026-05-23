"""Runtime patch for stage-completion money rewards."""

from . import constants as const


def calculate_stage_rewards(self, stage_id):
    stage_id = max(1, int(stage_id))
    score_bonus = const.STAGE_CLEAR_SCORE_BONUS + stage_id * const.STAGE_LEVEL_SCORE_MULTIPLIER
    money_bonus = const.STAGE_CLEAR_MONEY_BONUS + (stage_id - 1) * const.STAGE_LEVEL_MONEY_MULTIPLIER
    return int(score_bonus), int(money_bonus)


def apply_patch(GameClass):
    GameClass.calculate_stage_rewards = calculate_stage_rewards
