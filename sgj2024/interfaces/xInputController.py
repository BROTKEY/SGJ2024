from sgj2024.interfaces.baseController import BaseController
import pyglet.input as input 
import pyglet.input.controller as controller

class XInputController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    def getAnalogAxis(self):
        return 0,0

def XInputAdapter():
    def __init__(self):
        controllers = input.get_controllers()
        self.controller = controllers[0].open()

    @controller.event
    def on_stick_motion(controller, name, x_value, y_value):
        if name == "leftstick":
            pass
            # Do something with the x/y_values
        elif name == "rightstick":
            pass
            # Do something with the x/y_values