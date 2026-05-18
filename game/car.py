import random

import pygame as pg

from .constants import BASE_SPEED, BLACK, CYAN, HEIGHT, WHITE, WIDTH, PLAYER_SPEED_DEFAULT, MIN_SPEED
from . import constants as const


class Car:
    def __init__(self, x, y, color, player=False, car_type="sedan"):
        self.width = 50
        self.height = 90 if player else random.choice([80, 85, 90, 95])
        self.x = x
        self.y = y
        # `speed` is used for lateral movement for player, and forward speed for NPC cars
        self.speed = BASE_SPEED if player else random.randint(6, 10)
        # For player, keep a separate forward velocity that can be accelerated/braked
        if player:
            # start at default player speed (visual/player velocity)
            self.velocity = float(PLAYER_SPEED_DEFAULT)
            self.max_speed_bonus = 0.0
        else:
            self.velocity = None
        self.color = color
        self.player = player
        self.window_color = CYAN if player else WHITE
        self.type = car_type if player else random.choice(["sedan", "truck", "suv"])
        self.road_boundary_left = 150
        self.road_boundary_right = WIDTH - 200

    def draw(self, screen, y_override=None):
        y = self.y if y_override is None else y_override
        pg.draw.rect(screen, self.color, (self.x, y, self.width, self.height))
        pg.draw.rect(
            screen,
            (min(self.color[0] + 20, 255), min(self.color[1] + 20, 255), min(self.color[2] + 20, 255)),
            (self.x + 2, y + 2, self.width - 4, 10),
        )
        if self.type == "sedan":
            pg.draw.rect(screen, self.window_color, (self.x + 5, y + 10, self.width - 10, 25))
            pg.draw.rect(screen, self.window_color, (self.x + 5, y + 40, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 5, y + 10, self.width - 10, 25), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, y + 40, self.width - 10, 25), 1)
        elif self.type == "truck":
            pg.draw.rect(screen, self.window_color, (self.x + 10, y - 15, 30, 10))
            pg.draw.rect(screen, self.window_color, (self.x + 5, y + 10, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 10, y - 15, 30, 10), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, y + 10, self.width - 10, 25), 1)
        else:
            pg.draw.rect(screen, self.window_color, (self.x + 5, y + 10, self.width - 10, 40))
            pg.draw.rect(screen, BLACK, (self.x + 5, y + 10, self.width - 10, 40), 1)

        wheel_color = (20, 20, 20)
        rim_color = (80, 80, 80)
        for wheel_pos in [(5, self.height - 15), (self.width - 20, self.height - 15), (5, 0), (self.width - 20, 0)]:
            pg.draw.ellipse(screen, wheel_color, (self.x + wheel_pos[0], y + wheel_pos[1], 15, 15))
            pg.draw.ellipse(screen, rim_color, (self.x + wheel_pos[0] + 3, y + wheel_pos[1] + 3, 9, 9))

    def move(self, direction=None, speed_multiplier=1.0):
        if self.player:
            if direction == "left":
                self.x = max(self.road_boundary_left, self.x - self.speed)
            if direction == "right":
                self.x = min(self.road_boundary_right, self.x + self.speed)
            # player forward movement is handled by game world (current_speed)
        else:
            self.y += self.speed * speed_multiplier
            return self.y > HEIGHT

    def accelerate(self, amount: float):
        """Increase player forward velocity by `amount`, clamped to min/max."""
        if not self.player:
            return
        # clamp velocity to MIN_SPEED..MAX_SPEED so it never drops below minimum driving speed
        new_v = float(self.velocity + amount)
        max_speed = float(const.MAX_SPEED + getattr(self, "max_speed_bonus", 0.0))
        self.velocity = max(MIN_SPEED, min(max_speed, new_v))

    def get_velocity(self):
        return self.velocity
