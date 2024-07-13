import arcade
from sgj2024.config import *

class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.texture = arcade.load_texture("assets/player/cat.png")
        self.scale = SPRITE_SCALING_PLAYER
        self.fuel = 0.0


    def update(self, fuel_state):
        self.fuel = fuel_state
    

    def draw(self):
        # Draw black fuel background
        x, y = self.position
        x += 30 * self.scale
        y -= 10 * self.scale
        w = 40 * self.scale
        h = 110 * self.scale
        arcade.draw_rectangle_filled(x, y, w, h, (0, 0, 0))

        h2 = self.fuel * h
        y2 = y - (h - h2)/2
        arcade.draw_rectangle_filled(x, y2, w, h2, (128, 128, 255))
        
        super().draw()