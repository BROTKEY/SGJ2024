import arcade
from typing import Optional
import arcade.key
import numpy as np
import pymunk
import time
import pyglet.media

from sgj2024.sprites import PlayerSprite, BackgroundSprite
from sgj2024.config import *
from sgj2024.interfaces.baseController import BaseController
from sgj2024.interfaces.xInputController import XInputController
from sgj2024.interfaces.whistleController import WhistleController


LEVELS = {
    0: {
        "tilemap": arcade.load_tilemap("assets/TEST.json", SPRITE_SCALING_TILES)
    },
    1: {
        "tilemap": arcade.load_tilemap("assets/vertical.json", SPRITE_SCALING_TILES)
    }
}


class GameWindow(arcade.Window):
    def __init__(self, width, height, title, debug=False):
        super().__init__(width, height, title)
        self.debug = debug

        self.current_level = 1
        self.on_water = False
        self.background_elements: Optional[arcade.SpriteList] = None
        self.background_accents: Optional[arcade.SpriteList] = None
        self.wall_elements: Optional[arcade.SpriteList] = None
        self.bottles: Optional[arcade.SpriteList] = None
        self.cacti: Optional[arcade.SpriteList] = None
        self.water: Optional[arcade.SpriteList] = None

        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None
        self.player_sprite = None

        self.start_sprite: Optional[arcade.Sprite] = None
        self.finish_sprite: Optional[arcade.Sprite] = None
        self.finish_list: Optional[arcade.SpriteList] = None

        self.yeet_force = [0, 0]
        self.delta_v = MAX_DELTAV
        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False
        self.m_pressed = False
        self.space_pressed = False
        self.backspace_pressed = False

        self.bottle_00_texture: Optional[arcade.texture.Texture] = None
        self.bottle_01_texture: Optional[arcade.texture.Texture] = None
        self.bottle_02_texture: Optional[arcade.texture.Texture] = None

        self.active_bottles = {}

        self.controller: Optional[BaseController] = None

        self.theme: Optional[arcade.Sound] = None
        self.music_player: Optional[pyglet.media.Player] = None
        self.muted: bool = False


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

        self.theme = arcade.load_sound('assets/sound/music.mp3')

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
        self.background_camera = arcade.Camera(self.width, self.height, self)

        self.background_sprite = BackgroundSprite(tile_map.width*SPRITE_SCALING_TILES)

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
        self.water = tile_map.sprite_lists["Water"]

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

        self.physics_engine.add_sprite_list(
            self.cacti, collision_type="cacti", body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(
            self.water, collision_type="water", body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(
            self.bottles, friction=WALL_FRICTION, collision_type="bottle", body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(
            self.water, collision_type="water", body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_collision_handler(
            "player", "bottle", self.bottle_colision_handler)

        self.physics_engine.add_collision_handler(
            "player", "cacti", self.cacti_colision_handler)

        self.physics_engine.add_collision_handler(
            "player", "finish", begin_handler=self.level_finished)

        self.physics_engine.add_collision_handler(
            "player", "water", pre_handler=self.water_colision_handler, separate_handler=self.water_post_colision_handler)
        
        self.music_player = arcade.play_sound(self.theme, looping=True, volume=0.0 if self.muted else 1.0)



    def level_finished(self, _0, _1, _2, _3, _4):
        if self.debug:
            print("Level Finished!")
        return False

    def water_colision_handler(self, player_sprite: PlayerSprite, water_sprite: arcade.Sprite, _2, _3, _4):
        self.on_water = True
        diff = player_sprite.center_y - water_sprite.center_y
        return False

    def water_post_colision_handler(self, _0, _1, _2, _3, _4):
        self.on_water = False

    def cacti_colision_handler(self, player_sprite: PlayerSprite, cacti_sprite: arcade.Sprite, arbiter: pymunk.Arbiter, space, data):
        velocity = self.physics_engine.get_physics_object(
            self.player_sprite).body.velocity
        counterforce = np.array(velocity) * -1
        print(velocity)
        print(counterforce)
        self.physics_engine.set_velocity(
            self.player_sprite, tuple(counterforce))
        return True

    def bottle_colision_handler(self, player_sprite: PlayerSprite, bottle_sprite: arcade.Sprite, arbiter: pymunk.Arbiter, space, data):
        vector = np.zeros((2))
        vector[1] = np.cos(bottle_sprite.radians)
        vector[0] = -np.sin(bottle_sprite.radians)

        self.physics_engine.apply_force(
            player_sprite, tuple(vector * BOTTLE_ACCELERATION))

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
        self.background_camera.move_to((0, target_position[1]*CAMERA_PARALLAX), camera_speed)

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
            case arcade.key.SPACE:
                self.space_pressed = True
            case arcade.key.BACKSPACE:
                self.backspace_pressed = True
            case arcade.key.M:
                if not self.m_pressed:
                    self.m_pressed = True
                    self.muted = not self.muted
                    self.music_player.volume = 0 if self.muted else 1


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
            case arcade.key.SPACE:
                self.space_pressed = False
            case arcade.key.BACKSPACE:
                self.backspace_pressed = False
            case arcade.key.M:
                self.m_pressed = False

    def on_update(self, delta_time):
        self.camera.move((self.player_sprite.center_x-self.width/2,
                         self.player_sprite.center_y-self.height/2))

        impulse, angle = self.controller.pollAxis()

        player_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        self.player_sprite.pymunk.max_horizontal_velocity = PLAYER_MAX_HORIZONTAL_VELOCITY if player_on_ground else PLAYER_MAX_HORIZONTAL_AIR_VELOCITY


        if self.on_water:
            self.delta_v = min(self.delta_v+DELTA_DELTAV, MAX_DELTAV)
            if self.debug: print(self.delta_v)

        if self.debug and self.backspace_pressed:
            self.delta_v = 0

        if self.debug and self.space_pressed:
            impulse = 1

        if impulse != 0:
            vector = np.zeros((2))
            vector[0] = np.cos(angle)
            vector[1] = np.sin(angle) * (not player_on_ground or 
                                         ((angle > 0.2 or angle < -0.2) and (angle > -np.pi-0.2 and angle < np.pi-0.2)))

            if self.debug:
                if self.space_pressed: vector = np.zeros((2))
                if self.w_pressed: vector[1] += 1
                if self.a_pressed: vector[0] -= 1
                if self.s_pressed: vector[1] -= 1
                if self.d_pressed: vector[0] += 1

            vector[0] *= impulse * PLAYER_GROUND_ACCELERATION if player_on_ground else (min(self.delta_v, PLAYER_JETPACK_ACCELERATION) if self.delta_v > 0 else PLAYER_AIR_ACCELERATION)
            vector[1] *= impulse * \
                min(self.delta_v, PLAYER_JETPACK_ACCELERATION)

            sub = min(self.delta_v, np.sum(np.abs(vector)))
            self.delta_v = self.delta_v - \
                (0 if player_on_ground else sub)
            if self.debug:
                print(self.delta_v, vector, sub, angle)

            self.physics_engine.apply_force(self.player_sprite, tuple(vector))

        self.physics_engine.step()

        self.player_sprite.update(angle, impulse, self.delta_v / MAX_DELTAV)

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

        if self.player_sprite.position[0] < self.player_sprite.width/2 or self.player_sprite.position[0] > self.map_bounds_x - self.player_sprite.width/2:
            velocity = np.array(self.physics_engine.get_physics_object(self.player_sprite).body.velocity)
            if self.player_sprite.position[0] < self.player_sprite.width/2:
                velocity[0] = np.abs(velocity[0]*MAP_BOUNDS_BOUNCE*-1)
            else:
                velocity[0] = np.abs(velocity[0]*MAP_BOUNDS_BOUNCE*-1)*-1
            self.physics_engine.set_velocity(self.player_sprite, tuple(velocity))
            if self.debug: print(f"Bounce! {velocity}")

        self.scroll_to_player()

    def on_draw(self):
        self.clear()
        
        self.background_camera.use()
        self.background_sprite.draw()

        self.camera.use()

        self.background_elements.draw()
        self.bottles.draw()
        self.cacti.draw()
        self.water.draw()
        self.background_accents.draw()
        self.wall_elements.draw()
        self.finish_list.draw()
        self.player_sprite.draw()
