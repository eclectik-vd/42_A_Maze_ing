from typing import Any, Dict, List, Tuple
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
import arcade
from PIL import Image
import arcade.gui as gui


class Menu():
    def __init__(self, visualizer) -> None:
        self.visualizer = visualizer
 
        zone_x_start = self.visualizer.width // 30
        self.game_zone = (self.visualizer.width // 2, self.visualizer.height)
 
        cell_w = self.game_zone[0] // self.visualizer.maze_width
        cell_h = self.game_zone[1] // self.visualizer.maze_height
        self.cell = min(cell_w, cell_h)
        self.scale = self.cell / 64
 
        maze_pixel_width = self.visualizer.maze_width * self.cell
        maze_pixel_height = self.visualizer.maze_height * self.cell
 
        self.margin = (
            zone_x_start + (self.game_zone[0] - maze_pixel_width) // 2,
            (self.game_zone[1] - maze_pixel_height) // 2,
        )
 
        self.menu_start_x = zone_x_start * 2 + maze_pixel_width
        self.menu_start_y = self.visualizer.height * 0.55
        self.menu_width = self.visualizer.width - (zone_x_start * 3 + maze_pixel_width)
        self.menu_height = self.visualizer.height - (zone_x_start + self.visualizer.height * 0.55)
 
        self.title = "=== A-Maze-Ing ==="
        self.menu_options: List[str] = [
            "1. re-generate a new maze",
            "2. Show / Hide the shortest path",
            "3. Quit",
        ]
        self.selected_index = 0
 
        self.title_text = arcade.Text(
            self.title, 0, 0, arcade.color.BLACK, font_size=84, anchor_x="center"
        )
        self.option_texts = [
            arcade.Text(option, 0, 0, arcade.color.BLACK, font_size=24, anchor_x="center")
            for option in self.menu_options
        ]
 
        self.setup_ui()


    def setup_ui(self) -> None:
        """Recompute every label's position inside a (new) rectangle.
 
        The title is placed near the top of the rectangle; the
        options are then distributed evenly in the remaining space
        below it. Call this again whenever the menu zone moves or
        is resized (e.g. on a window resize event) to keep the menu
        responsive.
 
        Args:
            left (float): X coordinate of the rectangle's left edge.
            bottom (float): Y coordinate of the rectangle's bottom
                edge.
            width (float): Rectangle width, in pixels.
            height (float): Rectangle height, in pixels.
 
        Returns:
            None
        """
        center_x = self.menu_start_x + self.menu_width / 2
        top = self.menu_start_y + self.menu_height
 
        title_y = top - self.menu_height * 0.08
        self.title_text.x = center_x
        self.title_text.y = title_y - 20
        self.title_text.font_size = max(12, int(self.menu_height * 0.1))
 
        options_top = title_y - self.menu_height * 0.12 - 40
        options_bottom = self.menu_start_y + self.menu_height * 0.08
        available_height = max(options_top - options_bottom, 0)
        step = available_height / max(len(self.option_texts), 1)
 
        for i, text_obj in enumerate(self.option_texts):
            text_obj.x = center_x
            text_obj.y = options_top - i * step
            text_obj.font_size = max(10, int(self.menu_height * 0.06))



    def draw(self):
        arcade.draw_lbwh_rectangle_filled(self.menu_start_x,
                                          self.menu_start_y,
                                          self.menu_width,
                                          self.menu_height,
                                          arcade.color.WHITE)
 
        self.title_text.draw()
        for i, text_obj in enumerate(self.option_texts):
            text_obj.draw()
        self.draw_triangle()

        

    def draw_triangle(self) -> None:
        """Draw the selection marker beside the currently selected option.

        Returns:
            None
        """
        if not (0 <= self.selected_index < len(self.option_texts)):
            return
 
        selected_label = self.option_texts[self.selected_index]
        if selected_label.content_width <= 0:
            return
 
        y = selected_label.y
        x = selected_label.left - 25
        arcade.draw_triangle_filled(
            x, y - 2,
            x, y + 14,
            x + 12, y + 6,
            arcade.color.RED_DEVIL,
        )


    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle keyboard navigation in the pause menu.

        Args:
            symbol: Key code that was pressed.
            modifiers: Keyboard modifiers active during the press.

        Returns:
            None
        """
        if symbol == arcade.key.UP:
            self.selected_index = ((self.selected_index - 1)
                                   % len(self.menu_options))
        elif symbol == arcade.key.DOWN:
            self.selected_index = ((self.selected_index + 1)
                                   % len(self.menu_options))
        elif symbol == arcade.key.SPACE:
            self.execute_action()

    def execute_action(self) -> None:
        """Perform the action associated with the current menu selection.

        Returns:
            None
        """
        selected: str = self.menu_options[self.selected_index]
        if selected == "1. re-generate a new maze":
            pass
        elif selected == "2. Show / Hide the shortest path":
            self.visualizer.have_path = not self.visualizer.have_path
        elif selected == "3. Quit":
            arcade.exit()