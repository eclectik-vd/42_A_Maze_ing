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
    maze, toggle the path display, rotate wall colours, or quit.

    Attributes:
        ascii_maze (list): Lines of ASCII art representing the maze
            walls, without the path overlay.
        ascii_maze_path (list): Lines of ASCII art representing the
            maze with the shortest path overlaid.
        hide_path (bool): Whether the shortest path is currently
            hidden (True) or shown (False).
        colors (list): Available colorama foreground colors that can
            be cycled through for the maze walls.
        color_i (int): Index of the currently selected color in
            `colors`.
    """

    def __init__(self, maze: MazeGenerator):
        """Initialize the ASCII visualizer.

        Args:
            output_file (str): Path passed to the base Visualizer,
                used for any file output handling.
        """
        super().__init__(maze)
        init(autoreset=True)
        self.ascii_maze: list = []
        self.ascii_maze_path: list = []
        self.colors: list = [Fore.WHITE,
                             Fore.RED,
                             Fore.GREEN,
                             Fore.YELLOW,
                             Fore.BLUE,
                             Fore.CYAN]
        self.color_i = 0

    def draw(self):
        """Clear the terminal and render the maze and menu.

        Builds the ASCII representation of the maze via
        `upper_maze`, optionally overlays the shortest path via
        `show_path` depending on `have_path`, then prints the maze
        character by character (with a small delay for a typewriter
        effect) followed by the interactive menu options.

        Returns:
            None
        """
        os.system('clear')
        self.upper_maze()
        if not self.have_path:
            for line in self.ascii_maze:
                for c in line:
                    print(self.colors[self.color_i] + c, end="", flush=True)
                    time.sleep(0.005)
                print()
        else:
            self.show_path()
            for line in self.ascii_maze_path:
                for c in line:
                    print(self.colors[self.color_i] + c, end="", flush=True)
                    time.sleep(0.005)
                print()

        print()
        menu = ["=== A-Maze-ing ===",
                "1. re-generate a new maze",
                "2. Show / Hide the shortest path",
                "3. Rotate the wall colours",
                "4. Quit\n"]

        for line in menu:
            for c in line:
                print(c, end="", flush=True)
                time.sleep(0.01)
            print()

    def update(self):
        """Draw the maze and menu, then handle the user's menu choice.

        Prompts the user for a choice between 1 and 4:
            1: Regenerate a new maze (not yet implemented).
            2: Toggle showing/hiding the shortest path, then redraw.
            3: Rotate to the next wall color, then redraw.
            4: Exit the program.

        This method calls itself recursively after handling choices
        2 and 3 in order to refresh the display.

        Returns:
            None
        """
        self.draw()
        choice = input("choice (1-5): ")
        if choice == '1':
            os.system('clear')
            line = "Select the seed for the next maze: "
            for c in line:
                    print(c, end="", flush=True)
                    time.sleep(0.005)
            seed = input("")
            self.mazegen.regenerate_perfect_maze(seed)
            self.maze: list = self.mazegen.grid.copy()
            self.path: str = self.mazegen.solve_maze()
            self.update()
        if choice == '2':
            self.have_path = not self.have_path
            self.update()
        if choice == '3':
            if self.color_i < 5:
                self.color_i += 1
            else:
                self.color_i = 0
            self.update()
        if choice == '4':
            sys.exit(0)
        else:
            pass

    def upper_maze(self):
        """Build the wall-only ASCII representation of the maze.

        Populates `self.ascii_maze` with one top border line, then
        for each row of `self.maze` a middle line (side walls and
        cell markers for entry/exit) and a bottom line (south walls).
        Each cell in `self.maze` is expected to be a hexadecimal
        character ("0"-"F") whose bits encode which walls are present
        (north, east, south, west).

        Returns:
            None
        """
        self.ascii_maze = []
        north = [1, 3, 5, 7, 9, 11, 13, 15]
        east = [2, 3, 6, 7, 10, 11, 14, 15]
        south = [4, 5, 6, 7, 12, 13, 14, 15]
        west = [8, 9, 10, 11, 12, 13, 14, 15]

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        for row_index, row in enumerate(self.maze):
            if row_index == 0:
                top_line = "+"
                for cell in row:
                    top_line += ("---" if cell in north else "   ") + "+"
                self.ascii_maze.append(top_line)

            mid_line = ""
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

            bottom_line = "+"
            for cell in row:
                bottom_line += ("---" if cell in south else "   ") + "+"
            self.ascii_maze.append(bottom_line)

    def show_path(self):
        """Overlay the shortest path onto a copy of the ASCII maze.

        Copies `self.ascii_maze` into `self.ascii_maze_path`, then
        walks `self.path` (a string of "N"/"S"/"E"/"W" direction
        letters) starting from `self.entry`, marking each connector
        (the passage between two cells) and each intermediate cell
        center with a "•" symbol. Entry and exit cells are left
        untouched so their "E"/"S" markers remain visible.

        Returns:
            None
        """
        self.ascii_maze_path = self.ascii_maze.copy()

        direction_offsets = {
            "N": (-1, 0),
            "S": (1, 0),
            "E": (0, 1),
            "W": (0, -1),
        }

        current_row, current_col = self.entry

        for direction in self.path:
            row_offset, col_offset = direction_offsets[direction]

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

            entry_x, entry_y = self.entry
            exit_x, exit_y = self.exit

            current_cell = [current_row, current_col]
            exit_cell = [exit_y, exit_x]
            entry_cell = [entry_y, entry_x]
            if current_cell != exit_cell and current_cell != entry_cell:
                cell_line_index = 1 + 2 * current_row
                cell_column_index = 2 + 4 * current_col
                self._draw_path_char(cell_line_index, cell_column_index)

    def _draw_path_char(self, line_index, column_index, symbol="•"):
        """Replace a single character in `self.ascii_maze_path`.

        Since Python strings are immutable, the target line is
        rebuilt with the character at `column_index` replaced by
        `symbol`.

        Args:
            line_index (int): Index of the line in
                `self.ascii_maze_path` to modify.
            column_index (int): Index of the character within that
                line to replace.
            symbol (str): Single character to place at the given
                position. Defaults to "•".

        Returns:
            None
        """
        line = self.ascii_maze_path[line_index]
        self.ascii_maze_path[line_index] = (line[:column_index] +
                                            symbol + line[column_index + 1:])
