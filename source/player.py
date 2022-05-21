import math

import numpy as np

class Player:
    def __init__(self):
        self.pos = np.array([0, 0], dtype = float)
        self.angle = math.pi / 4
        self.height = 100
        self.pitch = 50
        self.angle_velocity = 0.01
        self.velocity = 5

    def update(self):
        pass