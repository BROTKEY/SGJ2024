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
        # if self.input_force <= 0:
        #     return
        
        def R(theta):
            return np.array([[np.cos(theta), -np.sin(theta)],
                             [np.sin(theta), np.cos(theta)]])
        
        def rotate(points, theta):
            v = np.reshape(points, (-1, 2)).T
            return np.dot(R(theta), v).T.reshape(points.shape)
        
        tri_w = 256 - 2*32
        tri_h = 256 - 2*20
        tri_w_2 = tri_w/2
        tri_h_2 = tri_h/2
        tri_x = -128 + 32
        tri_y = -128 + 20

        pos = [-128, -128]
        P = np.array([[32, 20], [220, 20], [128, 236]], dtype='float')

        P = np.array([[tri_x, tri_y],                   # bottom left
                      [tri_x+tri_w, tri_y],             # bottom right
                      [tri_x + tri_w - self.input_force*tri_w_2, tri_y + (self.input_force)*tri_h],     # top right
                      [tri_x + self.input_force*tri_w_2, tri_y + (self.input_force)*tri_h]      # top left
                     ],
                     dtype='float')

        # P += pos
        P *= self.scale

        P = rotate(P, self.input_direction)
        P += self.position

        arcade.draw_polygon_filled(P.tolist(), (0, 0, 255))
        P += pos

        super().draw()