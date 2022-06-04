import pygame as pg
import math
from os.path import exists
from renderer import Renderer, RendererSettings, BackgroundConfig, Map
from player import Player


class SizesNotMatchException(Exception):
    """
    Will be thrown if maps have different resolution
    """

    def __init__(self, *args):
        super.__init__(*args)


def load_map(color_map_path, height_map_path):
    """
    Load maps with all required checks
    :param color_map_path: path to color map
    :param height_map_path: path to height map
    :return: data structure with loaded maps

    :raise FileNotFoundError: if one of maps was not found
    :raise SizesNotMatchException: provided maps have different sizes
    """
    if not exists(color_map_path):
        raise FileNotFoundError("Failed to load color map, it is not existing")

    if not exists(height_map_path):
        raise FileNotFoundError("Failed to load height map, it is not existing")

    img = pg.image.load(color_map_path)
    colormap = pg.surfarray.array3d(img)

    img = pg.image.load(height_map_path)
    heightmap = pg.surfarray.array3d(img)

    if len(colormap) != len(heightmap) or len(colormap[0]) != len(heightmap[0]):
        raise SizesNotMatchException("Colormap and heightmap sizes don't match.")

    return Map(colormap, heightmap)


def get_custom_maps():
    """
    Get input from user
    First input is path to color map
    Second input is path to heightmap

    Every provided path is checked and if user will provide wrong path,
    he will be informed.
    :return: loaded map if it was successfully loaded
    """
    path_to_color_map = None

    # Get player input until it will be ok
    while path_to_color_map is None:
        path = input("Path to color map: ")
        if exists(path):
            path_to_color_map = path
            continue

        print("Failed to load color map, specify correct path, please")

    path_to_height_map = None
    # Get player input until it will be ok
    while path_to_height_map is None:
        path = input("Path to height map: ")
        if exists(path):
            path_to_height_map = path
            continue

        print("Failed to load height map, specify correct path, please")

    print("Loading begins")
    try:
        loaded = load_map(path_to_color_map, path_to_height_map)
        return loaded
    except Exception as e:
        print("Failed to load maps")
        print(e)
        raise e

    print("Map was successfully loaded")
    return map


class Game:
    def __init__(self):
        """
        Init game

        :var self.width: horizontal resolution
        :var self.height: vertical resolution
        :var self.resolution: resolution
        :var self.display: instance of pygame display
        :var self.clock: instance of pygame clock
        :var self.player: instance of player
        :var self.renderer: instance of renderer

        """

        map = load_map("textures/color_map_4.png", "textures/height_map_4.jpg")
        #map = get_custom_maps()

        self.width: int = 800
        self.height: int = 450
        self.resolution: tuple[int, int] = (self.width, self.height)
        self.display = pg.display.set_mode(self.resolution, pg.SCALED)
        self.clock = pg.time.Clock()

        self.player = Player()
        color_near_terrain = [75, 165, 210]
        high_color = [38, 95, 160]

        # Get height parameters from player and provide it to settings
        background = BackgroundConfig(self.player.minimum_height, self.player.maximum_height, color_near_terrain,
                                      high_color)

        # Create default settings
        settings = RendererSettings(2000, 300, math.pi / 3, math.pi / 4, background, 7, map)
        self.renderer = Renderer(self, settings)

    def run(self):
        """Run game cycle"""

        while True:
            self.update()
            self.render()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()

            self.clock.tick(60)
            pg.display.set_caption('berry cool game')

    def update(self):
        """Update game state."""

        self.player.update()
        self.renderer.update()

    def render(self):
        """Render game."""
        self.renderer.render()
        pg.display.flip()


game = Game()
game.run()
