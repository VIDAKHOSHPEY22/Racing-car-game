import pygame as pg

from .constants import WHITE


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = (50, 180, 80)
        self.hover_color = (80, 220, 100)
        self.shadow = pg.Surface((width, height), pg.SRCALPHA)
        self.shadow.fill((0, 0, 0, 50))

    def draw(self, screen, font):
        mouse_pos = pg.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        shadow = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        screen.blit(shadow, (self.rect.x + 3, self.rect.y + 3))
        pg.draw.rect(screen, color, self.rect, border_radius=8)
        pg.draw.rect(screen, (255, 255, 255, 80), self.rect, 2, border_radius=8)

        draw_font = font
        text = draw_font.render(self.text, True, WHITE)
        max_text_width = self.rect.width - 24
        max_text_height = self.rect.height - 12
        if text.get_width() > max_text_width or text.get_height() > max_text_height:
            font_size = max(16, min(font.get_height(), self.rect.height - 10))
            while font_size > 16:
                candidate_font = pg.font.Font(None, font_size)
                candidate_text = candidate_font.render(self.text, True, WHITE)
                if candidate_text.get_width() <= max_text_width and candidate_text.get_height() <= max_text_height:
                    draw_font = candidate_font
                    text = candidate_text
                    break
                font_size -= 2

        text_shadow = draw_font.render(self.text, True, (0, 0, 0, 100))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
