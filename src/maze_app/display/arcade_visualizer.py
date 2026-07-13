from src.maze_app.display.visualizer import Visualizer
from src.mazegen import MazeGenerator

import arcade.key as key
import arcade.gui as gui
import arcade


class ArcadeVisualizer(Visualizer, arcade.View):
    def __init__(self, maze: MazeGenerator):
        arcade.View.__init__(self)
        Visualizer.__init__(self, maze)
        from src.maze_app.display.map import Map
        from src.maze_app.display.menu import Menu
        self.map = Map(self)
        self.menu = Menu(self)
        self.background_texture = arcade.load_texture("src/maze_app/display"
                                                      + "/sprite/"
                                                      + "background.jpeg")
        self.on_menu: bool = True

    def on_draw(self):
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.LRBT(0, self.window.width, 0, self.window.height)
        )
        self.map.draw()
        self.menu.draw()

    def setup_ui(self) -> None:
        pass

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if not self.on_menu and symbol == arcade.key.ESCAPE:
            print("aaa")
            self.on_menu = not self.on_menu
        self.menu.on_key_press(symbol, modifiers)