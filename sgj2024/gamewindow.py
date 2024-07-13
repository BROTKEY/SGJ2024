import arcade
from typing import Optional
from sgj2024.sprites import PlayerSprite
from sgj2024.config import *
from sgj2024.interfaces.xInputController import *
import numpy as np

LEVELS = {
    0: {
        "tilemap": arcade.load_tilemap("assets/TEST.json", SPRITE_SCALING_TILES)
    },
    1: {
        "tilemap": arcade.load_tilemap("assets/Level1.json", SPRITE_SCALING_TILES)
    }
}


class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug

        self.current_level = 1
        self.background_elements: Optional[arcade.SpriteList] = None
        self.background_accents: Optional[arcade.SpriteList] = None
        self.wall_elements: Optional[arcade.SpriteList] = None

        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None
        self.player_sprite = None
        self.player_list = arcade.SpriteList()

        self.yeet_force = [0,0]
        self.delta_v = 0
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False
        
        self.controller: Optional[BaseController] = None

    def setup(self):
        arcade.set_background_color((140,0,255))
        self.player_sprite = PlayerSprite()
        self.player_list.append(self.player_sprite)

        self.controller = XInputController()
        self.controller.start()

        self.load_level(1)

    def cleanup(self):
        """Cleanup (like stopping our interfaces)"""
        pass

    def load_level(self, level):
        if self.debug:
            print(f"Debug: Loading Level: {level}")
        self.current_level = level
        tile_map = LEVELS[level]["tilemap"]

        self.map_bounds_x = tile_map.width * tile_map.tile_width * tile_map.scaling
        self.map_bounds_y = tile_map.height * tile_map.tile_height * tile_map.scaling

        self.camera = arcade.Camera(self.width, self.height, self)

        start_sprite = tile_map.sprite_lists["Spawn"][0]
        self.player_sprite.set_position(start_sprite.position[0], start_sprite.position[1])

        self.background_elements = tile_map.sprite_lists["Background"]
        self.background_accents = tile_map.sprite_lists["BackgroundAccents"]
        self.wall_elements = tile_map.sprite_lists["Platforms"]

        self.physics_engine = arcade.PymunkPhysicsEngine(damping=PHYSICS_DAMPING, gravity=(0,-PHYSICS_GRAVITY))
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_VELOCITY,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_VELOCITY
        )

        self.physics_engine.add_sprite_list(self.wall_elements,
                                       friction=WALL_FRICTION,
                                       collision_type="wall",
                                       body_type=arcade.PymunkPhysicsEngine.STATIC
        )

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        map_bounds = np.array([self.map_bounds_x, self.map_bounds_y])
        camera_size = np.array([self.camera.viewport_width, self.camera.viewport_height])

        target_position = np.array([self.player_sprite.center_x - self.width / 2,
                        self.player_sprite.center_y - self.height / 2])
        target_position = np.max([target_position, np.zeros(2)], axis=0)
        target_position = np.min([target_position, map_bounds-camera_size], axis=0)

        camera_speed = min(np.linalg.norm(target_position - np.array(self.camera.position)) * CAMERA_SPEED, 1)

        self.camera.move_to(tuple(target_position), camera_speed)

    def on_key_press(self, key, modifiers):
        match key:
            case arcade.key.W:
                self.w_pressed = True
            case arcade.key.A:
                self.a_pressed = True
            case arcade.key.S:
                self.s_pressed = True
            case arcade.key.D:
                self.d_pressed = True

    def on_key_release(self, key, modifiers):
        match key:
            case arcade.key.W:
                self.w_pressed = False
            case arcade.key.A:
                self.a_pressed = False
            case arcade.key.S:
                self.s_pressed = False
            case arcade.key.D:
                self.d_pressed = False 

    def on_update(self, delta_time):
        self.camera.move((self.player_sprite.center_x-self.width/2, self.player_sprite.center_y-self.height/2))

        impulse, angle = self.controller.pollAxis()

        player_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        if player_on_ground:
            self.delta_v = min(self.delta_v+DELTA_DELTAV, MAX_DELTAV)
            if self.debug: print(self.delta_v)

        if self.delta_v > 0 and impulse != 0:
            vector = np.zeros((2))
            vector[0] = np.cos(angle)
            vector[1] = np.sin(angle)
            vector *= impulse * min(self.delta_v, PLAYER_ACCELERATION)

            self.delta_v = self.delta_v - min(self.delta_v, impulse*PLAYER_ACCELERATION)
            if self.debug: print(self.delta_v, impulse)
            
            self.physics_engine.apply_force(self.player_sprite, tuple(vector))


        if self.debug:
            n_directions = self.w_pressed + self.a_pressed + self.s_pressed + self.d_pressed
            if n_directions != 0 and self.delta_v > 0:
                if self.w_pressed: self.yeet_force[1] += min(self.delta_v/n_directions, PLAYER_ACCELERATION)
                if self.a_pressed: self.yeet_force[0] -= min(self.delta_v/n_directions, PLAYER_ACCELERATION)
                if self.s_pressed: self.yeet_force[1] -= min(self.delta_v/n_directions, PLAYER_ACCELERATION)
                if self.d_pressed: self.yeet_force[0] += min(self.delta_v/n_directions, PLAYER_ACCELERATION)
                self.delta_v -= min(self.delta_v, PLAYER_ACCELERATION)
                if self.debug: print(self.delta_v, self.yeet_force)

                self.physics_engine.apply_force(self.player_sprite, tuple(self.yeet_force))
                self.yeet_force = [0,0]

        self.physics_engine.step()

        self.scroll_to_player()

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.background_elements.draw()
        self.background_accents.draw()
        self.wall_elements.draw()
        self.player_list.draw()
