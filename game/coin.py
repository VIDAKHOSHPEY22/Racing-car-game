import pygame as pg

from .constants import HEIGHT, COIN_MONEY_VALUE, COIN_SCORE_VALUE, GOLD, RED


class Coin:
    def __init__(self, x, y, variant="normal"):
        self.x = x
        self.y = y
        self.radius = 12
        self.variant = variant if variant in {"normal", "red"} else "normal"
        self.color = GOLD if self.variant == "normal" else RED
        self.speed = 8
        self.money_value = COIN_MONEY_VALUE
        self.score_value = COIN_SCORE_VALUE

    def draw(self, screen):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pg.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 2)

    def move(self, speed_multiplier=1.0):
        self.y += self.speed * speed_multiplier
        return self.y > HEIGHT

    def grow(self):
        self.radius += 5
