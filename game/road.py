import math
import random

import pygame as pg

from .constants import BASE_SPEED, HEIGHT, ROAD_COLOR, SHOULDER_COLOR, WHITE, WIDTH


class Road:
    def __init__(self, base_speed=10):
        self.road_width = 500
        self.base_road_x = (WIDTH - self.road_width) // 2
        self.curve_phase = 0.0
        self.curve_speed = 0.02 * max(0.8, base_speed / BASE_SPEED)
        self.curve_amplitude = 90
        self.curve_frequency = 0.012
        self.stripes = []
        for i in range(10):
            self.stripes.append({"y": i * 120 - 100, "width": 60, "height": 20, "speed": base_speed + 2})

    def get_bounds(self, y):
        sample_y = max(0, min(HEIGHT - 1, int(y)))
        primary_curve = math.sin(self.curve_phase + sample_y * self.curve_frequency)
        secondary_curve = math.sin((self.curve_phase * 0.55) + sample_y * self.curve_frequency * 0.45)
        curve_offset = int((primary_curve * 0.75 + secondary_curve * 0.25) * self.curve_amplitude)
        left = self.base_road_x + curve_offset
        left = max(40, min(WIDTH - self.road_width - 40, left))
        return left, left + self.road_width

    def get_drive_bounds(self, y, object_width=0):
        left, right = self.get_bounds(y)
        return left, right - object_width

    def get_travel_x(self, y, ratio, object_width=0):
        ratio = max(0.0, min(1.0, ratio))
        left, max_x = self.get_drive_bounds(y, object_width)
        return left + int((max_x - left) * ratio)

    def get_center_x(self, y):
        left, right = self.get_bounds(y)
        return (left + right) // 2

    def draw(self, screen):
        for i in range(HEIGHT):
            left, right = self.get_bounds(i)
            pg.draw.line(screen, SHOULDER_COLOR, (0, i), (left, i))
            pg.draw.line(screen, SHOULDER_COLOR, (right, i), (WIDTH, i))
            brightness = random.randint(-5, 5)
            shade = (
                max(0, min(255, ROAD_COLOR[0] + brightness)),
                max(0, min(255, ROAD_COLOR[1] + brightness)),
                max(0, min(255, ROAD_COLOR[2] + brightness)),
            )
            pg.draw.line(screen, shade, (left, i), (right, i), 1)

        for stripe in self.stripes:
            stripe_center_x = self.get_center_x(stripe["y"] + stripe["height"] // 2)
            stripe_x = stripe_center_x - stripe["width"] // 2
            pg.draw.rect(screen, WHITE, (stripe_x, stripe["y"], stripe["width"], stripe["height"]))
            if stripe["y"] % 240 < 120:
                reflect = pg.Surface((stripe["width"], stripe["height"] // 3), pg.SRCALPHA)
                reflect.fill((255, 255, 255, 30))
                screen.blit(reflect, (stripe_x, stripe["y"]))

        for i in range(HEIGHT - 1):
            current_left, current_right = self.get_bounds(i)
            next_left, next_right = self.get_bounds(i + 1)
            pg.draw.line(screen, WHITE, (current_left, i), (next_left, i + 1), 2)
            pg.draw.line(screen, WHITE, (current_right, i), (next_right, i + 1), 2)

    def update(self):
        self.curve_phase += self.curve_speed
        for stripe in self.stripes:
            stripe["y"] += stripe["speed"]
            if stripe["y"] > HEIGHT:
                stripe["y"] = -stripe["height"]
