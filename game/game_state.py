from enum import Enum, auto


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    STAGE_COMPLETE = auto()
    GAME_OVER = auto()
    HIGH_SCORE = auto()
    GARAGE = auto()
