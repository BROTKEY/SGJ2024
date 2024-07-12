import arcade

LEVELS = {
        1: {
            "tilemap": arcade.load_tilemap("assets/test.json")
            }
}

class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug

        self.current_level = 1
        self.wall_elements = Optional[arcade.SpriteList] = None

    def load_level(self, level):
        self.current_level = level
        tile_map = LEVELS[level]["tilemap"]
        
        self.wall_elements = tile_map.sprite_lists["Platforms"]

    def on_draw(self):
        self.clear()
        self.wall_elements.draw()