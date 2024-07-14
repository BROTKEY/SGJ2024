from sgj2024.interfaces.baseController import BaseController
from sgj2024.interfaces.whistleController import WhistleController
from sgj2024.interfaces.xInputController import XInputController

class HybridController(BaseController):
    def __init__(self, whistle, xinput):
        self.whistle = whistle
        self.xInput = xinput

    def start(self):
        pass
        # self.whistle.start()
        # self.xInput.start()

    def stop(self):
        pass
        # self.whistle.stop()
        # self.xInput.stop()

    def pollAxis(self):
        impulse1, angle1 = self.whistle.pollAxis()
        impulse2, angle2 = self.xInput.pollAxis()
        return impulse1, angle2
