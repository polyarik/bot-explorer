import math
import array
from data.search import Search


class Bot:

    def __init__(self):
        self._coords = None
        self.size = 1

        self.clear_memory()

    def memorize_chunk(self, coords, map_chunk, target=None):
        self.clear_memory() 
        self.memory["tiles"] = map_chunk

        chunk_width = len(map_chunk[0]) #TODO: find the widest line
        chunk_height = len(map_chunk) #TODO: find the highest col

        self.memory["passable_tiles"] = array.array('B', [0 for i in range((chunk_width*chunk_height + 7) // 8)])

        bot_size = self._size

        for y, line in enumerate(map_chunk):
            for x, tile in enumerate(line):
                if tile:
                    shape_coords = self.get_shape_coords((x, y))
                    curr_x = shape_coords[0] + coords[0]
                    curr_y = shape_coords[1] + coords[1]

                    if curr_x >= 0 and curr_x + bot_size <= chunk_width and curr_y >= 0 and curr_y + bot_size <= chunk_height:
                        chunk = [map_chunk[i][curr_x:curr_x + bot_size] for i in range(curr_y, curr_y + bot_size)]

                        if self.is_passable(chunk):
                            tile_x = x + coords[0]
                            tile_y = y + coords[1]

                            bit = chunk_width*tile_y + tile_x
                            self.memory["passable_tiles"][bit // 8] |= 1 << (bit % 8)

        if target:
            self.memory["target"] = target

        self.find_path(memorize=True)

    def is_passable(self, chunk):
        shape = self.shape
        chunk_width = len(chunk[0])
        chunk_height = len(chunk)
    
        for y, shape_line in enumerate(shape):
            for x, shape_tile in enumerate(shape_line):
                if shape_tile:
                    if x >= chunk_width or y >= chunk_height or chunk[y][x] <= 0:
                        return False

        return True

    def clear_memory(self):
        self.memory = {"tiles": None, "passable_tiles": array.array('B'), "target": None, "path": None}

    def calc_shape(self, size):
        if size:
            center_x = center_y = radius = size // 2
            shape = [[0 for x in range(size)] for y in range(size)]

            for y in range(len(shape)):
                for x in range(len(shape[0])):
                    rel_x = x - center_x
                    rel_y = y - center_y

                    dist = math.sqrt(rel_x*rel_x + rel_y*rel_y)

                    if dist <= radius + 0.42:
                        if abs(rel_x) < (radius + 0.42)/math.sqrt(2) and abs(rel_y) < (radius + 0.42)/math.sqrt(2):
                            # bot center
                            shape[y][x] = 2
                        else:
                            shape[y][x] = 1

            return shape
        
        return None

    def calc_shape_coords(self, coords, size=None):
        if size is None:
            size = self._size 

        if coords and size:
            center_x, center_y = coords
            x = center_x - size//2
            y = center_y - size//2

            return (x, y)
        
        return None

    def find_path(self, coords=None, memorize=False):
        tiles = self.memory["tiles"]
        passable_tiles = self.memory["passable_tiles"]
        target = self.memory["target"]
        shape = self.shape

        if tiles and target:
            start = self._coords if coords is None else coords
            path = Search.find_path(tiles, passable_tiles, start, target, shape)

            if memorize:
                self.memory["path"] = path

            return path

        return None

    def get_shape(self, size=None):
        if size is None:
            return self.shape

        return self.calc_shape(size)

    def get_shape_coords(self, coords=None, shape_size=None):
        if coords is None and shape_size is None:
            return self.shape_coords

        return self.calc_shape_coords(coords, shape_size)

    def get_passable_tiles(self):
        return self.memory["passable_tiles"]

    def get_path(self, start=None):
        if start is None:
            return self.memory["path"]

        return self.find_path(start)

    @property
    def size(self):
        return self._size

    @property
    def coords(self):
        return self._coords

    @size.setter
    def size(self, size):
        self._size = size
        self.shape_coords = self.calc_shape_coords(self._coords)
        self.shape = self.calc_shape(self._size)

    @coords.setter
    def coords(self, coords):
        self._coords = coords
        self.shape_coords = self.calc_shape_coords(self._coords)