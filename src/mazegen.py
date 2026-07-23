"""
Maze Generator Module
=====================

This standalone module generates and solves perfect or imperfect mazes.
It is designed to be independent of any user interface.

Example of use:
-----------------------
    from mazegen import MazeGenerator

    # 1. Instantiation
    maze = MazeGenerator(
        width=10, height=10,
        entry_coord=(0, 0), exit_coord=(9, 9),
        seed=42
        perfect=True,
        output_file=`maze.txt`
    )

    # 2. Initiate, create, validate, solve and export the maze
    maze.generate()

    # 3. Retrieving data for display
    # Returns a copy (to prevent accidental modifications) of the grid
    grid = maze.grid
    # Returns the path from entry to exit
    solution = exit_path

"""


import random
import warnings
from collections import deque
from copy import deepcopy


class MazeGenError(Exception):
    """Exception raised when maze generation fails or violates a rule."""
    pass


class MazeGenerator:
    """Maze generator based on the Recursive Backtracker algorithm."""

    # Wall constants (binary representation)
    # to store 4 states (North, East, South, West) in a single integer
    N: int = 1  # Binaire : 0001
    E: int = 2  # Binaire : 0010
    S: int = 4  # Binaire : 0100
    W: int = 8  # Binaire : 1000
    # combine walls bits using `|` (OR operator)
    ALL_WALLS: int = N | E | S | W

    # Relative coordinates of "42" pattern
    PATTERN_42: tuple[tuple[int, int], ...] = (
        (0, 0), (0, 1), (0, 2), (1, 2), (2, 1), (2, 2), (2, 3), (2, 4),
        (5, 0), (6, 0), (7, 0), (7, 1), (5, 2), (6, 2), (7, 2), (5, 3),
        (5, 4), (6, 4), (7, 4)
    )
    PATTERN_WIDTH: int = 8
    PATTERN_HEIGHT: int = 5

    # ---------------------------------------------------------------------
    #
    # --------------------- INSTANTIATE a labyrinth object ----------------
    #
    # ---------------------------------------------------------------------

    def __init__(
            self, width: int, height: int, entry_coord: tuple[int, int],
            exit_coord: tuple[int, int], perfect: bool, output_file: str,
            seed: int | None = None
    ) -> None:
        """Initialize the maze generator and validate its parameters.

        Args:
            width: Number of columns in the grid.
            height: Number of rows in the grid.
            entry_coord: (x, y) coordinates of the maze entrance.
            exit_coord: (x, y) coordinates of the maze exit.
            perfect: If True, generate a perfect maze (no loops, no
                isolated areas); if False, allow imperfections.
            output_file: Name of the file to which maze data will be exported.
            seed: Optional seed for the random number generator.

        Raises:
            ValueError: If width or height is smaller than 3.
        """

        # generator’s internal rules, for the exported module
        if width < 2 or height < 2:
            raise ValueError("The maze size must not be less than 3x3.")
        if not (0 <= entry_coord[0] < width and 0 <= entry_coord[1] < height):
            raise ValueError("entry_coord must be inside the grid boundaries.")
        if not (0 <= exit_coord[0] < width and 0 <= exit_coord[1] < height):
            raise ValueError("exit_coord must be inside the grid boundaries.")
        if entry_coord == exit_coord:
            raise ValueError("entry_coord and exit_coord must be different.")

        self.width = width
        self.height = height
        self.entry_coord = entry_coord
        self.exit_coord = exit_coord
        self.perfect = perfect
        self.output_file = output_file
        self._rng = random.Random(seed)

        self._grid: list[list[int]] = [[self.ALL_WALLS for _ in range(width)]
                                       for _ in range(height)]
        self.pattern_cells: set[tuple[int, int]] = set()
        self._exit_path: str = ""
        self._is_generated = False

    # ---------------------------------------------------------------------
    #
    # --------------------- READ-ONLY properties --------------------------
    #
    # ---------------------------------------------------------------------

    @property
    def grid(self) -> list[list[int]]:
        """Return a deep copy of the grid.

        The `grid` property is read-only: encapsulation prevents
        calling code from corrupting internal state.
        """
        return deepcopy(self._grid)

    @property
    def exit_path(self) -> str:
        """Read-only access to the path between entry and exit.

        The `exit_path` property is read-only: encapsulation prevents
        calling code from corrupting internal state.
        """
        return self._exit_path

    # ---------------------------------------------------------------------
    #
    # --------------------- methods for INTERNAL use ----------------------
    #
    # ---------------------------------------------------------------------

    def _apply_42_pattern(self) -> None:
        """Try to set the '42' pattern in the center of the grid.

        Locks the pattern cells so they are not used by the maze
        generation algorithm. The pattern is NOT applied :
            if the grid is too small, or
            if it collides with the entry or exit cell.
        """

        if (self.width < self.PATTERN_WIDTH + 2
                or self.height < self.PATTERN_HEIGHT + 2):
            warnings.warn("This maze is too small to display the '42' pattern")
            return

        pattern_x = (self.width - self.PATTERN_WIDTH) // 2
        pattern_y = (self.height - self.PATTERN_HEIGHT) // 2

        grid_pattern_cells = {
            (pattern_x + dx, pattern_y + dy) for dx, dy in self.PATTERN_42
        }

        if (self.entry_coord in grid_pattern_cells
                or self.exit_coord in grid_pattern_cells):
            warnings.warn("'42' pattern overlaps the entrance or exit. "
                          "It will be ignored.")
            return

        self.pattern_cells = grid_pattern_cells

    def _get_unvisited_adjacents(
            self, x: int, y: int) -> list[tuple[int, int, int]]:
        """Look around cell (x, y).

        Returns:
            The list of unvisited and valid adjacent cells.
            Each adjacent is returned as a tuple:
            (adj_x, adj_y, direction_to_go).
        """

        adjacents: list[tuple[int, int, int]] = []

        # to the north
        if (
            y > 0
            and self._grid[y - 1][x] == self.ALL_WALLS
            and (x, y - 1) not in self.pattern_cells
        ):
            adjacents.append((x, y - 1, self.N))

        # to the east
        if (
            x < self.width - 1
            and self._grid[y][x + 1] == self.ALL_WALLS
            and (x + 1, y) not in self.pattern_cells
        ):
            adjacents.append((x + 1, y, self.E))

        # to the south
        if (
            y < self.height - 1
            and self._grid[y + 1][x] == self.ALL_WALLS
            and (x, y + 1) not in self.pattern_cells
        ):
            adjacents.append((x, y + 1, self.S))

        # to the west
        if (
            x > 0
            and self._grid[y][x - 1] == self.ALL_WALLS
            and (x - 1, y) not in self.pattern_cells
        ):
            adjacents.append((x - 1, y, self.W))

        return adjacents

    def _break_wall(self, x: int, y: int, direction: int) -> None:
        """Break the wall of cell (x, y) in the given direction.

        Also breaks the opposite wall of the adjacent cell, so both
        sides stay consistent.
        """

        # North wall
        if direction == self.N and y > 0:
            self._grid[y][x] &= ~self.N
            self._grid[y - 1][x] &= ~self.S

        # East wall
        elif direction == self.E and x < self.width - 1:
            self._grid[y][x] &= ~self.E
            self._grid[y][x + 1] &= ~self.W

        # South wall
        elif direction == self.S and y < self.height - 1:
            self._grid[y][x] &= ~self.S
            self._grid[y + 1][x] &= ~self.N

        # West wall
        elif direction == self.W and x > 0:
            self._grid[y][x] &= ~self.W
            self._grid[y][x - 1] &= ~self.E

    # ---------------------------------------------------------------------
    #
    # ----------------------- maze (re)GENERATION -------------------------
    #
    # ---------------------------------------------------------------------

    def generate_perfect_maze(self) -> None:
        """Generate a perfect maze using Recursive Backtracker.

        The maze is generated starting from `self.entry_coord`.
        """

        self._apply_42_pattern()

        start_x, start_y = self.entry_coord

        stack: list[tuple[int, int]] = [(start_x, start_y)]

        while stack:
            current_x, current_y = stack[-1]
            adjacents = self._get_unvisited_adjacents(current_x, current_y)

            if adjacents:
                next_x, next_y, direction = self._rng.choice(adjacents)
                self._break_wall(current_x, current_y, direction)
                stack.append((next_x, next_y))

            else:
                stack.pop()

        self._is_generated = True

    def make_imperfect(self, percent_to_break: float = 0.4) -> None:
        """Make the maze imperfect by breaking random dead-end walls.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """

        if not self._is_generated:
            raise RuntimeError("NOT possible to make imperfect"
                               "a non-generated maze.")

        corridor_ends = [
            self.ALL_WALLS & ~self.N,  # (1110)
            self.ALL_WALLS & ~self.E,  # (1101)
            self.ALL_WALLS & ~self.S,  # (1011)
            self.ALL_WALLS & ~self.W   # (0111)
        ]

        dead_ends: list[tuple[int, int]] = [
            (x, y) for y in range(self.height) for x in range(self.width)
            if self._grid[y][x] in corridor_ends
            and (x, y) not in self.pattern_cells
        ]

        nb_walls_to_break = len(dead_ends)

        for x, y in dead_ends[:nb_walls_to_break]:
            cell = self._grid[y][x]
            may_be_broken = []

            # check north wall
            if (
                (cell & self.N)
                and y > 0
                and (x, y - 1) not in self.pattern_cells
            ):
                may_be_broken.append(self.N)

            # check east wall
            if (
                (cell & self.E)
                and x < self.width - 1
                and (x + 1, y) not in self.pattern_cells
            ):
                may_be_broken.append(self.E)

            # check south wall
            if (
                (cell & self.S)
                and y < self.height - 1
                and (x, y + 1) not in self.pattern_cells
            ):
                may_be_broken.append(self.S)

            # check west wall
            if (
                (cell & self.W)
                and x > 0
                and (x - 1, y) not in self.pattern_cells
            ):
                may_be_broken.append(self.W)

            # if there are breakable walls, break one randomly choosen
            if may_be_broken:
                self._break_wall(x, y, self._rng.choice(may_be_broken))

    def reset(self) -> None:
        """Clear the internal state of the maze in memory."""
        self._grid = [[self.ALL_WALLS for _ in range(self.width)]
                      for _ in range(self.height)]
        self.pattern_cells.clear()
        self._exit_path = ""
        self._is_generated = False

    def regenerate(self, new_seed: int | None = None) -> None:
        """ Reset and regenerate the maze with a new seed if provided. """
        if new_seed is not None:
            self._rng = random.Random(new_seed)

        self.reset()
        self.generate()

    # ---------------------------------------------------------------------
    #
    # ----------------------- CHECK maze VALIDITY -------------------------
    #
    # ---------------------------------------------------------------------

    def check_walls_integrity(self) -> bool:
        """Check that all walls are consistent between adjacent cells.

        Returns:
            True if the grid is valid.

        Raises:
            MazeGenError: If an inconsistency is found between two
                adjacent cells.
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                # check East|West, ie with right adjacent
                if x < self.width - 1:
                    adjacent_E = self.grid[y][x + 1]

                    if bool(cell & self.E) != bool(adjacent_E & self.W):
                        raise MazeGenError("East–West inconsistency "
                                           f"between ({x},{y}) "
                                           "and ({x+1},{y})")

                # check Sud|North, ie with bottom adjacent
                if y < self.height - 1:
                    adjacent_S = self.grid[y + 1][x]

                    if bool(cell & self.S) != bool(adjacent_S & self.N):
                        raise MazeGenError("South–North inconsistency "
                                           f"between ({x},{y}) "
                                           "and ({x},{y+1})")

        return True

    def is_3x3_open(self, start_x: int, start_y: int) -> bool:
        """Check if a 3x3 area is open (has no internal walls).

        The area's top-left cell is at (start_x, start_y).
        """

        found_wall = any(
            # Inspection of horizontal (south)
            (self.grid[y][x] & self.S)
            for y in range(start_y, start_y + 2)
            for x in range(start_x, start_x + 3)

        ) or any(
            # Inspection of vertical (east) walls
            (self.grid[y][x] & self.E)
            for y in range(start_y, start_y + 3)
            for x in range(start_x, start_x + 2)
        )

        return not found_wall

    def free_of_open_areas(self) -> bool:
        """Check that there is no open area of 3x3 cells or larger.

        Returns:
            True if the maze is valid.

        Raises:
            MazeGenError: If a 3x3 open area is found.
        """
        if self.width < 3 or self.height < 3:
            return True

        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if self.is_3x3_open(x, y):
                    raise MazeGenError(f"open area detected at ({x},{y})")

        return True

    # ---------------------------------------------------------------------
    #
    # --------------------------- SOLVE maze  -----------------------------
    #
    # ---------------------------------------------------------------------

    def solve_maze(self) -> str:
        """Use BFS to find the shortest path between entrance and exit.

        Starting from the entry cell, explores the grid using:
        - already_met: a set storing the coordinates of explored cells.
        - to_explore: a queue, storing cells to check adjacents and
                               for each cell the path taken from the entry.

        Returns:
            A string containing directions (N, E, S, W) step-by-step
            to the exit.

        Raises:
            RuntimeError: If the maze has not been generated yet, or
                if no path to the exit can be found.
        """

        if not self._is_generated:
            raise RuntimeError("NOT possible to solve a non-generated maze.")

        # start_x, start_y = self.entry_coord
        # exit_x, exit_y = self.exit_coord
        start_x: int = self.entry_coord[0]
        start_y: int = self.entry_coord[1]
        exit_x: int = self.exit_coord[0]
        exit_y: int = self.exit_coord[1]

        to_explore = deque([(start_x, start_y, "")])

        already_met: set[tuple[int, int]] = {(start_x, start_y)}

        while to_explore:
            x, y, path = to_explore.popleft()

            if x == exit_x and y == exit_y:
                self._exit_path = path
                return path

            cell = self._grid[y][x]

            # --------------------------------------------------------------
            # for each direction, if NO wall and NOT on the grid's perimeter
            # and next cell NOT yet visited

            # North
            if not (cell & self.N) and y > 0\
                    and (x, y - 1) not in already_met:
                already_met.add((x, y - 1))
                to_explore.append((x, y - 1, path + 'N'))

            # East
            if not (cell & self.E) and x < self.width - 1\
                    and (x + 1, y) not in already_met:
                already_met.add((x + 1, y))
                to_explore.append((x + 1, y, path + 'E'))

            # South
            if not (cell & self.S) and y < self.height - 1\
                    and (x, y + 1) not in already_met:
                already_met.add((x, y + 1))
                to_explore.append((x, y + 1, path + 'S'))

            # West
            if not (cell & self.W) and x > 0\
                    and (x - 1, y) not in already_met:
                already_met.add((x - 1, y))
                to_explore.append((x - 1, y, path + 'W'))

        # reached empty deque without finding exit, the maze is broken...
        raise RuntimeError("No path to exit was found.")

    # ---------------------------------------------------------------------
    #
    # ---------------------------- EXPORT maze  ---------------------------
    #
    # ---------------------------------------------------------------------

    def export_to_file(self) -> None:
        """
        Export the maze and its solution to the mandatory text file
        """
        with open(self.output_file, 'w', encoding='utf-8') as new_file:
            # Write grid in hexa
            for row in self._grid:
                # f"{integer:X}" converts integer to uppercase hexa (10->A)
                line_str = "".join(f"{cell:X}" for cell in row)
                new_file.write(line_str + "\n")

            # mandatory empty line
            new_file.write("\n")

            # entrance coordinates
            new_file.write(f"{self.entry_coord[0]},{self.entry_coord[1]}\n")
            # exit coordinates
            new_file.write(f"{self.exit_coord[0]},{self.exit_coord[1]}\n")
            # path from entrance to exit
            new_file.write(f"{self._exit_path}\n")

    # ---------------------------------------------------------------------
    #
    # ----------------------- maze generation A to Z ----------------------
    #
    # ---------------------------------------------------------------------

    def generate(self) -> None:
        """Generate a maze.

        Raises:
            MazeGenError: If the generated maze does not comply with
                the mandatory internal rules.
        """

        self.generate_perfect_maze()

        if not self.perfect:
            self.make_imperfect()

        if not self.check_walls_integrity() or not self.free_of_open_areas():
            raise MazeGenError("Generated maze does not comply internal rules")

        self._exit_path = self.solve_maze()
        self.export_to_file()
