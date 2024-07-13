import arcade
from typing import Optional
from sgj2024.sprites import PlayerSprite
from sgj2024.config import *

LEVELS = {
    1: {
        "tilemap": arcade.load_tilemap("assets/TEST.json", SPRITE_SCALING_TILES)
    }
}


class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug

        self.current_level = 1
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

    def setup(self):
        arcade.set_background_color((140,0,255))
        self.player_sprite = PlayerSprite()
        self.player_sprite.set_position(500,500)
        self.player_list.append(self.player_sprite)
        self.load_level(1)

    def load_level(self, level):
        if self.debug:
            print(f"Debug: Loading Level: {level}")
        self.current_level = level
        tile_map = LEVELS[level]["tilemap"]

        self.camera = arcade.Camera(self.width, self.height, self)

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

        player_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        if player_on_ground:
            self.delta_v = min(self.delta_v+DELTA_DELTAV, MAX_DELTAV)
            if self.debug: print(self.delta_v)

        n_directions = self.w_pressed + self.a_pressed + self.s_pressed + self.d_pressed
        if n_directions != 0 and self.delta_v > 0:
            force = [0,0]
            if self.w_pressed: force[1] += min(self.delta_v/n_directions, PLAYER_ACCELERATION)
            if self.a_pressed: force[0] -= min(self.delta_v/n_directions, PLAYER_ACCELERATION)
            if self.s_pressed: force[1] -= min(self.delta_v/n_directions, PLAYER_ACCELERATION)
            if self.d_pressed: force[0] += min(self.delta_v/n_directions, PLAYER_ACCELERATION)
            self.delta_v -= min(self.delta_v, PLAYER_ACCELERATION)
            if self.debug: print(self.delta_v, force)

            self.physics_engine.apply_force(self.player_sprite, tuple(force))
            self.yeet_force = [0,0]

        self.physics_engine.step()

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.wall_elements.draw()
        self.player_list.draw()
