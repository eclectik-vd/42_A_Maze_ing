from src.maze_app.display.visualizer import Visualizer
from src.mazegen import MazeGenerator

import time
import os
import sys
from colorama import Fore, init


class AsciiVisualizer(Visualizer):
    """Render a maze as colored ASCII art in the terminal.

    This visualizer draws the maze grid using box-drawing characters,
    optionally overlays the shortest path with a marker symbol, and
    displays an interactive menu allowing the user to regenerate the
    maze, toggle the path display, rotate wall colors, or quit.

    Attributes:
        ascii_maze (list[str]): Lines of ASCII art representing the maze
            walls, without the path overlay. Each line is a string of
            characters representing the maze structure.
        ascii_maze_path (list[str]): Lines of ASCII art representing the
            maze with the shortest path overlaid with "•" markers.
        colors (list[str]): Available colorama foreground color codes
            that can be cycled through for the maze walls.
        color_i (int): Index of the currently selected color in
            the `colors` list.
    """

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialize the ASCII visualizer.

        Initializes the parent Visualizer class with the given maze generator,
        sets up colorama for colored terminal output, and initializes the ASCII
        maze representations and color cycling properties.

        Args:
            maze (MazeGenerator): The maze generator instance containing grid,
                entry, exit, and pathfinding data.
        """
        super().__init__(maze)
        init(autoreset=True)
        self.ascii_maze: list[str] = []
        self.ascii_maze_path: list[str] = []
        self.colors: list[str] = [Fore.WHITE,
                                  Fore.RED,
                                  Fore.GREEN,
                                  Fore.BLUE,
                                  Fore.CYAN]
        self.color_i: int = 0
        self.is_first: bool = True

    def draw(self) -> None:
        """Clear the terminal and render the maze and menu.

        Clears the terminal, builds the ASCII representation of the maze
        via `upper_maze()`, optionally overlays the shortest path via
        `show_path()` depending on `self.have_path`, then prints the maze
        character by character (with a small delay for a typewriter effect)
        followed by the interactive menu options. Wall characters are colored
        based on the current color index, while entry/exit and path markers
        use fixed colors.

        Returns:
            None: This method performs terminal I/O and has no return value.
        """
        self.upper_maze()
        if not self.have_path:
            for line in self.ascii_maze:
                for c in line:
                    if c == "E":
                        print(Fore.GREEN + c, end="", flush=True)
                    elif c == "S":
                        print(Fore.RED + c, end="", flush=True)
                    elif c == "❀":
                        print(Fore.BLUE + c, end="", flush=True)
                    elif c == "•":
                        print(Fore.YELLOW + c, end="", flush=True)
                    else:
                        print(self.colors[self.color_i] + c,
                              end="", flush=True)
                    time.sleep(0.005)
                print()
        else:
            self.show_path()
            for line in self.ascii_maze_path:
                for c in line:
                    if c == "E":
                        print(Fore.GREEN + c, end="", flush=True)
                    elif c == "S":
                        print(Fore.RED + c, end="", flush=True)
                    elif c == "❀":
                        print(Fore.BLUE + c, end="", flush=True)
                    elif c == "•":
                        print(Fore.YELLOW + c, end="", flush=True)
                    else:
                        print(self.colors[self.color_i] + c,
                              end="", flush=True)
                    time.sleep(0.005)
                print()

        print()

        menu: list[str] = ["=== A-Maze-ing ===",
                           "1. re-generate a new maze",
                           "2. Show / Hide the shortest path",
                           "3. Rotate the wall colours",
                           "4. Quit\n"]

        for line in menu:
            for c in line:
                print(c, end="", flush=True)
                time.sleep(0.01)
            print()

    def update(self) -> None:
        """Draw the maze and menu, then handle the user's menu choice.

        Calls `draw()` to display the current maze and menu, then prompts
        the user for a choice (1-4):

        - Choice 1: Regenerate a new maze with a user-provided seed
        - Choice 2: Toggle showing/hiding the shortest path
        - Choice 3: Rotate to the next wall color
        - Choice 4: Exit the program

        After handling choices 2 and 3, this method calls itself recursively
        to refresh the display. Choice 1 regenerates the maze and then
        recurses. Choice 4 calls sys.exit(0).

        Returns:
            None: This method either recurses or exits the program.
        """
        if not self.is_first:
            os.system('clear')
        else:
            self.is_first = False

        self.draw()
        choice: str = input("choice (1-4): ")
        if choice == '1':
            os.system('clear')
            line: str = "Select the seed for the next maze: "
            for c in line:
                print(c, end="", flush=True)
                time.sleep(0.005)

            try:
                new_seed: int = int(input(""))
            except ValueError:
                raise ValueError("Error: The seed must be an int !!!!!!!!!!")
            self.mazegen.regenerate(new_seed)

            self.maze: list[list[int]] = self.mazegen.grid.copy()
            self.path: str = self.mazegen.solve_maze()
            self.update()
        if choice == '2':
            self.have_path = not self.have_path
            self.update()
        if choice == '3':
            if self.color_i < len(self.colors) - 1:
                self.color_i += 1
            else:
                self.color_i = 0
            self.update()
        if choice == '4':
            sys.exit(0)
        else:
            pass

    def upper_maze(self) -> None:
        """Build the wall-only ASCII representation of the maze.

        Populates `self.ascii_maze` with ASCII art representation of the
        maze grid using box-drawing characters. For each row of `self.maze`,
        generates one top border line, one middle line (side walls and
        cell markers for entry/exit), and one bottom line (south walls).

        Each cell in `self.maze` is expected to be a hexadecimal digit
        ("0"-"F") where the bits encode which walls are present:
        - Bit 0 (value 1, 3, 5, 7, ...): North wall
        - Bit 1 (value 2, 3, 6, 7, ...): East wall
        - Bit 2 (value 4, 5, 6, 7, ...): South wall
        - Bit 3 (value 8, 9, 10, 11, ...): West wall

        The entry cell is marked with "E" and the exit cell with "S".
        Cells with all walls open (value 15) are marked with "❀".

        Returns:
            None: Modifies `self.ascii_maze` in place.
        """
        self.ascii_maze = []
        north: list[int] = [1, 3, 5, 7, 9, 11, 13, 15]
        east: list[int] = [2, 3, 6, 7, 10, 11, 14, 15]
        south: list[int] = [4, 5, 6, 7, 12, 13, 14, 15]
        west: list[int] = [8, 9, 10, 11, 12, 13, 14, 15]

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        for row_index, row in enumerate(self.maze):
            if row_index == 0:
                top_line: str = "+"
                for cell in row:
                    top_line += ("---" if cell in north else "   ") + "+"
                self.ascii_maze.append(top_line)

            mid_line: str = ""
            for i, cell in enumerate(row):
                if i == 0:
                    mid_line += "|" if cell in west else " "
                # print(self.exit)
                # print([row_index, i])
                if entry_x == i and entry_y == row_index:
                    mid_line += " E "
                elif exit_x == i and exit_y == row_index:
                    mid_line += " S "
                elif cell == 15:
                    mid_line += " ❀ "
                else:
                    mid_line += "   "
                mid_line += "|" if cell in east else " "
            self.ascii_maze.append(mid_line)

            bottom_line: str = "+"
            for cell in row:
                bottom_line += ("---" if cell in south else "   ") + "+"
            self.ascii_maze.append(bottom_line)

    def show_path(self) -> None:
        """Overlay the shortest path onto a copy of the ASCII maze.

        Creates a copy of `self.ascii_maze` into `self.ascii_maze_path`,
        then walks through `self.path` (a string of direction letters:
        "N"/"S"/"E"/"W") starting from `self.entry`. For each direction,
        marks the connector (passage between two cells) with a "•" symbol
        and, except at the entry and exit cells, marks the intermediate
        cell center with a "•" as well.

        The path is traced by calculating ASCII grid positions based on
        the cell coordinates and direction. Entry ("E") and exit ("S")
        markers are left untouched to remain visible.

        Returns:
            None: Modifies `self.ascii_maze_path` in place.
        """
        self.ascii_maze_path = self.ascii_maze.copy()

        direction_offsets: dict[str, tuple[int, int]] = {
            "N": (-1, 0),
            "S": (1, 0),
            "E": (0, 1),
            "W": (0, -1),
        }

        current_row: int
        current_col: int
        current_col, current_row = self.entry

        for direction in self.path:
            row_offset: int
            col_offset: int
            row_offset, col_offset = direction_offsets[direction]

            line_index: int
            column_index: int
            if row_offset == 0:
                line_index = 1 + 2 * current_row
                if col_offset == 1:
                    column_index = 4 * (current_col + 1)
                else:
                    column_index = 4 * current_col
            else:
                if row_offset == 1:
                    line_index = 2 * (current_row + 1)
                else:
                    line_index = 2 * current_row
                column_index = 2 + 4 * current_col

            self._draw_path_char(line_index, column_index)

            current_row += row_offset
            current_col += col_offset

            entry_x: int
            entry_y: int
            exit_x: int
            exit_y: int
            entry_x, entry_y = self.entry
            exit_x, exit_y = self.exit

            current_cell: list[int] = [current_row, current_col]
            exit_cell: list[int] = [exit_y, exit_x]
            entry_cell: list[int] = [entry_y, entry_x]
            if current_cell != exit_cell and current_cell != entry_cell:
                cell_line_index: int = 1 + 2 * current_row
                cell_column_index: int = 2 + 4 * current_col
                self._draw_path_char(cell_line_index, cell_column_index)

    def _draw_path_char(self,
                        line_index: int,
                        column_index: int,
                        symbol: str = "•") -> None:
        """Replace a single character in `self.ascii_maze_path`.

        Modifies the ASCII maze path representation by replacing the
        character at the specified position with the given symbol.
        Since Python strings are immutable, the target line is rebuilt
        with the character at `column_index` replaced by `symbol`.

        Args:
            line_index (int): Index of the line in `self.ascii_maze_path`
                to modify (0-indexed).
            column_index (int): Index of the character within that line
                to replace (0-indexed).
            symbol (str, optional): Single character to place at the given
                position. Defaults to "•" (bullet point).

        Returns:
            None: Modifies `self.ascii_maze_path` in place.
        """
        line = self.ascii_maze_path[line_index]
        self.ascii_maze_path[line_index] = (line[:column_index] +
                                            symbol + line[column_index + 1:])
