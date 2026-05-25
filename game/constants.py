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
COIN_MONEY_VALUE = 10
COIN_RED_MONEY_VALUE = 75
COIN_RADIUS = 12
COIN_RED_RADIUS = 15
COIN_CHAIN_LENGTH = 3
COIN_CHAIN_VERTICAL_SPACING = 58
COIN_CHAIN_SPAWN_BASE_CHANCE = {
    "Easy": 0.08,
    "Medium": 0.10,
    "Hard": 0.12,
}
COIN_CHAIN_SPAWN_STAGE_STEP = 0.01
COIN_CHAIN_SPAWN_MAX_CHANCE = 0.22
COIN_RED_SPAWN_BASE_CHANCE = {
    "Easy": 0.025,
    "Medium": 0.035,
    "Hard": 0.035,
}
COIN_RED_SPAWN_STAGE_STEP = 0.005
COIN_RED_SPAWN_MAX_CHANCE = 0.09
OBSTACLE_PASS_SCORE = 1

# Collision economy: each damaging car collision reduces money based on stage.
# Stage 1 => 40, Stage 2 => 95, Stage 3 => 150, ...
COLLISION_MONEY_PENALTY_BASE = 40
COLLISION_MONEY_PENALTY_STAGE_STEP = 55

# Economy tuning values. Keep them data-driven so later stages / weather can
# adjust rewards without touching the gameplay loop.
ECONOMY_DISTANCE_REWARD_STEP = 500
ECONOMY_DISTANCE_REWARD_MONEY = 10
ECONOMY_STAGE_REWARD_MONEY = 100
# Maximum reasonable saved money to prevent runaway values from legacy bugs.
# Any saved `total_money` or `last_successful_total_money` above this will be
# clamped when loading the save.
MAX_SANE_TOTAL_MONEY = 3999
COIN_SPAWN_BASE_INTERVAL = {
    "Easy": 1600,
    "Medium": 1900,
    "Hard": 2200,
}
COIN_SPAWN_STAGE_STEP = 90
COIN_SPAWN_MIN_INTERVAL = 850
COIN_MAX_ACTIVE = {
    "Easy": 3,
    "Medium": 2,
    "Hard": 2,
}

# Stage completion reward system
STAGE_CLEAR_SCORE_BONUS = 25
STAGE_CLEAR_MONEY_BONUS = 8
STAGE_LEVEL_SCORE_MULTIPLIER = 10
STAGE_LEVEL_MONEY_MULTIPLIER = 2
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
    {
        "name": "Blue Racer",
        "color": BLUE,
        "type": "sedan",
        "price": 0,
        "speed_bonus": 0,
        "handling_bonus": 0,
        "unlocked_by_default": True,
    },
    {
        "name": "Red Speedster",
        "color": RED,
        "type": "sedan",
        "price": 30,
        "speed_bonus": 5,
        "handling_bonus": 1,
        "unlocked_by_default": False,
    },
    {
        "name": "Green Machine",
        "color": GREEN,
        "type": "suv",
        "price": 45,
        "speed_bonus": 2,
        "handling_bonus": 4,
        "unlocked_by_default": False,
    },
    {
        "name": "Yellow Lightning",
        "color": YELLOW,
        "type": "sedan",
        "price": 60,
        "speed_bonus": 7,
        "handling_bonus": 2,
        "unlocked_by_default": False,
    },
    {
        "name": "Purple Power",
        "color": PURPLE,
        "type": "suv",
        "price": 80,
        "speed_bonus": 4,
        "handling_bonus": 5,
        "unlocked_by_default": False,
    },
    {
        "name": "Orange Blaze",
        "color": ORANGE,
        "type": "truck",
        "price": 100,
        "speed_bonus": 3,
        "handling_bonus": 6,
        "unlocked_by_default": False,
    },
    {
        "name": "Cyan Cruiser",
        "color": CYAN,
        "type": "sedan",
        "price": 120,
        "speed_bonus": 9,
        "handling_bonus": 3,
        "unlocked_by_default": False,
    },
    {
        "name": "Pink Dream",
        "color": PINK,
        "type": "suv",
        "price": 150,
        "speed_bonus": 6,
        "handling_bonus": 7,
        "unlocked_by_default": False,
    },
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
    "total_money": 100,
    "best_stage": DEFAULT_STAGE,
    "best_distance": 0,
    "games_played": 0,
    "total_score": 0,
    "selected_skin": 0,
    "unlocked_skins": [0],
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
        "obstacle_frequency": 2250,
        "traffic_density": 0.72,  # 0..1 relative density
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 8,  # extra meters to cross finish line
    },
    2: {
        "stage_id": 2,
        "distance_target": 900,
        "enemy_speed_multiplier": 1.04,
        "obstacle_frequency": 1900,
        "traffic_density": 0.8,
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 8,
    },
    3: {
        "stage_id": 3,
        "distance_target": 1220,
        "enemy_speed_multiplier": 1.14,
        "obstacle_frequency": 1560,
        "traffic_density": 0.88,
        "future_weather_slot": None,
        "future_environment_flags": [],
        "finish_pass_buffer": 10,
    },
    4: {
        "stage_id": 4,
        "distance_target": 1600,
        "enemy_speed_multiplier": 1.24,
        "obstacle_frequency": 1360,
        "traffic_density": 0.95,
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

# Nitro system tuning
NITRO_MAX_CHARGE = 100.0
NITRO_PICKUP_CHARGE = 34.0
NITRO_MIN_ACTIVATION = 30.0
NITRO_DRAIN_PER_SECOND = 32.0
NITRO_COOLDOWN_MS = 2600
NITRO_SPAWN_INTERVAL = 6800
NITRO_BOOST_ACCEL = 78.0
NITRO_MAX_SPEED_BONUS = 24.0
NITRO_VISUAL_POP_BONUS = 10.0
NITRO_VISUAL_DECAY_PER_SECOND = 26.0
NITRO_WORLD_SPEED_MULTIPLIER = 1.42
