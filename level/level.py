import pygame
import json
import settings
pygame.init()


class TileMap:

    TYPES = {
        0: "path",
        1: "wall",
        2: "door",
        3: "tunnel",
        4: "restricted",
        5: "house",
        6: "void"
    }

    def __init__(self):
        with open("level/map.json") as json_map:
            self.map_info = json.load(json_map)
        self.image = settings.SPRITES['map']
        self.tile = self.create_map()
        self.add_tunnel_tiles()

    def __getitem__(self, item):
        return self.tile[item]

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

    def get_tile_index(self, position):
        return position[1] // self.map_info['tileheight'], position[0] // self.map_info['tilewidth']

    def get_tile(self, tile_index, col_offset=0, row_offset=0):
        return self.tile[tile_index[0] + row_offset, tile_index[1] + col_offset]

    def get_neighbours(self, tile_index):
        neighbours = []
        for offset in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # The order is the priority direction.
            try:
                neighbours.append(self.get_tile(tile_index, *offset))
            except KeyError:
                pass
        return neighbours

    def add_tunnel_tiles(self):
        width = self.map_info["tilewidth"]
        height = self.map_info["tileheight"]

        self.tile[17, 28] = Tile(pos=(width * 28, height * 17),  size=(width, height))
        self.tile[17, 29] = Tile(pos=(width * 29, height * 17),  size=(width, height))
        self.tile[17, -1] = Tile(pos=(width * -1, height * 17),  size=(width, height))
        self.tile[17, -2] = Tile(pos=(width * -2, height * 17),  size=(width, height))

    def create_map(self):
        width = self.map_info['tilewidth']
        height = self.map_info['tileheight']
        columns = self.map_info['tileswide']
        rows = self.map_info['tileshigh']
        tiles = self.map_info['tiles']
        tile_map = {}

        for row in range(rows):
            for col in range(columns):
                pos = (col * width, row * height)
                index = tiles[col + row * columns]['tile']
                tile_type = TileMap.TYPES[max(1, index - 6)] if index > -1 else TileMap.TYPES[0]
                tile = Tile(pos=pos, size=(width, height), type_=tile_type)
                tile_map[row, col] = tile
        return tile_map


class Tile:

    def __init__(self, pos, size, type_="path"):
        self.rect = pygame.Rect(pos, size)
        self.type_ = type_
        self.content = set()

    def add_content(self, item):
        self.content.add(item)

    def remove_content(self, item=None):
        if item is None:
            self.content = set()
        elif item in self.content:
            self.content.remove(item)

    def is_any_type(self, *types):
        return self.type_ in types

    def is_type(self, type_):
        return type_ == self.type_

    def contains(self, item):
        return item in self.content

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return "Tile: index={0}, type={1}".format(settings.get_tile_index(self.rect.center), self.type_)
