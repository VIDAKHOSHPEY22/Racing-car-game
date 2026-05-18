WIDTH, HEIGHT = 800, 600
FPS = 60
BASE_SPEED = 10
PLAYER_START_LIVES = 3
DEFAULT_STAGE = 1
DEFAULT_DIFFICULTY = "Medium"
MENU_CARD_WIDTH = 560
MENU_CARD_HEIGHT = 500

SAVE_FILE_NAME = "save_data.json"

COIN_SCORE_VALUE = 5
COIN_MONEY_VALUE = 1
OBSTACLE_PASS_SCORE = 1
TRACK_OBJECT_WEIGHTS = {
    "Easy": {
        "car": 74,
        "oil_spill": 8,
        "water_puddle": 7,
        "pothole": 5,
        "barrier": 3,
    },
    "Medium": {
        "car": 64,
        "oil_spill": 12,
        "water_puddle": 10,
        "pothole": 8,
        "barrier": 6,
    },
    "Hard": {
        "car": 52,
        "oil_spill": 16,
        "water_puddle": 14,
        "pothole": 12,
        "barrier": 10,
    },
}
HAZARD_EFFECT_DURATIONS = {
    "oil_spill": 1400,
    "water_puddle": 1900,
    "pothole": 1100,
}

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

# Toggle whether the finish sign is visually drawn on screen.
# Set to False to keep an invisible trigger (finish still works).
# User requested visible finish line at end of each level — enable it.
SHOW_FINISH_SIGN = True

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
    "Easy": {
        "base_speed": 8,
        "obstacle_freq": 2200,
        "speed_increase": 0.08,
        "obstacle_speed": (5, 8),
        "max_speed": 80,
        "spawn_spacing": 190,
        "freq_floor": 1450,
        "freq_step": 70,
    },
    "Medium": {
        "base_speed": 10,
        "obstacle_freq": 1650,
        "speed_increase": 0.12,
        "obstacle_speed": (7, 10),
        "max_speed": 120,
        "spawn_spacing": 155,
        "freq_floor": 1100,
        "freq_step": 85,
    },
    "Hard": {
        "base_speed": 12,
        "obstacle_freq": 1180,
        "speed_increase": 0.18,
        "obstacle_speed": (9, 13),
        "max_speed": 160,
        "spawn_spacing": 125,
        "freq_floor": 760,
        "freq_step": 100,
    },
}

DEFAULT_SAVE_DATA = {
    "high_score": 0,
    "total_money": 0,
    "best_stage": DEFAULT_STAGE,
    "best_distance": 0,
    "games_played": 0,
    "total_score": 0,
    "selected_skin": 0,
    "selected_difficulty": DEFAULT_DIFFICULTY,
}

# Stage configuration definitions. Keep these small and data-driven so future
# systems (weather, night, curves) can be attached via the 'future_*' fields.
# Only tune minimal gameplay-facing values here.
STAGE_DEFINITIONS = {
    1: {
        "stage_id": 1,
        "distance_target": 560,  # meters to reach finish line
        "enemy_speed_multiplier": 0.9,
        "obstacle_frequency": 2400,
        "traffic_density": 0.6,  # 0..1 relative density
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 8,  # extra meters to cross finish line
    },
    2: {
        "stage_id": 2,
        "distance_target": 900,
        "enemy_speed_multiplier": 1.04,
        "obstacle_frequency": 2050,
        "traffic_density": 0.68,
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 8,
    },
    3: {
        "stage_id": 3,
        "distance_target": 1220,
        "enemy_speed_multiplier": 1.14,
        "obstacle_frequency": 1700,
        "traffic_density": 0.78,
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 10,
    },
    4: {
        "stage_id": 4,
        "distance_target": 1600,
        "enemy_speed_multiplier": 1.24,
        "obstacle_frequency": 1500,
        "traffic_density": 0.86,
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 10,
    },
}

# Maximum stage players can reach before the game ends.
# (Previous STAGE_MAX removed — stages are unbounded by this constant)

# Player speed / physics tuning (units: speed units per second)
# Default player forward speed while driving
PLAYER_SPEED_DEFAULT = 50.0
# ACCELERATION: how many speed units are added per second while accelerating
ACCELERATION = 10.0
# FRICTION: how many speed units are removed per second when not accelerating
FRICTION = 5.0
# Speed bounds (visual/player velocity)
MIN_SPEED = 30.0       # minimum allowed player speed (brake limit)
MAX_SPEED = 120.0     # max allowed player speed
# deceleration per second when braking (S / Down)
BRAKE_DECEL = 40.0
# Health system
DAMAGE_COOLDOWN = 1500  # milliseconds


WEATHER_SPEED_LIMIT_RATIOS = {
    "rain": {
        "safe": 0.65,
        "high_risk": 0.85,
    },
    "snow": {
        "safe": 0.55,
        "high_risk": 0.75,
    },
}

WEATHER_DIFFICULTY_MODIFIERS = {
    "Easy": {
        "slip_multiplier": 0.75,
        "visibility_multiplier": 0.75,
        "particle_multiplier": 0.75,
    },
    "Medium": {
        "slip_multiplier": 1.0,
        "visibility_multiplier": 1.0,
        "particle_multiplier": 1.0,
    },
    "Hard": {
        "slip_multiplier": 1.25,
        "visibility_multiplier": 1.15,
        "particle_multiplier": 1.2,
    },
}

WEATHER_BASE_PARTICLES = {
    "rain": 45,
    "snow": 30,
}

WEATHER_ALERT_DURATION = 2600