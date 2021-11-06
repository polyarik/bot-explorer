import pygame
from pygame.locals import *
from data.constants import *
from data.interface.counter import Counter
#textbox
#button


class Interface:
    def __init__(self):
        self._display = None
        self.updated = False

        self.objects = {}
        self.mode = 0

    def process_event(self, event):
        for id, obj in self.objects.items():
            res = obj.process_event(event)
 
            if res:
                self.updated = True

        if self.updated:
            self.render()

    def switch_mode(self, mode):
        self.mode = mode

        # map creation
        if self.mode == 0:
            #self.objects["title"] = Box()

            settings = {
                "hover_color": TP_GRAY,
                "text": "width:",
                "font_size": 32,
                "text_color": GRAY,
                "value_font_size": 80,
                "value": DEFAULT_MAP_WIDTH,
                "min": 1
            }
            self.objects["map_width_box"] = Counter(self.display, (0, 0), (.5, 1.), settings)

            settings.update({
                "text": "height:",
                "value": DEFAULT_MAP_HEIGHT
            })
            self.objects["map_height_box"] = Counter(self.display, (.5, 0), (.5, 1.), settings)

            #TODO: object for tile_type
            self.map_tile_type = 0 #TEMP
            
        # map editing
        elif self.mode == 1:
            self.objects = {}
        '''# bot n target placing
        elif self.mode == 2:
            '''

        self.render()

    # ---------- mode 0: map creation ---------- #

    def get_map_settings(self):
        width = self.objects["map_width_box"].value
        height = self.objects["map_height_box"].value
        tile_type = self.map_tile_type #TEMP

        return {"size": (width, height), "tile_type": tile_type}

    # ---------- mode 1: map editing ---------- #

    #
                
    # ---------- mode 2: bot n target placing ---------- #

    #

    # ---------------------------------------- #

    def set_display(self, surface):
        self.display = surface

        for id, obj in self.objects.items():
            obj.calc_render_data(self.display)

    def render(self):
        self.display.fill(EMPTY)

        if self.display:
            for id, obj in self.objects.items():
                obj.render(self.display)