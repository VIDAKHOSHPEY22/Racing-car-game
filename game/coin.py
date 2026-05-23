import pygame as pg

from .constants import (
    COIN_CHAIN_LENGTH,
    COIN_MONEY_VALUE,
    COIN_RADIUS,
    COIN_RED_MONEY_VALUE,
    COIN_RED_RADIUS,
    COIN_SCORE_VALUE,
    GOLD,
    HEIGHT,
    BLUE,
    WHITE,
)


class Coin:
    def __init__(self, x, y, variant="normal"):
        self.variant = variant if variant in {"normal", "chain", "red"} else "normal"
        self.x = x
        self.y = y
        if self.variant == "red":
            self.radius = COIN_RED_RADIUS
            # Show red-variant coins in blue color as requested
            self.color = BLUE
            self.highlight_color = (180, 210, 255)
            self.glow_color = (88, 140, 255)
            self.rim_color = (220, 240, 255)
            self.money_value = COIN_RED_MONEY_VALUE
        else:
            self.radius = COIN_RADIUS
            self.color = (240, 220, 50)
            self.highlight_color = (255, 255, 255)
            self.glow_color = GOLD
            self.rim_color = WHITE
            self.money_value = COIN_MONEY_VALUE
        self.speed = 8
        self.score_value = COIN_SCORE_VALUE

    def draw(self, screen):
        if self.variant == "red":
            glow = pg.Surface((self.radius * 4, self.radius * 4), pg.SRCALPHA)
            pg.draw.circle(glow, (*self.glow_color, 78), (self.radius * 2, self.radius * 2), self.radius + 8)
            pg.draw.circle(glow, (*self.glow_color, 46), (self.radius * 2, self.radius * 2), self.radius + 14, 4)
            screen.blit(glow, (self.x - self.radius * 2, self.y - self.radius * 2))
        pg.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pg.draw.circle(screen, self.highlight_color, (self.x - 3, self.y - 4), max(3, self.radius // 3))
        pg.draw.circle(screen, self.rim_color, (self.x, self.y), self.radius, 2)
        if self.variant == "red":
            pg.draw.circle(screen, (255, 255, 255), (self.x + 2, self.y + 1), max(2, self.radius // 4))

    def move(self, speed_multiplier=1.0):
        self.y += self.speed * speed_multiplier
        return self.y > HEIGHT

    def grow(self):
        self.radius += 5
