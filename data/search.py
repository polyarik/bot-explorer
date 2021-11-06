import heapq
import array


class Search:

    @classmethod
    def find_path(self, tiles, passable_tiles, start, target, bot_shape=[[1]]):
        target_bit = len(tiles[0])*target[1] + target[0]

        if passable_tiles[target_bit // 8] & 1 << (target_bit % 8):
            prev_tiles, tiles_cost = self.a_star_search(tiles, passable_tiles, start, target, bot_shape)

            if prev_tiles[target[1]][target[0]]:
                path = []
                curr_tile = target

                while curr_tile:
                    path.append((curr_tile, tiles_cost[curr_tile[1]][curr_tile[0]]))
                    curr_tile = prev_tiles[curr_tile[1]][curr_tile[0]]

                path.reverse()
                return path

        return None

    @classmethod
    def a_star_search(self, tiles, passable_tiles, start, target, bot_shape=[[1]]):
        important_tiles = self.get_important_tiles(tiles, passable_tiles, bot_shape)

        start_bit = len(tiles[0])*start[1] + start[0]
        important_tiles[start_bit // 8] &= ~(1 << (start_bit % 8)) # remove start

        target_bit = len(tiles[0])*target[1] + target[0]
        important_tiles[target_bit // 8] |= 1 << (target_bit % 8) # add target

        frontier = PriorityQueue()
        frontier.put(start, 0)

        prev_tiles = [[None for x in range(len(tiles[0]))] for y in range(len(tiles))]
        tiles_cost = [[0 for x in range(len(tiles[0]))] for y in range(len(tiles))]

        while not frontier.is_empty():
            curr_tile = frontier.get()

            if curr_tile == target:
                break

            reachable_tiles = self.get_reachable_tiles(tiles, passable_tiles, important_tiles, curr_tile, bot_shape)

            for next_tile, next_tile_cost in reachable_tiles.items():
                new_cost = tiles_cost[curr_tile[1]][curr_tile[0]] + next_tile_cost

                is_new_tile = True if not tiles_cost[next_tile[1]][next_tile[0]] else False

                if is_new_tile or new_cost < tiles_cost[next_tile[1]][next_tile[0]]:
                    replace = True if not is_new_tile else False

                    tiles_cost[next_tile[1]][next_tile[0]] = new_cost

                    priority = new_cost + self.heuristic(next_tile, target)
                    frontier.put(next_tile, priority, replace)

                    prev_tiles[next_tile[1]][next_tile[0]] = curr_tile

        return prev_tiles, tiles_cost

    @staticmethod
    def get_important_tiles(tiles, passable_tiles, shape=[[1]]):
        tiles_width = len(tiles[0])
        tiles_height = len(tiles)

        shape_width = len(shape[0]) + 2
        shape_height = len(shape) + 2

        shift_x = -(shape_width // 2)
        shift_y = -(shape_height // 2)

        important_tiles = array.array('B', [0 for i in range((tiles_width*tiles_height + 7) // 8)])
        bit = 0

        while bit//8 < len(passable_tiles):
            if passable_tiles[bit // 8] >> (bit % 8) & 1:
                tile_y = bit // tiles_width
                tile_x = bit % tiles_width

                flag = False
                tile = tiles[tile_y][tile_x]
            
                for y in range(shape_height):
                    for x in range(shape_width):
                        curr_x = tile_x + shift_x + x
                        curr_y = tile_y + shift_y + y

                        if 0 <= curr_x < tiles_width and 0 <= curr_y < tiles_height and tiles[curr_y][curr_x] != tile:
                            important_tiles[bit // 8] |= 1 << (bit % 8)
                            flag = True
                            break
                    
                    if flag:
                        break

            bit += 1

        return important_tiles

    @classmethod
    def get_reachable_tiles(self, tiles, passable_tiles, important_tiles, coords, bot_shape=[[1]]):
        map_size = [len(tiles[0]), len(tiles)]
        available_paths = self.get_available_paths(passable_tiles, important_tiles, map_size, coords)
        reachable_tiles = {}

        for path in available_paths:
            path_cost = self.calc_movement_cost(tiles, path, bot_shape)

            last_tile = path[-1][0]
            reachable_tiles[last_tile] = path_cost

        return reachable_tiles

    @classmethod
    def get_available_paths(self, passable_tiles, important_tiles, map_size, start):
        available_paths = []
        bit = 0

        while bit//8 < len(important_tiles):
            if important_tiles[bit // 8] >> (bit % 8) & 1:
                y = bit // map_size[0]
                x = bit % map_size[0]

                tile = (x, y)

                if tile != start:
                    path = self.get_tile_line(start, tile, map_size, passable_tiles)

                    if path:
                        available_paths.append(path)

            bit += 1
        
        return available_paths

    @classmethod
    def heuristic(self, coords, target):
        start_x, start_y = coords
        end_x, end_y = target

        del_x = abs(end_x - start_x)
        del_y = abs(end_y - start_y)

        dist = (del_x**2 + del_y**2)**(1/2)
        res = dist + del_x + del_y
        return res

    @classmethod
    def get_tile_line(self, start, coords, map_size, passable_tiles=None):
        tile_line = []
        
        start_x, start_y = start
        end_x, end_y = coords

        sign_x = 1 if end_x > start_x else -1 if end_x < start_x else 0
        sign_y = 1 if end_y > start_y else -1 if end_y < start_y else 0

        del_width = abs(start_x - end_x)
        del_height = abs(start_y - end_y)
        is_horizontal = True

        if del_height > del_width:
            del_width, del_height = del_height, del_width
            is_horizontal = False

        height_shift = 0

        for width_shift in range(del_width + 1):
            if is_horizontal:
                shift_x = width_shift
                shift_y = height_shift

                shift_sign_x = 0
                shift_sign_y = sign_y
            else:
                shift_x = height_shift
                shift_y = width_shift

                shift_sign_x = sign_x
                shift_sign_y = 0

            x = start_x + shift_x*sign_x
            y = start_y + shift_y*sign_y

            if shift_sign_x or shift_sign_y:
                for i in range(5):
                    tile_coeff = 0

                    if x >= 0 and x < map_size[0] and y >= 0 and y < map_size[1]:
                        tile_coeff = self.calc_tile_coeff((start, coords), (x, y))

                    if tile_coeff:
                        bit = map_size[0]*y + x

                        if passable_tiles and not passable_tiles[bit // 8] & 1 << (bit % 8):
                            return None

                        tile_line.append(((x, y), tile_coeff))

                        if (x, y) == coords:
                            break
                    elif i == 0:
                        height_shift += abs(sign_y) if is_horizontal else abs(sign_x)
                    else:
                        break

                    x += shift_sign_x
                    y += shift_sign_y
            else:
                bit = map_size[0]*y + x

                if (x < 0 or x >= map_size[0] or y < 0 or y >= map_size[1]
                    or passable_tiles and not passable_tiles[bit // 8] & 1 << (bit % 8)):
                    return None

                tile_line.append(((x, y), 1))

        return tile_line

    @classmethod
    def calc_tile_coeff(self, line, tile):
        (start_x, start_y), (end_x, end_y) = line
        tile_x, tile_y = tile

        start_x -= tile_x
        end_x -= tile_x
        start_y -= tile_y
        end_y -= tile_y

        if abs(end_x - start_x) < abs(end_y - start_y):
            start_x, start_y = -start_y, start_x
            end_x, end_y = -end_y, end_x

        if end_x < start_x:
            start_x = -start_x
            end_x = -end_x

        if end_y < start_y:
            start_y = -start_y
            end_y = -end_y

        k = (end_y - start_y) / (end_x - start_x)
        b = start_y - k*start_x

        if b > 0:
            b = -b

        b += (k + 1) / 2

        # no crossing
        if b <= -(k + 1) / 2:
            return 0

        if b == (k + 1) / 2:
            coeff = 1
        elif b <= (k - 1) / 2 and b <= (1 - k) / 2:
            coeff = (b*2 + k + 1)**2 / (k*8)
        elif b > (k - 1) / 2 and b > (1 - k) / 2:
            coeff = 1 - (b*2 - k - 1)**2 / (k*8)
        else:
            coeff = b + 0.5

        return coeff

    @staticmethod
    def calc_line_coeff(start, end):
        start_x, start_y = start
        end_x, end_y = end

        del_x = abs(end_x - start_x)
        del_y = abs(end_y - start_y)

        if del_x < del_y:
            del_x, del_y = del_y, del_x

        if del_x:
            k = del_y / del_x
        else:
            k = 0

        return k

    @classmethod
    def calc_movement_cost(self, tiles, path, shape):
        #line_coeff = self.calc_line_coeff(path[0][0], path[-1][0])
        del_x = abs(path[0][0][0] - path[-1][0][0])
        del_y = abs(path[0][0][1] - path[-1][0][1])

        path.pop(0)

        shape_shift_x = -(len(shape[0]) // 2)
        shape_shift_y = -(len(shape) // 2)

        cost = 0

        for y, shape_line in enumerate(shape):
            for x, shape_tile in enumerate(shape_line):
                if shape_tile:
                    for (tile_x, tile_y), coeff in path:
                        curr_x = tile_x + shape_shift_x + x
                        curr_y = tile_y + shape_shift_y + y

                        cost += tiles[curr_y][curr_x] * coeff

        dist = (del_x**2 + del_y**2)**(1/2)
        cost += dist
        #cost *= (line_coeff**2 + 1)**(1/2) / (line_coeff + 1)
        return cost


class PriorityQueue:
    def __init__(self):
        self.items = []
        self.entry_finder = {}
    
    def is_empty(self):
        return len(self.entry_finder) == 0
    
    def put(self, item, priority, replace=False):
        if replace:
            self.remove(item)

        entry = [priority, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.items, entry)

    def remove(self, item):
        entry = self.entry_finder.pop(item)
        entry[1] = (-1, -1)

    def get(self):
        while self.items:
            entry = heapq.heappop(self.items)
            item = entry[1]

            if item > (-1, -1):
                del self.entry_finder[item]
                return item