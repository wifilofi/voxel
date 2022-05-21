import math

import pygame as pg
import numpy as np

from numba import njit

colormap_img = pg.image.load('textures/C1W.png')
colormap = pg.surfarray.array3d(colormap_img)

heightmap_img = pg.image.load('textures/D1.png')
heightmap = pg.surfarray.array3d(heightmap_img)

map_height = len(heightmap[0])
map_width = len(heightmap)

@njit(fastmath = True)
def raycast(screen_data, player_pos, player_angle, player_height, player_pitch,
            screen_width, screen_height, delta_angle, ray_distance, fov_x, scale_height):

    screen_data[:] = np.array([0, 0, 0])
    y_buffer = np.full(screen_width, screen_height)

    ray_angle = player_angle - fov_x

    for ray_index in range(screen_width):
        contacted = False
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, ray_distance):
            x = int(player_pos[0] + depth * cos_a)

            if 0 < x < map_width:
                y = int(player_pos[1] + depth * sin_a)
                if 0 < y < map_height:
                    height_on_screen = int((player_height - heightmap[x, y][0])
                                           / depth * scale_height + player_pitch)

                    if height_on_screen < y_buffer[ray_index]:
                        for screen_y in range(height_on_screen, y_buffer[ray_index]):
                            screen_data[ray_index, screen_y] = colormap[x, y]

                        y_buffer[ray_index] = height_on_screen

        ray_angle += delta_angle
    return screen_data


class Renderer:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.fov_y = math.pi / 6
        self.fov_x = self.fov_y / 2
        self.rays_amount = game.width
        self.delta_angle = (self.fov_x / self.rays_amount)
        self.ray_distance = 2000
        self.scale_height = 920
        self.screen_data = np.full((game.width, game.height, 3), (0, 0, 0))

    def update(self):
        self.screen_data = raycast(screen_data = self.screen_data,
                                   player_pos = self.player.pos,
                                   player_angle = self.player.angle,
                                   player_height = self.player.height,
                                   player_pitch = self.player.pitch,
                                   screen_width = self.game.width,
                                   screen_height = self.game.height,
                                   delta_angle = self.delta_angle,
                                   ray_distance = self.ray_distance,
                                   fov_x = self.fov_x,
                                   scale_height = self.scale_height)



    def render(self):
        pg.surfarray.blit_array(self.game.display, self.screen_data)