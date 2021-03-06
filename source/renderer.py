import math

import pygame as pg
import numpy as np

from numba import njit


class Map:
    """
    Data structure with loaded maps
    """

    def __init__(self, color_map, heightmap):
        """
        Create map data structure
        :param color_map: loaded array of colors
        :param heightmap: loaded array of heights
        """

        self.color_map = color_map
        self.heightmap = heightmap


@njit(fastmath=True)
def mix_colors(a, b, factor):
    """
    Mix colors with linear interpolation.
    For example for 0.5 factor the result color will be average between a na b.
    :param a: first color, will be result for 0 factor. Array of 3 elements
    :param b:second color, will be result for 1 factor. Array of 3 elements
    :param factor: linear mix factor
    :return: mix of 2 colors
    """
    result = [0, 0, 0]
    for i in range(3):
        result[i] = (b[i] - a[i]) * factor + a[i]


@njit(fastmath=True)
def raycast(
        screen_data,
        player_pos,
        player_angle,
        player_height,
        player_pitch,
        screen_width,
        screen_height,
        delta_angle,
        ray_distance,
        fov_x,
        scale_height,
        background_color,
        fading_size,
        colormap,
        heightmap,
):
    """
    Perform raycasting 1d raycasting.
    How it works:
    Image 1d line of color. Every pixel in that line represents ray.
    Every single ray goes throw whole map and check every height map value it can cross.
    Every crossed value will be drawn on screen as vertical bar

    :param colormap: 2d color map
    :param heightmap: 2d map of heights
    :param fading_size: amount of pixel will be mixed with background color
    :param background_color: color of screen where no terrain was rendered
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

    map_height = len(heightmap[0])
    map_width = len(heightmap)
    screen_data[:] = np.array(background_color)

    # horizontal buffer for each ray
    y_buffer = np.full(screen_width, screen_height)

    ray_angle = player_angle - fov_x / 2
    tan_of_pitch = math.sin(player_pitch)

    for ray_index in range(screen_width):
        contacted = False
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        max_vertical_position = -1
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

            # Create vertical bars
            if height_on_screen < y_buffer[ray_index]:
                max_vertical_position = y_buffer[ray_index] - 1
                for screen_y in range(height_on_screen, y_buffer[ray_index]):
                    screen_data[ray_index, screen_y] = colormap[x, y]

                y_buffer[ray_index] = height_on_screen

        ray_angle += delta_angle
        if max_vertical_position < 0:
            continue

        # That part corresponds on fading
        # It is used to make border between terrain and sky look better
        for delta in range(0, fading_size):
            screen_y = max_vertical_position + delta
            if screen_y < 0:
                continue

            current_color = screen_data[ray_index, screen_y]
            result = [0, 0, 0]
            factor = delta / fading_size
            for i in range(3):
                result[i] = (current_color[i] - background_color[i]) * factor + background_color[i]
            screen_data[ray_index, screen_y] = result

    return screen_data


class BackgroundConfig:
    """
    Data structure to describe,
    how background color will change depending on height.
    """

    def __init__(self, min_height, max_height, min_color, max_color):
        self.min_height = min_height
        self.max_height = max_height
        self.min_color = min_color
        self.max_color = max_color


class RendererSettings:
    """
    Data structure to provide access to temporal and permanent
    settings of rendering.
    """

    def __init__(self, ray_distance, scale_height, fov_x, fov_y, background_config, fading_size, map):
        """
        Create settings
        :param ray_distance: max distance of draw
        :param scale_height: coefficient to transform height to pixels
        :param fov_x: field of view for horizontal
        :param fov_y: field of view for vertical
        :param background_config: config of background color
        :param fading_size: amount of pixel to create transition from background to terrain
        """
        self.ray_distance = ray_distance
        self.scale_height = scale_height
        self.fov_x = fov_x
        self.fov_y = fov_y
        self.fading_size = fading_size
        self.__background_config = background_config
        self.map = map

    def get_background_color(self, height):
        """
        Calculate background color depending on height
        :param height: current height to calculate background color
        :return: background color
        """
        config = self.__background_config
        clamped = np.clip(height, config.min_height, config.max_height)
        coeff = (clamped - config.min_height) / (config.max_height - config.min_height)
        result_color = [0, 0, 0]
        for i in range(3):
            result_color[i] = (config.max_color[i] - config.min_color[i]) * coeff + config.min_color[i]
        return result_color


class Renderer:
    def __init__(self, game, renderer_settings):
        """
        Init renderer.

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
        self.rays_amount = game.width
        self.renderer_settings = renderer_settings
        self.delta_angle = (renderer_settings.fov_x / self.rays_amount)
        self.screen_data = np.full((game.width, game.height, 3), (0, 0, 0))

    def update(self):
        """
        Update state of renderer.
        Cast all horizontal rays
        """
        background_color = self.renderer_settings.get_background_color(self.player.height)

        self.screen_data = raycast(screen_data=self.screen_data,
                                   player_pos=self.player.pos,
                                   player_angle=self.player.angle,
                                   player_height=self.player.height,
                                   player_pitch=self.player.pitch,
                                   screen_width=self.game.width,
                                   screen_height=self.game.height,
                                   delta_angle=self.delta_angle,
                                   ray_distance=self.renderer_settings.ray_distance,
                                   fov_x=self.renderer_settings.fov_x,
                                   scale_height=self.renderer_settings.scale_height,
                                   background_color=background_color,
                                   fading_size=self.renderer_settings.fading_size,
                                   colormap=self.renderer_settings.map.color_map,
                                   heightmap=self.renderer_settings.map.heightmap)

    def render(self):
        """
        Copy array of colors to player screen
        """
        pg.surfarray.blit_array(self.game.display, self.screen_data)
