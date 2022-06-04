import math

import pygame as pg
import numpy as np

from numba import njit

colormap_img = pg.image.load('textures/color_map_4.png')
colormap = pg.surfarray.array3d(colormap_img)

heightmap_img = pg.image.load('textures/height_map_4.jpg')
heightmap = pg.surfarray.array3d(heightmap_img)

map_height = len(heightmap[0])
map_width = len(heightmap)


@njit(fastmath=True)
def raycast(screen_data, player_pos, player_angle, player_height, player_pitch,
            screen_width, screen_height, delta_angle, ray_distance, fov_x, scale_height):
    """Perform raycasting.

    :param screen_data: array of points on screen
    :param player_pos: player position
    :param player_angle: player rotation
    :param player_height: player height
    :param player_pitch: player vertical fov
    :param screen_width: screen horizontal resolution
    :param screen_height: screen vertical resolution
    :param delta_angle: angle difference
    :param ray_distance: render distance
    :param fov_x: horizontal fov
    :param scale_height: vertical scale

    """

    screen_data[:] = np.array([0, 0, 0])

    # horizontal buffer for each ray
    y_buffer = np.full(screen_width, screen_height)

    ray_angle = player_angle - fov_x / 2
    tan_of_pitch = math.sin(player_pitch)

    for ray_index in range(screen_width):
        contacted = False
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, ray_distance):
            x = int(player_pos[0] + depth * cos_a)

            # check whether coords are out of horizontal bound
            if x < 0 or x >= map_width:
                continue

            y = int(player_pos[1] + depth * sin_a) % map_height

            # check whether coords are out of vertical bound
            if y < 0 or y >= map_height:
                continue

            curvature = (depth / ray_distance) ** 2 * 500
            corrected_height = heightmap[x, y][0] - curvature

            # fix fish eye effect
            depth *= math.cos(player_angle - ray_angle)
            height_on_screen = int((player_height - corrected_height) / depth * scale_height * tan_of_pitch)

            # fix clamping
            if not contacted:
                y_buffer[ray_index] = min(height_on_screen, screen_height)
                contacted = True

            # fix mirror rendering
            if height_on_screen < 0:
                height_on_screen = 0

            # create vertical line
            if height_on_screen < y_buffer[ray_index]:
                for screen_y in range(height_on_screen, y_buffer[ray_index]):
                    screen_data[ray_index, screen_y] = colormap[x, y]

                y_buffer[ray_index] = height_on_screen

        ray_angle += delta_angle

    return screen_data


class Renderer:
    def __init__(self, game):
        """Init renderer.

        :param game: instance of game

        :var self.player: instance of player
        :var self.fov_y: vertical fov
        :var self.fov_x: horizontal fov
        :var self.rays_amount: horizontal resolution
        :var self.delta_angle: angle difference
        :var self.ray_distance: render distance
        :var self.scale_height: vertical scale
        :var self.screen_data: array of points on screen

        """

        self.game = game
        self.player = game.player
        self.fov_y = math.pi / 4
        self.fov_x = math.pi / 3
        self.rays_amount = game.width
        self.delta_angle = (self.fov_x / self.rays_amount)
        self.ray_distance = 2000
        self.scale_height = 300
        self.screen_data = np.full((game.width, game.height, 3), (0, 0, 0))

    def update(self):
        """Update state of renderer. Execute raycasting. """
        self.screen_data = raycast(screen_data=self.screen_data,
                                   player_pos=self.player.pos,
                                   player_angle=self.player.angle,
                                   player_height=self.player.height,
                                   player_pitch=self.player.pitch,
                                   screen_width=self.game.width,
                                   screen_height=self.game.height,
                                   delta_angle=self.delta_angle,
                                   ray_distance=self.ray_distance,
                                   fov_x=self.fov_x,
                                   scale_height=self.scale_height)

    def render(self):
        """Render raycasting result on screen."""
        pg.surfarray.blit_array(self.game.display, self.screen_data)
