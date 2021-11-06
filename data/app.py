import os
import math
import random
import pygame
from pygame.locals import *
from data.constants import *
from data.interface.interface import Interface
from data.map import Map


class App:

    def __init__(self, tile_types):
        pygame.init()
        self.clock = pygame.time.Clock()

        self.tiles_type = [type["name"] for type in tile_types]
        self.map = Map(tile_types)

        self.interface = Interface()

        self.set_displays(DEFAULT_RESOLUTION)
        self.init_images()

        self.mode = 0
        self.switch_mode()

        self.init_events()

    def init_images(self):
        self.images = {"tiles": {}, "bot": {}, "target": {}}

        for folder in self.images:
            self.images[folder] = self.load_images(folder)

        self.images["picked"] = {
            "bot": self.get_rand_img("bot"),
            "target": self.get_rand_img("target")
        }

    def load_images(self, folder):
        images = {}
        path = "./assets/images/{}".format(folder)

        for file_name in os.listdir(path):
            if file_name.endswith(".png"):
                img = pygame.image.load("{}/{}".format(path, file_name))

                if img.get_alpha():
                    img = img.convert_alpha()
                else:
                    img = img.convert()
                    img.set_colorkey(WHITE)

                images[file_name] = img

        return images

    def switch_mode(self, change=0):
        if self.mode + change < 0 or self.mode + change > 4:
            change = 0

        # process all changes
        for i in range(change):
            mode = self.mode + i

            if mode == 0:
                self.create_map()
                self.mode = 1
            elif mode == 1:
                self.map.place_bot()
                self.map.place_target()
                self.mode = 2
            elif mode == 2:
                if self.map.get_bot_pos()["coords"] and self.map.get_target_pos():
                    self.set_caption("Bot Explorer is finding the shortest path...") 
                    self.map.scan() #TEMP
                    self.mode = 3
            elif mode == 3:
                self.mode = 4

        if change < 0:
            self.mode += change

        self.interface.switch_mode(self.mode)
        print("mode:", self.mode)

        # map creation
        if self.mode == 0:
            self.set_caption("Bot Explorer: map creation")
            self.set_bot_icon()
        # map editing
        elif self.mode == 1:
            self.set_caption("Bot Explorer: map editing")

            self.placing_tile_type = 1 if len(self.tiles_type) else 0
            self.erasing_tile_type = 0
            self.drawing_lock = [False, False]

            self.set_tile_icon()
            self.set_tile_caption()
        # bot n target placing
        elif self.mode == 2:
            self.set_caption("Bot Explorer: bot & target placing")
            self.set_bot_icon()
            self.bot_placing = True
        elif self.mode == 3:
            self.set_caption("Bot Explorer: blocked tiles")
        elif self.mode == 4:
            self.set_caption("Bot Explorer: path")
            #TODO: show tiles cost in A* / or only on mousemove in case of small tile_size

        self.render()

    def init_events(self):
        self.key_pressed = {"shift": False, "ctrl": False}

        running = True
        while running:
            for event in pygame.event.get():
                self.interface.process_event(event)

                if event.type == VIDEORESIZE:
                    self.resize(event.size)
                elif event.type == MOUSEBUTTONDOWN:
                    if self.mode == 1:
                        if event.button == 1 or event.button == 3:
                            tile_type = self.placing_tile_type if event.button == 1 else self.erasing_tile_type
                            self.set_tile(event.pos, tile_type)
                        elif event.button == 2:
                            # peak type from the tile
                            tile_coords = self.get_tile_coords(event.pos)

                            if tile_coords:
                                self.placing_tile_type = self.map.get_tile(tile_coords)
                                self.set_tile_icon()
                                self.set_tile_caption()
                        else:
                            if event.button == 4:
                                self.placing_tile_type = (self.placing_tile_type + 1) % len(self.tiles_type)
                            else:
                                self.placing_tile_type = (self.placing_tile_type - 1) % len(self.tiles_type)

                            self.set_tile_icon()
                            self.set_tile_caption()
                    elif self.mode == 2:
                        if event.button == 1:
                            if self.bot_placing:
                                self.place_bot(event.pos)
                                self.set_bot_icon()
                            else:
                                self.place_target(event.pos)
                                self.set_target_icon()
                        elif event.button == 3:
                            if self.bot_placing:
                                res = self.map.remove_bot()

                                if res:
                                    self.clear_display("bot")
                                    self.update_screen()
                            else:
                                res = self.map.remove_target()

                                if res:
                                    self.clear_display("target")
                                    self.update_screen()
                        elif event.button == 2:
                            #TODO: place bot/goal on wherever possible (near the click)
                            pass
                        elif event.button == 4 or event.button == 5:
                            if self.key_pressed["ctrl"]:
                                if self.bot_placing:
                                    change = 2 if event.button == 4 else -2
                                    self.change_bot_size(change)
                            else:
                                self.bot_placing = not self.bot_placing

                                if self.bot_placing:
                                    self.set_bot_icon()
                                else:
                                    self.set_target_icon()

                elif event.type == MOUSEBUTTONUP:
                    if hasattr(self, "drawing_lock"):
                        self.drawing_lock = [False, False]
                elif event.type == MOUSEMOTION:
                    if self.mode == 1:
                        if event.buttons[0] or event.buttons[2]:
                            tile_type = self.placing_tile_type if event.buttons[0] else self.erasing_tile_type
                            start_x = event.pos[0] - event.rel[0]
                            start_y = event.pos[1] - event.rel[1]

                            self.set_tile_curve((start_x, start_y), event.rel, tile_type)
                    elif self.mode == 2:
                        if event.buttons[0]:
                            if self.bot_placing:
                                self.place_bot(event.pos, False)
                            else:
                                self.place_target(event.pos, False)
                elif event.type == KEYDOWN:
                    if event.key == 304:
                        self.key_pressed["shift"] = True
                    elif event.key == 306:
                        self.key_pressed["ctrl"] = True
                elif event.type == KEYUP:
                    if event.key == 304:
                        self.key_pressed["shift"] = False
                        self.drawing_lock = [False, False]
                    elif event.key == 306:
                        self.key_pressed["ctrl"] = False
                    elif event.key == 27:
                        self.switch_mode(-1)
                    elif event.key == 13:
                        self.switch_mode(1)
                elif event.type == QUIT:
                    running = False

            if self.interface.updated:
                self.update_screen()

            self.clock.tick(FPS)

        pygame.quit()

    # ---------- mode 0: map creation ---------- #

    def create_map(self):
        map_settings = self.interface.get_map_settings()
        self.map.create_tiles(map_settings["size"], map_settings["tile_type"])
        self.calc_render_data()

    # ---------- mode 1: map editing ---------- #

    def set_tile(self, pos, type):
        pos_x, pos_y = pos

        if self.drawing_lock[0]: pos_x = self.drawing_lock[0]
        if self.drawing_lock[1]: pos_y = self.drawing_lock[1]

        tile_coords = self.get_tile_coords((pos_x, pos_y))

        if tile_coords:
            self.map.set_tile(tile_coords, type)
            self.draw_tile(tile_coords)

            self.update_screen()

    def set_tile_curve(self, start, rel, type):
        start_x, start_y = start
        rel_x, rel_y = rel

        if self.key_pressed["shift"]:
            if self.drawing_lock[0] or self.drawing_lock[1]:
                if self.drawing_lock[0]:
                    start_x = self.drawing_lock[0]
                    rel_x = 0
                if self.drawing_lock[1]:
                    start_y = self.drawing_lock[1]
                    rel_y = 0
            else:
                if abs(rel_x) > abs(rel_y):
                    self.drawing_lock[1] = start_y
                    rel_y = 0
                else:
                    self.drawing_lock[0] = start_x
                    rel_x = 0

        dist = max(abs(rel_x), abs(rel_y))

        if dist:
            end = (start_x + rel_x, start_y + rel_y)

            if self.get_tile_coords(end):
                start_x += rel_x
                start_y += rel_y
                rel_x = -rel_x
                rel_y = -rel_y

            for i in range(dist // self.render_data["tile_size"] + 1):
                tile_coords = self.get_tile_coords((
                    start_x + i*rel_x/dist*self.render_data["tile_size"],
                    start_y + i*rel_y/dist*self.render_data["tile_size"]
                ))

                if tile_coords:
                    self.map.set_tile(tile_coords, type)
                    self.draw_tile(tile_coords)
                else:
                    i -= 1
                    break

            if i > -1:
                self.update_screen()
                
    # ---------- mode 2: bot n target placing ---------- #

    def place_bot(self, pos, rand_img=True):
        coords = self.get_tile_coords(pos)
        res = self.map.place_bot(coords)

        if res:
            if rand_img:
                self.images["picked"]["bot"] = self.get_rand_img("bot")

            self.render_bot()
            self.update_screen()

    def change_bot_size(self, change):
        res = self.map.change_bot_size(change)

        if res:
            self.render_bot()
            self.update_screen()

    def place_target(self, pos, rand_img=True):
        coords = self.get_tile_coords(pos)
        res = self.map.place_target(coords)

        if res:
            if rand_img:
                self.images["picked"]["target"] = self.get_rand_img("target")

            self.render_target()
            self.update_screen()

    # ---------------------------------------- #

    def set_displays(self, size):
        self.screen = pygame.display.set_mode(size, HWSURFACE|DOUBLEBUF|RESIZABLE, 0, 32)
        self.displays = {}

        display = pygame.Surface(size, pygame.SRCALPHA|HWSURFACE)
        display.set_colorkey(WHITE)

        self.interface.set_display(display.copy())

        #TODO: add "costs"
        types = [
            ("tiles", 0, 1),
            ("bot", 1, 2),
            ("target", 4, 2),
            ("blocked", 2, 3),
            ("path", 3, 4),
        ] 

        for type in types:
            name, z_index, mode = type
            self.displays[name] = {"display": display.copy(), "z_index": z_index, "mode": mode}

    def clear_display(self, name):
        self.displays[name]["display"].fill(EMPTY)

    def resize(self, size=DEFAULT_RESOLUTION):
        self.set_displays(size)
        self.calc_render_data()
        self.render()

    def calc_render_data(self):
        self.render_data = {"map_width": 0, "map_height": 0, "tile_size": 0, "start_x": 0, "start_y": 0}

        if self.map.get_size():
            self.render_data["map_width"], self.render_data["map_height"] = self.map.get_size()
            screen_width, screen_height = self.screen.get_size()

            self.render_data["tile_size"] = max(
                1,
                math.floor(
                    min(
                        screen_width / self.render_data["map_width"],
                        screen_height / self.render_data["map_height"]
                    )
                )
            )

            self.render_data["outline_width"] = min(round(self.render_data["tile_size"] * 0.06), 10)

            self.render_data["start_x"] = round(screen_width/2 - self.render_data["tile_size"]*self.render_data["map_width"]/2)
            self.render_data["start_y"] = round(screen_height/2 - self.render_data["tile_size"]*self.render_data["map_height"]/2)

    def get_tile_pos(self, coords):
        x, y = coords

        tile_pos = (
            self.render_data["start_x"] + x*self.render_data["tile_size"],
            self.render_data["start_y"] + y*self.render_data["tile_size"]
        )

        return tile_pos

    def get_tile_coords(self, mouse_coords):
        mouse_x, mouse_y = mouse_coords

        render_start_x = self.render_data["start_x"]
        render_end_x = render_start_x + self.render_data["tile_size"]*self.render_data["map_width"]
        render_start_y = self.render_data["start_y"]
        render_end_y = render_start_y + self.render_data["tile_size"]*self.render_data["map_height"]


        if mouse_x < render_start_x or mouse_x >= render_end_x or mouse_y < render_start_y or mouse_y >= render_end_y:
            return None

        tile_coords = (
            int((mouse_x - render_start_x) // self.render_data["tile_size"]),
            int((mouse_y - render_start_y) // self.render_data["tile_size"])
        )

        return tile_coords

    def render(self):
        self.interface.render()

        if self.mode:
            self.clear_display("tiles")
            self.draw_tiles()

            if self.mode > 1:
                self.render_bot()
                self.render_target()

                if self.mode > 2:
                    #TODO: render tiles cost

                    if self.mode == 3:
                        self.render_blocked_tiles()

                    if self.mode > 3:
                        self.render_bot_path()

        self.update_screen()

    def render_bot(self):
        self.clear_display("bot")
        bot = self.map.get_bot_pos()

        if bot["coords"]:
            display = self.displays["bot"]["display"]

            tile_size = self.render_data["tile_size"]
            start_x, start_y = bot["coords"]

            picked_img = self.images["picked"]["bot"]
            img = picked_img if picked_img else self.get_rand_img("bot")
            color = pygame.transform.average_color(img) if img else PINK #BUG: sometimes return tp color / TODO: peak dominate color
            color = pygame.Color(color[0], color[1], color[2])
            color.a = 255

            center_start_coords = None
            center_end_coords = None

            for y, line in enumerate(bot["shape"]):
                for x, tile in enumerate(line):
                    if tile == 1:
                        pos_x, pos_y = self.get_tile_pos((start_x + x, start_y + y))
                        pygame.draw.rect(display, color, (pos_x, pos_y, tile_size, tile_size))
                    elif tile == 2:
                        if not center_start_coords:
                            center_start_coords = (x, y)
                        center_end_coords = (x, y)

            center_size = tile_size * (center_end_coords[0] - center_start_coords[0] + 1)
            center_start_x, center_start_y = self.get_tile_pos((start_x + center_start_coords[0], start_y + center_start_coords[1]))

            if img:
                display.blit(pygame.transform.scale(img, (center_size, center_size)), (center_start_x, center_start_y))
            else:
                pygame.draw.rect(display, color, (center_start_x, center_start_y, center_size, center_size))

    def render_target(self):
        self.clear_display("target")
        target = self.map.get_target_pos()

        if target:
            display = self.displays["target"]["display"]

            size = self.render_data["tile_size"]
            pos_x, pos_y = self.get_tile_pos(target)

            picked_img = self.images["picked"]["target"]
            img = picked_img if picked_img else self.get_rand_img("target")

            if img:
                display.blit(pygame.transform.scale(img, (size, size)), (pos_x, pos_y))
            else:
                pygame.draw.rect(display, PINK, (pos_x, pos_y, size, size))

    def render_blocked_tiles(self):
        self.clear_display("blocked")
        passable_tiles = self.map.get_passable_tiles()

        if passable_tiles:
            display = self.displays["blocked"]["display"]
            size = self.render_data["tile_size"]

            map_width, map_height = self.map.get_size()

            for y in range(map_height):
                for x in range(map_width):
                    bit = map_width*y + x

                    if not passable_tiles[bit // 8] & 1 << (bit % 8):
                        pos_x, pos_y = self.get_tile_pos((x, y))
                        pygame.draw.rect(display, TP_RED, (pos_x, pos_y, size, size))

    def render_bot_path(self):
        self.clear_display("blocked")
        self.clear_display("path")

        path = self.map.get_bot_path()

        if not path: #TEMP / not here
            self.switch_mode(-1)
        elif path:
            display = self.displays["path"]["display"]
            render_x = self.render_data["start_x"]
            render_y = self.render_data["start_y"]

            size = self.render_data["tile_size"]

            line_width = size // 3
            if size % 2 != line_width % 2: line_width += 1
            line_width = max(line_width, 1)

            for i in range(len(path) - 1):
                (x, y), cost = path[i]
                (next_x, next_y), next_cost = path[i + 1]

                '''if x > next_x:
                    x, next_x = next_x, x
                if y > next_y:
                    y, next_y = next_y, y

                start_x = render_x + x*size + (size - line_width)//2
                start_y = render_y + y*size + (size - line_width)//2

                width = (next_x - x)*size + line_width
                height = (next_y - y)*size + line_width

                pygame.draw.rect(display, TP_GOLD, (start_x, start_y, width, height))'''

                start_x = render_x + x*size + size//2
                start_y = render_y + y*size + size//2

                end_x = render_x + next_x*size + size//2
                end_y = render_y + next_y*size + size//2

                pygame.draw.line(display, TP_GOLD, (start_x, start_y), (end_x, end_y), line_width)
                pygame.draw.circle(display, TP_GOLD, (start_x, start_y), line_width)

    def draw_tiles(self, section_size=None, section_coords=(0, 0)):
        if section_size is None:
            section_size = (self.render_data["map_width"], self.render_data["map_height"])

        for y in range(section_size[1]):
            for x in range(section_size[0]):
                self.draw_tile((x + section_coords[0], y + section_coords[1]))

    def draw_tile(self, coords):
        type = self.map.get_tile(coords)

        if not type is None:
            display = self.displays["tiles"]["display"]

            size = self.render_data["tile_size"]
            pos_x, pos_y = self.get_tile_pos(coords)

            img_name = self.tiles_type[type] + ".png"

            if img_name in self.images["tiles"]:
                img = self.images["tiles"][img_name]
                display.blit(pygame.transform.scale(img, (size, size)), (pos_x, pos_y))
            else:
                pygame.draw.rect(display, PINK, (pos_x, pos_y, size, size))

            if self.render_data["outline_width"]:
                outline = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.rect(outline, TP_BLUE, (0, 0, size, size), self.render_data["outline_width"])
                display.blit(outline, (pos_x, pos_y))

    def update_screen(self):
        self.screen.fill(WHITE)

        displays = sorted(self.displays.items(), key=lambda x: x[1]["z_index"]) 

        for name, display in displays:
            if self.mode >= display["mode"]:
                self.screen.blit(display["display"], (0, 0))

        self.screen.blit(self.interface.display, (0, 0))
        self.interface.updated = False

        pygame.display.update()

    def get_rand_img(self, category):
        return random.choice(list(self.images[category].items()))[1]

    def set_tile_caption(self):
        tile_type = self.tiles_type[self.placing_tile_type]
        caption = "Bot Explorer: map editing [{}]".format(tile_type)
        self.set_caption(caption)

    def set_caption(self, caption):
        pygame.display.set_caption(caption)

    def set_tile_icon(self):
        img_name = self.tiles_type[self.placing_tile_type] + ".png"
        icon = self.images["tiles"][img_name] if img_name in self.images["tiles"] else None
        self.set_icon(icon)

    def set_bot_icon(self):
        self.set_icon(self.images["picked"]["bot"])

    def set_target_icon(self):
        self.set_icon(self.images["picked"]["target"])

    def set_icon(self, img):
        if not img:
            img = pygame.Surface((16, 16))
            img.fill(PINK)

        pygame.display.set_icon(img)