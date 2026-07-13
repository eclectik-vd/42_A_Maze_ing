from src.maze_app.display.visualizer import Visualizer

import arcade.key as key
import arcade.gui as gui
import arcade


class ArcadeVisualizer(Visualizer, arcade.View):
    def __init__(self, output_file: str):
        arcade.View.__init__(self)
        Visualizer.__init__(self, output_file)
        from src.maze_app.display.map import Map
        from src.maze_app.display.menu import Menu
        self.map = Map(self)
        self.menu = Menu(self)
        self.background_texture = arcade.load_texture("display"
                                                      + "/sprite/"
                                                      + "background.jpeg")

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
        self.menu.on_key_press(symbol, modifiers)