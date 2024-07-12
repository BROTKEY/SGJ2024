from sgj2024.interfaces.baseController import BaseController
import pyglet.input as input 

class XInputController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    def getAnalogAxis(self):
        return 0,0

def XInputAdapter():
    def __init__(self):
        controllers = input.get_controllers()
        self.controller = input.