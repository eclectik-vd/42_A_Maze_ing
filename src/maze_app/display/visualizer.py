from src.mazegen import MazeGenerator


class Visualizer:
    """Base class for maze visualization implementations.

    Serves as an abstract base class for different visualization modes
    (ASCII, Arcade, etc.). Stores the maze grid, dimensions, entry/exit
    coordinates, and pathfinding solution. Subclasses extend this class
    to implement specific rendering strategies.

    Attributes:
        mazegen (MazeGenerator): Reference to the maze generator instance.
        maze (list[list[int]]): A deep copy of the 2D grid of maze cells.
            Each cell contains information about the walls.
            Must be refreshed after a maze regeneration.
        path (str): Solution path as a string of direction letters
            (N/S/E/W). Must be refreshed after a maze regeneration.
        maze_width (int): Number of columns in the maze grid.
        maze_height (int): Number of rows in the maze grid.
        entry (tuple[int, int]): Entry point coordinates (x, y).
        exit (tuple[int, int]): Exit point coordinates (x, y).
        have_path (bool): Flag for whether to display the path solution.
    """

    def __init__(self, mazegen: MazeGenerator) -> None:
        """Initialize the base visualizer with maze data.

        Copies the maze grid from the generator, extracts maze dimensions,
        entry/exit coordinates, and the solution path. Initializes the
        path display flag to False.

        Args:
            mazegen (MazeGenerator): The maze generator instance containing
                grid, width, height, entry/exit coordinates, exit_path.
        """

        self.mazegen: MazeGenerator = mazegen
        self.maze: list[list[int]] = mazegen.grid
        self.path: str = mazegen.exit_path
        self.maze_width: int = mazegen.width
        self.maze_height: int = mazegen.height
        self.entry: tuple[int, int] = mazegen.entry_coord
        self.exit: tuple[int, int] = mazegen.exit_coord
        self.have_path: bool = False
