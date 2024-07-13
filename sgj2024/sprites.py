import arcade
from sgj2024.config import *

class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.texture = arcade.load_texture("assets/player/cat.png")
        self.scale = SPRITE_SCALING_PLAYER
