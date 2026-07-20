from typing import Tuple, List

from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
import arcade
from PIL import Image


class Map:
    """Manages maze rendering and sprite-based tile display.

    Handles the conversion of the maze grid into arcade sprites, including
    wall tiles, borders, entry/exit markers, and the shortest path overlay.
    Calculates pixel coordinates for each cell and manages texture loading
    and sprite positioning based on the game window size.

    Attributes:
        visualizer (ArcadeVisualizer): Reference to the arcade visualizer.
        tile_list (arcade.SpriteList): Sprite list for maze walls and borders.
        path_list (arcade.SpriteList): Sprite list for path visualization.
        wall_textures (list[arcade.Texture]): Loaded wall tile textures.
        bordure_textures (list[arcade.Texture]): Loaded border textures.
        exit_textures (list[arcade.Texture]): Entry/exit marker textures.
        game_zone (Tuple[int, int]): Pixel dimensions of the playable area.
        cell (int): Width/height of one maze cell in pixels.
        scale (float): Scaling factor for sprites relative to 64x64 base.
        margin (Tuple[int, int]): Pixel offset for maze positioning.
        grid (list[list[Tuple[int, int]]]): Pixel coordinates for each cell.
        path_texture (arcade.Texture): Texture for path marker sprites.
    """

    def __init__(self, visualizer: ArcadeVisualizer) -> None:
        """Initialize the Map with the given visualizer and calculate layout.

        Computes cell size and positioning based on window dimensions,
        initializes sprite lists and texture storage, then generates the
        initial maze sprite layout.

        Args:
            visualizer (ArcadeVisualizer): The arcade visualizer instance
                containing window and maze data.
        """
        self.visualizer: ArcadeVisualizer = visualizer

        self.tile_list: arcade.SpriteList = arcade.SpriteList()
        self.path_list: arcade.SpriteList = arcade.SpriteList()
        self.wall_textures: list[arcade.Texture] = []
        self.bordure_textures: list[arcade.Texture] = []
        self.exit_textures: list[arcade.Texture] = []
        self.first: bool = True

        zone_x_start: int = int(self.visualizer.width) // 32
        zone_y_start: int = int(self.visualizer.height) // 32
        self.game_zone: Tuple[int, int] = (
            int(self.visualizer.width) // 32 * 18 - 2 * zone_x_start,
            int(self.visualizer.height) - 2 * zone_y_start,
        )

        cell_w: int = self.game_zone[0] // self.visualizer.maze_width
        cell_h: int = self.game_zone[1] // self.visualizer.maze_height
        self.cell: int = min(cell_w, cell_h)
        self.scale: float = self.cell / 64

        maze_pixel_width: int = self.visualizer.maze_width * self.cell
        maze_pixel_height: int = self.visualizer.maze_height * self.cell

        self.margin: Tuple[int, int] = (
            int(zone_x_start + (self.game_zone[0] - maze_pixel_width) // 2),
            int(zone_y_start + (self.game_zone[1] - maze_pixel_height) // 2),
        )
        self.grid: list[list[Tuple[int, int]]] = []
        self.path_texture: arcade.Texture

        self.generate_maze()

    def generate_maze(self) -> None:
        """Generate or regenerate the maze sprite layout.

        Recalculates the grid coordinates for all cells, clears existing
        sprites if regenerating, reinitializes the player position, and
        rebuilds all sprite lists from the current maze state.

        Returns:
            None: Modifies sprite lists and grid in place.
        """
        self.calculate_grid()
        if not self.first:
            self.path_list.clear()
            self.tile_list.clear()
            self.visualizer.player.init_player()
        self.build_sprites()
        self.first = False

    def build_sprites(self) -> None:
        """Load textures and build all sprites for the maze display.

        Loads texture sheets from disk, extracts individual tile textures,
        creates sprites for all maze cells (walls, borders, entry/exit),
        and builds the path sprite list based on the shortest path solution.

        Returns:
            None: Populates tile_list and path_list with arcade sprites.
        """
        wall_sheet: Image.Image = Image.open("src/maze_app/display/sprite/e.png")
        bordure_sheet: Image.Image = Image.open("src/maze_app/display/sprite/bordure.png")
        exit_sheet: Image.Image = Image.open("src/maze_app/display/sprite/exit.png")
        path_sheet: Image.Image = Image.open("src/maze_app/display/sprite/path.png")

        for i in range(4):
            for j in range(4):
                region = wall_sheet.crop((j * 64,
                                         i * 64,
                                         j * 64 + 64,
                                         i * 64 + 64))
                wall_texture: arcade.Texture = arcade.Texture(image=region, name=f"tile_{i}")
                self.wall_textures.append(wall_texture)

        for i in range(3):
            for j in range(3):
                region = bordure_sheet.crop((j * 64,
                                            i * 64,
                                            j * 64 + 64,
                                            i * 64 + 64))
                bordure_texture: arcade.Texture = arcade.Texture(image=region,
                                                                  name=f"bordure_{i}")
                self.bordure_textures.append(bordure_texture)

        for i in range(2):
            region = exit_sheet.crop((i * 64, 0, i * 64 + 64, 64))
            exit_texture: arcade.Texture = arcade.Texture(image=region, name=f"tile_{i}")
            self.exit_textures.append(exit_texture)

        self.path_texture = arcade.Texture(image=path_sheet, name="path")

        for y in range(self.visualizer.maze_height + 2):
            for x in range(self.visualizer.maze_width + 2):
                if x == 0 and y == 0:
                    cx: int
                    cy: int
                    cx, cy = self.grid[0][0]
                    cx -= self.cell
                    cy += self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[0],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif (y >= self.visualizer.maze_height + 1 and
                      x >= self.visualizer.maze_width + 1):
                    mh = self.visualizer.maze_height - 1
                    mw = self.visualizer.maze_width - 1
                    cx, cy = self.grid[mh][mw]
                    cx += self.cell
                    cy -= self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[8],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif (y >= self.visualizer.maze_height + 1 and
                      x == 0):
                    cx, cy = self.grid[self.visualizer.maze_height - 1][0]
                    cx -= self.cell
                    cy -= self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[6],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif (x >= self.visualizer.maze_width + 1 and
                      y == 0):
                    cx, cy = self.grid[0][self.visualizer.maze_width - 1]
                    cx += self.cell
                    cy += self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[2],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif x == 0:
                    cx, cy = self.grid[y - 1][0]
                    cx -= self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[3],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif y == 0:
                    cx, cy = self.grid[0][x - 1]
                    cy += self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[1],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif y >= self.visualizer.maze_height + 1:
                    cx, cy = self.grid[self.visualizer.maze_height - 1][x - 1]
                    cy -= self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[7],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                elif x >= self.visualizer.maze_width + 1:
                    cx, cy = self.grid[y - 1][self.visualizer.maze_width - 1]
                    cx += self.cell
                    sprite = arcade.Sprite(
                        self.bordure_textures[5],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                else:
                    cx, cy = self.grid[y-1][x-1]
                    cell_index: int = self.visualizer.maze[y-1][x-1]

                    sprite = arcade.Sprite(
                        self.wall_textures[cell_index],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                sprite.alpha = 230
                self.tile_list.append(sprite)

        ex: int
        ey: int
        ex, ey = self.visualizer.entry
        cx, cy = self.grid[int(ex)][int(ey)]
        sprite = arcade.Sprite(
            self.exit_textures[0],
            scale=self.scale,
            center_x=cx,
            center_y=cy
        )
        sprite.alpha = 230
        self.tile_list.append(sprite)

        ex, ey = self.visualizer.exit
        cx, cy = self.grid[int(ey)][int(ex)]
        sprite = arcade.Sprite(
            self.exit_textures[1],
            scale=self.scale,
            center_x=cx,
            center_y=cy
        )
        sprite.alpha = 230
        self.tile_list.append(sprite)
        self.path()

    def path(self) -> None:
        """Build sprites for visualizing the shortest maze path.

        Walks through the solution path string (containing "N"/"S"/"E"/"W"
        directions), creating a sprite at each cell along the path with
        appropriate rotation based on movement direction. Sprites are added
        to path_list for optional rendering.

        Returns:
            None: Populates path_list with path marker sprites.
        """
        direction_offsets: dict[str, Tuple[int, int]] = {
            "N": (-1, 0),
            "S": (1, 0),
            "E": (0, 1),
            "W": (0, -1),
        }
        x: int
        y: int
        x, y = self.visualizer.entry
        path: str = self.visualizer.path
        for i in range(0, len(path)):
            angle: int
            if path[i] == "N":
                angle = 0
            elif path[i] == "S":
                angle = 180
            elif path[i] == "E":
                angle = 90
            elif path[i] == "W":
                angle = 270
            cx, cy = self.grid[y][x]
            sprite = arcade.Sprite(
                self.path_texture,
                scale=self.scale,
                center_x=cx,
                center_y=cy,
                angle=angle
            )
            sprite.alpha = 180
            self.path_list.append(sprite)
            dy: int
            dx: int
            dy, dx = direction_offsets[path[i]]
            x += dx
            y += dy

    def draw(self) -> None:
        """Draw all maze tiles and optionally the shortest path.

        Renders all wall and border sprites from tile_list, and if the
        visualizer's have_path flag is set, also renders the path_list.

        Returns:
            None: This method performs rendering and has no return value.
        """
        self.tile_list.draw()
        if self.visualizer.have_path:
            self.path_list.draw()

    def calculate_grid(self) -> None:
        """Compute the pixel center coordinates of every maze cell.

        Fills ``grid`` with a 2D list of ``(x, y)`` pixel positions,
        one per maze cell, based on the cell size and margins
        computed in ``__init__``. The grid is cleared and rebuilt
        each time this is called.

        Returns:
            None: Populates self.grid with pixel coordinates.
        """
        x0: int = self.margin[0] + self.cell // 2
        y0: int = int(self.visualizer.height) - self.margin[1] - self.cell // 2

        for y in range(self.visualizer.maze_height):
            self.grid.append([])
            for x in range(self.visualizer.maze_width):
                self.grid[y].append((x0 + x * self.cell, y0 - y * self.cell))
