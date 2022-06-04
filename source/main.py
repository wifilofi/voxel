import pygame as pg
import math
from renderer import Renderer, RendererSettings, BackgroundConfig
from player import Player


class Game:
    def __init__(self):
        """Init game.

        :var self.width: horizontal resolution
        :var self.height: vertical resolution
        :var self.resolution: resolution
        :var self.display: instance of pygame display
        :var self.clock: instance of pygame clock
        :var self.player: instance of player
        :var self.renderer: instance of renderer

        """

        self.width: int = 800
        self.height: int = 450
        self.resolution: tuple[int, int] = (self.width, self.height)
        self.display = pg.display.set_mode(self.resolution, pg.SCALED)
        self.clock = pg.time.Clock()

        self.player = Player()
        background = BackgroundConfig(self.player.minimum_height, self.player.maximum_height, [75, 165, 210],
                                      [38, 95, 160])
        settings = RendererSettings(2000, 300, math.pi / 3, math.pi / 4, background, 7)
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
