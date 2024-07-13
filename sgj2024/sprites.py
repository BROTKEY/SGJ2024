import arcade
from sgj2024.config import *

class PlayerSprite(arcade.Sprite):
    FUEL_BOX = (138, 80, 180, 188)

    def __init__(self):
        super().__init__()

        self.texture = arcade.load_texture("assets/player/cat.png")
        self.scale = SPRITE_SCALING_PLAYER
        self.fuel = 0.0

        x1, y1, x2, y2 = PlayerSprite.FUEL_BOX
        w, h = x2 - x1, y2 - y1
        # self.fuel_box = PlayerSprite.FUEL_BOX
        cx = x1 - w / 2
        cy = y1 - h / 2
        self.fuel_box_cx = cx * self.scale
        self.fuel_box_cy = cy * self.scale
        self.fuel_box_width = w * self.scale
        self.fuel_box_height = h * self.scale



    def update(self, fuel_state):
        self.fuel = fuel_state
    

    def draw(self):
        # Draw black fuel background
        x, y = self.position
        x, y = self.left, self.bottom
        x += self.fuel_box_cx
        y += self.fuel_box_cy
        # arcade.draw_rectangle_filled(x, y, self.fuel_box_width, self.fuel_box_height, (32, 32, 32))
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