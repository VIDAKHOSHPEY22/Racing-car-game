import pygame as pg

from .constants import HEIGHT, COIN_MONEY_VALUE, COIN_SCORE_VALUE


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (240, 220, 50)
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
