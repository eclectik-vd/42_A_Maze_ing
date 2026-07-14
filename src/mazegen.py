
"""
Maze Generator Module
=====================

This standalone module generates and solves perfect or imperfect mazes.
It is designed to be independent of any user interface.

Example of use:
-----------------------
    from mazegen import MazeGenerator

    # 1. Instantiation (width, height, entry, exit)
    maze = MazeGenerator(
                    width=10, height=10,
                    entry_coord=(0, 0), exit_coord=(9, 9),
                    seed=42
    )

    # 2. Generation
    maze.generate_perfect_maze()
    # Optional: creates loops
    maze.make_imperfect(percent_to_break=0.2)

    # 3. Solving
    path_to_exit = maze.solve_maze()

    # 4. Retrieving data for display
    # Returns a copy (to prevent accidental modifications) of the grid
    grid = maze.grid
"""

import random
import warnings
from collections import deque
from copy import deepcopy


class MazeGenerator:
    """ class for generating a maze with Recursive Backtracker """

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
        (4, 0), (5, 0), (6, 0), (6, 1), (4, 2), (5, 2), (6, 2), (4, 3),
        (4, 4), (5, 4), (6, 4)
    )
    # TODO: add function to calculate width and height
    PATTERN_WIDTH: int = 7
    PATTERN_HEIGHT: int = 5

    def __init__(
            self, width: int, height: int, entry_coord: tuple[int, int],
            exit_coord: tuple[int, int], seed: int | None = None
    ) -> None:

        # Validation des données entrantes (Fail Fast)
        if width < 3 or height < 3:
            raise ValueError("The maze size must not be less than 3x3.")

        self.width = width
        self.height = height
        self.entry_coord = entry_coord
        self.exit_coord = exit_coord
        # State check, to prevent access to a maze not yet generated
        self._is_generated = False

        # initialise random seed, if provided.
        # /!\ `if seed:` would be dangerous, because `seed = 0` ... == False
        if seed is not None:
            random.seed(seed)

        # Initialize the grid, with 4 walls for each cell
        self._grid: list[list[int]] = [[self.ALL_WALLS for _ in range(width)]
                                       for _ in range(height)]

        # Initialize an empty set, to store pattern 42 coordinates
        # (searching in a `set` takes O(1) time, much faster than a list)
        self.pattern_cells: set[tuple[int, int]] = set()

        # initialize an empty string, to store step by step the shortest way
        # between entry and exit
        self._exit_path: str = ""

    @property
    def grid(self) -> list[list[int]]:
        """
        Returns a deep copy of the grid (`grid` = read-only property):
        encapsulation prevents calling code from corrupting internal state.
        """
        return deepcopy(self._grid)

    @property
    def exit_path(self) -> str:
        """ Read-only permission to access the path between entry and exit."""
        return self._exit_path

    def _break_wall(self, x: int, y: int, direction: int) -> None:
        """
        Break the wall of cell (x, y) in the given direction,
        and break the opposite wall of adjacent cell
        """

        # The binary AND NOT operator `&= ~` removes a specific bit :
        # Ex: North wall = 0001 => ~N gives 1110 => 1111 & 1110 = 1110
        #     => North wall is broken :D

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

    # Do NOT call this _method outside the class
    def _get_unvisited_adjacents(
            self, x: int, y: int) -> list[tuple[int, int, int]]:
        """
        Look around cell (x, y)

        Return:
        the list of unvisited and valid adjacent cells,
        each adjacent is returned as a tuple: (adj_x, adj_y, direction_to_go)
        """

        adjacents: list[tuple[int, int, int]] = []

        # For each direction, 3 conditions to check:
        # do not go beyond the grid boundaries;
        # adjacent cell is intact (ALL_WALLS), so has not been visited yet;
        # adjacent cell is not reserved by pattern 42.

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

    # Do NOT call this _method outside the class
    def _apply_42_pattern(self) -> None:
        """
        Try to set '42' pattern in the center of the grid and lock the cells.
        Will NOT set the pattern :
            if grid too small or
            if collision between pattern and entry/exit
        """

        # check maze size is sufficient for this pattern
        if (self.width < self.PATTERN_WIDTH + 2
                or self.height < self.PATTERN_HEIGHT + 2):
            # calling script will handle this alert and display in the terminal
            warnings.warn("This maze is too small to display the '42' pattern")
            return

        # Calculating starting coordinates to centre the pattern
        pattern_x = (self.width - self.PATTERN_WIDTH) // 2
        pattern_y = (self.height - self.PATTERN_HEIGHT) // 2

        # convert relative coordinates into absolute coordinates on the grid
        grid_pattern_cells = {
            (pattern_x + dx, pattern_y + dy) for dx, dy in self.PATTERN_42
        }

        # check there is NO collision between pattern and entry/exit
        if (self.entry_coord in grid_pattern_cells
                or self.exit_coord in grid_pattern_cells):
            # calling script will handle this alert and display in the terminal
            warnings.warn("'42' pattern overlaps the entrance or exit. "
                          "It will be ignored.")
            return

        # Recording prohibited cells, so the algorithm will avoid them
        self.pattern_cells = grid_pattern_cells

    def generate_perfect_maze(self) -> None:
        """
        Generate a perfect maze using the "Recursive Backtracker" algorithm

        Args:
            start_x (int): starting X coordinate (default 0)
            start_y (int): starting Y coordinate (default 0)
        """

        # try to place '42' pattern
        self._apply_42_pattern()

        start_x, start_y = self.entry_coord

        # Initialising the stack for backtracking.
        stack: list[tuple[int, int]] = [(start_x, start_y)]

        # Main loop: as long as remains cells in the stack
        while stack:
            # get current cell (last added) coordinates, without removing it
            current_x, current_y = stack[-1]
            # get all available adjacents
            adjacents = self._get_unvisited_adjacents(current_x, current_y)

            if adjacents:
                # pick a random adjacent
                next_x, next_y, direction = random.choice(adjacents)

                # break the wall between current and next
                self._break_wall(current_x, current_y, direction)

                # add next to the stack, so it becomes the new current cell.
                stack.append((next_x, next_y))

            else:
                # dead-end => backtrack : pop current cell out of the stack
                stack.pop()

        # status update
        self._is_generated = True

    def make_imperfect(self, percent_to_break: float = 0.4) -> None:
        """
        Make the maze imperfect by breaking random dead end walls

        Raise RuntimeError if maze NOT generated yet
        """

        # state check (Guard Clause)
        if not self._is_generated:
            raise RuntimeError("NOT possible to make imperfect"
                               "a non-generated maze.")

        # values that refer to cells that are dead ends :
        # which has exactly 3 closed walls and 1 open wall
        corridor_ends = (
            self.ALL_WALLS & ~self.N,  # (1110)
            self.ALL_WALLS & ~self.E,  # (1101)
            self.ALL_WALLS & ~self.S,  # (1011)
            self.ALL_WALLS & ~self.W   # (0111)
        )

        # search and store all dead ends except in 42 pattern
        dead_ends: list[tuple[int, int]] = [
            (x, y) for y in range(self.height) for x in range(self.width)
            if self._grid[y][x] in corridor_ends
            and (x, y) not in self.pattern_cells
        ]

        # count the number of dead ends to be opened
        nb_walls_to_break = int(len(dead_ends) * percent_to_break)

        # Shuffle the list to break random walls
        random.shuffle(dead_ends)

        # iterate over the number of walls to break, to open dead-ends
        for x, y in dead_ends[:nb_walls_to_break]:
            cell = self._grid[y][x]
            may_be_broken = []

            # checks which walls exist (`&` checks if the bit/wall is set)
            # and are NOT on the grid's perimeter, neither next the 42 pattern

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
                self._break_wall(x, y, random.choice(may_be_broken))

    def check_walls_integrity(self) -> bool:
        """
        Checks all walls are consistent between adjacent cells
        Returns True if the grid is valid, else False
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                # check East|West, ie with right adjacent
                if x < self.width - 1:
                    adjacent_E = self.grid[y][x + 1]

                    # East wall of current cell and west wall of cell at right
                    # MUST have same open/close state
                    if bool(cell & self.E) != bool(adjacent_E & self.W):
                        warnings.warn("East–West inconsistency "
                                      f"between ({x},{y}) and ({x+1},{y})")
                        return False

                # check Sud|North, ie with bottom adjacent
                if y < self.height - 1:
                    adjacent_S = self.grid[y + 1][x]

                    # South wall of current cell and north wall of bottom cell
                    # MUST have same open/close state
                    if bool(cell & self.S) != bool(adjacent_S & self.N):
                        warnings.warn("South–North inconsistency "
                                      f"between ({x},{y}) and ({x},{y+1})")
                        return False

        return True

    def check_no_large_areas(self) -> bool:
        """
        Check if there is open area of 3x3 cells or larger
        Return True if the maze is valid, False if a 3x3 area is found
        """

        # The maze is smaller than 3x3, so it's impossible to have such an area
        if self.width < 3 or self.height < 3:
            return True

        # traverse the grid, stopping 2 squares before the end
        # to avoid going off the grid when viewing at +2 in X and +2 in Y
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                # assume there is no wall in this 3x3 area being checking
                is_3x3_open = True

                # check internal walls in this 3x3 square
                for range_y in range(3):
                    for range_x in range(3):
                        cell = self.grid[y + range_y][x + range_x]

                        # if an internal wall (east or south) is found,
                        # area is not fully open => break to go check next area
                        if ((range_x < 2 and (cell & self.E))
                                or (range_y < 2 and (cell & self.S))):
                            is_3x3_open = False
                            break
                    if not is_3x3_open:
                        break

                # no wall found, so this 3x3 area is really open '(
                if is_3x3_open:
                    warnings.warn(f"open area detected at ({x},{y})")
                    return False

        return True

    def reset(self) -> None:
        """ Clear internal state of the maze in memory """
        self._grid = [[self.ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)]
        self.pattern_cells.clear()
        self._exit_path = ""
        self._is_generated = False

    def regenerate_perfect_maze(self, new_seed: int | None = None) -> None:
        """
        shortcut for Enzo :)
            Reset and regenerate the maze with new seed if provided
        """
        if new_seed is not None:
            random.seed(new_seed)

        self.reset()
        self.generate_perfect_maze()

    def solve_maze(self) -> str:
        """
        Use BFS to find the shortest path between the entrance and the exit

        Starting with entry cell, explore the grid using :
        visited_yet, a set to store the coordonates of explored cells
        to_visit, a queue to store, for each visited cell, the path from entry

        Raise RuntimeError:
            if maze NOT generated yet
            if NO path to exit can be found

        Returns:
        a string containing directions (N, E, S, W) step-by-step to exit
        """

        # state check (Guard Clause)
        if not self._is_generated:
            raise RuntimeError("NOT possible to solve a non-generated maze.")

        # start_x, start_y = self.entry_coord
        # exit_x, exit_y = self.exit_coord
        start_x: int = self.entry_coord[0]
        start_y: int = self.entry_coord[1]
        exit_x: int = self.exit_coord[0]
        exit_y: int = self.exit_coord[1]

        # store (x, y, distance_traveled) for each cell, for grid exploration
        # to_visit: list[tuple[int, int, str]] = [(start_x, start_y, "")]
        to_visit = deque([(start_x, start_y, "")])

        # store cells alreay visited coordinates, to NOT visit again
        visited_yet: set[tuple[int, int]] = {(start_x, start_y)}

        while to_visit:
            # remove oldest cell from to_visit
            x, y, path = to_visit.popleft()

            # check if exit is reached
            if x == exit_x and y == exit_y:
                self._exit_path = path
                return path

            # get current cell walls data, to explore the 4 directions
            cell = self._grid[y][x]

            # for each direction, if NO wall and NOT on the grid's perimeter
            # and next cell NOT yet visited

            # North
            if not (cell & self.N) and y > 0\
                    and (x, y - 1) not in visited_yet:
                visited_yet.add((x, y - 1))
                to_visit.append((x, y - 1, path + 'N'))

            # East
            if not (cell & self.E) and x < self.width - 1\
                    and (x + 1, y) not in visited_yet:
                visited_yet.add((x + 1, y))
                to_visit.append((x + 1, y, path + 'E'))

            # South
            if not (cell & self.S) and y < self.height - 1\
                    and (x, y + 1) not in visited_yet:
                visited_yet.add((x, y + 1))
                to_visit.append((x, y + 1, path + 'S'))

            # West
            if not (cell & self.W) and x > 0\
                    and (x - 1, y) not in visited_yet:
                visited_yet.add((x - 1, y))
                to_visit.append((x - 1, y, path + 'W'))

        # reached empty deque without finding exit, the maze is broken...
        raise RuntimeError("No path to exit was found.")
