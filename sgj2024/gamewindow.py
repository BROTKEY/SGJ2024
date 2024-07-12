import arcade

class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug


    def setup(self):
        """ Set up everything with the game """
        pass

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        pass

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """
        pass

    def on_draw(self):
        """ Draw everything """
        self.clear()
