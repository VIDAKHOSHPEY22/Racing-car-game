import random

import pygame as pg

from .constants import BASE_SPEED, BLACK, CYAN, HEIGHT, WHITE, WIDTH


class Car:
    def __init__(self, x, y, color, player=False, car_type="sedan"):
        self.width = 50
        self.height = 90 if player else random.choice([80, 85, 90, 95])
        self.x = x
        self.y = y
        self.speed = BASE_SPEED if player else random.randint(6, 10)
        self.color = color
        self.player = player
        self.window_color = CYAN if player else WHITE
        self.type = car_type if player else random.choice(["sedan", "truck", "suv"])
        self.road_boundary_left = 150
        self.road_boundary_right = WIDTH - 200

    def draw(self, screen):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(
            screen,
            (min(self.color[0] + 20, 255), min(self.color[1] + 20, 255), min(self.color[2] + 20, 255)),
            (self.x + 2, self.y + 2, self.width - 4, 10),
        )
        if self.type == "sedan":
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25))
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 40, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 40, self.width - 10, 25), 1)
        elif self.type == "truck":
            pg.draw.rect(screen, self.window_color, (self.x + 10, self.y - 15, 30, 10))
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 25))
            pg.draw.rect(screen, BLACK, (self.x + 10, self.y - 15, 30, 10), 1)
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 25), 1)
        else:
            pg.draw.rect(screen, self.window_color, (self.x + 5, self.y + 10, self.width - 10, 40))
            pg.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 40), 1)

        wheel_color = (20, 20, 20)
        rim_color = (80, 80, 80)
        for wheel_pos in [(5, self.height - 15), (self.width - 20, self.height - 15), (5, 0), (self.width - 20, 0)]:
            pg.draw.ellipse(screen, wheel_color, (self.x + wheel_pos[0], self.y + wheel_pos[1], 15, 15))
            pg.draw.ellipse(screen, rim_color, (self.x + wheel_pos[0] + 3, self.y + wheel_pos[1] + 3, 9, 9))

    def move(self, direction=None):
        if self.player:
            if direction == "left":
                self.x = max(self.road_boundary_left, self.x - self.speed)
            if direction == "right":
                self.x = min(self.road_boundary_right, self.x + self.speed)
        else:
            self.y += self.speed
            return self.y > HEIGHT
