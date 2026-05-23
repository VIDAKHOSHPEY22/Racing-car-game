from .game import Game
try:
	from . import coin_patch
	coin_patch.apply_patch(Game)
except Exception:
	pass
try:
	from . import collision_patch
	collision_patch.apply_patch(Game)
except Exception:
	pass
try:
	from . import stage_reward_patch
	stage_reward_patch.apply_patch(Game)
except Exception:
	pass
