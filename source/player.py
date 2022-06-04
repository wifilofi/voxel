import math

import numpy as np
import pygame as pg


class Player:
    def __init__(self):
        """Init player variables.

        :var self.pos: position on 2D map
        :var self.angle: rotation angle
        :var self.pitch: vertical field of view
        :var self.angle_velocity: rotation speed
        :var self.velocity: movement speed.
        """

        self.pos = np.array([0, 0], dtype=float)
        self.angle = math.pi / 4
        self.height = 500
        self.pitch = math.pi / 4
        self.angle_velocity = math.pi / 240
        self.velocity = 10

    def normalize_vector(self, vector):
        """Normalize vector.

        :param vector: input vector
        :returns: normalized input vector.
        """
        return vector / math.sqrt(vector[0] ** 2 + vector[1] ** 2)


    def update(self):
        """Update player state. Check controls.
        """

        pressed_key = pg.key.get_pressed()
        if pressed_key[pg.K_UP]:
            self.pitch -= self.angle_velocity

        if pressed_key[pg.K_DOWN]:
            self.pitch += self.angle_velocity

        if pressed_key[pg.K_LEFT]:
            self.angle -= self.angle_velocity

        if pressed_key[pg.K_RIGHT]:
            self.angle += self.angle_velocity

        if pressed_key[pg.K_q]:
            self.height += self.velocity

        if pressed_key[pg.K_e]:
            self.height -= self.velocity

        x_velocity = 0
        y_velocity = 0
        if pressed_key[pg.K_w]:
            y_velocity += 1
        if pressed_key[pg.K_s]:
            y_velocity -= 1
        if pressed_key[pg.K_a]:
            x_velocity += 1
        if pressed_key[pg.K_d]:
            x_velocity -= 1

        if x_velocity == 0 and y_velocity == 0:
            return

        normalized = self.normalize_vector(np.array([x_velocity, y_velocity])) * self.velocity
        theta = self.angle - math.pi / 2
        sin = math.sin(theta)
        cos = math.cos(theta)
        self.pos[0] += normalized[0] * cos - normalized[1] * sin
        self.pos[1] += normalized[0] * sin + normalized[1] * cos
