import pygame as pg

from .constants import HEIGHT


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (240, 220, 50)
        self.speed = 8

    def draw(self, screen):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pg.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 2)

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

    def grow(self):
        self.radius += 5
