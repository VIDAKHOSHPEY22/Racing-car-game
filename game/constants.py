WIDTH, HEIGHT = 800, 600
FPS = 60
BASE_SPEED = 10
PLAYER_START_LIVES = 3
DEFAULT_STAGE = 1
DEFAULT_DIFFICULTY = "Medium"
MENU_CARD_WIDTH = 560
MENU_CARD_HEIGHT = 500

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
ORANGE = (255, 140, 0)
PURPLE = (180, 60, 180)
PINK = (255, 105, 180)
NAVY = (15, 28, 45)
TEAL = (40, 140, 160)
GOLD = (214, 180, 64)
SLATE = (24, 31, 44)
SURFACE = (18, 20, 30)
SURFACE_ALT = (32, 40, 58)

CAR_SKINS = [
    {"name": "Blue Racer", "color": BLUE, "type": "sedan"},
    {"name": "Red Speedster", "color": RED, "type": "sedan"},
    {"name": "Green Machine", "color": GREEN, "type": "suv"},
    {"name": "Yellow Lightning", "color": YELLOW, "type": "sedan"},
    {"name": "Purple Power", "color": PURPLE, "type": "suv"},
    {"name": "Orange Blaze", "color": ORANGE, "type": "truck"},
    {"name": "Cyan Cruiser", "color": CYAN, "type": "sedan"},
    {"name": "Pink Dream", "color": PINK, "type": "suv"},
]

DIFFICULTY_SETTINGS = {
    "Easy": {"base_speed": 8, "obstacle_freq": 1500, "speed_increase": 0.1, "obstacle_speed": (6, 9)},
    "Medium": {"base_speed": 10, "obstacle_freq": 1200, "speed_increase": 0.15, "obstacle_speed": (8, 12)},
    "Hard": {"base_speed": 12, "obstacle_freq": 900, "speed_increase": 0.2, "obstacle_speed": (10, 15)},
}
