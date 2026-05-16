import random

import pygame as pg

from .constants import HEIGHT


HAZARD_SPECS = {
    "oil_spill": {
        "label": "Oil Spill",
        "size": (78, 38),
        "shadow": False,
        "damage_on_hit": False,
        "remove_on_hit": True,
        "base_color": (26, 26, 30),
        "accent_color": (112, 90, 172),
    },
    "water_puddle": {
        "label": "Water Puddle",
        "size": (84, 42),
        "shadow": False,
        "damage_on_hit": False,
        "remove_on_hit": True,
        "base_color": (52, 146, 226),
        "accent_color": (214, 242, 255),
    },
    "pothole": {
        "label": "Pothole",
        "size": (64, 36),
        "shadow": False,
        "damage_on_hit": False,
        "remove_on_hit": True,
        "base_color": (24, 22, 22),
        "accent_color": (154, 128, 114),
    },
    "barrier": {
        "label": "Barrier",
        "size": (86, 38),
        "shadow": True,
        "damage_on_hit": True,
        "remove_on_hit": True,
        "base_color": (232, 98, 32),
        "accent_color": (255, 236, 198),
    },
}


class Hazard:
    def __init__(self, x, y, hazard_type, speed):
        spec = HAZARD_SPECS[hazard_type]
        self.kind = hazard_type
        self.label = spec["label"]
        self.width, self.height = spec["size"]
        self.x = x
        self.y = y
        self.speed = speed
        self.shadow = spec["shadow"]
        self.damage_on_hit = spec["damage_on_hit"]
        self.remove_on_hit = spec["remove_on_hit"]
        self.base_color = spec["base_color"]
        self.accent_color = spec["accent_color"]
        self.road_ratio = 0.5

        if self.kind == "oil_spill":
            self.blobs = [
                (random.randint(10, self.width - 16), random.randint(10, self.height - 16), random.randint(9, 17))
                for _ in range(5)
            ]
        elif self.kind == "water_puddle":
            self.ripples = [
                (random.randint(16, self.width - 16), random.randint(12, self.height - 10), random.randint(16, 26))
                for _ in range(4)
            ]
        elif self.kind == "pothole":
            self.cracks = [
                (
                    random.randint(12, self.width - 12),
                    random.randint(8, self.height - 8),
                    random.randint(-18, 18),
                    random.randint(-10, 10),
                )
                for _ in range(3)
            ]

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT + self.height

    def get_collision_rect(self):
        inset_x = 6 if self.kind != "barrier" else 4
        inset_y = 4
        return pg.Rect(
            self.x + inset_x,
            self.y + inset_y,
            self.width - inset_x * 2,
            self.height - inset_y * 2,
        )

    def draw(self, screen):
        if self.kind == "oil_spill":
            self._draw_oil_spill(screen)
        elif self.kind == "water_puddle":
            self._draw_water_puddle(screen)
        elif self.kind == "pothole":
            self._draw_pothole(screen)
        elif self.kind == "barrier":
            self._draw_barrier(screen)

    def _draw_oil_spill(self, screen):
        sheen = pg.Surface((self.width, self.height), pg.SRCALPHA)
        shadow_rect = pg.Rect(4, 8, self.width - 8, self.height - 12)
        pg.draw.ellipse(sheen, (0, 0, 0, 60), shadow_rect)
        pg.draw.ellipse(sheen, (18, 18, 22, 190), (1, 5, self.width - 2, self.height - 10))
        for blob_x, blob_y, radius in self.blobs:
            pg.draw.circle(sheen, (*self.base_color, 236), (blob_x, blob_y), radius)
            pg.draw.circle(sheen, (166, 112, 214, 70), (blob_x - 3, blob_y - 4), max(4, radius // 2))
            pg.draw.circle(sheen, (84, 180, 214, 45), (blob_x + 2, blob_y - 1), max(3, radius // 3))
        pg.draw.arc(sheen, (150, 120, 225, 105), (10, 8, self.width - 22, self.height - 16), 0.22, 1.72, 2)
        pg.draw.arc(sheen, (76, 204, 224, 85), (16, 14, self.width - 34, self.height - 24), 0.55, 2.25, 2)
        pg.draw.arc(sheen, (255, 255, 255, 36), (20, 10, self.width - 42, self.height - 22), 0.7, 1.8, 1)
        screen.blit(sheen, (self.x, self.y))

    def _draw_water_puddle(self, screen):
        puddle = pg.Surface((self.width, self.height), pg.SRCALPHA)
        pg.draw.ellipse(puddle, (0, 0, 0, 38), (4, 10, self.width - 8, self.height - 12))
        pg.draw.ellipse(puddle, (*self.base_color, 178), (0, 5, self.width, self.height - 10))
        pg.draw.ellipse(puddle, (124, 210, 255, 160), (7, 8, self.width - 14, self.height - 20))
        pg.draw.ellipse(puddle, (*self.accent_color, 190), (12, 9, self.width - 28, self.height // 2))
        pg.draw.ellipse(puddle, (255, 255, 255, 95), (20, 11, self.width - 44, 10))
        for ripple_x, ripple_y, ripple_radius in self.ripples:
            ripple_rect = pg.Rect(0, 0, ripple_radius, max(8, ripple_radius // 2))
            ripple_rect.center = (ripple_x, ripple_y)
            pg.draw.ellipse(puddle, (220, 248, 255, 130), ripple_rect, 1)
        pg.draw.arc(puddle, (255, 255, 255, 80), (8, 10, self.width - 16, self.height - 16), 0.1, 2.5, 1)
        screen.blit(puddle, (self.x, self.y))

    def _draw_pothole(self, screen):
        pothole = pg.Surface((self.width, self.height), pg.SRCALPHA)
        pg.draw.ellipse(pothole, (118, 106, 96, 120), (1, 4, self.width - 2, self.height - 8))
        pg.draw.ellipse(pothole, (78, 70, 64, 210), (4, 7, self.width - 8, self.height - 12))
        pg.draw.ellipse(pothole, (*self.base_color, 255), (8, 10, self.width - 16, self.height - 18))
        pg.draw.ellipse(pothole, (*self.accent_color, 112), (10, 8, self.width - 20, self.height - 12), 2)
        for crack_x, crack_y, delta_x, delta_y in self.cracks:
            pg.draw.line(
                pothole,
                (164, 140, 126, 170),
                (crack_x, crack_y),
                (crack_x + delta_x, crack_y + delta_y),
                2,
            )
        pg.draw.arc(pothole, (255, 255, 255, 45), (16, 10, self.width - 30, self.height - 18), 3.8, 5.1, 1)
        screen.blit(pothole, (self.x, self.y))

    def _draw_barrier(self, screen):
        shadow = pg.Surface((self.width + 8, self.height + 6), pg.SRCALPHA)
        pg.draw.ellipse(shadow, (0, 0, 0, 55), (4, self.height - 6, self.width, 10))
        screen.blit(shadow, (self.x - 4, self.y - 2))

        body_rect = pg.Rect(self.x, self.y + 8, self.width, self.height - 10)
        pg.draw.rect(screen, self.base_color, body_rect, border_radius=10)
        pg.draw.rect(screen, (78, 56, 36), body_rect, 2, border_radius=10)
        pg.draw.rect(screen, (255, 180, 118), (self.x + 4, self.y + 10, self.width - 8, 6), border_radius=3)

        stripe_width = max(12, self.width // 5)
        for index in range(4):
            stripe_rect = pg.Rect(self.x + 6 + index * (stripe_width + 2), self.y + 14, stripe_width, self.height - 20)
            pg.draw.rect(screen, self.accent_color, stripe_rect, border_radius=4)
            pg.draw.line(screen, self.base_color, stripe_rect.topleft, stripe_rect.bottomright, 3)
            pg.draw.line(screen, (255, 255, 255), stripe_rect.bottomleft, stripe_rect.topright, 2)

        for post_x in (self.x + 10, self.x + self.width - 16):
            pg.draw.rect(screen, (88, 88, 94), (post_x, self.y + 2, 6, self.height - 2), border_radius=3)
            pg.draw.circle(screen, (132, 132, 138), (post_x + 3, self.y + self.height - 3), 4)
        pg.draw.circle(screen, (255, 214, 126), (self.x + 18, self.y + 16), 4)
        pg.draw.circle(screen, (255, 214, 126), (self.x + self.width - 18, self.y + 16), 4)