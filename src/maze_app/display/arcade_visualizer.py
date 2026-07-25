from src.maze_app.display.visualizer import Visualizer
from src.mazegen import MazeGenerator

import arcade


class ArcadeVisualizer(Visualizer, arcade.View):
    """Arcade-based visualization of the maze with interactive player movement.

    This visualizer extends both the Visualizer base class and arcade.View to
    provide a graphical game-like interface for the maze. It displays the maze
    map, menu, and handles player movement via keyboard input. The player can
    toggle between menu and gameplay modes using the ESCAPE key.

    Attributes:
        map: The Map object responsible for rendering the maze.
        menu: The Menu object for displaying and handling menu interactions.
        player: The Player object representing the character in the maze.
        player_list (arcade.SpriteList): List of sprites to render (player).
        background_texture: Loaded texture image for the game background.
        on_menu (bool): Flag indicating whether the menu is currently active.
    """

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialize the Arcade visualizer with maze and game components.

        Initializes both the arcade.View and Visualizer base classes,
        then creates and configures the Map, Menu, and Player components.
        Loads the background texture and initializes the sprite list for
        rendering. Sets the initial state to display the menu.

        Args:
            maze (MazeGenerator): The maze generator instance containing grid,
                entry, exit, and pathfinding data.
        """
        arcade.View.__init__(self)
        Visualizer.__init__(self, maze)
        from src.maze_app.display.map import Map
        from src.maze_app.display.menu import Menu
        from src.maze_app.display.player import Player
        self.music = arcade.load_sound("src/maze_app/display/sound/music.mp3")
        self.music_player = arcade.play_sound(self.music, volume=0.5)
        self.map: Map = Map(self)
        self.menu: Menu = Menu(self)
        self.player: Player = Player(self)
        self.mazegen: MazeGenerator = maze
        self.player_list: arcade.SpriteList[arcade.Sprite]
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        background_path: str = ("src/maze_app/display"
                                + "/sprite/"
                                + "background.jpeg")
        self.background_texture: arcade.Texture =\
            arcade.load_texture(background_path)
        self.on_menu: bool = True

    def on_draw(self) -> None:
        """Render all visual components of the game.

        Called by the arcade framework each frame. Clears the screen, draws
        the background texture at full window size, then renders the map,
        menu, and player sprite list in order from back to front.

        Returns:
            None: This method performs rendering and has no return value.
        """
        self.clear()
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.LRBT(0, self.window.width, 0, self.window.height)
        )
        self.map.draw()
        self.menu.draw()
        self.player_list.draw()

    def on_update(self, delta_time: float) -> None:
        """Update game logic each frame.

        Called by the arcade framework at each frame interval. Updates the
        player position and animation state based on elapsed time.

        Args:
            delta_time (float): Time elapsed since the last frame update,
                in seconds.

        Returns:
            None: This method updates internal state and has no return value.
        """
        self.player.update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle keyboard input events.

        Called by the arcade framework when a key is pressed. Forwards the
        key press to both the player and menu for handling. Additionally,
        toggles the menu state when ESCAPE is pressed during gameplay
        (i.e., when not already in the menu).

        Args:
            symbol (int): The keyboard symbol/key code pressed.
            modifiers (int): Bitmask of modifier keys held (shift, ctrl, alt).

        Returns:
            None: This method handles input and has no return value.
        """
        self.player.on_key_press(symbol, modifiers)
        self.menu.on_key_press(symbol, modifiers)
        if not self.on_menu and symbol == arcade.key.ESCAPE:
            self.on_menu = not self.on_menu
