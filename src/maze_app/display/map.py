from typing import Any, Dict, List, Tuple
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
import arcade
from PIL import Image


class Map:
    def __init__(self, visualizer) -> None:
        self.visualizer = visualizer

        self.tile_list: arcade.SpriteList = arcade.SpriteList()
        self.path_list: arcade.SpriteList = arcade.SpriteList()
        self.wall_textures = []
        self.bordure_textures = []
        self.exit_textures = []

        zone_x_start: int = self.visualizer.width // 30
        self.game_zone: Tuple[int, int] = (
            self.visualizer.width // 2,
            self.visualizer.height,
        )
 
        cell_w: int = self.game_zone[0] // self.visualizer.maze_width
        cell_h: int = self.game_zone[1] // self.visualizer.maze_height
        self.cell: int = min(cell_w, cell_h)
        self.scale: float = self.cell / 64
 
        maze_pixel_width: int = self.visualizer.maze_width * self.cell
        maze_pixel_height: int = self.visualizer.maze_height * self.cell
 
        self.margin: Tuple[int, int] = (
            zone_x_start + (self.game_zone[0] - maze_pixel_width) // 2,
            (self.game_zone[1] - maze_pixel_height) // 2,
        )
 
        self.grid = []
 
        self.generate_maze()


    def generate_maze(self) -> None:
        self.calculate_grid()
        self.build_sprites()

    def build_sprites(self) -> None:
        wall_sheet = Image.open("display/sprite/e.png")
        bordure_sheet = Image.open("display/sprite/bordure.png")
        exit_sheet = Image.open("display/sprite/exit.png")
        path_sheet = Image.open("display/sprite/path.png")

        for i in range(4):
            for j in range(4):
                region = wall_sheet.crop((j * 64, i * 64, j * 64 + 64, i * 64 + 64))
                wall_texture = arcade.Texture(image=region, name=f"tile_{i}")
                self.wall_textures.append(wall_texture)
                
        for i in range(3):
            for j in range(3):
                region = bordure_sheet.crop((j * 64, i * 64, j * 64 + 64, i * 64 + 64))
                bordure_texture = arcade.Texture(image=region, name=f"bordure_{i}")
                self.bordure_textures.append(bordure_texture)

        for i in range(2):
            region = exit_sheet.crop((i * 64, 0, i * 64 + 64, 64))
            exit_texture = arcade.Texture(image=region, name=f"tile_{i}")
            self.exit_textures.append(exit_texture)

        self.path_texture = arcade.Texture(image=path_sheet, name=f"path")

        for y in range(self.visualizer.maze_height + 2):
            for x in range(self.visualizer.maze_width + 2):
                if x == 0 and y == 0:
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
                    cx, cy = self.grid[self.visualizer.maze_height - 1][self.visualizer.maze_width - 1]
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
                    cell_index = int(self.visualizer.maze[y-1][x-1], 16)

                    sprite = arcade.Sprite(
                        self.wall_textures[cell_index],
                        scale=self.scale,
                        center_x=cx,
                        center_y=cy
                    )
                sprite.alpha = 230
                self.tile_list.append(sprite)

        cx, cy = self.grid[int(self.visualizer.entry[0])][int(self.visualizer.entry[1])]
        sprite = arcade.Sprite(
            self.exit_textures[0],
            scale=self.scale,
            center_x=cx,
            center_y=cy
        )
        sprite.alpha = 230
        self.tile_list.append(sprite)

        cx, cy = self.grid[int(self.visualizer.exit[0])][int(self.visualizer.exit[1])]
        sprite = arcade.Sprite(
            self.exit_textures[1],
            scale=self.scale,
            center_x=cx,
            center_y=cy
        )
        sprite.alpha = 230
        self.tile_list.append(sprite)
        self.path()


    def path(self):
        direction_offsets = {
            "N": (-1, 0),
            "S": (1, 0),
            "E": (0, 1),
            "W": (0, -1),
        }
        ey, ex = self.visualizer.exit
        x = self.visualizer.entry[1]
        y = self.visualizer.entry[0]
        for dir in self.visualizer.path:
            dy, dx = direction_offsets[dir]
       
            # print(x, y , "->", dir)
            x += dx
            y += dy
            # print(x, y)
            if x == ex and y == ey:
                break
            cx, cy = self.grid[y][x]
            sprite = arcade.Sprite(
                self.path_texture,
                scale=self.scale,
                center_x=cx,
                center_y=cy
            )
            sprite.alpha = 230
            self.path_list.append(sprite)
        

        

    def draw(self) -> None:
        """Draw the maze tiles, pac-gums, and super pac-gums.

        Returns:
            None
        """
        self.tile_list.draw()
        if self.visualizer.have_path:
            self.path_list.draw()

    def calculate_grid(self) -> None:
        """Compute the pixel center coordinates of every maze cell.

        Fills ``grid`` with a 2D list of ``(x, y)`` pixel positions,
        one per maze cell, based on the cell size and margins
        computed in ``__init__``.

        Returns:
            None
        """
        x0 = self.margin[0] + self.cell // 2
        y0 = self.visualizer.height - self.margin[1] - self.cell // 2

        for y in range(self.visualizer.maze_height):
            self.grid.append([])
            for x in range(self.visualizer.maze_width):
                self.grid[y].append((x0 + x * self.cell, y0 - y * self.cell))