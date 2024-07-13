from sgj2024.interfaces.baseController import BaseController
import pyglet.input as input 
import numpy as np
import pyglet

class XInputController(BaseController):
    def __init__(self):
        super().__init__()
        self.controllers = input.get_controllers()
        self.angle = 0
        self.impulse = 0

    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(self, v1, v2):
        _, ly = v1
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        side = 1 if ly < 0 else -1
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) / side

    def start(self):
        if len(self.controllers) > 0:
            self.controller = self.controllers[0]
            self.controller.open()
            pyglet.clock.schedule_interval(self.getAnalogAxis, 1/60.0)

    def stop(self):
        self.controller.close()

    def getAnalogAxis(self, delta_time):
        if self.controller.leftx < -0.8 or self.controller.leftx > 0.8 or self.controller.lefty < -0.8 or self.controller.lefty > 0.8:
            self.angle = self.angle_between((self.controller.leftx, self.controller.lefty), (1,0))
        self.impulse = self.controller.righttrigger
        self.controller.rumble_play_strong(self.impulse, delta_time)
    
    def pollAxis(self):
        return self.impulse, self.angle
