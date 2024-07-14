from sgj2024.interfaces.baseController import BaseController
from sgj2024.interfaces.whistleController import WhistleController
from sgj2024.interfaces.xInputController import XInputController

class HybridController(BaseController):
    def __init__(self):
        self.whistle = WhistleController()
        self.xInput = XInputController()

    def start(self):
        self.whistle.start()
        self.xInput.start()

    def stop(self):
        self.whistle.stop()
        self.xInput.stop()

    def pollAxis(self):
        impulse1, angle1 = self.whistle.pollAxis()
        impulse2, angle2 = self.xInput.pollAxis()
        return impulse1, angle2
