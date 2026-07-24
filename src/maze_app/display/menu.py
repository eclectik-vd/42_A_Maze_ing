from typing import List, Tuple
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
import arcade
from random import randint


class Menu:
    """Menu interface for maze game navigation and settings.

    Displays a menu with options to regenerate the maze, toggle the
    shortest path display, start playing, or quit. Handles keyboard
    navigation (up/down arrows) and selection (spacebar). Updates menu
    UI positioning when the game window is resized.

    Attributes:
        visualizer (ArcadeVisualizer): Reference to the arcade visualizer.
        menu_start_x (int): Left edge X coordinate of menu box.
        menu_start_y (int): Bottom edge Y coordinate of menu box.
        menu_zone (Tuple[int, int]): Available menu area dimensions.
        menu_width (int): Menu box width in pixels.
        menu_height (int): Menu box height in pixels.
        title (str): Menu title text.
        menu_options (List[str]): List of selectable menu options.
        selected_index (int): Currently highlighted option index.
        title_text (arcade.Text): Rendered title text object.
        option_texts (List[arcade.Text]): Rendered menu option text objects.
    """

    def __init__(self, visualizer: ArcadeVisualizer) -> None:
        """Initialize the menu with options and text rendering.

        Creates arcade.Text objects for the title and each menu option,
        calculates menu positioning and dimensions based on window size,
        and sets up the initial UI layout.

        Args:
            visualizer (ArcadeVisualizer): The arcade visualizer instance.
        """
        self.visualizer: ArcadeVisualizer = visualizer

        self.menu_start_x: float = self.visualizer.width // 32 * 19
        self.menu_start_y: float = self.visualizer.height // 18 * 11
        self.menu_zone: Tuple[float, float] = (
            self.visualizer.width // 32 * 18 - 2 * self.menu_start_x,
            self.visualizer.height - 2 * self.menu_start_y,
        )

        self.menu_width: float = self.visualizer.width // 32 * 12
        self.menu_height: float = self.visualizer.height // 18 * 6

        self.title: str = "=== A-Maze-Ing ==="
        self.menu_options: List[str] = [
            "1. re-generate a new maze",
            "2. Show / Hide the shortest path",
            "3. Play",
            "4. Quit",
        ]
        self.selected_index: int = 0

        self.title_text: arcade.Text = arcade.Text(
            self.title,
            0,
            0,
            arcade.color.BLACK,
            font_size=84,
            anchor_x="center"
        )
        self.option_texts: List[arcade.Text] = [
            arcade.Text(
                option,
                0,
                0,
                arcade.color.BLACK,
                font_size=24,
                anchor_x="center"
            )
            for option in self.menu_options
        ]

        self.setup_ui()

    def setup_ui(self) -> None:
        """Reposition menu labels based on current menu dimensions.

        The title is placed near the top of the menu box; the options
        are distributed evenly in the remaining space below. Call this
        whenever the menu zone is resized to keep the menu responsive.

        Returns:
            None: Modifies position and font_size of text objects in place.
        """
        center_x: float = self.menu_start_x + self.menu_width / 2
        top: float = self.menu_start_y + self.menu_height

        title_y: float = top - self.menu_height * 0.08
        self.title_text.x = center_x
        self.title_text.y = title_y - 20
        self.title_text.font_size = max(12, int(self.menu_height * 0.1))

        options_top: float = title_y - self.menu_height * 0.12 - 40
        options_bottom: float = self.menu_start_y + self.menu_height * 0.08
        available_height: float = max(options_top - options_bottom, 0)
        step: float = available_height / max(len(self.option_texts), 1)

        for i, text_obj in enumerate(self.option_texts):
            text_obj.x = center_x
            text_obj.y = options_top - i * step
            text_obj.font_size = max(10, int(self.menu_height * 0.06))

    def draw(self) -> None:
        """Render the menu box, title, options, and selection marker.

        Draws a white rectangular background for the menu, renders the
        title and option text, and displays the selection indicator
        triangle (red if in menu, green if in gameplay).

        Returns:
            None: This method performs rendering and has no return value.
        """
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

        Displays a red triangle when in menu mode or a green triangle
        when in gameplay mode to indicate the currently selected option.

        Returns:
            None: This method performs rendering and has no return value.
        """
        if not (0 <= self.selected_index < len(self.option_texts)):
            return

        selected_label: arcade.Text = self.option_texts[self.selected_index]
        if selected_label.content_width <= 0:
            return

        y: float = selected_label.y
        x: float = selected_label.left - 25
        if self.visualizer.on_menu:
            arcade.draw_triangle_filled(
                x, y - 2,
                x, y + 14,
                x + 12, y + 6,
                arcade.color.RED,
            )
        else:
            arcade.draw_triangle_filled(
                x, y - 2,
                x, y + 14,
                x + 12, y + 6,
                arcade.color.GREEN,
            )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle keyboard navigation in the menu.

        When the menu is active, allows UP/DOWN arrow keys to cycle through
        options and SPACE to select the current option. Modifies selected_index
        and calls execute_action() when SPACE is pressed.

        Args:
            symbol (int): The arcade key code that was pressed.
            modifiers (int): Bitmask of active modifier keys.

        Returns:
            None: Updates selected_index or executes menu action.
        """
        if self.visualizer.on_menu:
            if symbol == arcade.key.UP:
                self.selected_index = ((self.selected_index - 1)
                                       % len(self.menu_options))
            elif symbol == arcade.key.DOWN:
                self.selected_index = ((self.selected_index + 1)
                                       % len(self.menu_options))
            elif symbol == arcade.key.SPACE:
                self.execute_action()

    def execute_action(self) -> None:
        """Execute the action for the currently selected menu option.

        Handles the four menu choices: regenerate maze, toggle path display,
        start playing, or quit the application.

        Returns:
            None: Modifies visualizer state or calls arcade.exit().
        """
        selected: str = self.menu_options[self.selected_index]
        if selected == "1. re-generate a new maze":
            self.visualizer.mazegen.regenerate(randint(0, 10000))
            self.visualizer.maze = self.visualizer.mazegen.grid.copy()
            self.visualizer.path = self.visualizer.mazegen.exit_path
            self.visualizer.map.generate_maze()
        elif selected == "2. Show / Hide the shortest path":
            self.visualizer.have_path = not self.visualizer.have_path
        elif selected == "3. Play":
            self.visualizer.on_menu = False
        elif selected == "4. Quit":
            arcade.exit()
