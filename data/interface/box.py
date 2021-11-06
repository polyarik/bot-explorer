import pygame
from pygame.locals import *
from data.constants import *


class Box:
    def __init__(self, surface, pos, size, settings={}):
        self.pos = pos
        self.size = size

        self.hovered = False

        self.apply_settings(settings)
        self.calc_render_data(surface)

    def apply_settings(self, settings):
        params = {
            "color": EMPTY,
            "hover_color": EMPTY,
            "text": None,
            "font": DEFAULT_FONT,
            "font_size": 16,
            "text_color": BLACK
        }

        for setting in settings:
            if setting in settings:
                params[setting] = settings[setting]

        self.__dict__.update(params)

    def process_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            return self.on_hover(event)
            
    def on_hover(self, event):
        prev_state = self.hovered
        self.hovered = True if self.check_collision(event.pos) else False

        return prev_state != self.hovered

    def check_collision(self, pos):
        pos_x, pos_y = pos

        if (pos_x < self.left) or (pos_x >= self.left + self.width) or (pos_y < self.top) or (pos_y >= self.top + self.height):
            return False

        return True

    def calc_render_data(self, surface):
        if type(self.pos[0]) is float:
            self.left = round(surface.get_width() * self.pos[0])
        else:
            self.left = self.pos[0]

        if type(self.pos[1]) is float:
            self.top = round(surface.get_height() * self.pos[1])
        else:
            self.top = self.pos[1]

        if type(self.size[0]) is float:
            self.width = round(surface.get_width() * self.size[0])
        else:
            self.width = self.size[0]

        if type(self.size[1]) is float:
            self.height = round(surface.get_height() * self.size[1])
        else:
            self.height = self.size[1]

    def render(self, surface):
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        box_surface_center = box_surface.get_rect().center

        self.render_rect(box_surface)

        text = self.render_text()
        if text:
            text_rect = text.get_rect(center=box_surface_center)
            box_surface.blit(text, text_rect)

        surface.blit(box_surface, (self.left, self.top))

    def render_rect(self, surface):
        color = self.hover_color if self.hovered else self.color
        width, height = surface.get_size()

        if color:
            pygame.draw.rect(surface, color, (0, 0, width, height))

    def render_text(self):
        font = pygame.font.Font(self.font, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)

        return text_surface