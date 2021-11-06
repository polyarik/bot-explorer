import math
import pygame
from data.constants import *
from data.interface.box import Box


class Counter(Box):
    def __init__(self, surface, pos, size, settings={}):
        super().__init__(surface, pos, size, settings)

    def apply_settings(self, settings):
        super().apply_settings(settings)

        params = {
            "value": 0,
            "value_font": DEFAULT_FONT,
            "value_font_size": 32,
            "value_text_color": BLACK,
            "min": -math.inf,
            "max": math.inf,
        }

        for setting in settings:
            if setting in settings:
                params[setting] = settings[setting]

        self.__dict__.update(params)

    def process_event(self, event):
        if super().process_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().check_collision(event.pos):
                if event.button == 4:
                    return self.inc()
                if event.button == 5:
                    return self.dec()

    def inc(self):
        prev = self.value
        self.value = min(self.value + 1, self.max)

        return prev != self.value

    def dec(self):
        prev = self.value
        self.value = max(self.value - 1, self.min)

        return prev != self.value

    def render_text(self):
        text_surface = super().render_text()
        value_surface = self.render_value()

        #TODO: rewrite this ...

        width = max(text_surface.get_width(), value_surface.get_width())
        height = text_surface.get_height() + value_surface.get_height() + MARGIN

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface_center = surface.get_rect().center

        text_center = (surface_center[0], surface_center[1] - (value_surface.get_height() + MARGIN)/2)
        text_rect = text_surface.get_rect(center=text_center)
        surface.blit(text_surface, text_rect)

        value_center =  (surface_center[0], surface_center[1] + (text_surface.get_height() + MARGIN)/2)
        value_rect = value_surface.get_rect(center=value_center)
        surface.blit(value_surface, value_rect)

        return surface

    def render_value(self):
        font = pygame.font.Font(self.value_font, self.value_font_size)
        value_surface = font.render(str(self.value), True, self.value_text_color)

        return value_surface