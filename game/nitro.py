import pygame as pg

from .constants import HEIGHT, NITRO_PICKUP_CHARGE


class NitroPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 13
        self.speed = 9
        self.charge_value = NITRO_PICKUP_CHARGE
        self.core_color = (64, 220, 255)
        self.accent_color = (210, 245, 255)

    def draw(self, screen):
        body_rect = pg.Rect(0, 0, 18, 30)
        body_rect.center = (self.x, self.y)
        pg.draw.rect(screen, self.core_color, body_rect, border_radius=7)
        pg.draw.rect(screen, self.accent_color, body_rect, 2, border_radius=7)
        nozzle_rect = pg.Rect(body_rect.x + 5, body_rect.y - 6, 8, 8)
        pg.draw.rect(screen, self.accent_color, nozzle_rect, border_radius=3)
        pg.draw.line(screen, self.accent_color, (self.x, body_rect.y + 7), (self.x, body_rect.bottom - 7), 2)
        pg.draw.line(screen, self.accent_color, (body_rect.x + 4, self.y), (body_rect.right - 4, self.y), 2)

    def move(self, speed_multiplier=1.0):
        self.y += self.speed * speed_multiplier
        return self.y > HEIGHT