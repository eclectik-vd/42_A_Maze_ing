import argparse
import sys
import arcade
from pydantic import ValidationError
from src.maze_app.parsing.config_main import load_config
from src.maze_app.output.export import export_to_file
from src.mazegen import MazeGenerator
from src.maze_app.exceptions import MazeGenerationError
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
from src.maze_app.display.ascii_visualizer import AsciiVisualizer
from debug_utils import print_italic, print_green, debug_draw_maze


def main(config_path: str) -> None:
    # Load and validate maze config
    config = load_config(config_path)

    # -------------------- TODO ---------------------------------
    # --- GÉNÉRER LE LABYRINTHE AVEC LA CONFIG VALIDÉE ---

    # INSTANCIE le labyrinthe selon la config
    print_italic("\nGenerating the maze")
    try:
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            seed=config.seed,
            entry_coord=config.entry_coord,
            exit_coord=config.exit_coord
        )
    except ValueError as err:
        print(f"Error: Can't instantiate the maze, {err}", file=sys.stderr)
        sys.exit(1)

    # GENERE le labyrinthe
    maze.generate_perfect_maze()

    if not config.perfect:
        print_italic("Setting the maze to imperfect")
        try:
            maze.make_imperfect()
        except RuntimeError as err:
            print(f"Error: maze must be firstly generated, {err}",
                  file=sys.stderr)
            sys.exit(1)

    # VALIDE le labyrinthe
    # if mandatory rules not followed -> throw an exception
    if not maze.check_walls_integrity() or not maze.free_of_open_areas():
        raise MazeGenerationError("Generated maze does not comply with rules.")

    print_italic("The maze is compliant with mandatory rules")

    # -------------------- TODO ---------------------------------
    # --- AFFICHER LE LABYRINTHE
    if config.display_mode == "ascii":
        visualizer = AsciiVisualizer(maze)
        visualizer.update()
    elif config.display_mode == "arcade":
        window = arcade.Window(1280, 720,
                            "A-Maze-Ing",
                            fullscreen=False)
        visualizer = ArcadeVisualizer(maze)
        window.show_view(visualizer)
        arcade.run()

    # -------------------- TODO ---------------------------------
    # --- TROUVER LE CHEMIN LE PLUS COURT
    try:
        shortest_path: str = maze.solve_maze()
        print(shortest_path)
    except RuntimeError as err:
        print(f"Error: maze must be firstly generated, {err}",
              file=sys.stderr)
        sys.exit(1)

    # -------------------- TODO ---------------------------------
    # --- EXPORTER le labyrinthe et la solution dans un fichier texte
    # if not done yet, first solve: `shortest_path: str = maze.solve_maze()`
    export_to_file(maze.grid, maze.entry_coord, maze.exit_coord, shortest_path,
                   config.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mazegen execution script")
    parser.add_argument("config_path", type=str,
                        help="Path to the maze configuration file")

    args = parser.parse_args()
    main(args.config_path)
