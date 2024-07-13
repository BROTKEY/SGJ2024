from sgj2024.interfaces.baseController import BaseController
import pyglet.input as input 
import numpy as np
import pyglet

class XInputController(BaseController):
    def __init__(self):
        super().__init__()
        self.controller = None
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
        self.manager = input.ControllerManager()
        controllers = self.manager.get_controllers()
        print(controllers)
        pyglet.clock.schedule_interval(self.getAnalogAxis, 1/60)
        if len(controllers) > 0:
            self.controller = controllers[0]
            self.controller.open()

        @self.manager.event
        def on_connect(controller):
            self.controller = controller
            self.controller.open()
        @self.manager.event
        def on_disconnect(controller):
            self.controller.close()
        

    def getAnalogAxis(self, delta_time):
        try:
            if self.controller == None : return
            if self.controller.leftx < -0.8 or self.controller.leftx > 0.8 or self.controller.lefty < -0.8 or self.controller.lefty > 0.8:
                self.angle = self.angle_between((self.controller.leftx, self.controller.lefty), (1,0))
            self.impulse = self.controller.righttrigger
            self.controller.rumble_play_weak(self.impulse/4, delta_time)
        except OSError:
            return
    
    def pollAxis(self):
        return self.impulse, self.angle
