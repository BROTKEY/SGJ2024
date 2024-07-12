import arcade
from typing import Optional

LEVELS = {
    1: {
        "tilemap": arcade.load_tilemap("assets/TEST.json")
    }
}


class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug

        self.current_level = 1
        self.wall_elements: Optional[arcade.SpriteList] = None
        self.load_level(1)

    def load_level(self, level):
        if self.debug:
            print(f"Debug: Loading Level: {level}")
        self.current_level = level
        tile_map = LEVELS[level]["tilemap"]

        self.camera = arcade.Camera(self.width, self.height, self)

        self.wall_elements = tile_map.sprite_lists["Platforms"]

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.wall_elements.draw()
