import argparse
import sys
import arcade
from pydantic import ValidationError
from src.maze_app.parsing.config_main import load_config
from src.maze_app.output.export import export_to_file
from src.mazegen import MazeGenerator, MazeGenError
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
from src.maze_app.display.ascii_visualizer import AsciiVisualizer
from debug_utils import print_italic, print_green, debug_draw_maze


def main(config_path: str) -> None:
    # LOAD and VALIDATE maze config
    config = load_config(config_path)

    # INITIATES, CREATES, VALIDATES and SOLVE the maze
    print_italic("\nGenerating the maze...")
    try:
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            seed=config.seed,
            entry_coord=config.entry_coord,
            exit_coord=config.exit_coord,
            perfect=config.perfect,
        )
        maze.generate()
        print_italic("The generated maze is compliant with mandatory rules.")

    except (ValueError, RuntimeError, MazeGenError) as err:
        print(f"Error during maze processing: {err}", file=sys.stderr)
        sys.exit(1)

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

    # --- EXPORTER le labyrinthe et la solution dans un fichier texte
    # TODO if not done yet, first solve: `maze.solve_maze()`
    export_to_file(maze.grid, maze.entry_coord, maze.exit_coord,
                   maze.exit_path, config.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mazegen execution script")
    parser.add_argument("config_path", type=str,
                        help="Path to the maze configuration file")

    args = parser.parse_args()
    main(args.config_path)
