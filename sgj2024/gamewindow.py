import arcade
from typing import Optional
import numpy as np
import pymunk
import time

from sgj2024.sprites import PlayerSprite
from sgj2024.config import *
from sgj2024.interfaces.baseController import BaseController
from sgj2024.interfaces.xInputController import XInputController
from sgj2024.interfaces.whistleController import WhistleController


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
        self.bottles: Optional[arcade.SpriteList] = None
        self.cacti: Optional[arcade.SpriteList] = None

        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None
        self.player_sprite = None
        
        self.start_sprite: Optional[arcade.Sprite] = None
        self.finish_sprite: Optional[arcade.Sprite] = None
        self.finish_list: Optional[arcade.SpriteList] = None

        self.yeet_force = [0, 0]
        self.delta_v = 0
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False

        self.bottle_00_texture: Optional[arcade.texture.Texture] = None
        self.bottle_01_texture: Optional[arcade.texture.Texture] = None
        self.bottle_02_texture: Optional[arcade.texture.Texture] = None

        self.active_bottles = {}

        self.controller: Optional[BaseController] = None

    def setup(self):
        arcade.set_background_color((140, 0, 255))
        self.player_sprite = PlayerSprite()

        self.finish_list = arcade.SpriteList()

        self.bottle_00_texture = arcade.load_texture(
                "assets/SGJ24TILES/not_yet_sploding_cola.png"
        )
        self.bottle_01_texture = arcade.load_texture(
                "assets/SGJ24TILES/sploding_cola_1.png"
        )
        self.bottle_02_texture = arcade.load_texture(
                "assets/SGJ24TILES/sploding_cola_2.png"
        )

        self.controller = XInputController()
        self.controller.start()

        self.load_level(1)

    def cleanup(self):
        """Cleanup (like stopping our interfaces)"""
        self.controller.stop()

    def load_level(self, level):
        if self.debug:
            print(f"Debug: Loading Level: {level}")
        self.current_level = level
        tile_map = LEVELS[level]["tilemap"]

        self.map_bounds_x = tile_map.width * tile_map.tile_width * tile_map.scaling
        self.map_bounds_y = tile_map.height * tile_map.tile_height * tile_map.scaling

        self.camera = arcade.Camera(self.width, self.height, self)

        self.start_sprite = tile_map.sprite_lists["Spawn"][0]
        self.player_sprite.set_position(*self.
            start_sprite.position)

        self.finish_sprite = tile_map.sprite_lists["Finish"][0]
        self.finish_list.append(self.finish_sprite)

        self.background_elements = tile_map.sprite_lists["Background"]
        self.background_accents = tile_map.sprite_lists["BackgroundAccents"]
        self.wall_elements = tile_map.sprite_lists["Platforms"]
        self.bottles = tile_map.sprite_lists["Bottles"]
        self.cacti = tile_map.sprite_lists["Cacti"]

        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=PHYSICS_DAMPING, gravity=(0, -PHYSICS_GRAVITY))
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

        self.physics_engine.add_sprite(self.finish_sprite,
                                       collision_type="finish",
                                       body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.physics_engine.add_sprite_list(self.cacti, collision_type="cacti", body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(
            self.bottles, friction=WALL_FRICTION, collision_type="bottle", body_type=arcade.PymunkPhysicsEngine.STATIC)
        
        self.physics_engine.add_collision_handler("player", "bottle", self.bottle_colision_handler)

        self.physics_engine.add_collision_handler("player", "cacti", self.cacti_colision_handler)

        self.physics_engine.add_collision_handler("player", "finish", begin_handler=self.level_finished)

    def level_finished(self, _0, _1, _2, _3, _4):
        if self.debug: print("Level Finished!")
        return False

    def cacti_colision_handler(self, player_sprite: PlayerSprite, cacti_sprite: arcade.Sprite, arbiter: pymunk.Arbiter, space, data):
        velocity = self.physics_engine.get_physics_object(self.player_sprite).body.velocity
        counterforce = np.array(velocity) * -1
        print(velocity)
        print(counterforce)
        self.physics_engine.set_velocity(self.player_sprite, tuple(counterforce))
        return True

    def bottle_colision_handler(self, player_sprite: PlayerSprite, bottle_sprite: arcade.Sprite, arbiter: pymunk.Arbiter, space, data):
        vector = np.zeros((2))
        vector[1] = np.cos(bottle_sprite.radians)
        vector[0] = -np.sin(bottle_sprite.radians)

        self.physics_engine.apply_force(player_sprite, tuple(vector * BOTTLE_ACCELERATION))

        self.active_bottles[bottle_sprite] = 90
        
        return False

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        map_bounds = np.array([self.map_bounds_x, self.map_bounds_y])
        camera_size = np.array(
            [self.camera.viewport_width, self.camera.viewport_height])

        target_position = np.array([self.player_sprite.center_x - self.width / 2,
                                    self.player_sprite.center_y - self.height / 2])
        target_position = np.max([target_position, np.zeros(2)], axis=0)
        target_position = np.min(
            [target_position, map_bounds-camera_size], axis=0)

        camera_speed = min(np.linalg.norm(
            target_position - np.array(self.camera.position)) * CAMERA_SPEED, 1)

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
        self.camera.move((self.player_sprite.center_x-self.width/2,
                         self.player_sprite.center_y-self.height/2))

        impulse, angle = self.controller.pollAxis()

        player_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
    
        self.player_sprite.pymunk.max_horizontal_velocity = PLAYER_MAX_HORIZONTAL_VELOCITY if player_on_ground else PLAYER_MAX_HORIZONTAL_AIR_VELOCITY

        if player_on_ground:
            self.delta_v = min(self.delta_v+DELTA_DELTAV, MAX_DELTAV)

        if impulse != 0:
            vector = np.zeros((2))
            vector[0] = np.cos(angle)
            vector[1] = np.sin(angle) * (not player_on_ground or ((angle > 0.3 or angle < -0.3) and (angle > -2.8 or angle < 2.8)))
            vector[0] *= impulse * min(self.delta_v, PLAYER_GROUND_ACCELERATION if player_on_ground else PLAYER_JETPACK_ACCELERATION if self.delta_v > 0 else PLAYER_AIR_ACCELERATION)
            vector[1] *= impulse * min(self.delta_v, PLAYER_JETPACK_ACCELERATION)

            sub = min(self.delta_v, np.sum(np.abs(vector)))
            self.delta_v = self.delta_v - (0 if player_on_ground else sub)
            if self.debug:
                print(self.delta_v, vector, sub)

            self.physics_engine.apply_force(self.player_sprite, tuple(vector))

        if self.debug:
            yeet_angle = 0.0
            yeet_strength = 0.0
            n_directions = self.w_pressed + self.a_pressed + self.s_pressed + self.d_pressed
            if n_directions != 0 and self.delta_v > 0:
                if self.w_pressed:
                    self.yeet_force[1] += min(self.delta_v /
                                              n_directions, PLAYER_JETPACK_ACCELERATION)
                if self.a_pressed:
                    self.yeet_force[0] -= min(self.delta_v /
                                              n_directions, PLAYER_JETPACK_ACCELERATION)
                if self.s_pressed:
                    self.yeet_force[1] -= min(self.delta_v /
                                              n_directions, PLAYER_JETPACK_ACCELERATION)
                if self.d_pressed:
                    self.yeet_force[0] += min(self.delta_v /
                                              n_directions, PLAYER_JETPACK_ACCELERATION)
                self.delta_v -= min(self.delta_v, PLAYER_JETPACK_ACCELERATION)
                if self.debug:
                    print(self.delta_v, self.yeet_force)

                self.physics_engine.apply_force(
                    self.player_sprite, tuple(self.yeet_force))
                yeet_angle = np.atan2(*self.yeet_force)
                yeet_strength = np.linalg.norm(self.yeet_force) / np.linalg.norm((PLAYER_JETPACK_ACCELERATION, PLAYER_JETPACK_ACCELERATION))
                self.yeet_force = [0, 0]

        self.physics_engine.step()

        self.player_sprite.update(angle, impulse, self.delta_v / MAX_DELTAV)
        if self.debug and yeet_strength > 0:
            self.player_sprite.update(-yeet_angle, yeet_strength, self.delta_v / MAX_DELTAV)

        mark_delete = []
        for bottle, timer in self.active_bottles.items():
            if timer % (BOTTLE_FRAME_TIMER*2) == 0:
                bottle.texture = self.bottle_01_texture
            elif timer % BOTTLE_FRAME_TIMER == 0:
                bottle.texture = self.bottle_02_texture
            self.active_bottles[bottle] -= 1
            if timer == 0:
                bottle.texture = self.bottle_00_texture
                mark_delete.append(bottle)

        for bottle in mark_delete:
            self.active_bottles.pop(bottle)

        if self.player_sprite.position[0] < 60: self.physics_engine.set_position(self.player_sprite, (60, self.player_sprite.position[1]))
        elif self.player_sprite.position[0] > self.map_bounds_x-60: self.physics_engine.set_position(self.player_sprite, (self.map_bounds_x-60, self.player_sprite.position[1]))

        self.scroll_to_player()

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.background_elements.draw()
        self.background_accents.draw()
        self.wall_elements.draw()
        self.finish_list.draw()
        self.bottles.draw()
        self.cacti.draw()
        self.player_sprite.draw()