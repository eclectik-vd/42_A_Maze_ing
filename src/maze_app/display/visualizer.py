from src.mazegen import MazeGenerator

class Visualizer:
    def __init__(self, mazegen: MazeGenerator):
        self.maze: list = mazegen.grid.copy()
        self.maze_width: int = mazegen.width
        self.maze_height: int = mazegen.height
        self.entry: list = mazegen.entry_coord
        self.exit: list = mazegen.exit_coord
        self.path: str = mazegen.solve_maze()
        self.have_path: bool = False
        self.mazegen = mazegen
        


