import arcade

from sgj2024.gamewindow import GameWindow
from sgj2024.config import *

def main():
    game = GameWindow(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    arcade.run()
