import arcade
from sgj2024.config import *
import numpy as np


class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.texture = arcade.load_texture("assets/player/cat.png")
        self.scale = SPRITE_SCALING_PLAYER
        self.fuel = 0.0

        self.direction_indicator = DirectionIndicator(self, 'assets/SGJ24TILES/Cursor.png', scale=0.5*self.scale)


    def update(self, direction, force, fuel_state):
        self.input_direction = direction
        self.input_force = force
        self.fuel = fuel_state
        # physics_engine.get_physics_object(self.direction_indicator).body.position = self.position
        self.direction_indicator.update(self.position, direction, force)
    

    def draw(self):
        # Draw black fuel background
        x, y = self.position
        x += 30 * self.scale
        y -= 10 * self.scale
        w = 40 * self.scale
        h = 110 * self.scale
        arcade.draw_rectangle_filled(x, y, w, h, (0, 0, 0))

        # Draw blue fuel fill status
        h2 = self.fuel * h
        y2 = y - (h - h2)/2
        arcade.draw_rectangle_filled(x, y2, w, h2, (128, 128, 255))
        
        # Draw character itself
        super().draw()

        # Draw direction indicator
        self.direction_indicator.draw()
        


class DirectionIndicator(arcade.Sprite):
    def __init__(self, player_sprite: PlayerSprite, filename, scale=1.0):
        super().__init__()
        self.player_sprite = player_sprite
        self.texture = arcade.load_texture(filename)
        self.scale = scale
        self.input_direction = 0.0
        self.input_force = 0.0
        self.player_position = player_sprite.position
    
    def update(self, player_position, direction, force):
        self.player_position = player_position
        self.input_direction = direction
        self.input_force = force

        self.angle = np.degrees(self.input_direction)
        x, y = player_position
        x -= np.sin(self.input_direction) * self.scale * 500
        y += np.cos(self.input_direction) * self.scale * 500
        self.position = x, y
        

    def draw(self):
        if self.input_force > 0:
            super().draw()