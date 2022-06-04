import math

import numpy as np
import pygame as pg


class Player:
    """
    Represents current player state and provides methods to get input
    """
    def __init__(self):
        """
        Init player variables.

        :var self.pos: position on 2D map
        :var self.angle: rotation angle
        :var self.pitch: vertical field of view
        :var self.angle_velocity: rotation speed
        :var self.velocity: movement speed
        :var self.minimum_height minimum height that player can move on
        :var self.maximum_height maximum height that player can move on
        """

        # Set initial position in South America.
        self.pos = np.array([4000, 4000], dtype=float)
        self.angle = math.pi / 4
        self.height = 400
        self.pitch = math.pi / 4
        self.angle_velocity = math.pi / 240
        self.velocity = 4
        self.minimum_height = 250
        self.maximum_height = 750

    def normalize_vector(self, vector):
        """Normalize vector.

        :param vector: input vector
        :returns: normalized input vector.
        """
        return vector / math.sqrt(vector[0] ** 2 + vector[1] ** 2)


    def handle_input(self):
        """
        Get input from player
        """
        pressed_key = pg.key.get_pressed()

        # W key to move down
        if pressed_key[pg.K_w]:
            self.height -= self.velocity

        # S key to move up
        if pressed_key[pg.K_s]:
            self.height += self.velocity

        # A key to rotate camera left
        if pressed_key[pg.K_a]:
            self.angle -= self.angle_velocity

        # D key to rotate camera right
        if pressed_key[pg.K_d]:
            self.angle += self.angle_velocity


    def update(self):
        """
        Update player state. Check controls.
        """

        self.handle_input()
        # Limit possible player height.
        self.height = np.clip(self.height, self.minimum_height, self.maximum_height)

        # Get normalized velocity vector to get rid of acceleration when players press two key at the same time.
        normalized = self.normalize_vector(np.array([0, 1])) * self.velocity

        # Angle correction, to move zero point 90 degrees counterclockwise
        theta = self.angle - math.pi / 2
        sin = math.sin(theta)
        cos = math.cos(theta)

        # Use 2d rotation matrix to rotate player
        self.pos[0] += normalized[0] * cos - normalized[1] * sin
        self.pos[1] += normalized[0] * sin + normalized[1] * cos
