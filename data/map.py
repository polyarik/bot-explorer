from data.bot import Bot


class Map:

    def __init__(self, tile_types):
        self.tiles_cost = [type["cost"] for type in tile_types]

        self.size = 0
        self.tiles = None

        self.bot = Bot()
        self.target = None
    
    def create_tiles(self, size=(32, 18), type=0):
        self.size = size
        self.tiles = [[type for x in range(size[0])] for y in range(size[1])]

        self.remove_bot()
        self.remove_target()
        self.bot.size = 1

    #TODO: scan only cells that are visible from bot current pos
    #def scan(self, coords):
    def scan(self):
        #TEMP
        map_chunk = self.get_tiles_cost((0, 0), self.size)
        target = self.target
        self.bot.memorize_chunk((0, 0), map_chunk, target)

    def check_collision(self, matrix, coords):
        for y, line in enumerate(matrix):
            for x, tile in enumerate(line):
                current_x = coords[0] + x
                current_y = coords[1] + y

                map_tile = self.get_tile((current_x, current_y))

                if (map_tile is None) or (tile and not self.tiles_cost[map_tile]):
                    return True

        return False

    def get_size(self):
        return self.size

    def get_tile(self, coords):
        if 0 <= coords[0] < self.size[0] and 0 <= coords[1] < self.size[1]:
            return self.tiles[coords[1]][coords[0]]

        return None

    def get_bot_pos(self):
        return {"shape": self.bot.get_shape(), "coords": self.bot.get_shape_coords()}

    def get_target_pos(self):
        return self.target

    def get_tiles_cost(self, coords, size):
        start_x, start_y = coords
        width, height = size

        res = [[0 for x in range(width)] for y in range(height)]

        for y in range(height):
            for x in range(width):
                tile = self.get_tile((start_x + x, start_y + y))

                if not tile is None:
                    res[y][x] = self.tiles_cost[tile]

        return res

    def get_passable_tiles(self):
        return self.bot.get_passable_tiles()

    def get_bot_path(self):
        return self.bot.get_path()

    def set_tile(self, coords, type):
        self.tiles[coords[1]][coords[0]] = type

    def place_bot(self, coords=None):
        if coords != self.bot.coords:
            shape_coords = self.bot.get_shape_coords(coords)

            if shape_coords:
                shape = self.bot.get_shape()
                res = not self.check_collision(shape, shape_coords)

                if res and coords:
                    self.bot.coords = coords
                elif not res and not coords:
                    self.bot.coords = None

                return res

        return False

    def change_bot_size(self, change):
        if change and change % 2 == 0:
            prev_size = self.bot.size

            if prev_size:
                size = max(prev_size + change, 1)
                coords = self.bot.coords

                if coords:
                    shape_coords = self.bot.get_shape_coords(coords, size)

                    if shape_coords:
                        shape = self.bot.get_shape(size)
                        res = not self.check_collision(shape, shape_coords)

                        if res:
                            self.bot.size = size

                        return res

                    return False

                self.bot.size = size
                return True
            
        return False

    def place_target(self, coords=None):
        if coords != self.target:
            if coords:
                prev_coords = self.target
            else:
                coords = self.target
                prev_coords = None

            if coords:
                res = True
                tile = self.get_tile(coords)

                if (not tile is None) and (not self.tiles_cost[tile]):
                    res = False

                self.target = coords if res else prev_coords
                return res

        return False

    def remove_bot(self):
        prev = self.bot.coords
        self.bot.coords = None

        return bool(prev)

    def remove_target(self):
        prev = self.target
        self.target = None

        return bool(prev)